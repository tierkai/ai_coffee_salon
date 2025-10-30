"""
主程序入口
启动和协调整个Coze集成系统
"""
import asyncio
import signal
import sys
import logging
from typing import Optional
from pathlib import Path

from .config_manager import get_config_manager, SystemConfig
from .auth_manager import get_auth_manager, User, Role, Permission
from .integration_gateway import get_gateway, IntegrationGateway
from .kai_manager import get_agent_manager
from .message_router import get_message_router


def setup_logging(config: SystemConfig):
    """设置日志配置"""
    log_level = getattr(logging, config.monitoring.log_level.upper(), logging.INFO)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    return root_logger


def setup_signal_handlers(gateway: IntegrationGateway):
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger = logging.getLogger(__name__)
        logger.info(f"接收到信号 {signum}，开始优雅关闭...")
        
        # 启动关闭流程
        asyncio.create_task(graceful_shutdown(gateway))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def graceful_shutdown(gateway: IntegrationGateway, timeout: int = 30):
    """优雅关闭"""
    logger = logging.getLogger(__name__)
    logger.info("开始优雅关闭系统...")
    
    try:
        # 停止网关服务
        await gateway.stop()
        logger.info("网关服务已停止")
        
        # 等待一小段时间确保所有任务完成
        await asyncio.sleep(1)
        
        logger.info("系统已安全关闭")
        
    except Exception as e:
        logger.error(f"关闭过程中发生错误: {e}")
    
    finally:
        sys.exit(0)


async def initialize_system():
    """初始化系统"""
    logger = logging.getLogger(__name__)
    logger.info("初始化Coze集成系统...")
    
    # 1. 加载配置
    config_manager = get_config_manager()
    config = config_manager.get_config()
    
    # 2. 设置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info(f"系统配置加载完成，环境: {config.environment}")
    
    # 3. 初始化认证系统
    auth_manager = get_auth_manager()
    
    # 创建默认租户
    from .auth_manager import Tenant
    default_tenant = Tenant(
        tenant_id="default",
        name="默认租户",
        quota={"max_users": 100, "max_requests_per_hour": 10000}
    )
    auth_manager.create_tenant(default_tenant)
    
    # 创建默认管理员用户
    admin_user = User(
        user_id="admin_001",
        username="admin",
        email="admin@coffee-salon.com",
        tenant_id="default",
        roles={Role.ADMIN}
    )
    auth_manager.register_user(admin_user)
    
    logger.info("认证系统初始化完成")
    
    # 4. 初始化网关服务
    gateway = get_gateway()
    
    logger.info("系统初始化完成")
    return gateway, config


async def run_health_check(gateway: IntegrationGateway) -> bool:
    """运行健康检查"""
    logger = logging.getLogger(__name__)
    logger.info("运行系统健康检查...")
    
    try:
        # 检查各个组件
        from .coze_client import get_coze_client
        coze_client = get_coze_client()
        
        # Coze API健康检查
        if not coze_client.health_check():
            logger.error("Coze API健康检查失败")
            return False
        
        # 网关服务健康检查
        health_result = await gateway.handle_request(
            type('HealthRequest', (), {
                'request_id': 'health_check',
                'endpoint': type('Endpoint', (), {'value': '/v1/system/health'})(),
                'method': 'GET',
                'user': None,
                'tenant_id': 'default',
                'data': {},
                'headers': {},
                'timestamp': 0
            })()
        )
        
        if not health_result.success:
            logger.error(f"网关健康检查失败: {health_result.error}")
            return False
        
        logger.info("系统健康检查通过")
        return True
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return False


