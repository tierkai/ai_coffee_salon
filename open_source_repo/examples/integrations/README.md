# 集成示例

这些示例展示了如何将 AI Tech Innovation Suite 的各个组件集成在一起，以及与第三方服务的集成。

## 目录

- [多平台内容发布](#多平台内容发布)
- [知识图谱构建](#知识图谱构建)
- [实时分析系统](#实时分析系统)
- [第三方API集成](#第三方api集成)

## 多平台内容发布

展示如何将小红书Agent与其他平台的内容发布系统集成。

```python
# examples/integrations/multi_platform_publisher.py
import asyncio
from typing import List, Dict, Any
from packages.xiaohongshu_agent import XiaohongshuAgent
from packages.scheduler_agent import SchedulerAgent

class MultiPlatformPublisher:
    """多平台内容发布器"""
    
    def __init__(self):
        self.xiaohongshu_agent = XiaohongshuAgent()
        self.scheduler = SchedulerAgent()
        self.platform_configs = {
            "xiaohongshu": {
                "enabled": True,
                "api_config": "xiaohongshu_config",
                "content_format": "xiaohongshu_style"
            },
            "weibo": {
                "enabled": False,  # 示例中禁用
                "api_config": "weibo_config", 
                "content_format": "weibo_style"
            },
            "douyin": {
                "enabled": False,  # 示例中禁用
                "api_config": "douyin_config",
                "content_format": "douyin_style"
            }
        }
    
    async def create_multi_platform_campaign(self, campaign_data: Dict[str, Any]):
        """创建多平台营销活动"""
        print(f"🚀 创建多平台营销活动: {campaign_data['name']}")
        
        # 为每个启用的平台生成内容
        platform_contents = {}
        
        for platform, config in self.platform_configs.items():
            if not config["enabled"]:
                continue
                
            print(f"📱 为平台 {platform} 生成内容...")
            
            if platform == "xiaohongshu":
                content = await self._generate_xiaohongshu_content(campaign_data)
            else:
                # 其他平台的生成逻辑
                content = await self._generate_platform_content(platform, campaign_data)
            
            platform_contents[platform] = content
        
        # 调度发布
        scheduled_tasks = await self._schedule_publication(platform_contents, campaign_data)
        
        return {
            "campaign_id": campaign_data["id"],
            "platform_contents": platform_contents,
            "scheduled_tasks": scheduled_tasks,
            "status": "scheduled"
        }
    
    async def _generate_xiaohongshu_content(self, campaign_data: Dict[str, Any]):
        """生成小红书内容"""
        content = await self.xiaohongshu_agent.generate_content(
            topic=campaign_data["topic"],
            brand_info=campaign_data["brand_info"],
            content_type=campaign_data.get("content_type", "product_promotion"),
            additional_context={
                "target_audience": campaign_data.get("target_audience"),
                "key_messages": campaign_data.get("key_messages", []),
                "hashtag_strategy": campaign_data.get("hashtag_strategy")
            }
        )
        
        # 根据平台特性调整内容
        content["platform"] = "xiaohongshu"
        content["character_limit"] = 2200  # 小红书字符限制
        content["image_requirements"] = {
            "aspect_ratio": "1:1",
            "max_size": (1080, 1080),
            "format": "JPG"
        }
        
        return content
    
    async def _generate_platform_content(self, platform: str, campaign_data: Dict[str, Any]):
        """为其他平台生成内容"""
        # 这里可以实现其他平台的内容生成逻辑
        # 例如微博、抖音等
        
        base_content = {
            "platform": platform,
            "title": f"{campaign_data['topic']} - {platform}",
            "content": f"在{platform}上分享关于{campaign_data['topic']}的内容",
            "hashtags": [f"#{campaign_data['topic']}", f"#{platform}"],
            "character_limit": 140 if platform == "weibo" else 2200,
            "image_requirements": {
                "aspect_ratio": "16:9" if platform == "weibo" else "1:1",
                "max_size": (1080, 1080),
                "format": "JPG"
            }
        }
        
        return base_content
    
    async def _schedule_publication(self, platform_contents: Dict[str, Any], campaign_data: Dict[str, Any]):
        """调度内容发布"""
        scheduled_tasks = []
        
        for platform, content in platform_contents.items():
            # 计算最佳发布时间
            optimal_time = await self._calculate_optimal_time(platform, campaign_data)
            
            # 创建调度任务
            task = await self.scheduler.schedule_task(
                task_type="content_publication",
                target_time=optimal_time,
                task_data={
                    "platform": platform,
                    "content": content,
                    "campaign_id": campaign_data["id"]
                },
                priority=campaign_data.get("priority", "normal")
            )
            
            scheduled_tasks.append({
                "platform": platform,
                "task_id": task["task_id"],
                "scheduled_time": optimal_time,
                "status": "scheduled"
            })
            
            print(f"✅ {platform} 内容已调度到 {optimal_time}")
        
        return scheduled_tasks
    
    async def _calculate_optimal_time(self, platform: str, campaign_data: Dict[str, Any]):
        """计算最佳发布时间"""
        # 简单的最佳时间计算逻辑
        # 实际应用中可以使用更复杂的算法
        
        from datetime import datetime, timedelta
        
        base_time = datetime.now()
        
        # 平台特定的发布时间策略
        platform_strategies = {
            "xiaohongshu": {"hour": 20, "minute": 0},  # 晚上8点
            "weibo": {"hour": 12, "minute": 0},        # 中午12点
            "douyin": {"hour": 19, "minute": 30}       # 晚上7点半
        }
        
        strategy = platform_strategies.get(platform, {"hour": 10, "minute": 0})
        
        # 设置为今天的最佳时间，如果已过则设为明天
        optimal_time = base_time.replace(
            hour=strategy["hour"],
            minute=strategy["minute"],
            second=0,
            microsecond=0
        )
        
        if optimal_time <= base_time:
            optimal_time += timedelta(days=1)
        
        return optimal_time
    
    async def sync_content_performance(self, campaign_id: str):
        """同步内容表现数据"""
        print(f"📊 同步活动 {campaign_id} 的表现数据...")
        
        performance_data = {}
        
        for platform in self.platform_configs:
            if not self.platform_configs[platform]["enabled"]:
                continue
            
            # 获取平台表现数据
            platform_data = await self._fetch_platform_metrics(platform, campaign_id)
            performance_data[platform] = platform_data
        
        # 生成综合报告
        report = await self._generate_performance_report(performance_data)
        
        return report
    
    async def _fetch_platform_metrics(self, platform: str, campaign_id: str):
        """获取平台指标"""
        # 模拟API调用获取平台数据
        # 实际应用中需要调用各平台的API
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "views": 1000,
            "likes": 150,
            "comments": 25,
            "shares": 12,
            "engagement_rate": 0.187,
            "reach": 850,
            "impressions": 1200
        }
    
    async def _generate_performance_report(self, performance_data: Dict[str, Any]):
        """生成表现报告"""
        total_views = sum(data["views"] for data in performance_data.values())
        total_likes = sum(data["likes"] for data in performance_data.values())
        total_comments = sum(data["comments"] for data in performance_data.values())
        
        report = {
            "summary": {
                "total_platforms": len(performance_data),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "overall_engagement": (total_likes + total_comments) / total_views if total_views > 0 else 0
            },
            "platform_breakdown": performance_data,
            "recommendations": await self._generate_recommendations(performance_data)
        }
        
        return report
    
    async def _generate_recommendations(self, performance_data: Dict[str, Any]):
        """生成优化建议"""
        recommendations = []
        
        for platform, data in performance_data.items():
            if data["engagement_rate"] < 0.1:
                recommendations.append({
                    "platform": platform,
                    "type": "engagement_improvement",
                    "suggestion": f"提高{platform}上的互动率，考虑调整内容策略"
                })
            
            if data["views"] < 500:
                recommendations.append({
                    "platform": platform,
                    "type": "reach_improvement", 
                    "suggestion": f"增加{platform}的曝光量，考虑使用付费推广"
                })
        
        return recommendations
    
    async def cleanup(self):
        """清理资源"""
        await self.xiaohongshu_agent.cleanup()
        await self.scheduler.cleanup()

# 使用示例
async def main():
    publisher = MultiPlatformPublisher()
    
    try:
        # 创建营销活动
        campaign_data = {
            "id": "campaign_001",
            "name": "夏日护肤新品推广",
            "topic": "夏日护肤心得",
            "brand_info": {
                "name": "美丽日记",
                "category": "护肤",
                "target_audience": "18-35岁女性"
            },
            "content_type": "product_promotion",
            "key_messages": ["天然成分", "温和无刺激", "夏日专用"],
            "hashtag_strategy": ["#护肤", "#夏日", "#美丽日记"],
            "priority": "high",
            "budget": 10000
        }
        
        # 创建多平台活动
        result = await publisher.create_multi_platform_campaign(campaign_data)
        print(f"活动创建结果: {result['status']}")
        
        # 等待一段时间后同步表现数据
        print("⏳ 等待24小时以收集表现数据...")
        await asyncio.sleep(2)  # 实际应用中等待24小时
        
        # 同步表现数据
        performance_report = await publisher.sync_content_performance(campaign_data["id"])
        print(f"表现报告: {performance_report['summary']}")
        
    finally:
        await publisher.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 知识图谱构建

展示如何构建和分析知识图谱。

```python
# examples/integrations/knowledge_graph_builder.py
import asyncio
from typing import List, Dict, Any, Set
from packages.knowledge_emergence import KnowledgeEmergenceAnalyzer
from packages.knowledge_management import KnowledgeManager

class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.knowledge_analyzer = KnowledgeEmergenceAnalyzer()
        self.knowledge_manager = KnowledgeManager()
        self.graph_data = {
            "nodes": [],
            "edges": [],
            "metadata": {}
        }
    
    async def build_knowledge_graph(self, source_documents: List[Dict[str, Any]]):
        """从文档构建知识图谱"""
        print(f"🔍 开始构建知识图谱，处理 {len(source_documents)} 个文档...")
        
        # 第一步：提取实体
        entities = await self._extract_entities(source_documents)
        print(f"📝 提取到 {len(entities)} 个实体")
        
        # 第二步：识别关系
        relationships = await self._extract_relationships(source_documents, entities)
        print(f"🔗 识别到 {len(relationships)} 个关系")
        
        # 第三步：构建图谱
        await self._construct_graph(entities, relationships)
        
        # 第四步：计算图谱指标
        metrics = await self._calculate_graph_metrics()
        
        # 第五步：生成可视化
        visualization = await self._generate_visualization()
        
        return {
            "graph_data": self.graph_data,
            "metrics": metrics,
            "visualization": visualization,
            "statistics": {
                "total_nodes": len(self.graph_data["nodes"]),
                "total_edges": len(self.graph_data["edges"]),
                "density": self._calculate_density(),
                "connected_components": self._find_connected_components()
            }
        }
    
    async def _extract_entities(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []
        
        for doc in documents:
            # 使用知识分析器提取实体
            doc_entities = await self.knowledge_analyzer.extract_entities(doc["content"])
            
            for entity in doc_entities:
                entity_data = {
                    "id": f"entity_{len(entities)}",
                    "name": entity["text"],
                    "type": entity["type"],
                    "confidence": entity["confidence"],
                    "source_document": doc.get("id", "unknown"),
                    "context": entity.get("context", ""),
                    "properties": entity.get("properties", {})
                }
                entities.append(entity_data)
        
        # 去重和合并相似实体
        merged_entities = await self._merge_similar_entities(entities)
        return merged_entities
    
    async def _extract_relationships(self, documents: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取关系"""
        relationships = []
        
        for doc in documents:
            # 使用知识分析器提取关系
            doc_relationships = await self.knowledge_analyzer.extract_relationships(
                doc["content"], entities
            )
            
            for rel in doc_relationships:
                relationship_data = {
                    "id": f"rel_{len(relationships)}",
                    "source": rel["source_entity"],
                    "target": rel["target_entity"],
                    "relation_type": rel["type"],
                    "confidence": rel["confidence"],
                    "source_document": doc.get("id", "unknown"),
                    "context": rel.get("context", ""),
                    "properties": rel.get("properties", {})
                }
                relationships.append(relationship_data)
        
        return relationships
    
    async def _merge_similar_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并相似实体"""
        merged = []
        processed = set()
        
        for i, entity in enumerate(entities):
            if i in processed:
                continue
            
            # 查找相似实体
            similar_entities = [entity]
            for j, other_entity in enumerate(entities[i+1:], i+1):
                if j in processed:
                    continue
                
                if self._are_entities_similar(entity, other_entity):
                    similar_entities.append(other_entity)
                    processed.add(j)
            
            # 合并相似实体
            merged_entity = self._merge_entity_group(similar_entities)
            merged.append(merged_entity)
            processed.add(i)
        
        return merged
    
    def _are_entities_similar(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> bool:
        """判断实体是否相似"""
        # 简单的相似性判断逻辑
        # 实际应用中可以使用更复杂的算法
        
        if entity1["type"] != entity2["type"]:
            return False
        
        # 检查名称相似性
        name1 = entity1["name"].lower()
        name2 = entity2["name"].lower()
        
        # 完全匹配
        if name1 == name2:
            return True
        
        # 部分匹配
        if name1 in name2 or name2 in name1:
            return True
        
        # 包含共同关键词
        words1 = set(name1.split())
        words2 = set(name2.split())
        if len(words1 & words2) / len(words1 | words2) > 0.7:
            return True
        
        return False
    
    def _merge_entity_group(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并实体组"""
        # 选择置信度最高的作为主实体
        main_entity = max(entities, key=lambda x: x["confidence"])
        
        # 合并属性
        merged_properties = {}
        all_sources = []
        
        for entity in entities:
            merged_properties.update(entity["properties"])
            all_sources.append(entity["source_document"])
        
        return {
            "id": main_entity["id"],
            "name": main_entity["name"],
            "type": main_entity["type"],
            "confidence": main_entity["confidence"],
            "source_documents": list(set(all_sources)),
            "context": main_entity["context"],
            "properties": merged_properties,
            "merged_from": [e["id"] for e in entities]
        }
    
    async def _construct_graph(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        """构建图谱"""
        # 添加节点
        self.graph_data["nodes"] = entities
        
        # 添加边
        self.graph_data["edges"] = relationships
        
        # 设置元数据
        self.graph_data["metadata"] = {
            "created_at": asyncio.get_event_loop().time(),
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "source_documents": list(set(
                entity["source_document"] for entity in entities
            ))
        }
    
    async def _calculate_graph_metrics(self) -> Dict[str, Any]:
        """计算图谱指标"""
        metrics = {
            "node_metrics": await self._calculate_node_metrics(),
            "edge_metrics": await self._calculate_edge_metrics(),
            "graph_metrics": await self._calculate_global_metrics()
        }
        
        return metrics
    
    async def _calculate_node_metrics(self) -> Dict[str, Any]:
        """计算节点指标"""
        node_types = {}
        centrality_scores = {}
        
        for node in self.graph_data["nodes"]:
            # 统计节点类型
            node_type = node["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
            # 计算度中心性
            degree = self._calculate_node_degree(node["id"])
            centrality_scores[node["id"]] = degree
        
        return {
            "type_distribution": node_types,
            "centrality_scores": centrality_scores,
            "top_central_nodes": sorted(
                centrality_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    async def _calculate_edge_metrics(self) -> Dict[str, Any]:
        """计算边指标"""
        edge_types = {}
        
        for edge in self.graph_data["edges"]:
            edge_type = edge["relation_type"]
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            "type_distribution": edge_types,
            "average_confidence": sum(edge["confidence"] for edge in self.graph_data["edges"]) / len(self.graph_data["edges"])
        }
    
    async def _calculate_global_metrics(self) -> Dict[str, Any]:
        """计算全局指标"""
        return {
            "density": self._calculate_density(),
            "connected_components": self._find_connected_components(),
            "average_clustering": self._calculate_clustering_coefficient()
        }
    
    def _calculate_node_degree(self, node_id: str) -> int:
        """计算节点度"""
        degree = 0
        for edge in self.graph_data["edges"]:
            if edge["source"] == node_id or edge["target"] == node_id:
                degree += 1
        return degree
    
    def _calculate_density(self) -> float:
        """计算图密度"""
        n = len(self.graph_data["nodes"])
        if n <= 1:
            return 0.0
        
        max_edges = n * (n - 1)  # 有向图
        actual_edges = len(self.graph_data["edges"])
        
        return actual_edges / max_edges if max_edges > 0 else 0.0
    
    def _find_connected_components(self) -> int:
        """查找连通分量"""
        # 简单的连通分量计算
        visited = set()
        components = 0
        
        for node in self.graph_data["nodes"]:
            if node["id"] not in visited:
                components += 1
                self._dfs(node["id"], visited)
        
        return components
    
    def _dfs(self, node_id: str, visited: Set[str]):
        """深度优先搜索"""
        visited.add(node_id)
        
        for edge in self.graph_data["edges"]:
            if edge["source"] == node_id:
                neighbor = edge["target"]
                if neighbor not in visited:
                    self._dfs(neighbor, visited)
            elif edge["target"] == node_id:
                neighbor = edge["source"]
                if neighbor not in visited:
                    self._dfs(neighbor, visited)
    
    def _calculate_clustering_coefficient(self) -> float:
        """计算聚类系数"""
        # 简化的聚类系数计算
        total_coefficient = 0.0
        node_count = 0
        
        for node in self.graph_data["nodes"]:
            neighbors = self._get_node_neighbors(node["id"])
            if len(neighbors) < 2:
                continue
            
            # 计算邻居之间的连接数
            possible_edges = len(neighbors) * (len(neighbors) - 1)
            actual_edges = 0
            
            for i, neighbor1 in enumerate(neighbors):
                for neighbor2 in neighbors[i+1:]:
                    if self._are_connected(neighbor1, neighbor2):
                        actual_edges += 1
            
            if possible_edges > 0:
                coefficient = actual_edges / possible_edges
                total_coefficient += coefficient
                node_count += 1
        
        return total_coefficient / node_count if node_count > 0 else 0.0
    
    def _get_node_neighbors(self, node_id: str) -> List[str]:
        """获取节点邻居"""
        neighbors = []
        for edge in self.graph_data["edges"]:
            if edge["source"] == node_id:
                neighbors.append(edge["target"])
            elif edge["target"] == node_id:
                neighbors.append(edge["source"])
        return neighbors
    
    def _are_connected(self, node1: str, node2: str) -> bool:
        """判断两个节点是否直接连接"""
        for edge in self.graph_data["edges"]:
            if ((edge["source"] == node1 and edge["target"] == node2) or
                (edge["source"] == node2 and edge["target"] == node1)):
                return True
        return False
    
    async def _generate_visualization(self) -> Dict[str, Any]:
        """生成可视化数据"""
        # 生成用于可视化的数据格式
        visualization_data = {
            "nodes": [
                {
                    "id": node["id"],
                    "label": node["name"],
                    "type": node["type"],
                    "size": self._calculate_node_degree(node["id"]) * 10 + 10,
                    "color": self._get_node_color(node["type"])
                }
                for node in self.graph_data["nodes"]
            ],
            "edges": [
                {
                    "from": edge["source"],
                    "to": edge["target"],
                    "label": edge["relation_type"],
                    "width": edge["confidence"] * 5,
                    "color": self._get_edge_color(edge["relation_type"])
                }
                for edge in self.graph_data["edges"]
            ]
        }
        
        return visualization_data
    
    def _get_node_color(self, node_type: str) -> str:
        """获取节点颜色"""
        color_map = {
            "person": "#FF6B6B",
            "organization": "#4ECDC4", 
            "location": "#45B7D1",
            "concept": "#96CEB4",
            "event": "#FFEAA7",
            "product": "#DDA0DD"
        }
        return color_map.get(node_type, "#95A5A6")
    
    def _get_edge_color(self, relation_type: str) -> str:
        """获取边颜色"""
        color_map = {
            "related_to": "#BDC3C7",
            "part_of": "#3498DB",
            "located_in": "#E74C3C",
            "works_for": "#2ECC71",
            "influences": "#F39C12"
        }
        return color_map.get(relation_type, "#95A5A6")

# 使用示例
async def main():
    builder = KnowledgeGraphBuilder()
    
    # 示例文档
    documents = [
        {
            "id": "doc_1",
            "title": "人工智能发展史",
            "content": "人工智能是计算机科学的重要分支，机器学习是AI的核心技术之一。深度学习在近年来取得了重大突破。"
        },
        {
            "id": "doc_2", 
            "title": "机器学习应用",
            "content": "机器学习在自然语言处理、计算机视觉等领域有广泛应用。神经网络是机器学习的重要模型。"
        },
        {
            "id": "doc_3",
            "title": "深度学习进展",
            "content": "深度学习基于神经网络，通过多层结构学习数据的复杂模式。卷积神经网络在图像识别中表现出色。"
        }
    ]
    
    try:
        # 构建知识图谱
        result = await builder.build_knowledge_graph(documents)
        
        print("✅ 知识图谱构建完成!")
        print(f"📊 统计信息:")
        print(f"  节点数: {result['statistics']['total_nodes']}")
        print(f"  边数: {result['statistics']['total_edges']}")
        print(f"  图密度: {result['statistics']['density']:.3f}")
        print(f"  连通分量: {result['statistics']['connected_components']}")
        
        print(f"\n🎯 核心节点:")
        for node_id, score in result['metrics']['node_metrics']['top_central_nodes'][:5]:
            print(f"  {node_id}: {score}")
        
        print(f"\n🔗 关系类型分布:")
        for rel_type, count in result['metrics']['edge_metrics']['type_distribution'].items():
            print(f"  {rel_type}: {count}")
        
    finally:
        await builder.knowledge_analyzer.cleanup()
        await builder.knowledge_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

这些集成示例展示了如何在实际应用中将多个组件组合使用，实现复杂的业务场景。每个示例都提供了完整的实现代码，可以直接运行和扩展。
