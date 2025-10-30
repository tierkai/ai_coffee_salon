"""
Kai智能体管理器
负责管理AI咖啡知识沙龙系统的多智能体编排和协作
"""
import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor

from .config_manager import get_config
from .auth_manager import get_auth_manager, User, Permission
from .coze_client import CozeAPIClient, ChatRequest, ChatResponse, MessageRole
from .message_router import MessageRouter, EventType, EventPublisher

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """智能体类型"""
    RESEARCHER = "researcher"      # 研究员
    EVALUATOR = "evaluator"        # 评估者
    SUMMARIZER = "summarizer"      # 总结者
    QNA_AGENT = "qna_agent"        # 问答智能体
    DISPATCHER = "dispatcher"      # 调度智能体
    PRINT_AGENT = "print_agent"    # 打印智能体


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVIEWING = "reviewing"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    tenant_id: str
    user_id: str
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class Task:
    """任务对象"""
    task_id: str
    task_type: str
    agent_type: AgentType
    priority: TaskPriority
    status: TaskStatus
    context: TaskContext
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    estimated_duration: Optional[int] = None  # 秒


@dataclass
class AgentConfig:
    """智能体配置"""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    bot_id: str  # Coze机器人ID
    capabilities: List[str]
    max_concurrent_tasks: int = 5
    timeout: int = 300  # 5分钟
    prompt_template: str = ""
    system_prompt: str = ""


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, config: AgentConfig, coze_client: CozeAPIClient, 
                 message_router: MessageRouter):
        self.config = config
        self.coze_client = coze_client
        self.message_router = message_router
        self.event_publisher = EventPublisher(message_router)
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._task_history: List[Task] = []
        self._executor = ThreadPoolExecutor(max_workers=3)
    
    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务"""
        pass
    
    async def execute_task(self, task: Task) -> Task:
        """执行任务"""
        logger.info(f"智能体 {self.config.name} 开始执行任务: {task.task_id}")
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            
            # 发布任务开始事件
            await self.event_publisher.publish(
                EventType.KB_UPDATED,  # 使用通用事件类型
                task.context.tenant_id,
                {
                    'task_id': task.task_id,
                    'agent_type': self.config.agent_type.value,
                    'action': 'started'
                },
                task.context.user_id
            )
            
            # 执行任务
            result = await self.process_task(task)
            
            # 更新任务结果
            task.output_data = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # 发布任务完成事件
            await self.event_publisher.publish(
                EventType.RAG_COMPLETED,
                task.context.tenant_id,
                {
                    'task_id': task.task_id,
                    'agent_type': self.config.agent_type.value,
                    'result': result,
                    'duration': task.completed_at - task.started_at
                },
                task.context.user_id
            )
            
            logger.info(f"智能体 {self.config.name} 完成任务: {task.task_id}")
            
        except Exception as e:
            logger.error(f"智能体 {self.config.name} 执行任务失败: {e}")
            
            task.error_message = str(e)
            task.status = TaskStatus.FAILED
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                logger.info(f"任务 {task.task_id} 将进行第 {task.retry_count} 次重试")
            
            # 发布任务失败事件
            await self.event_publisher.publish(
                EventType.RAG_FAILED,
                task.context.tenant_id,
                {
                    'task_id': task.task_id,
                    'agent_type': self.config.agent_type.value,
                    'error': str(e),
                    'retry_count': task.retry_count
                },
                task.context.user_id
            )
        
        finally:
            # 清理运行中的任务
            if task.task_id in self._running_tasks:
                del self._running_tasks[task.task_id]
            
            # 添加到历史记录
            self._task_history.append(task)
        
        return task
    
    async def chat_with_coze(self, query: str, context: Optional[Dict] = None) -> str:
        """与Coze机器人对话"""
        request = ChatRequest(
            bot_id=self.config.bot_id,
            query=query,
            context=context
        )
        
        response = await asyncio.get_event_loop().run_in_executor(
            self._executor,
            lambda: self.coze_client.chat(request)
        )
        
        return response.content


class ResearcherAgent(BaseAgent):
    """研究员智能体"""
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理研究任务"""
        query = task.input_data.get('query', '')
        context = task.input_data.get('context', {})
        
        # 构建研究提示
        research_prompt = f"""
        作为咖啡知识研究员，请深入研究以下问题：
        
        问题：{query}
        
        请提供：
        1. 详细的背景信息
        2. 相关的咖啡知识
        3. 权威来源和引用
        4. 关键要点总结
        
        上下文信息：{json.dumps(context, ensure_ascii=False)}
        """
        
        # 与Coze机器人对话
        response = await self.chat_with_coze(research_prompt, context)
        
        return {
            'research_result': response,
            'query': query,
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }


