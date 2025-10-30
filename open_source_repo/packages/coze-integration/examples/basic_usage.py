"""
使用示例
展示如何使用Coze集成接口的各种功能
"""
import asyncio
import json
from typing import Dict, Any

# 导入主要组件
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
    APIEndpoint
)


async def example_1_basic_setup():
    """示例1: 基础系统设置"""
    print("=== 示例1: 基础系统设置 ===")
    
    # 1. 加载配置
    config_manager = get_config_manager()
    config = config_manager.get_config()
    print(f"系统环境: {config.environment}")
    print(f"Coze API地址: {config.coze.base_url}")
    
    # 2. 初始化认证系统
    auth_manager = get_auth_manager()
    
    # 创建租户
    from coze_integration.auth_manager import Tenant
    tenant = Tenant(
        tenant_id="coffee_shop_001",
        name="咖啡店001",
        quota={"max_users": 50, "max_requests_per_hour": 5000}
    )
    auth_manager.create_tenant(tenant)
    
    # 创建用户
    user = User(
        user_id="user_001",
        username="咖啡师张三",
        email="zhangsan@coffee.com",
        tenant_id="coffee_shop_001",
        roles={Role.RESEARCHER, Role.PRINT_OPERATOR}
    )
    auth_manager.register_user(user)
    
    print(f"创建用户: {user.username} ({user.user_id})")
    print(f"用户权限: {[p.value for p in auth_manager.get_user_permissions(user)]}")
    
    return user, tenant


