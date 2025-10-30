"""
消息路由器
负责事件驱动架构中的消息路由、队列管理和异步处理
"""
import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from .config_manager import get_config
from .auth_manager import get_auth_manager

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型"""
    # 知识库事件
    KB_UPDATED = "coffee.salon.knowledge.update"
    KB_CREATED = "coffee.salon.knowledge.created"
    KB_DELETED = "coffee.salon.knowledge.deleted"
    
    # 检索事件
    RAG_COMPLETED = "coffee.salon.rag.completed"
    RAG_FAILED = "coffee.salon.rag.failed"
    
    # 审稿事件
    REVIEW_APPROVED = "coffee.salon.review.approved"
    REVIEW_REJECTED = "coffee.salon.review.rejected"
    REVIEW_SUBMITTED = "coffee.salon.review.submitted"
    
    # 打印事件
    PRINT_COMPLETED = "coffee.salon.print.completed"
    PRINT_FAILED = "coffee.salon.print.failed"
    PRINT_STARTED = "coffee.salon.print.started"
    
    # 认证事件
    AUTH_LOGIN = "coffee.salon.auth.login"
    AUTH_LOGOUT = "coffee.salon.auth.logout"
    AUTH_FAILED = "coffee.salon.auth.failed"
    
    # 系统事件
    SYSTEM_ERROR = "coffee.salon.system.error"
    SYSTEM_HEALTH = "coffee.salon.system.health"


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """事件对象"""
    event_id: str
    event_type: EventType
    tenant_id: str
    user_id: Optional[str]
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    idempotency_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """从字典创建事件"""
        data['event_type'] = EventType(data['event_type'])
        data['priority'] = EventPriority(data['priority'])
        return cls(**data)


@dataclass
class Subscription:
    """订阅配置"""
    subscription_id: str
    event_types: List[EventType]
    callback: Callable[[Event], Any]
    filter_func: Optional[Callable[[Event], bool]] = None
    max_concurrent: int = 10
    retry_policy: Dict[str, Any] = field(default_factory=dict)


class MessageRouter:
    """消息路由器"""
    
    def __init__(self):
        self.config = get_config()
        self.mq_config = self.config.message_queue
        self.auth_manager = get_auth_manager()
        
        # 订阅者管理
        self._subscriptions: Dict[str, Subscription] = {}
        self._event_handlers: Dict[EventType, List[Subscription]] = {}
        
        # 事件队列
        self._event_queue = asyncio.Queue()
        self._dead_letter_queue = asyncio.Queue()
        
        # 运行状态
        self._running = False
        self._workers: List[asyncio.Task] = []
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # 统计信息
        self._stats = {
            'events_processed': 0,
            'events_failed': 0,
            'events_retried': 0,
            'subscribers_count': 0
        }
    
    async def start(self):
        """启动消息路由器"""
        if self._running:
            return
        
        logger.info("启动消息路由器")
        self._running = True
        
        # 启动工作线程
        worker_count = 5
        for i in range(worker_count):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(task)
        
        # 启动死信队列处理器
        dlq_task = asyncio.create_task(self._dead_letter_worker())
        self._workers.append(dlq_task)
        
        # 启动统计报告任务
        stats_task = asyncio.create_task(self._stats_reporter())
        self._workers.append(stats_task)
    
    async def stop(self):
        """停止消息路由器"""
        if not self._running:
            return
        
        logger.info("停止消息路由器")
        self._running = False
        
        # 取消所有工作任务
        for task in self._workers:
            task.cancel()
        
        # 等待所有任务完成
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        # 关闭线程池
        self._executor.shutdown(wait=True)
    
    def subscribe(self, subscription: Subscription) -> str:
        """订阅事件"""
        self._subscriptions[subscription.subscription_id] = subscription
        
        # 注册事件处理器
        for event_type in subscription.event_types:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(subscription)
        
        self._stats['subscribers_count'] = len(self._subscriptions)
        logger.info(f"订阅事件: {subscription.subscription_id} -> {[et.value for et in subscription.event_types]}")
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        if subscription_id not in self._subscriptions:
            return False
        
        subscription = self._subscriptions[subscription_id]
        
        # 移除事件处理器
        for event_type in subscription.event_types:
            if event_type in self._event_handlers:
                self._event_handlers[event_type] = [
                    sub for sub in self._event_handlers[event_type]
                    if sub.subscription_id != subscription_id
                ]
        
        del self._subscriptions[subscription_id]
        self._stats['subscribers_count'] = len(self._subscriptions)
        logger.info(f"取消订阅: {subscription_id}")
        return True
    
    async def publish_event(self, event: Event) -> bool:
        """发布事件"""
        try:
            # 设置幂等性键
            if not event.idempotency_key:
                event.idempotency_key = f"{event.event_type.value}:{hash(str(event.payload))}"
            
            # 添加追踪信息
            event.metadata.update({
                'router_timestamp': time.time(),
                'source': 'message_router'
            })
            
            # 放入事件队列
            await self._event_queue.put(event)
            logger.debug(f"发布事件: {event.event_type.value} (ID: {event.event_id})")
            return True
            
        except Exception as e:
            logger.error(f"发布事件失败: {e}")
            return False
    
    async def publish(self, event_type: EventType, tenant_id: str, payload: Dict[str, Any],
                     user_id: Optional[str] = None, priority: EventPriority = EventPriority.NORMAL) -> str:
        """便捷发布方法"""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            tenant_id=tenant_id,
            user_id=user_id,
            payload=payload,
            priority=priority
        )
        
        await self.publish_event(event)
        return event.event_id
    
    async def _worker(self, worker_id: str):
        """工作线程"""
        logger.info(f"启动工作线程: {worker_id}")
        
        while self._running:
            try:
                # 获取事件
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # 处理事件
                await self._process_event(event, worker_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"工作线程 {worker_id} 错误: {e}")
    
    async def _process_event(self, event: Event, worker_id: str):
        """处理事件"""
        try:
            # 查找匹配的订阅者
            subscribers = self._event_handlers.get(event.event_type, [])
            
            if not subscribers:
                logger.warning(f"没有找到事件 {event.event_type.value} 的订阅者")
                return
            
            # 并发处理事件（受限于每个订阅者的并发限制）
            tasks = []
            for subscription in subscribers:
                # 应用过滤器
                if subscription.filter_func and not subscription.filter_func(event):
                    continue
                
                # 创建处理任务
                task = asyncio.create_task(
                    self._handle_event_with_subscription(event, subscription, worker_id)
                )
                tasks.append(task)
            
            # 等待所有任务完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            self._stats['events_processed'] += 1
            
        except Exception as e:
            logger.error(f"处理事件失败: {e}")
            self._stats['events_failed'] += 1
    
    async def _handle_event_with_subscription(self, event: Event, subscription: Subscription, worker_id: str):
        """使用订阅者处理事件"""
        try:
            # 在线程池中执行回调（避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                subscription.callback,
                event
            )
            
            logger.debug(f"事件 {event.event_id} 由订阅者 {subscription.subscription_id} 处理完成")
            
        except Exception as e:
            logger.error(f"订阅者 {subscription.subscription_id} 处理事件失败: {e}")
            
            # 检查是否需要重试
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                self._stats['events_retried'] += 1
                
                # 延迟重试
                delay = 2 ** event.retry_count  # 指数退避
                await asyncio.sleep(delay)
                await self._event_queue.put(event)
                
                logger.info(f"事件 {event.event_id} 将在 {delay} 秒后重试 (第 {event.retry_count} 次)")
            else:
                # 放入死信队列
                await self._dead_letter_queue.put(event)
                logger.error(f"事件 {event.event_id} 达到最大重试次数，放入死信队列")
    
    async def _dead_letter_worker(self):
        """死信队列处理器"""
        logger.info("启动死信队列处理器")
        
        while self._running:
            try:
                event = await asyncio.wait_for(self._dead_letter_queue.get(), timeout=1.0)
                
                # 记录死信事件
                logger.error(f"死信事件: {event.event_type.value} (ID: {event.event_id})")
                
                # 发送告警（实际实现中可以发送到监控系统）
                await self._send_dlq_alert(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"死信队列处理器错误: {e}")
    
    async def _send_dlq_alert(self, event: Event):
        """发送死信队列告警"""
        alert_data = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'tenant_id': event.tenant_id,
            'retry_count': event.retry_count,
            'payload': event.payload,
            'timestamp': event.timestamp
        }
        
        logger.critical(f"死信队列告警: {json.dumps(alert_data, indent=2)}")
    
    async def _stats_reporter(self):
        """统计报告器"""
        while self._running:
            await asyncio.sleep(60)  # 每分钟报告一次
            
            if self._stats['events_processed'] > 0:
                logger.info(f"消息路由器统计: {self._stats}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            'queue_size': self._event_queue.qsize(),
            'dlq_size': self._dead_letter_queue.qsize(),
            'subscribers_count': len(self._subscriptions),
            'running': self._running
        }
    
    async def get_events_by_type(self, event_type: EventType, limit: int = 100) -> List[Event]:
        """获取指定类型的事件（用于调试）"""
        # 这是一个简化实现，实际生产环境中应该查询持久化存储
        events = []
        # TODO: 实现事件查询逻辑
        return events
    
    async def replay_event(self, event_id: str) -> bool:
        """重放事件（用于调试和恢复）"""
        # TODO: 实现事件重放逻辑
        logger.info(f"重放事件: {event_id}")
        return True


class EventPublisher:
    """事件发布器"""
    
    def __init__(self, router: MessageRouter):
        self.router = router
    
    async def publish_knowledge_updated(self, tenant_id: str, kb_id: str, version: str, user_id: str = None):
        """发布知识库更新事件"""
        await self.router.publish(
            EventType.KB_UPDATED,
            tenant_id,
            {
                'kb_id': kb_id,
                'version': version,
                'action': 'updated'
            },
            user_id
        )
    
    async def publish_rag_completed(self, tenant_id: str, query_id: str, references: List[str], user_id: str = None):
        """发布RAG完成事件"""
        await self.router.publish(
            EventType.RAG_COMPLETED,
            tenant_id,
            {
                'query_id': query_id,
                'references': references,
                'completion_time': time.time()
            },
            user_id
        )
    
    async def publish_review_approved(self, tenant_id: str, report_id: str, version: str, user_id: str = None):
        """发布审稿通过事件"""
        await self.router.publish(
            EventType.REVIEW_APPROVED,
            tenant_id,
            {
                'report_id': report_id,
                'version': version,
                'approval_time': time.time()
            },
            user_id
        )
    
    async def publish_print_completed(self, tenant_id: str, ticket_id: str, device_id: str, user_id: str = None):
        """发布打印完成事件"""
        await self.router.publish(
            EventType.PRINT_COMPLETED,
            tenant_id,
            {
                'ticket_id': ticket_id,
                'device_id': device_id,
                'completion_time': time.time()
            },
            user_id
        )
    
    async def publish_auth_login(self, tenant_id: str, user_id: str, ip_address: str):
        """发布登录事件"""
        await self.router.publish(
            EventType.AUTH_LOGIN,
            tenant_id,
            {
                'user_id': user_id,
                'ip_address': ip_address,
                'login_time': time.time()
            },
            user_id
        )


# 全局消息路由器实例
_message_router: Optional[MessageRouter] = None


def get_message_router() -> MessageRouter:
    """获取全局消息路由器实例"""
    global _message_router
    if _message_router is None:
        _message_router = MessageRouter()
    return _message_router


def get_event_publisher() -> EventPublisher:
    """获取事件发布器"""
    return EventPublisher(get_message_router())