class EvaluatorAgent(BaseAgent):
    """评估者智能体"""
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理评估任务"""
        content = task.input_data.get('content', '')
        criteria = task.input_data.get('criteria', {})
        
        # 构建评估提示
        eval_prompt = f"""
        作为咖啡知识评估者，请对以下内容进行专业评估：
        
        内容：{content}
        
        评估标准：{json.dumps(criteria, ensure_ascii=False)}
        
        请提供：
        1. 事实性检查结果
        2. 逻辑一致性评估
        3. 引用完整性分析
        4. 改进建议
        5. 评估结论（通过/不通过）
        """
        
        response = await self.chat_with_coze(eval_prompt)
        
        # 解析评估结果
        evaluation_result = {
            'evaluation': response,
            'content_hash': hash(content),
            'criteria': criteria,
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }
        
        return evaluation_result


class SummarizerAgent(BaseAgent):
    """总结者智能体"""
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理总结任务"""
        materials = task.input_data.get('materials', [])
        format_type = task.input_data.get('format', 'report')
        
        # 构建总结提示
        materials_text = '\n\n'.join([f"材料 {i+1}:\n{material}" for i, material in enumerate(materials)])
        
        summary_prompt = f"""
        作为咖啡知识总结者，请基于以下材料生成{format_type}：
        
        {materials_text}
        
        要求：
        1. 结构清晰，逻辑严密
        2. 包含完整的引用和来源
        3. 语言专业且易懂
        4. 适合目标受众
        """
        
        response = await self.chat_with_coze(summary_prompt)
        
        return {
            'summary': response,
            'materials_count': len(materials),
            'format': format_type,
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }


class QNAAgent(BaseAgent):
    """问答智能体"""
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理问答任务"""
        question = task.input_data.get('question', '')
        context = task.input_data.get('context', {})
        
        # 构建问答提示
        qna_prompt = f"""
        作为咖啡知识问答助手，请回答以下问题：
        
        问题：{question}
        
        要求：
        1. 提供准确、专业的答案
        2. 包含相关引用和来源
        3. 如果信息不足，请明确说明
        4. 保持友好和专业的语调
        
        上下文：{json.dumps(context, ensure_ascii=False)}
        """
        
        response = await self.chat_with_coze(qna_prompt, context)
        
        return {
            'answer': response,
            'question': question,
            'context': context,
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }


class DispatcherAgent(BaseAgent):
    """调度智能体"""
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理调度任务"""
        request = task.input_data.get('request', {})
        available_agents = task.input_data.get('agents', [])
        
        # 分析请求并选择合适的智能体
        task_type = request.get('type', 'qna')
        
        # 简单的路由逻辑
        agent_mapping = {
            'research': AgentType.RESEARCHER,
            'evaluation': AgentType.EVALUATOR,
            'summary': AgentType.SUMMARIZER,
            'qna': AgentType.QNA_AGENT
        }
        
        selected_agent_type = agent_mapping.get(task_type, AgentType.QNA_AGENT)
        
        # 查找可用的智能体
        selected_agent = None
        for agent in available_agents:
            if agent['type'] == selected_agent_type and agent['available']:
                selected_agent = agent
                break
        
        if not selected_agent:
            raise ValueError(f"没有找到可用的 {selected_agent_type.value} 智能体")
        
        return {
            'routing_decision': {
                'requested_type': task_type,
                'selected_agent': selected_agent,
                'reasoning': f'基于任务类型 {task_type} 选择 {selected_agent_type.value} 智能体'
            },
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }


