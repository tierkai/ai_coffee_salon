#!/usr/bin/env python3
"""
Coze集成接口快速演示脚本
展示系统的主要功能和使用方法
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coze_integration import (
    get_config_manager,
    get_auth_manager,
    get_coze_client,
    get_message_router,
    get_agent_manager,
    get_gateway,
    User,
    Role,
    Permission,
    TaskContext,
    TaskPriority,
    AgentType,
    EventType,
    APIEndpoint
)


async def quick_demo():
    """快速演示"""
    print("🚀 Coze集成接口快速演示")
    print("=" * 50)
    
    try:
        # 1. 初始化系统
        print("1️⃣ 初始化系统...")
        config_manager = get_config_manager()
        config = config_manager.get_config()
        print(f"   ✅ 环境: {config.environment}")
        print(f"   ✅ Coze API: {config.coze.base_url}")
        
        # 2. 创建用户
        print("\n2️⃣ 创建测试用户...")
        auth_manager = get_auth_manager()
        
        from coze_integration.auth_manager import Tenant
        tenant = Tenant(
            tenant_id="demo_tenant",
            name="演示租户",
            quota={"max_users": 10, "max_requests_per_hour": 1000}
        )
        auth_manager.create_tenant(tenant)
        
        user = User(
            user_id="demo_user",
            username="演示用户",
            email="demo@example.com",
            tenant_id="demo_tenant",
            roles={Role.RESEARCHER, Role.PRINT_OPERATOR}
        )
        auth_manager.register_user(user)
        print(f"   ✅ 用户: {user.username}")
        print(f"   ✅ 权限: {[p.value for p in auth_manager.get_user_permissions(user)]}")
        
        # 3. Coze API测试
        print("\n3️⃣ Coze API健康检查...")
        coze_client = get_coze_client()
        is_healthy = coze_client.health_check()
        print(f"   {'✅' if is_healthy else '❌'} Coze API状态: {'正常' if is_healthy else '异常'}")
        
        # 4. 智能体管理
        print("\n4️⃣ 智能体管理...")
        agent_manager = get_agent_manager()
        await agent_manager.start()
        
        stats = agent_manager.get_stats()
        print(f"   ✅ 智能体数量: {stats['total_agents']}")
        print(f"   ✅ 智能体类型: {list(stats['agent_types'].keys())}")
        
        # 创建任务
        task_context = TaskContext(
            task_id="demo_task_001",
            tenant_id="demo_tenant",
            user_id="demo_user"
        )
        
        task = agent_manager.create_task(
            task_type="qna",
            agent_type=AgentType.QNA_AGENT,
            input_data={"question": "什么是咖啡？"},
            context=task_context,
            priority=TaskPriority.NORMAL
        )
        print(f"   ✅ 创建任务: {task.task_id}")
        
        # 5. 消息路由
        print("\n5️⃣ 消息路由...")
        router = get_message_router()
        await router.start()
        
        events_processed = []
        def demo_handler(event):
            events_processed.append(event)
        
        from coze_integration.message_router import Subscription
        subscription = Subscription(
            subscription_id="demo_sub",
            event_types=[EventType.KB_UPDATED],
            callback=demo_handler
        )
        router.subscribe(subscription)
        
        await router.publish(
            EventType.KB_UPDATED,
            "demo_tenant",
            {"kb_id": "demo_kb", "version": "v1.0"},
            "demo_user"
        )
        
        await asyncio.sleep(0.5)  # 等待事件处理
        print(f"   ✅ 事件处理: {len(events_processed)} 个事件")
        
        # 6. API网关
        print("\n6️⃣ API网关测试...")
        gateway = get_gateway()
        await gateway.start()
        
        from coze_integration.integration_gateway import APIRequest
        health_request = APIRequest(
            request_id="demo_health",
            endpoint=APIEndpoint.SYSTEM_HEALTH,
            method="GET",
            user=user,
            tenant_id="demo_tenant",
            data={},
            headers={"Authorization": "Bearer demo_token"}
        )
        
        response = await gateway.handle_request(health_request)
        print(f"   {'✅' if response.success else '❌'} 健康检查: {response.success}")
        if response.success:
            print(f"   ✅ 系统状态: {response.data.get('status', 'unknown')}")
        
        # 7. 演示问答
        print("\n7️⃣ 演示问答流程...")
        query_request = APIRequest(
            request_id="demo_query",
            endpoint=APIEndpoint.QUERY,
            method="POST",
            user=user,
            tenant_id="demo_tenant",
            data={
                "query": "请介绍一下咖啡的种类",
                "context": {"language": "zh-CN"}
            },
            headers={"Authorization": "Bearer demo_token"}
        )
        
        query_response = await gateway.handle_request(query_request)
        print(f"   {'✅' if query_response.success else '❌'} 问答响应: {query_response.success}")
        if query_response.success:
            print(f"   ✅ 响应时间: {query_response.execution_time:.3f}s")
            answer = query_response.data.get('answer', '')
            if answer:
                print(f"   📝 答案预览: {answer[:100]}...")
        
        # 8. 系统统计
        print("\n8️⃣ 系统统计...")
        gateway_stats = gateway.get_stats()
        agent_stats = agent_manager.get_stats()
        router_stats = router.get_stats()
        
        print(f"   📊 网关请求: {gateway_stats['total_requests']}")
        print(f"   📊 智能体任务: {agent_stats['total_tasks']}")
        print(f"   📊 消息队列: {router_stats['queue_size']}")
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！系统运行正常")
        print("\n💡 使用提示:")
        print("   - 查看 README.md 了解详细用法")
        print("   - 运行 examples/basic_usage.py 学习完整示例")
        print("   - 运行 tests/test_coze_integration.py 进行测试")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        try:
            await gateway.stop()
            await agent_manager.stop()
            await router.stop()
        except:
            pass


def show_help():
    """显示帮助信息"""
    print("""
Coze集成接口演示脚本

用法:
    python demo.py [选项]

选项:
    demo        运行快速演示 (默认)
    help        显示此帮助信息

示例:
    python demo.py demo
    python demo.py help

更多信息请查看 README.md
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "help":
            show_help()
        elif sys.argv[1] == "demo":
            asyncio.run(quick_demo())
        else:
            print(f"未知选项: {sys.argv[1]}")
            show_help()
    else:
        # 默认运行演示
        asyncio.run(quick_demo())