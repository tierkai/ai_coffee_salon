"""
测试用例
对Coze集成接口的各个组件进行单元测试和集成测试
"""
import unittest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

# 导入测试目标
from coze_integration import (
    ConfigManager,
    AuthManager,
    CozeAPIClient,
    MessageRouter,
    KaiAgentManager,
    IntegrationGateway,
    User,
    Role,
    Permission,
    TaskContext,
    TaskPriority,
    AgentType,
    EventType,
    APIEndpoint
)


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write("""
coze:
  base_url: "https://api.coze.cn"
  timeout: 30
database:
  mysql_host: "localhost"
security:
  jwt_secret_key: "test_key"
environment: "testing"
        """)
        self.temp_config.close()
    
    def tearDown(self):
        """测试后清理"""
        os.unlink(self.temp_config.name)
    
    def test_load_config(self):
        """测试配置加载"""
        config_manager = ConfigManager(self.temp_config.name)
        config = config_manager.get_config()
        
        self.assertEqual(config.coze.base_url, "https://api.coze.cn")
        self.assertEqual(config.coze.timeout, 30)
        self.assertEqual(config.database.mysql_host, "localhost")
        self.assertEqual(config.security.jwt_secret_key, "test_key")
        self.assertEqual(config.environment, "testing")
    
    def test_default_config(self):
        """测试默认配置"""
        config_manager = ConfigManager("non_existent_file.yaml")
        config = config_manager.get_config()
        
        self.assertIsNotNone(config.coze.base_url)
        self.assertIsNotNone(config.security.jwt_secret_key)


class TestAuthManager(unittest.TestCase):
    """认证管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.auth_manager = AuthManager()
        
        # 创建测试用户
        self.test_user = User(
            user_id="test_user_001",
            username="测试用户",
            email="test@example.com",
            tenant_id="test_tenant",
            roles={Role.RESEARCHER}
        )
        self.auth_manager.register_user(self.test_user)
        
        # 创建测试租户
        from coze_integration.auth_manager import Tenant
        self.test_tenant = Tenant(
            tenant_id="test_tenant",
            name="测试租户"
        )
        self.auth_manager.create_tenant(self.test_tenant)
    
    def test_jwt_token_creation(self):
        """测试JWT令牌创建"""
        jwt_token = self.auth_manager.create_jwt_token(
            user_id="test_user_001",
            tenant_id="test_tenant",
            scope=["test_scope"]
        )
        
        self.assertIsNotNone(jwt_token)
        self.assertIsInstance(jwt_token, str)
    
    def test_token_exchange(self):
        """测试令牌交换"""
        jwt_token = self.auth_manager.create_jwt_token(
            user_id="test_user_001",
            tenant_id="test_tenant"
        )
        
        auth_token = self.auth_manager.exchange_access_token(jwt_token)
        
        self.assertIsNotNone(auth_token.access_token)
        self.assertEqual(auth_token.user_id, "test_user_001")
        self.assertEqual(auth_token.tenant_id, "test_tenant")
    
    def test_access_token_verification(self):
        """测试访问令牌验证"""
        jwt_token = self.auth_manager.create_jwt_token(
            user_id="test_user_001",
            tenant_id="test_tenant"
        )
        
        auth_token = self.auth_manager.exchange_access_token(jwt_token)
        user = self.auth_manager.verify_access_token(auth_token.access_token)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, "test_user_001")
    
    def test_permission_check(self):
        """测试权限检查"""
        # 研究员应该有检索权限
        has_search_permission = self.auth_manager.check_permission(
            self.test_user,
            Permission.SEARCH_READ
        )
        self.assertTrue(has_search_permission)
        
        # 研究员不应该有系统管理权限
        has_admin_permission = self.auth_manager.check_permission(
            self.test_user,
            Permission.SYSTEM_ADMIN
        )
        self.assertFalse(has_admin_permission)
    
    def test_tenant_isolation(self):
        """测试租户隔离"""
        # 创建另一个租户的用户
        other_user = User(
            user_id="other_user_001",
            username="其他用户",
            email="other@example.com",
            tenant_id="other_tenant",
            roles={Role.RESEARCHER}
        )
        self.auth_manager.register_user(other_user)
        
        # 测试跨租户权限检查
        has_permission = self.auth_manager.check_permission(
            other_user,
            Permission.SEARCH_READ,
            tenant_id="test_tenant"  # 尝试访问其他租户
        )
        self.assertFalse(has_permission)


class TestCozeAPIClient(unittest.TestCase):
    """Coze API客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = CozeAPIClient()
    
    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get):
        """测试健康检查成功"""
        # 模拟成功的健康检查响应
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        self.assertTrue(result)
    
    @patch('requests.Session.get')
    def test_health_check_failure(self, mock_get):
        """测试健康检查失败"""
        # 模拟失败的健康检查响应
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        self.assertFalse(result)
    
    @patch.object(CozeAPIClient, '_get_access_token')
    @patch('requests.Session.post')
    def test_chat_request(self, mock_post, mock_get_token):
        """测试聊天请求"""
        # 模拟令牌获取
        mock_get_token.return_value = "test_access_token"
        
        # 模拟聊天响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "conversation_id": "conv_001",
            "message_id": "msg_001",
            "content": "Hello, this is a test response",
            "timestamp": 1234567890
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 创建聊天请求
        from coze_client import ChatRequest
        request = ChatRequest(
            bot_id="test_bot_001",
            query="Hello",
            stream=False
        )
        
        # 发送请求
        response = self.client.chat(request)
        
        self.assertEqual(response.conversation_id, "conv_001")
        self.assertEqual(response.content, "Hello, this is a test response")