class PrintAgent(BaseAgent):
    """打印智能体"""
    
    async def process_task(self: Task) -> Dict[str, Any]:
        """处理打印任务"""
        content = task.input_data.get('content', '')
        printer_config = task.input_data.get('printer_config', {})
        
        # 模拟打印过程
        logger.info(f"开始打印任务: {task.task_id}")
        
        # 模拟打印延迟
        await asyncio.sleep(2)
        
        # 实际实现中，这里会调用打印服务
        print_result = {
            'print_success': True,
            'printer_id': printer_config.get('printer_id', 'default'),
            'pages_printed': len(content) // 1000 + 1,
            'timestamp': time.time(),
            'agent_type': self.config.agent_type.value
        }
        
        # 发布打印完成事件
        await self.event_publisher.publish_print_completed(
            task.context.tenant_id,
            task.task_id,
            print_result['printer_id'],
            task.context.user_id
        )
        
        return print_result


class KaiAgentManager:
    """Kai智能体管理器"""
    
    def __init__(self):
        self.config = get_config()
        self.auth_manager = get_auth_manager()
        self.coze_client = CozeAPIClient()
        self.message_router = MessageRouter()
        
        # 智能体管理
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        
        # 任务管理
        self._tasks: Dict[str, Task] = {}
        self._task_queue = asyncio.Queue()
        self._running = False
        
        # 初始化默认智能体
        self._init_default_agents()
    
    def _init_default_agents(self):
        """初始化默认智能体"""
        # 研究员智能体
        researcher_config = AgentConfig(
            agent_id="researcher_01",
            agent_type=AgentType.RESEARCHER,
            name="咖啡研究员",
            description="专门负责咖啡知识的深入研究和信息收集",
            bot_id="bot_researcher_001",
            capabilities=["research", "knowledge_collection", "fact_checking"]
        )
        
        # 评估者智能体
        evaluator_config = AgentConfig(
            agent_id="evaluator_01",
            agent_type=AgentType.EVALUATOR,
            name="知识评估师",
            description="负责评估内容的事实性和逻辑一致性",
            bot_id="bot_evaluator_001",
            capabilities=["evaluation", "quality_check", "fact_verification"]
        )
        
        # 总结者智能体
        summarizer_config = AgentConfig(
            agent_id="summarizer_01",
            agent_type=AgentType.SUMMARIZER,
            name="报告总结师",
            description="负责将研究结果整合为结构化报告",
            bot_id="bot_summarizer_001",
            capabilities=["summarization", "report_generation", "content_synthesis"]
        )
        
        # 问答智能体
        qna_config = AgentConfig(
            agent_id="qna_01",
            agent_type=AgentType.QNA_AGENT,
            name="咖啡问答助手",
            description="为用户提供咖啡相关的问答服务",
            bot_id="bot_qna_001",
            capabilities=["question_answering", "knowledge_retrieval", "chat"]
        )
        
        # 调度智能体
        dispatcher_config = AgentConfig(
            agent_id="dispatcher_01",
            agent_type=AgentType.DISPATCHER,
            name="任务调度员",
            description="负责智能体任务的智能分配和调度",
            bot_id="bot_dispatcher_001",
            capabilities=["task_routing", "agent_coordination", "workflow_management"]
        )
        
        # 打印智能体
        print_config = AgentConfig(
            agent_id="print_01",
            agent_type=AgentType.PRINT_AGENT,
            name="打印服务专员",
            description="负责处理各种文档和票据的打印任务",
            bot_id="bot_print_001",
            capabilities=["document_printing", "ticket_generation", "output_management"]
        )
        
        # 注册配置
        for config in [researcher_config, evaluator_config, summarizer_config, 
                      qna_config, dispatcher_config, print_config]:
            self._agent_configs[config.agent_id] = config
        
        logger.info(f"初始化了 {len(self._agent_configs)} 个智能体配置")
    
    def register_agent(self, agent: BaseAgent):
        """注册智能体"""
        self._agents[agent.config.agent_id] = agent
        logger.info(f"注册智能体: {agent.config.name} ({agent.config.agent_id})")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取智能体"""
        return self._agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """根据类型获取智能体"""
        return [agent for agent in self._agents.values() 
                if agent.config.agent_type == agent_type]
    
    def create_task(self, task_type: str, agent_type: AgentType, 
                   input_data: Dict[str, Any], context: TaskContext,
                   priority: TaskPriority = TaskPriority.NORMAL) -> Task:
        """创建任务"""
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            agent_type=agent_type,
            priority=priority,
            status=TaskStatus.PENDING,
            context=context,
            input_data=input_data
        )
        
        self._tasks[task.task_id] = task
        logger.info(f"创建任务: {task.task_id} ({task_type} -> {agent_type.value})")
        
        return task
    
    async def submit_task(self, task: Task) -> bool:
        """提交任务"""
        try:
            # 查找合适的智能体
            agents = self.get_agents_by_type(task.agent_type)
            if not agents:
                logger.error(f"没有找到类型为 {task.agent_type.value} 的智能体")
                return False
            
            # 选择可用的智能体（简单负载均衡）
            selected_agent = self._select_available_agent(agents)
            if not selected_agent:
                logger.error(f"没有可用的 {task.agent_type.value} 智能体")
                return False
            
            # 执行任务
            await selected_agent.execute_task(task)
            
            return True
            
        except Exception as e:
            logger.error(f"提交任务失败: {e}")
            return False
    
    def _select_available_agent(self, agents: List[BaseAgent]) -> Optional[BaseAgent]:
        """选择可用的智能体"""
        available_agents = [agent for agent in agents 
                          if len(agent._running_tasks) < agent.config.max_concurrent_tasks]
        
        if not available_agents:
            return None
        
        # 简单负载均衡：选择运行任务最少的智能体
        return min(available_agents, key=lambda a: len(a._running_tasks))
    
    async def process_task_queue(self):
        """处理任务队列"""
        while self._running:
            try:
                # 从队列获取任务
                task = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
                
                # 提交任务
                await self.submit_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"处理任务队列失败: {e}")
    
    async def start(self):
        """启动管理器"""
        if self._running:
            return
        
        logger.info("启动Kai智能体管理器")
        self._running = True
        
        # 注册所有智能体
        for config in self._agent_configs.values():
            agent = self._create_agent_from_config(config)
            if agent:
                self.register_agent(agent)
        
        # 启动任务队列处理
        asyncio.create_task(self.process_task_queue())
    
    async def stop(self):
        """停止管理器"""
        if not self._running:
            return
        
        logger.info("停止Kai智能体管理器")
        self._running = False
    
    def _create_agent_from_config(self, config: AgentConfig) -> Optional[BaseAgent]:
        """根据配置创建智能体"""
        agent_classes = {
            AgentType.RESEARCHER: ResearcherAgent,
            AgentType.EVALUATOR: EvaluatorAgent,
            AgentType.SUMMARIZER: SummarizerAgent,
            AgentType.QNA_AGENT: QNAAgent,
            AgentType.DISPATCHER: DispatcherAgent,
            AgentType.PRINT_AGENT: PrintAgent
        }
        
        agent_class = agent_classes.get(config.agent_type)
        if not agent_class:
            logger.error(f"未知的智能体类型: {config.agent_type}")
            return None
        
        return agent_class(config, self.coze_client, self.message_router)
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self._tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None, 
                  agent_type: Optional[AgentType] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        if agent_type:
            tasks = [task for task in tasks if task.agent_type == agent_type]
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_tasks = len(self._tasks)
        completed_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.FAILED])
        running_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING])
        
        return {
            'total_agents': len(self._agents),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'running_tasks': running_tasks,
            'success_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'agent_types': {agent_type.value: len(self.get_agents_by_type(agent_type)) 
                           for agent_type in AgentType}
        }


# 全局智能体管理器实例
_agent_manager: Optional[KaiAgentManager] = None


def get_agent_manager() -> KaiAgentManager:
    """获取全局智能体管理器实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = KaiAgentManager()
    return _agent_manager