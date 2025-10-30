# 用例示例

这些实际用例展示了如何在不同场景中应用 AI Tech Innovation Suite。

## 目录

- [智能客服系统](#智能客服系统)
- [内容营销平台](#内容营销平台)
- [知识分析平台](#知识分析平台)
- [企业内部协作系统](#企业内部协作系统)

## 智能客服系统

展示如何使用多智能体框架构建企业级智能客服系统。

```python
# examples/use-cases/intelligent_customer_service.py
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from packages.multi_agent_framework import AgentRegistry, HostAgent, ExpertAgent
from packages.knowledge_management import KnowledgeManager

class IntelligentCustomerService:
    """智能客服系统"""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.knowledge_manager = KnowledgeManager()
        self.conversation_sessions = {}
        self.service_metrics = {
            "total_conversations": 0,
            "successful_resolutions": 0,
            "average_response_time": 0.0,
            "customer_satisfaction": 0.0
        }
    
    async def setup_service_system(self):
        """设置客服系统"""
        # 创建主持人智能体
        host = HostAgent(
            name="客服主持人",
            role="客户问题分流和协调",
            system_prompt="""你是一个专业的客服主持人，负责：
            1. 理解客户问题并分类
            2. 将问题分配给合适的专家智能体
            3. 协调多个智能体共同解决复杂问题
            4. 确保客户获得满意的解答"""
        )
        
        # 创建专家智能体
        experts = [
            ExpertAgent(
                name="产品专家",
                specialty="产品咨询",
                system_prompt="你是一个产品专家，熟悉所有产品的功能、规格、使用方法等"
            ),
            ExpertAgent(
                name="技术支持专家",
                specialty="技术支持", 
                system_prompt="你是一个技术支持专家，擅长解决技术问题和故障排除"
            ),
            ExpertAgent(
                name="订单专家",
                specialty="订单处理",
                system_prompt="你是一个订单专家，负责处理订单查询、修改、退换货等问题"
            ),
            ExpertAgent(
                name="投诉处理专家",
                specialty="投诉处理",
                system_prompt="你是一个投诉处理专家，善于倾听客户不满并提供解决方案"
            )
        ]
        
        # 注册智能体
        await self.registry.register_agent("host", host)
        for expert in experts:
            await self.registry.register_agent(expert.name, expert)
        
        print("✅ 智能客服系统设置完成")
    
    async def handle_customer_inquiry(self, customer_id: str, inquiry: str, context: Dict[str, Any] = None):
        """处理客户咨询"""
        print(f"👤 处理客户 {customer_id} 的咨询...")
        
        # 创建会话记录
        session_id = f"{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_sessions[session_id] = {
            "customer_id": customer_id,
            "inquiry": inquiry,
            "context": context or {},
            "start_time": datetime.now(),
            "messages": [],
            "assigned_experts": [],
            "resolution_status": "in_progress"
        }
        
        # 分析问题并分配专家
        assigned_experts = await self._analyze_and_assign(inquiry)
        
        # 协调解决
        resolution = await self._coordinate_resolution(session_id, inquiry, assigned_experts)
        
        # 更新指标
        await self._update_metrics(resolution["success"])
        
        return {
            "session_id": session_id,
            "customer_id": customer_id,
            "inquiry": inquiry,
            "resolution": resolution,
            "assigned_experts": assigned_experts,
            "response_time": (datetime.now() - self.conversation_sessions[session_id]["start_time"]).total_seconds()
        }
    
    async def _analyze_and_assign(self, inquiry: str) -> List[str]:
        """分析问题并分配专家"""
        # 关键词分析
        inquiry_lower = inquiry.lower()
        
        expert_assignments = []
        
        # 产品相关问题
        if any(keyword in inquiry_lower for keyword in ["产品", "功能", "规格", "使用方法", "怎么用"]):
            expert_assignments.append("产品专家")
        
        # 技术支持问题
        if any(keyword in inquiry_lower for keyword in ["错误", "bug", "故障", "无法", "技术", "系统"]):
            expert_assignments.append("技术支持专家")
        
        # 订单相关问题
        if any(keyword in inquiry_lower for keyword in ["订单", "购买", "支付", "发货", "物流", "退货", "退款"]):
            expert_assignments.append("订单专家")
        
        # 投诉问题
        if any(keyword in inquiry_lower for keyword in ["投诉", "不满", "问题", "建议", "反馈"]):
            expert_assignments.append("投诉处理专家")
        
        # 如果没有匹配到特定专家，分配给产品专家
        if not expert_assignments:
            expert_assignments.append("产品专家")
        
        return expert_assignments
    
    async def _coordinate_resolution(self, session_id: str, inquiry: str, assigned_experts: List[str]):
        """协调解决客户问题"""
        session = self.conversation_sessions[session_id]
        
        # 记录分配的专家
        session["assigned_experts"] = assigned_experts
        
        # 依次询问专家
        expert_responses = []
        
        for expert_name in assigned_experts:
            print(f"🔄 咨询 {expert_name}...")
            
            # 发送问题给专家
            response = await self.registry.send_message(
                agent_name=expert_name,
                message=f"客户咨询：{inquiry}\n\n请提供专业的解答和解决方案。"
            )
            
            expert_responses.append({
                "expert": expert_name,
                "response": response,
                "timestamp": datetime.now()
            })
            
            # 记录消息
            session["messages"].append({
                "type": "expert_response",
                "expert": expert_name,
                "content": response,
                "timestamp": datetime.now()
            })
        
        # 综合专家意见生成最终回复
        final_response = await self._generate_final_response(inquiry, expert_responses)
        
        # 更新会话状态
        session["resolution_status"] = "resolved"
        session["final_response"] = final_response
        session["end_time"] = datetime.now()
        
        return {
            "success": True,
            "response": final_response,
            "expert_responses": expert_responses,
            "resolution_time": (session["end_time"] - session["start_time"]).total_seconds()
        }
    
    async def _generate_final_response(self, inquiry: str, expert_responses: List[Dict[str, Any]]) -> str:
        """生成最终回复"""
        # 使用主持人智能体综合专家意见
        combined_responses = "\n\n".join([
            f"{resp['expert']}的解答：\n{resp['response']}"
            for resp in expert_responses
        ])
        
        final_response = await self.registry.send_message(
            agent_name="host",
            message=f"""客户原始咨询：{inquiry}

各位专家的解答：
{combined_responses}

请综合各位专家的意见，生成一个完整、清晰、有帮助的最终回复。"""
        )
        
        return final_response
    
    async def _update_metrics(self, success: bool):
        """更新服务指标"""
        self.service_metrics["total_conversations"] += 1
        
        if success:
            self.service_metrics["successful_resolutions"] += 1
        
        # 计算成功率
        success_rate = (
            self.service_metrics["successful_resolutions"] / 
            self.service_metrics["total_conversations"]
        )
        
        # 模拟客户满意度（实际中应该从客户反馈获取）
        self.service_metrics["customer_satisfaction"] = min(0.95, success_rate + 0.1)
    
    async def get_service_analytics(self) -> Dict[str, Any]:
        """获取服务分析数据"""
        # 统计专家工作量
        expert_workload = {}
        for session in self.conversation_sessions.values():
            for expert in session["assigned_experts"]:
                expert_workload[expert] = expert_workload.get(expert, 0) + 1
        
        # 计算平均响应时间
        response_times = []
        for session in self.conversation_sessions.values():
            if "end_time" in session:
                duration = (session["end_time"] - session["start_time"]).total_seconds()
                response_times.append(duration)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "service_metrics": self.service_metrics,
            "expert_workload": expert_workload,
            "average_response_time": avg_response_time,
            "total_sessions": len(self.conversation_sessions),
            "resolution_rate": (
                self.service_metrics["successful_resolutions"] / 
                self.service_metrics["total_conversations"]
                if self.service_metrics["total_conversations"] > 0 else 0
            )
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.registry.cleanup()
        await self.knowledge_manager.cleanup()

# 使用示例
async def main():
    service = IntelligentCustomerService()
    await service.setup_service_system()
    
    try:
        # 模拟客户咨询
        inquiries = [
            {
                "customer_id": "customer_001",
                "inquiry": "我想了解一下你们的新产品有什么功能？",
                "context": {"customer_type": "new", "previous_purchases": []}
            },
            {
                "customer_id": "customer_002", 
                "inquiry": "我的订单为什么还没有发货？订单号是12345",
                "context": {"customer_type": "existing", "order_id": "12345"}
            },
            {
                "customer_id": "customer_003",
                "inquiry": "系统总是提示错误，无法正常使用你们的软件",
                "context": {"customer_type": "premium", "error_code": "ERR_500"}
            }
        ]
        
        # 处理咨询
        results = []
        for inquiry_data in inquiries:
            result = await service.handle_customer_inquiry(
                inquiry_data["customer_id"],
                inquiry_data["inquiry"],
                inquiry_data["context"]
            )
            results.append(result)
            
            print(f"\n💬 客户咨询处理完成:")
            print(f"  会话ID: {result['session_id']}")
            print(f"  分配专家: {', '.join(result['assigned_experts'])}")
            print(f"  解决状态: {result['resolution']['success']}")
            print(f"  响应时间: {result['response_time']:.2f}秒")
        
        # 获取分析数据
        analytics = await service.get_service_analytics()
        print(f"\n📊 服务分析:")
        print(f"  总咨询数: {analytics['total_sessions']}")
        print(f"  解决率: {analytics['resolution_rate']:.1%}")
        print(f"  平均响应时间: {analytics['average_response_time']:.2f}秒")
        print(f"  客户满意度: {analytics['service_metrics']['customer_satisfaction']:.1%}")
        
        print(f"\n👥 专家工作量:")
        for expert, count in analytics['expert_workload'].items():
            print(f"  {expert}: {count}次")
        
    finally:
        await service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 内容营销平台

展示如何使用小红书Agent构建内容营销平台。

```python
# examples/use-cases/content_marketing_platform.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from packages.xiaohongshu_agent import XiaohongshuAgent
from packages.scheduler_agent import SchedulerAgent
from packages.knowledge_emergence import KnowledgeEmergenceAnalyzer

class ContentMarketingPlatform:
    """内容营销平台"""
    
    def __init__(self):
        self.xiaohongshu_agent = XiaohongshuAgent()
        self.scheduler = SchedulerAgent()
        self.knowledge_analyzer = KnowledgeEmergenceAnalyzer()
        self.campaigns = {}
        self.content_library = []
        self.performance_data = {}
    
    async def create_marketing_campaign(self, campaign_config: Dict[str, Any]):
        """创建营销活动"""
        print(f"🚀 创建营销活动: {campaign_config['name']}")
        
        campaign_id = f"campaign_{len(self.campaigns) + 1}"
        
        # 创建活动
        campaign = {
            "id": campaign_id,
            "name": campaign_config["name"],
            "brand_info": campaign_config["brand_info"],
            "target_audience": campaign_config["target_audience"],
            "content_strategy": campaign_config["content_strategy"],
            "budget": campaign_config.get("budget", 0),
            "duration": campaign_config.get("duration", 30),  # 天
            "created_at": datetime.now(),
            "status": "active",
            "content_items": [],
            "performance_metrics": {
                "total_content": 0,
                "total_views": 0,
                "total_engagement": 0,
                "cost_per_engagement": 0.0
            }
        }
        
        self.campaigns[campaign_id] = campaign
        
        # 生成内容计划
        content_plan = await self._generate_content_plan(campaign)
        
        # 批量生成内容
        content_items = await self._batch_generate_content(campaign, content_plan)
        
        # 调度发布
        scheduled_posts = await self._schedule_content_publishing(campaign_id, content_items)
        
        campaign["content_items"] = content_items
        campaign["scheduled_posts"] = scheduled_posts
        
        print(f"✅ 营销活动创建完成")
        print(f"  活动ID: {campaign_id}")
        print(f"  内容数量: {len(content_items)}")
        print(f"  计划发布: {len(scheduled_posts)}篇")
        
        return campaign_id
    
    async def _generate_content_plan(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成内容计划"""
        content_plan = []
        duration_days = campaign["duration"]
        content_frequency = campaign["content_strategy"].get("frequency", "daily")  # daily, weekly
        
        # 根据频率计算内容数量
        if content_frequency == "daily":
            content_count = duration_days
        elif content_frequency == "weekly":
            content_count = duration_days // 7
        else:
            content_count = duration_days
        
        # 内容类型分布
        content_types = campaign["content_strategy"].get("content_types", [
            "product_showcase", "user_experience", "educational", "behind_scenes"
        ])
        
        for i in range(content_count):
            content_type = content_types[i % len(content_types)]
            
            # 根据内容类型生成主题
            topics = self._generate_topics_for_type(content_type, campaign)
            topic = topics[i % len(topics)]
            
            content_plan.append({
                "id": f"content_{i+1}",
                "type": content_type,
                "topic": topic,
                "priority": self._calculate_content_priority(i, content_count),
                "scheduled_date": campaign["created_at"] + timedelta(days=i),
                "target_metrics": self._set_target_metrics(content_type)
            })
        
        return content_plan
    
    def _generate_topics_for_type(self, content_type: str, campaign: Dict[str, Any]) -> List[str]:
        """为内容类型生成主题"""
        base_topics = {
            "product_showcase": [
                "新品发布", "产品功能介绍", "使用场景展示", "产品对比"
            ],
            "user_experience": [
                "用户故事", "使用心得", "效果展示", "真实反馈"
            ],
            "educational": [
                "使用教程", "技巧分享", "行业知识", "常见问题解答"
            ],
            "behind_scenes": [
                "制作过程", "团队介绍", "企业文化", "研发故事"
            ]
        }
        
        topics = base_topics.get(content_type, ["通用内容"])
        
        # 结合品牌信息调整主题
        brand_name = campaign["brand_info"]["name"]
        adjusted_topics = [f"{brand_name}的{topic}" for topic in topics]
        
        return adjusted_topics
    
    def _calculate_content_priority(self, index: int, total: int) -> str:
        """计算内容优先级"""
        if index < total * 0.2:
            return "high"  # 前20%为高优先级
        elif index < total * 0.6:
            return "medium"  # 中间40%为中等优先级
        else:
            return "low"  # 后40%为低优先级
    
    def _set_target_metrics(self, content_type: str) -> Dict[str, Any]:
        """设置目标指标"""
        targets = {
            "product_showcase": {"views": 5000, "engagement": 500, "conversion": 0.05},
            "user_experience": {"views": 3000, "engagement": 400, "conversion": 0.03},
            "educational": {"views": 2000, "engagement": 300, "conversion": 0.02},
            "behind_scenes": {"views": 1500, "engagement": 200, "conversion": 0.01}
        }
        
        return targets.get(content_type, {"views": 1000, "engagement": 100, "conversion": 0.01})
    
    async def _batch_generate_content(self, campaign: Dict[str, Any], content_plan: List[Dict[str, Any]]):
        """批量生成内容"""
        content_items = []
        
        print(f"📝 开始批量生成 {len(content_plan)} 个内容...")
        
        for plan_item in content_plan:
            print(f"  生成内容: {plan_item['topic']}")
            
            # 生成内容
            content = await self.xiaohongshu_agent.generate_content(
                topic=plan_item["topic"],
                brand_info=campaign["brand_info"],
                content_type=plan_item["type"],
                additional_context={
                    "target_audience": campaign["target_audience"],
                    "content_strategy": campaign["content_strategy"],
                    "priority": plan_item["priority"]
                }
            )
            
            # 添加元数据
            content_item = {
                "id": plan_item["id"],
                "plan": plan_item,
                "generated_content": content,
                "generated_at": datetime.now(),
                "status": "ready_to_publish",
                "performance": {
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "engagement_rate": 0.0
                }
            }
            
            content_items.append(content_item)
            self.content_library.append(content_item)
        
        return content_items
    
    async def _schedule_content_publishing(self, campaign_id: str, content_items: List[Dict[str, Any]]):
        """调度内容发布"""
        scheduled_posts = []
        
        for content_item in content_items:
            scheduled_date = content_item["plan"]["scheduled_date"]
            
            # 创建发布任务
            task = await self.scheduler.schedule_task(
                task_type="content_publication",
                target_time=scheduled_date,
                task_data={
                    "campaign_id": campaign_id,
                    "content_id": content_item["id"],
                    "content": content_item["generated_content"],
                    "platform": "xiaohongshu"
                },
                priority=content_item["plan"]["priority"]
            )
            
            scheduled_posts.append({
                "content_id": content_item["id"],
                "task_id": task["task_id"],
                "scheduled_time": scheduled_date,
                "status": "scheduled"
            })
        
        return scheduled_posts
    
    async def analyze_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """分析活动表现"""
        if campaign_id not in self.campaigns:
            raise ValueError(f"活动 {campaign_id} 不存在")
        
        campaign = self.campaigns[campaign_id]
        
        print(f"📊 分析活动表现: {campaign['name']}")
        
        # 收集表现数据
        performance_data = await self._collect_performance_data(campaign_id)
        
        # 分析内容表现
        content_analysis = await self._analyze_content_performance(campaign["content_items"])
        
        # 生成洞察
        insights = await self._generate_campaign_insights(performance_data, content_analysis)
        
        # 更新活动指标
        campaign["performance_metrics"] = performance_data["summary"]
        campaign["content_analysis"] = content_analysis
        campaign["insights"] = insights
        campaign["last_analyzed"] = datetime.now()
        
        return {
            "campaign_id": campaign_id,
            "performance_data": performance_data,
            "content_analysis": content_analysis,
            "insights": insights,
            "recommendations": await self._generate_recommendations(insights)
        }
    
    async def _collect_performance_data(self, campaign_id: str) -> Dict[str, Any]:
        """收集表现数据"""
        campaign = self.campaigns[campaign_id]
        
        # 模拟表现数据收集（实际中需要调用平台API）
        total_views = 0
        total_engagement = 0
        total_content = len(campaign["content_items"])
        
        for content_item in campaign["content_items"]:
            # 模拟数据
            views = content_item["performance"]["views"]
            engagement = content_item["performance"]["engagement"]
            
            total_views += views
            total_engagement += engagement
        
        return {
            "summary": {
                "total_content": total_content,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "average_views_per_content": total_views / total_content if total_content > 0 else 0,
                "average_engagement_per_content": total_engagement / total_content if total_content > 0 else 0,
                "engagement_rate": total_engagement / total_views if total_views > 0 else 0
            },
            "content_performance": [
                {
                    "content_id": item["id"],
                    "topic": item["plan"]["topic"],
                    "type": item["plan"]["type"],
                    "performance": item["performance"]
                }
                for item in campaign["content_items"]
            ]
        }
    
    async def _analyze_content_performance(self, content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析内容表现"""
        # 按类型分析
        type_performance = {}
        
        for item in content_items:
            content_type = item["plan"]["type"]
            if content_type not in type_performance:
                type_performance[content_type] = {
                    "count": 0,
                    "total_views": 0,
                    "total_engagement": 0
                }
            
            type_performance[content_type]["count"] += 1
            type_performance[content_type]["total_views"] += item["performance"]["views"]
            type_performance[content_type]["total_engagement"] += item["performance"]["engagement"]
        
        # 计算平均值
        for content_type, data in type_performance.items():
            if data["count"] > 0:
                data["avg_views"] = data["total_views"] / data["count"]
                data["avg_engagement"] = data["total_engagement"] / data["count"]
                data["engagement_rate"] = data["total_engagement"] / data["total_views"] if data["total_views"] > 0 else 0
        
        return {
            "type_performance": type_performance,
            "top_performing_content": sorted(
                content_items,
                key=lambda x: x["performance"]["engagement"],
                reverse=True
            )[:5]
        }
    
    async def _generate_campaign_insights(self, performance_data: Dict[str, Any], content_analysis: Dict[str, Any]):
        """生成活动洞察"""
        insights = []
        
        # 总体表现洞察
        summary = performance_data["summary"]
        
        if summary["engagement_rate"] > 0.1:
            insights.append({
                "type": "positive",
                "category": "overall_performance",
                "message": "活动整体表现优秀，用户参与度高于预期"
            })
        elif summary["engagement_rate"] < 0.05:
            insights.append({
                "type": "concern",
                "category": "overall_performance", 
                "message": "活动整体参与度较低，建议优化内容策略"
            })
        
        # 内容类型洞察
        type_performance = content_analysis["type_performance"]
        best_type = max(type_performance.items(), key=lambda x: x[1]["engagement_rate"])
        
        insights.append({
            "type": "insight",
            "category": "content_strategy",
            "message": f"'{best_type[0]}'类型内容表现最佳，建议增加此类内容比例"
        })
        
        return insights
    
    async def _generate_recommendations(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成建议"""
        recommendations = []
        
        for insight in insights:
            if insight["category"] == "overall_performance":
                if insight["type"] == "concern":
                    recommendations.append({
                        "action": "optimize_content_strategy",
                        "description": "调整内容策略，提高用户参与度",
                        "priority": "high"
                    })
            
            elif insight["category"] == "content_strategy":
                recommendations.append({
                    "action": "adjust_content_mix",
                    "description": f"增加'{insight['message'].split("'")[1]}'类型内容",
                    "priority": "medium"
                })
        
        return recommendations
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """获取平台分析数据"""
        total_campaigns = len(self.campaigns)
        total_content = len(self.content_library)
        
        # 计算总体表现
        total_views = sum(
            item["performance"]["views"] 
            for item in self.content_library
        )
        total_engagement = sum(
            item["performance"]["engagement"] 
            for item in self.content_library
        )
        
        return {
            "platform_overview": {
                "total_campaigns": total_campaigns,
                "total_content": total_content,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "average_engagement_rate": total_engagement / total_views if total_views > 0 else 0
            },
            "campaign_status": {
                "active": len([c for c in self.campaigns.values() if c["status"] == "active"]),
                "completed": len([c for c in self.campaigns.values() if c["status"] == "completed"]),
                "paused": len([c for c in self.campaigns.values() if c["status"] == "paused"])
            },
            "top_campaigns": sorted(
                self.campaigns.values(),
                key=lambda x: x["performance_metrics"]["total_engagement"],
                reverse=True
            )[:5]
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.xiaohongshu_agent.cleanup()
        await self.scheduler.cleanup()
        await self.knowledge_analyzer.cleanup()

# 使用示例
async def main():
    platform = ContentMarketingPlatform()
    
    try:
        # 创建营销活动
        campaign_config = {
            "name": "夏季护肤新品推广",
            "brand_info": {
                "name": "美丽日记",
                "category": "护肤",
                "target_market": "18-35岁女性"
            },
            "target_audience": {
                "age_range": "18-35",
                "interests": ["护肤", "美容", "时尚"],
                "platform_preference": "xiaohongshu"
            },
            "content_strategy": {
                "frequency": "daily",
                "content_types": ["product_showcase", "user_experience", "educational"],
                "tone": "friendly_professional",
                "visual_style": "clean_minimalist"
            },
            "budget": 50000,
            "duration": 30
        }
        
        campaign_id = await platform.create_marketing_campaign(campaign_config)
        
        # 模拟等待内容发布
        print("⏳ 等待内容发布和表现数据收集...")
        await asyncio.sleep(2)  # 实际中等待更长时间
        
        # 分析活动表现
        analysis = await platform.analyze_campaign_performance(campaign_id)
        
        print(f"\n📊 活动表现分析:")
        print(f"  总内容数: {analysis['performance_data']['summary']['total_content']}")
        print(f"  总浏览量: {analysis['performance_data']['summary']['total_views']}")
        print(f"  总互动量: {analysis['performance_data']['summary']['total_engagement']}")
        print(f"  平均互动率: {analysis['performance_data']['summary']['engagement_rate']:.1%}")
        
        print(f"\n💡 关键洞察:")
        for insight in analysis["insights"]:
            print(f"  - {insight['message']}")
        
        print(f"\n📋 优化建议:")
        for rec in analysis["recommendations"]:
            print(f"  - {rec['description']} (优先级: {rec['priority']})")
        
        # 获取平台分析
        platform_analytics = await platform.get_platform_analytics()
        print(f"\n🏢 平台概览:")
        print(f"  总活动数: {platform_analytics['platform_overview']['total_campaigns']}")
        print(f"  总内容数: {platform_analytics['platform_overview']['total_content']}")
        print(f"  活跃活动: {platform_analytics['campaign_status']['active']}")
        
    finally:
        await platform.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

这些用例示例展示了如何在真实业务场景中应用 AI Tech Innovation Suite 的各个组件。每个示例都包含了完整的业务逻辑和实现细节，可以作为实际项目的参考模板。