class TestMessageRouter(unittest.TestCase):
    """消息路由器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.router = MessageRouter()
    
    def test_event_creation(self):
        """测试事件创建"""
        event = Event(
            event_id="test_event_001",
            event_type=EventType.KB_UPDATED,
            tenant_id="test_tenant",
            user_id="test_user",
            payload={"kb_id": "kb_001", "version": "v1.0"}
        )
        
        self.assertEqual(event.event_id, "test_event_001")
        self.assertEqual(event.event_type, EventType.KB_UPDATED)
        self.assertEqual(event.tenant_id, "test_tenant")
    
    def test_subscription_creation(self):
        """测试订阅创建"""
        def test_handler(event):
            print(f"处理事件: {event.event_id}")
        
        subscription = Subscription(
            subscription_id="test_sub_001",
            event_types=[EventType.KB_UPDATED],
            callback=test_handler
        )
        
        self.assertEqual(subscription.subscription_id, "test_sub_001")
        self.assertIn(EventType.KB_UPDATED, subscription.event_types)
    
    async def test_event_publishing(self):
        """测试事件发布"""
        # 启动路由器
        await self.router.start()
        
        # 定义事件处理器
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # 创建订阅
        subscription = Subscription(
            subscription_id="test_sub_001",
            event_types=[EventType.KB_UPDATED],
            callback=event_handler
        )
        
        self.router.subscribe(subscription)
        
        # 发布事件
        await self.router.publish(
            EventType.KB_UPDATED,
            tenant_id="test_tenant",
            payload={"kb_id": "kb_001", "version": "v1.0"},
            user_id="test_user"
        )
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        # 验证事件被处理
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].payload["kb_id"], "kb_001")
        
        # 停止路由器
        await self.router.stop()


class TestKaiAgentManager(unittest.TestCase):
    """Kai智能体管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.agent_manager = KaiAgentManager()
    
    async def test_agent_manager_start(self):
        """测试智能体管理器启动"""
        await self.agent_manager.start()
        
        stats = self.agent_manager.get_stats()
        self.assertGreater(stats['total_agents'], 0)
        self.assertEqual(stats['total_tasks'], 0)
        
        await self.agent_manager.stop()
    
    async def test_task_creation(self):
        """测试任务创建"""
        await self.agent_manager.start()
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id="test_task_001",
            tenant_id="test_tenant",
            user_id="test_user"
        )
        
        # 创建任务
        task = self.agent_manager.create_task(
            task_type="qna",
            agent_type=AgentType.QNA_AGENT,
            input_data={"question": "什么是咖啡？"},
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        self.assertEqual(task.task_type, "qna")
        self.assertEqual(task.agent_type, AgentType.QNA_AGENT)
        self.assertEqual(task.context.task_id, "test_task_001")
        
        await self.agent_manager.stop()
    
    async def test_task_submission(self):
        """测试任务提交"""
        await self.agent_manager.start()
        
        # 创建任务上下文
        task_context = TaskContext(
            task_id="test_task_002",
            tenant_id="test_tenant",
            user_id="test_user"
        )
        
        # 创建任务
        task = self.agent_manager.create_task(
            task_type="qna",
            agent_type=AgentType.QNA_AGENT,
            input_data={"question": "什么是咖啡？"},
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        
        # 提交任务
        success = await self.agent_manager.submit_task(task)
        self.assertTrue(success)
        
        # 等待任务处理
        await asyncio.sleep(2)
        
        # 检查任务状态
        task_status = self.agent_manager.get_task_status(task.task_id)
        self.assertIsNotNone(task_status)
        
        await self.agent_manager.stop()


class TestIntegrationGateway(unittest.TestCase):
    """集成网关测试"""
    
    def setUp(self):
        """测试前准备"""
        self.gateway = IntegrationGateway()
    
    async def test_gateway_start_stop(self):
        """测试网关启动和停止"""
        await self.gateway.start()
        
        # 检查网关是否正常运行
        stats = self.gateway.get_stats()
        self.assertIsInstance(stats, dict)
        
        await self.gateway.stop()
    
    async def test_api_request_handling(self):
        """测试API请求处理"""
        await self.gateway.start()
        
        # 创建模拟用户
        auth_manager = get_auth_manager()
        user = auth_manager._users.get("admin_001")
        
        if not user:
            # 创建管理员用户
            user = User(
                user_id="admin_001",
                username="admin",
                email="admin@test.com",
                tenant_id="default",
                roles={Role.ADMIN}
            )
            auth_manager.register_user(user)
        
        # 创建API请求
        from integration_gateway import APIRequest
        request = APIRequest(
            request_id="test_req_001",
            endpoint=APIEndpoint.SYSTEM_HEALTH,
            method="GET",
            user=user,
            tenant_id="default",
            data={},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 处理请求
        response = await self.gateway.handle_request(request)
        
        self.assertIsInstance(response.success, bool)
        self.assertIsNotNone(response.timestamp)
        
        await self.gateway.stop()


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    async def test_full_workflow(self):
        """测试完整工作流程"""
        # 启动所有组件
        gateway = IntegrationGateway()
        await gateway.start()
        
        # 创建用户
        auth_manager = get_auth_manager()
        user = User(
            user_id="integration_test_user",
            username="集成测试用户",
            email="integration@test.com",
            tenant_id="test_tenant",
            roles={Role.RESEARCHER}
        )
        auth_manager.register_user(user)
        
        # 创建API请求
        from integration_gateway import APIRequest
        request = APIRequest(
            request_id="integration_test_001",
            endpoint=APIEndpoint.QUERY,
            method="POST",
            user=user,
            tenant_id="test_tenant",
            data={
                "query": "什么是手冲咖啡？",
                "context": {"language": "zh-CN"}
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 处理请求
        response = await gateway.handle_request(request)
        
        # 验证响应
        self.assertIsInstance(response.success, bool)
        self.assertIsNotNone(response.execution_time)
        
        # 清理
        await gateway.stop()


def create_test_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestConfigManager,
        TestAuthManager,
        TestCozeAPIClient,
        TestMessageRouter,
        TestKaiAgentManager,
        TestIntegrationGateway,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


async def run_async_tests():
    """运行异步测试"""
    print("运行异步测试...")
    
    # 创建事件循环
    loop = asyncio.get_event_loop()
    
    # 运行异步测试
    test_instance = TestMessageRouter()
    test_instance.setUp()
    await test_instance.test_event_publishing()
    print("消息路由器测试通过")
    
    test_instance = TestKaiAgentManager()
    test_instance.setUp()
    await test_instance.test_agent_manager_start()
    await test_instance.test_task_creation()
    await test_instance.test_task_submission()
    print("智能体管理器测试通过")
    
    test_instance = TestIntegrationGateway()
    test_instance.setUp()
    await test_instance.test_gateway_start_stop()
    await test_instance.test_api_request_handling()
    print("集成网关测试通过")
    
    test_instance = TestIntegration()
    await test_instance.test_full_workflow()
    print("集成测试通过")


if __name__ == "__main__":
    print("开始运行Coze集成接口测试...")
    
    # 运行同步测试
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    
    # 输出测试结果
    print(f"\n测试完成!")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("所有测试通过! ✅")
    else:
        print("部分测试失败 ❌")