async def example_2_coze_client():
    """示例2: Coze API客户端使用"""
    print("\n=== 示例2: Coze API客户端使用 ===")
    
    # 获取Coze客户端
    coze_client = get_coze_client()
    
    try:
        # 健康检查
        is_healthy = coze_client.health_check()
        print(f"Coze API健康状态: {'正常' if is_healthy else '异常'}")
        
        # 列出可用机器人
        bots = coze_client.list_bots()
        print(f"可用机器人数量: {len(bots)}")
        
        # 创建对话（如果需要）
        # conversation = coze_client.create_conversation("your_bot_id")
        # print(f"创建对话: {conversation.conversation_id}")
        
        # 发送聊天消息
        from coze_client import ChatRequest
        request = ChatRequest(
            bot_id="demo_bot_001",
            query="请介绍一下阿拉比卡咖啡的特点",
            stream=False
        )
        
        response = coze_client.chat(request)
        print(f"聊天响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"Coze API调用失败: {e}")


async def example_3_agent_management():
    """示例3: 智能体管理"""
    print("\n=== 示例3: 智能体管理 ===")
    
    # 获取智能体管理器
    agent_manager = get_agent_manager()
    
    # 启动管理器
    await agent_manager.start()
    
    # 查看智能体统计
    stats = agent_manager.get_stats()
    print(f"智能体统计:")
    print(f"  总智能体数: {stats['total_agents']}")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  成功率: {stats['success_rate']:.2%}")
    print(f"  智能体类型: {stats['agent_types']}")
    
    # 创建任务上下文
    task_context = TaskContext(
        task_id="task_001",
        tenant_id="coffee_shop_001",
        user_id="user_001"
    )
    
    # 创建问答任务
    qna_task = agent_manager.create_task(
        task_type="qna",
        agent_type=AgentType.QNA_AGENT,
        input_data={
            "question": "什么是手冲咖啡？",
            "context": {"language": "zh-CN"}
        },
        context=task_context,
        priority=TaskPriority.NORMAL
    )
    
    print(f"创建任务: {qna_task.task_id} ({qna_task.task_type})")
    
    # 提交任务
    success = await agent_manager.submit_task(qna_task)
    print(f"任务提交: {'成功' if success else '失败'}")
    
    # 等待任务完成并查看结果
    await asyncio.sleep(3)  # 等待处理
    
    task_status = agent_manager.get_task_status(qna_task.task_id)
    if task_status:
        print(f"任务状态: {task_status.status.value}")
        if task_status.output_data:
            print(f"任务结果: {task_status.output_data.get('answer', '')[:100]}...")


async def example_4_message_routing():
    """示例4: 消息路由"""
    print("\n=== 示例4: 消息路由 ===")
    
    # 获取消息路由器
    router = get_message_router()
    
    # 启动路由器
    await router.start()
    
    # 定义事件处理器
    def knowledge_update_handler(event):
        print(f"知识库更新事件: {event.payload}")
    
    def rag_completed_handler(event):
        print(f"RAG完成事件: 查询ID {event.payload.get('query_id')}")
    
    # 订阅事件
    from message_router import Subscription, EventType
    subscription1 = Subscription(
        subscription_id="kb_sub_001",
        event_types=[EventType.KB_UPDATED],
        callback=knowledge_update_handler
    )
    
    subscription2 = Subscription(
        subscription_id="rag_sub_001", 
        event_types=[EventType.RAG_COMPLETED],
        callback=rag_completed_handler
    )
    
    router.subscribe(subscription1)
    router.subscribe(subscription2)
    
    # 发布事件
    await router.publish(
        EventType.KB_UPDATED,
        tenant_id="coffee_shop_001",
        payload={"kb_id": "kb_001", "version": "v1.2"},
        user_id="user_001"
    )
    
    await router.publish(
        EventType.RAG_COMPLETED,
        tenant_id="coffee_shop_001", 
        payload={"query_id": "query_001", "references": ["ref1", "ref2"]},
        user_id="user_001"
    )
    
    # 等待事件处理
    await asyncio.sleep(2)
    
    # 查看统计
    stats = router.get_stats()
    print(f"路由器统计: {stats}")


async def example_5_api_gateway():
    """示例5: API网关使用"""
    print("\n=== 示例5: API网关使用 ===")
    
    # 获取网关
    gateway = get_gateway()
    
    # 启动网关
    await gateway.start()
    
    # 创建用户（用于认证）
    auth_manager = get_auth_manager()
    user = auth_manager._users.get("user_001")
    
    # 模拟API请求
    from integration_gateway import APIRequest
    
    # 1. 问答查询
    query_request = APIRequest(
        request_id="req_001",
        endpoint=APIEndpoint.QUERY,
        method="POST",
        user=user,
        tenant_id="coffee_shop_001",
        data={
            "query": "如何制作拿铁咖啡？",
            "context": {"difficulty": "beginner"}
        },
        headers={"Authorization": "Bearer demo_token"}
    )
    
    response = await gateway.handle_request(query_request)
    print(f"查询响应: 成功={response.success}, 耗时={response.execution_time:.3f}s")
    if response.success:
        print(f"答案: {response.data.get('answer', '')[:100]}...")
    
    # 2. 智能体调度
    dispatch_request = APIRequest(
        request_id="req_002",
        endpoint=APIEndpoint.AGENTS_DISPATCH,
        method="POST",
        user=user,
        tenant_id="coffee_shop_001",
        data={
            "task_type": "research",
            "input_data": {
                "query": "研究咖啡豆的产地对风味的影响",
                "depth": "detailed"
            }
        },
        headers={"Authorization": "Bearer demo_token"}
    )
    
    response = await gateway.handle_request(dispatch_request)
    print(f"调度响应: 成功={response.success}")
    if response.success:
        print(f"任务ID: {response.data.get('task_id')}")
    
    # 3. 系统指标
    metrics_request = APIRequest(
        request_id="req_003",
        endpoint=APIEndpoint.SYSTEM_METRICS,
        method="GET",
        user=user,
        tenant_id="coffee_shop_001",
        data={},
        headers={"Authorization": "Bearer demo_token"}
    )
    
    response = await gateway.handle_request(metrics_request)
    if response.success:
        metrics = response.data
        print(f"系统指标: 总请求={metrics['gateway_stats']['total_requests']}")


async def example_6_comprehensive_workflow():
    """示例6: 综合工作流程"""
    print("\n=== 示例6: 综合工作流程 ===")
    
    print("模拟完整的咖啡知识问答流程...")
    
    # 1. 用户提问
    user_question = "请介绍一下埃塞俄比亚咖啡豆的特点"
    print(f"用户问题: {user_question}")
    
    # 2. 通过网关处理查询
    gateway = get_gateway()
    auth_manager = get_auth_manager()
    user = auth_manager._users.get("user_001")
    
    query_request = APIRequest(
        request_id="workflow_001",
        endpoint=APIEndpoint.QUERY,
        method="POST",
        user=user,
        tenant_id="coffee_shop_001",
        data={
            "query": user_question,
            "context": {"user_level": "intermediate"}
        },
        headers={"Authorization": "Bearer demo_token"}
    )
    
    response = await gateway.handle_request(query_request)
    
    if response.success:
        answer = response.data.get('answer', '')
        print(f"AI回答: {answer[:200]}...")
        
        # 3. 发布相关事件
        router = get_message_router()
        await router.publish(
            EventType.RAG_COMPLETED,
            "coffee_shop_001",
            {"query_id": "workflow_001", "answer_length": len(answer)},
            "user_001"
        )
        
        # 4. 如果需要，打印相关资料
        print("生成打印资料...")
        print_request = APIRequest(
            request_id="workflow_002",
            endpoint=APIEndpoint.PRINT_TICKET,
            method="POST",
            user=user,
            tenant_id="coffee_shop_001",
            data={
                "content": f"咖啡知识问答\n\n问题: {user_question}\n\n答案: {answer[:300]}...",
                "printer_config": {"printer_id": "coffee_printer"}
            },
            headers={"Authorization": "Bearer demo_token"}
        )
        
        print_response = await gateway.handle_request(print_request)
        if print_response.success:
            print(f"打印任务已创建: {print_response.data.get('task_id')}")
    
    print("工作流程完成")


async def run_all_examples():
    """运行所有示例"""
    print("Coze集成接口使用示例")
    print("=" * 50)
    
    try:
        # 运行各个示例
        await example_1_basic_setup()
        await example_2_coze_client()
        await example_3_agent_management()
        await example_4_message_routing()
        await example_5_api_gateway()
        await example_6_comprehensive_workflow()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行所有示例
    asyncio.run(run_all_examples())