async def run_demo_scenario(gateway: IntegrationGateway):
    """运行演示场景"""
    logger = logging.getLogger(__name__)
    logger.info("开始运行演示场景...")
    
    try:
        # 获取管理员用户
        auth_manager = get_auth_manager()
        admin_user = auth_manager._users.get("admin_001")
        
        if not admin_user:
            logger.error("管理员用户不存在")
            return
        
        # 场景1: 问答查询
        logger.info("场景1: 问答查询")
        query_request = type('Request', (), {
            'request_id': 'demo_query_001',
            'endpoint': type('Endpoint', (), {'value': '/v1/query'})(),
            'method': 'POST',
            'user': admin_user,
            'tenant_id': 'default',
            'data': {
                'query': '什么是阿拉比卡咖啡？',
                'context': {'language': 'zh-CN'}
            },
            'headers': {'Authorization': 'Bearer demo_token'},
            'timestamp': 0
        })()
        
        response = await gateway.handle_request(query_request)
        logger.info(f"查询响应: {response.success}, 耗时: {response.execution_time:.2f}s")
        
        # 场景2: 智能体调度
        logger.info("场景2: 智能体调度")
        dispatch_request = type('Request', (), {
            'request_id': 'demo_dispatch_001',
            'endpoint': type('Endpoint', (), {'value': '/v1/agents/dispatch'})(),
            'method': 'POST',
            'user': admin_user,
            'tenant_id': 'default',
            'data': {
                'task_type': 'research',
                'input_data': {
                    'query': '研究咖啡烘焙工艺',
                    'depth': 'detailed'
                }
            },
            'headers': {'Authorization': 'Bearer demo_token'},
            'timestamp': 0
        })()
        
        response = await gateway.handle_request(dispatch_request)
        logger.info(f"调度响应: {response.success}, 任务ID: {response.data.get('task_id') if response.success else 'N/A'}")
        
        # 场景3: 打印票据
        logger.info("场景3: 打印票据")
        print_request = type('Request', (), {
            'request_id': 'demo_print_001',
            'endpoint': type('Endpoint', (), {'value': '/v1/print/ticket'})(),
            'method': 'POST',
            'user': admin_user,
            'tenant_id': 'default',
            'data': {
                'content': '咖啡知识沙龙门票\n时间: 2025-10-29\n地点: 咖啡厅',
                'printer_config': {'printer_id': 'default_printer'}
            },
            'headers': {'Authorization': 'Bearer demo_token'},
            'timestamp': 0
        })()
        
        response = await gateway.handle_request(print_request)
        logger.info(f"打印响应: {response.success}, 任务ID: {response.data.get('task_id') if response.success else 'N/A'}")
        
        # 场景4: 系统指标
        logger.info("场景4: 系统指标查询")
        metrics_request = type('Request', (), {
            'request_id': 'demo_metrics_001',
            'endpoint': type('Endpoint', (), {'value': '/v1/system/metrics'})(),
            'method': 'GET',
            'user': admin_user,
            'tenant_id': 'default',
            'data': {},
            'headers': {'Authorization': 'Bearer demo_token'},
            'timestamp': 0
        })()
        
        response = await gateway.handle_request(metrics_request)
        if response.success:
            metrics = response.data
            logger.info(f"系统指标: 请求总数 {metrics['gateway_stats']['total_requests']}, "
                       f"成功率 {metrics['gateway_stats']['successful_requests']}")
        
        logger.info("演示场景运行完成")
        
    except Exception as e:
        logger.error(f"演示场景运行失败: {e}")


async def main():
    """主函数"""
    try:
        # 初始化系统
        gateway, config = await initialize_system()
        
        # 设置信号处理器
        setup_signal_handlers(gateway)
        
        # 启动网关服务
        await gateway.start()
        logger = logging.getLogger(__name__)
        logger.info("Coze集成系统已启动")
        
        # 运行健康检查
        if not await run_health_check(gateway):
            logger.error("健康检查失败，系统退出")
            return
        
        # 如果是开发环境，运行演示场景
        if config.environment.lower() == 'development':
            await run_demo_scenario(gateway)
        
        # 保持服务运行
        logger.info("系统运行中，按 Ctrl+C 停止...")
        
        # 定期输出系统状态
        while True:
            await asyncio.sleep(60)  # 每分钟输出一次状态
            
            stats = gateway.get_stats()
            logger.info(f"系统状态: 总请求 {stats['total_requests']}, "
                       f"成功率 {stats['successful_requests']}/{stats['total_requests']}, "
                       f"平均响应时间 {stats['average_response_time']:.3f}s")
        
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("接收到中断信号，开始关闭系统...")
        await graceful_shutdown(gateway)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"系统运行失败: {e}")
        raise


def create_cli():
    """创建命令行界面"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coze集成系统')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--demo', '-d', action='store_true', help='运行演示模式')
    parser.add_argument('--health-check', '-h', action='store_true', help='运行健康检查')
    parser.add_argument('--version', '-v', action='version', version='1.0.0')
    
    args = parser.parse_args()
    
    return args


if __name__ == "__main__":
    # 解析命令行参数
    args = create_cli()
    
    # 设置配置文件路径
    if args.config:
        import os
        os.environ['COZE_CONFIG_PATH'] = args.config
    
    try:
        # 运行主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)