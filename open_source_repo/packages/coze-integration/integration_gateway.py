"""
集成网关服务
作为整个系统的主要入口点，提供统一的API接口和协调各组件
"""
import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager

from .config_manager import get_config
from .auth_manager import get_auth_manager, get_permission_manager, User, Permission
from .coze_client import CozeAPIClient, ChatRequest
from .kai_manager import get_agent_manager, TaskContext, TaskPriority, AgentType
from .message_router import get_message_router, get_event_publisher, EventType
from .config_manager import SystemConfig

logger = logging.getLogger(__name__)


class APIEndpoint(Enum):
    """API端点"""
    # 查询相关
    QUERY = "/v1/query"
    QUERY_STREAM = "/v1/query/stream"
    
    # 智能体相关
    AGENTS_LIST = "/v1/agents"
    AGENTS_DISPATCH = "/v1/agents/dispatch"
    AGENTS_STATUS = "/v1/agents/status"
    
    # 检索相关
    RAG_RETRIEVE = "/v1/rag/retrieve"
    RAG_SEARCH = "/v1/rag/search"
    
    # 知识库相关
    KB_CREATE = "/v1/kb/create"
    KB_UPDATE = "/v1/kb/update"
    KB_QUERY = "/v1/kb/query"
    
    # 打印相关
    PRINT_TICKET = "/v1/print/ticket"
    PRINT_STATUS = "/v1/print/status"
    
    # 审稿相关
    REVIEW_SUBMIT = "/v1/review/submit"
    REVIEW_APPROVE = "/v1/review/approve"
    REVIEW_QUERY = "/v1/review/query"
    
    # 系统相关
    SYSTEM_HEALTH = "/v1/system/health"
    SYSTEM_METRICS = "/v1/system/metrics"
    SYSTEM_AUDIT = "/v1/system/audit"


@dataclass
class APIRequest:
    """API请求"""
    request_id: str
    endpoint: APIEndpoint
    method: str
    user: Optional[User]
    tenant_id: str
    data: Dict[str, Any]
    headers: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class APIResponse:
    """API响应"""
    request_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    execution_time: float = 0.0


