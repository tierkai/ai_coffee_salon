"""
Coze集成接口包
提供Coze平台与AI咖啡知识沙龙系统的集成能力
"""

__version__ = "1.0.0"
__author__ = "Coffee Salon Team"
__description__ = "Coze平台与AI咖啡知识沙龙系统集成接口"

# 导入主要组件
from .config_manager import (
    ConfigManager,
    SystemConfig,
    CozeConfig,
    DatabaseConfig,
    MessageQueueConfig,
    SecurityConfig,
    MonitoringConfig,
    get_config_manager,
    get_config
)

from .auth_manager import (
    AuthManager,
    PermissionManager,
    User,
    Tenant,
    AuthToken,
    Permission,
    Role,
    get_auth_manager,
    get_permission_manager
)

from .coze_client import (
    CozeAPIClient,
    AsyncCozeAPIClient,
    ChatRequest,
    ChatResponse,
    Message,
    Conversation,
    MessageRole,
    StreamMode,
    CozeAPIError,
    get_coze_client,
    get_async_coze_client
)

from .message_router import (
    MessageRouter,
    EventPublisher,
    Event,
    EventType,
    EventPriority,
    Subscription,
    get_message_router,
    get_event_publisher
)

from .kai_manager import (
    KaiAgentManager,
    BaseAgent,
    AgentConfig,
    Task,
    TaskContext,
    TaskStatus,
    TaskPriority,
    AgentType,
    ResearcherAgent,
    EvaluatorAgent,
    SummarizerAgent,
    QNAAgent,
    DispatcherAgent,
    PrintAgent,
    get_agent_manager
)

from .integration_gateway import (
    IntegrationGateway,
    APIRequest,
    APIResponse,
    APIEndpoint,
    get_gateway,
    handle_api_request
)

from .main import main

# 便捷导入
__all__ = [
    # 配置管理
    "ConfigManager",
    "SystemConfig", 
    "CozeConfig",
    "DatabaseConfig",
    "MessageQueueConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "get_config_manager",
    "get_config",
    
    # 认证授权
    "AuthManager",
    "PermissionManager",
    "User",
    "Tenant",
    "AuthToken",
    "Permission",
    "Role",
    "get_auth_manager",
    "get_permission_manager",
    
    # Coze客户端
    "CozeAPIClient",
    "AsyncCozeAPIClient",
    "ChatRequest",
    "ChatResponse",
    "Message",
    "Conversation",
    "MessageRole",
    "StreamMode",
    "CozeAPIError",
    "get_coze_client",
    "get_async_coze_client",
    
    # 消息路由
    "MessageRouter",
    "EventPublisher",
    "Event",
    "EventType",
    "EventPriority",
    "Subscription",
    "get_message_router",
    "get_event_publisher",
    
    # 智能体管理
    "KaiAgentManager",
    "BaseAgent",
    "AgentConfig",
    "Task",
    "TaskContext",
    "TaskStatus",
    "TaskPriority",
    "AgentType",
    "ResearcherAgent",
    "EvaluatorAgent",
    "SummarizerAgent",
    "QNAAgent",
    "DispatcherAgent",
    "PrintAgent",
    "get_agent_manager",
    
    # 集成网关
    "IntegrationGateway",
    "APIRequest",
    "APIResponse",
    "APIEndpoint",
    "get_gateway",
    "handle_api_request",
    
    # 主程序
    "main"
]

# 版本信息
VERSION_INFO = {
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "components": [
        "config_manager",
        "auth_manager", 
        "coze_client",
        "message_router",
        "kai_manager",
        "integration_gateway",
        "main"
    ]
}

def get_version_info():
    """获取版本信息"""
    return VERSION_INFO.copy()

def create_system():
    """创建系统实例"""
    from .main import initialize_system
    return initialize_system

# 快速启动函数
async def quick_start():
    """快速启动系统"""
    from .main import initialize_system, run_demo_scenario
    from .config_manager import get_config
    
    gateway, config = await initialize_system()
    await gateway.start()
    
    if config.environment.lower() == 'development':
        await run_demo_scenario(gateway)
    
    return gateway

# 健康检查函数
async def health_check():
    """系统健康检查"""
    from .main import run_health_check
    from .integration_gateway import get_gateway
    
    gateway = get_gateway()
    return await run_health_check(gateway)