class IntegrationGateway:
    """集成网关服务"""
    
    def __init__(self):
        self.config = get_config()
        self.auth_manager = get_auth_manager()
        self.permission_manager = get_permission_manager()
        self.coze_client = CozeAPIClient()
        self.agent_manager = get_agent_manager()
        self.message_router = get_message_router()
        self.event_publisher = get_event_publisher()
        
        # 路由表
        self._routes: Dict[APIEndpoint, callable] = {
            APIEndpoint.QUERY: self._handle_query,
            APIEndpoint.QUERY_STREAM: self._handle_query_stream,
            APIEndpoint.AGENTS_LIST: self._handle_agents_list,
            APIEndpoint.AGENTS_DISPATCH: self._handle_agents_dispatch,
            APIEndpoint.AGENTS_STATUS: self._handle_agents_status,
            APIEndpoint.RAG_RETRIEVE: self._handle_rag_retrieve,
            APIEndpoint.RAG_SEARCH: self._handle_rag_search,
            APIEndpoint.KB_CREATE: self._handle_kb_create,
            APIEndpoint.KB_UPDATE: self._handle_kb_update,
            APIEndpoint.KB_QUERY: self._handle_kb_query,
            APIEndpoint.PRINT_TICKET: self._handle_print_ticket,
            APIEndpoint.PRINT_STATUS: self._handle_print_status,
            APIEndpoint.REVIEW_SUBMIT: self._handle_review_submit,
            APIEndpoint.REVIEW_APPROVE: self._handle_review_approve,
            APIEndpoint.REVIEW_QUERY: self._handle_review_query,
            APIEndpoint.SYSTEM_HEALTH: self._handle_system_health,
            APIEndpoint.SYSTEM_METRICS: self._handle_system_metrics,
            APIEndpoint.SYSTEM_AUDIT: self._handle_system_audit,
        }
        
        # 统计信息
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'requests_per_minute': [],
            'endpoint_stats': {}
        }
    
    async def start(self):
        """启动网关服务"""
        logger.info("启动集成网关服务")
        
        # 启动各个组件
        await self.message_router.start()
        await self.agent_manager.start()
        
        logger.info("集成网关服务启动完成")
    
    async def stop(self):
        """停止网关服务"""
        logger.info("停止集成网关服务")
        
        # 停止各个组件
        await self.agent_manager.stop()
        await self.message_router.stop()
        
        logger.info("集成网关服务已停止")
    
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """处理API请求"""
        start_time = time.time()
        request_id = request.request_id
        
        try:
            # 更新统计
            self._stats['total_requests'] += 1
            
            # 认证检查
            if not await self._authenticate_request(request):
                return APIResponse(
                    request_id=request_id,
                    success=False,
                    error="认证失败",
                    error_code="AUTH_FAILED"
                )
            
            # 权限检查
            if not await self._authorize_request(request):
                return APIResponse(
                    request_id=request_id,
                    success=False,
                    error="权限不足",
                    error_code="PERMISSION_DENIED"
                )
            
            # 路由处理
            handler = self._routes.get(request.endpoint)
            if not handler:
                return APIResponse(
                    request_id=request_id,
                    success=False,
                    error=f"未知的端点: {request.endpoint.value}",
                    error_code="UNKNOWN_ENDPOINT"
                )
            
            # 执行处理逻辑
            result = await handler(request)
            
            # 更新统计
            self._stats['successful_requests'] += 1
            execution_time = time.time() - start_time
            self._update_response_time(execution_time)
            
            return APIResponse(
                request_id=request_id,
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            self._stats['failed_requests'] += 1
            
            return APIResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def _authenticate_request(self, request: APIRequest) -> bool:
        """认证请求"""
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header[7:]  # 移除 'Bearer ' 前缀
        
        # 验证令牌
        user = self.auth_manager.verify_access_token(token)
        if not user:
            return False
        
        # 绑定用户到请求
        request.user = user
        
        # 记录登录事件
        await self.event_publisher.publish_auth_login(
            request.tenant_id,
            user.user_id,
            request.headers.get('X-Forwarded-For', 'unknown')
        )
        
        return True
    
    async def _authorize_request(self, request: APIRequest) -> bool:
        """授权请求"""
        if not request.user:
            return False
        
        # 根据端点检查权限
        endpoint_permissions = {
            APIEndpoint.QUERY: Permission.SEARCH_READ,
            APIEndpoint.QUERY_STREAM: Permission.SEARCH_READ,
            APIEndpoint.AGENTS_LIST: Permission.SYSTEM_ADMIN,
            APIEndpoint.AGENTS_DISPATCH: Permission.SYSTEM_ADMIN,
            APIEndpoint.RAG_RETRIEVE: Permission.SEARCH_READ,
            APIEndpoint.KB_CREATE: Permission.KB_WRITE,
            APIEndpoint.KB_UPDATE: Permission.KB_WRITE,
            APIEndpoint.PRINT_TICKET: Permission.PRINT_WRITE,
            APIEndpoint.REVIEW_SUBMIT: Permission.REVIEW_WRITE,
            APIEndpoint.REVIEW_APPROVE: Permission.REVIEW_APPROVE,
            APIEndpoint.SYSTEM_HEALTH: Permission.SYSTEM_ADMIN,
            APIEndpoint.SYSTEM_METRICS: Permission.SYSTEM_ADMIN,
            APIEndpoint.SYSTEM_AUDIT: Permission.SYSTEM_AUDIT,
        }
        
        required_permission = endpoint_permissions.get(request.endpoint)
        if required_permission:
            return self.auth_manager.check_permission(
                request.user, required_permission, request.tenant_id
            )
        
        return True
    
    # ==================== 处理器实现 ====================
    
    async def _handle_query(self, request: APIRequest) -> Dict[str, Any]:
        """处理查询请求"""
        query = request.data.get('query', '')
        context = request.data.get('context', {})
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            user_id=request.user.user_id if request.user else None,
            metadata={'request_id': request.request_id}
        )
        
        # 创建问答任务
        task = self.agent_manager.create_task(
            task_type="qna",
            agent_type=AgentType.QNA_AGENT,
            input_data={
                'question': query,
                'context': context
            },
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        # 提交任务
        success = await self.agent_manager.submit_task(task)
        if not success:
            raise Exception("任务提交失败")
        
        # 等待任务完成
        while True:
            task_status = self.agent_manager.get_task_status(task.task_id)
            if task_status and task_status.status.value in ['completed', 'failed']:
                break
            await asyncio.sleep(0.1)
        
        if task_status.status.value == 'failed':
            raise Exception(f"任务执行失败: {task_status.error_message}")
        
        return {
            'task_id': task.task_id,
            'answer': task.output_data.get('answer', ''),
            'context': context,
            'timestamp': time.time()
        }
    
    async def _handle_query_stream(self, request: APIRequest) -> Dict[str, Any]:
        """处理流式查询请求"""
        # 流式处理逻辑（简化实现）
        query = request.data.get('query', '')
        return {'stream_url': f'/v1/stream/{request.request_id}', 'query': query}
    
    async def _handle_agents_list(self, request: APIRequest) -> Dict[str, Any]:
        """处理智能体列表请求"""
        stats = self.agent_manager.get_stats()
        return {
            'agents': stats['agent_types'],
            'total_agents': stats['total_agents'],
            'timestamp': time.time()
        }
    
    async def _handle_agents_dispatch(self, request: APIRequest) -> Dict[str, Any]:
        """处理智能体调度请求"""
        task_type = request.data.get('task_type', 'qna')
        input_data = request.data.get('input_data', {})
        
        # 映射任务类型到智能体类型
        type_mapping = {
            'research': AgentType.RESEARCHER,
            'evaluation': AgentType.EVALUATOR,
            'summary': AgentType.SUMMARIZER,
            'qna': AgentType.QNA_AGENT,
            'print': AgentType.PRINT_AGENT
        }
        
        agent_type = type_mapping.get(task_type, AgentType.QNA_AGENT)
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            user_id=request.user.user_id if request.user else None,
            metadata={'request_id': request.request_id}
        )
        
        # 创建任务
        task = self.agent_manager.create_task(
            task_type=task_type,
            agent_type=agent_type,
            input_data=input_data,
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        # 提交任务
        success = await self.agent_manager.submit_task(task)
        if not success:
            raise Exception("任务提交失败")
        
        return {
            'task_id': task.task_id,
            'task_type': task_type,
            'agent_type': agent_type.value,
            'status': task.status.value,
            'timestamp': time.time()
        }
    
    async def _handle_agents_status(self, request: APIRequest) -> Dict[str, Any]:
        """处理智能体状态查询"""
        task_id = request.data.get('task_id')
        if not task_id:
            raise Exception("缺少task_id参数")
        
        task = self.agent_manager.get_task_status(task_id)
        if not task:
            raise Exception("任务不存在")
        
        return {
            'task_id': task.task_id,
            'status': task.status.value,
            'progress': self._calculate_progress(task),
            'output_data': task.output_data,
            'error_message': task.error_message,
            'timestamp': time.time()
        }
    
    async def _handle_rag_retrieve(self, request: APIRequest) -> Dict[str, Any]:
        """处理RAG检索请求"""
        query = request.data.get('query', '')
        
        # 模拟RAG检索
        references = [f"ref_{i}" for i in range(3)]
        
        # 发布检索完成事件
        await self.event_publisher.publish_rag_completed(
            request.tenant_id,
            request.request_id,
            references,
            request.user.user_id if request.user else None
        )
        
        return {
            'query': query,
            'references': references,
            'retrieval_time': time.time(),
            'timestamp': time.time()
        }
    
    async def _handle_rag_search(self, request: APIRequest) -> Dict[str, Any]:
        """处理RAG搜索请求"""
        # 简化实现
        return {'results': [], 'total': 0, 'timestamp': time.time()}
    
    async def _handle_kb_create(self, request: APIRequest) -> Dict[str, Any]:
        """处理知识库创建"""
        name = request.data.get('name', '')
        description = request.data.get('description', '')
        
        # 发布知识库更新事件
        await self.event_publisher.publish_knowledge_updated(
            request.tenant_id,
            request.request_id,
            "v1.0",
            request.user.user_id if request.user else None
        )
        
        return {
            'kb_id': request.request_id,
            'name': name,
            'description': description,
            'version': "v1.0",
            'timestamp': time.time()
        }
    
    async def _handle_kb_update(self, request: APIRequest) -> Dict[str, Any]:
        """处理知识库更新"""
        kb_id = request.data.get('kb_id', '')
        version = request.data.get('version', 'v1.1')
        
        await self.event_publisher.publish_knowledge_updated(
            request.tenant_id,
            kb_id,
            version,
            request.user.user_id if request.user else None
        )
        
        return {
            'kb_id': kb_id,
            'version': version,
            'timestamp': time.time()
        }
    
    async def _handle_kb_query(self, request: APIRequest) -> Dict[str, Any]:
        """处理知识库查询"""
        # 简化实现
        return {'results': [], 'total': 0, 'timestamp': time.time()}
    
    async def _handle_print_ticket(self, request: APIRequest) -> Dict[str, Any]:
        """处理打印票据请求"""
        content = request.data.get('content', '')
        printer_config = request.data.get('printer_config', {})
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            user_id=request.user.user_id if request.user else None,
            metadata={'request_id': request.request_id}
        )
        
        # 创建打印任务
        task = self.agent_manager.create_task(
            task_type="print",
            agent_type=AgentType.PRINT_AGENT,
            input_data={
                'content': content,
                'printer_config': printer_config
            },
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        # 提交任务
        success = await self.agent_manager.submit_task(task)
        if not success:
            raise Exception("打印任务提交失败")
        
        return {
            'task_id': task.task_id,
            'status': task.status.value,
            'timestamp': time.time()
        }
    
    async def _handle_print_status(self, request: APIRequest) -> Dict[str, Any]:
        """处理打印状态查询"""
        task_id = request.data.get('task_id')
        if not task_id:
            raise Exception("缺少task_id参数")
        
        task = self.agent_manager.get_task_status(task_id)
        if not task:
            raise Exception("任务不存在")
        
        return {
            'task_id': task.task_id,
            'status': task.status.value,
            'output_data': task.output_data,
            'timestamp': time.time()
        }
    
    async def _handle_review_submit(self, request: APIRequest) -> Dict[str, Any]:
        """处理审稿提交"""
        content = request.data.get('content', '')
        criteria = request.data.get('criteria', {})
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            user_id=request.user.user_id if request.user else None,
            metadata={'request_id': request.request_id}
        )
        
        # 创建评估任务
        task = self.agent_manager.create_task(
            task_type="evaluation",
            agent_type=AgentType.EVALUATOR,
            input_data={
                'content': content,
                'criteria': criteria
            },
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        # 提交任务
        success = await self.agent_manager.submit_task(task)
        if not success:
            raise Exception("审稿任务提交失败")
        
        return {
            'task_id': task.task_id,
            'status': task.status.value,
            'timestamp': time.time()
        }
    
    async def _handle_review_approve(self, request: APIRequest) -> Dict[str, Any]:
        """处理审稿通过"""
        report_id = request.data.get('report_id', '')
        version = request.data.get('version', 'v1.0')
        
        # 发布审稿通过事件
        await self.event_publisher.publish_review_approved(
            request.tenant_id,
            report_id,
            version,
            request.user.user_id if request.user else None
        )
        
        return {
            'report_id': report_id,
            'version': version,
            'status': 'approved',
            'timestamp': time.time()
        }
    
    async def _handle_review_query(self, request: APIRequest) -> Dict[str, Any]:
        """处理审稿查询"""
        # 简化实现
        return {'reviews': [], 'total': 0, 'timestamp': time.time()}
    
    async def _handle_system_health(self, request: APIRequest) -> Dict[str, Any]:
        """处理系统健康检查"""
        # 检查各个组件状态
        coze_healthy = self.coze_client.health_check()
        agent_stats = self.agent_manager.get_stats()
        router_stats = self.message_router.get_stats()
        
        overall_health = coze_healthy
        
        return {
            'status': 'healthy' if overall_health else 'unhealthy',
            'components': {
                'coze_api': 'healthy' if coze_healthy else 'unhealthy',
                'agents': f"{agent_stats['running_tasks']} running tasks",
                'message_router': f"{router_stats['queue_size']} queued events"
            },
            'timestamp': time.time()
        }
    
    async def _handle_system_metrics(self, request: APIRequest) -> Dict[str, Any]:
        """处理系统指标查询"""
        agent_stats = self.agent_manager.get_stats()
        router_stats = self.message_router.get_stats()
        
        return {
            'gateway_stats': self._stats,
            'agent_stats': agent_stats,
            'router_stats': router_stats,
            'timestamp': time.time()
        }
    
    async def _handle_system_audit(self, request: APIRequest) -> Dict[str, Any]:
        """处理系统审计查询"""
        # 简化实现，返回模拟审计数据
        return {
            'audit_events': [],
            'total_events': 0,
            'timestamp': time.time()
        }
    
    # ==================== 工具方法 ====================
    
    def _calculate_progress(self, task) -> float:
        """计算任务进度"""
        if task.status.value == 'completed':
            return 100.0
        elif task.status.value == 'running':
            return 50.0
        elif task.status.value == 'pending':
            return 0.0
        else:
            return 0.0
    
    def _update_response_time(self, response_time: float):
        """更新响应时间统计"""
        current_avg = self._stats['average_response_time']
        total_requests = self._stats['total_requests']
        
        # 计算新的平均响应时间
        self._stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取网关统计信息"""
        return {
            **self._stats,
            'timestamp': time.time()
        }


# 全局网关实例
_gateway: Optional[IntegrationGateway] = None


def get_gateway() -> IntegrationGateway:
    """获取全局网关实例"""
    global _gateway
    if _gateway is None:
        _gateway = IntegrationGateway()
    return _gateway


# 便捷函数
async def handle_api_request(endpoint: str, method: str, data: Dict[str, Any], 
                           headers: Dict[str, Any], user: Optional[User] = None,
                           tenant_id: str = "default") -> APIResponse:
    """便捷API请求处理函数"""
    gateway = get_gateway()
    
    # 解析端点
    endpoint_enum = None
    for ep in APIEndpoint:
        if ep.value == endpoint:
            endpoint_enum = ep
            break
    
    if not endpoint_enum:
        return APIResponse(
            request_id=str(uuid.uuid4()),
            success=False,
            error=f"未知的端点: {endpoint}",
            error_code="UNKNOWN_ENDPOINT"
        )
    
    request = APIRequest(
        request_id=str(uuid.uuid4()),
        endpoint=endpoint_enum,
        method=method,
        user=user,
        tenant_id=tenant_id,
        data=data,
        headers=headers
    )
    
    return await gateway.handle_request(request)