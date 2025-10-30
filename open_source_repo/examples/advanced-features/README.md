# 高级功能示例

这些示例展示了 AI Tech Innovation Suite 的高级功能和复杂用例。

## 目录

- [完整咖啡沙龙流程](#完整咖啡沙龙流程)
- [企业级部署](#企业级部署)
- [自定义扩展](#自定义扩展)
- [性能优化](#性能优化)
- [安全配置](#安全配置)

## 完整咖啡沙龙流程

这个示例展示了如何构建一个完整的AI咖啡沙龙系统，包含多智能体协作、实时交互和知识沉淀。

```python
# examples/advanced-features/coffee_salon_workflow.py
import asyncio
from datetime import datetime, timedelta
from packages.multi_agent_framework import AgentRegistry, HostAgent, ExpertAgent
from packages.knowledge_emergence import KnowledgeEmergenceAnalyzer
from packages.xiaohongshu_agent import XiaohongshuAgent

class CoffeeSalonWorkflow:
    """咖啡沙龙工作流管理器"""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.knowledge_analyzer = KnowledgeEmergenceAnalyzer()
        self.content_agent = XiaohongshuAgent()
        self.salon_session = None
    
    async def setup_salon(self, topic: str, duration: int = 60):
        """设置沙龙"""
        # 创建主持人
        host = HostAgent(
            name="咖啡沙龙主持人",
            role="协调讨论",
            system_prompt="你是一个专业的咖啡沙龙主持人，善于引导话题和协调讨论"
        )
        
        # 创建专家
        experts = [
            ExpertAgent(
                name="咖啡专家",
                specialty="咖啡制作",
                system_prompt="你是一位咖啡制作专家，分享专业的咖啡知识和经验"
            ),
            ExpertAgent(
                name="咖啡文化专家", 
                specialty="咖啡文化",
                system_prompt="你是一位咖啡文化专家，了解咖啡的历史和文化内涵"
            )
        ]
        
        # 注册智能体
        await self.registry.register_agent("host", host)
        for i, expert in enumerate(experts):
            await self.registry.register_agent(f"expert_{i}", expert)
        
        # 创建沙龙会话
        self.salon_session = {
            "topic": topic,
            "start_time": datetime.now(),
            "duration": duration,
            "participants": ["host"] + [f"expert_{i}" for i in range(len(experts))],
            "knowledge_items": [],
            "dialogue_log": []
        }
        
        print(f"✅ 咖啡沙龙已设置完成")
        print(f"📝 主题: {topic}")
        print(f"⏰ 时长: {duration}分钟")
        print(f"👥 参与者: {', '.join(self.salon_session['participants'])}")
    
    async def run_salon_session(self):
        """运行沙龙会话"""
        if not self.salon_session:
            raise ValueError("沙龙未设置，请先调用setup_salon")
        
        topic = self.salon_session["topic"]
        
        # 欢迎环节
        welcome_msg = await self.registry.send_message(
            agent_name="host",
            message=f"欢迎大家参加今天的咖啡沙龙！今天我们要讨论的主题是：{topic}"
        )
        self.salon_session["dialogue_log"].append({
            "agent": "host",
            "message": welcome_msg,
            "timestamp": datetime.now()
        })
        
        # 专家讨论
        discussion_topics = [
            f"请{expert_name}分享关于{topic}的专业见解"
            for expert_name in self.salon_session["participants"][1:]
        ]
        
        for topic_msg in discussion_topics:
            response = await self.registry.send_message(
                agent_name="host",
                message=topic_msg
            )
            self.salon_session["dialogue_log"].append({
                "agent": "host",
                "message": response,
                "timestamp": datetime.now()
            })
            
            # 提取知识项
            knowledge_item = {
                "id": f"knowledge_{len(self.salon_session['knowledge_items']) + 1}",
                "content": response,
                "source": "咖啡沙龙讨论",
                "timestamp": datetime.now(),
                "topic": topic
            }
            self.salon_session["knowledge_items"].append(knowledge_item)
        
        # 总结环节
        summary_msg = await self.registry.send_message(
            agent_name="host",
            message="请对今天的讨论进行总结，并提取关键知识点"
        )
        self.salon_session["dialogue_log"].append({
            "agent": "host", 
            "message": summary_msg,
            "timestamp": datetime.now()
        })
        
        return self.salon_session
    
    async def analyze_knowledge(self):
        """分析沙龙产生的知识"""
        if not self.salon_session["knowledge_items"]:
            return None
        
        print("🔍 开始知识分析...")
        
        # 质量评估
        quality_result = await self.knowledge_analyzer.assess_quality(
            self.salon_session["knowledge_items"]
        )
        
        # 价值分析
        value_result = await self.knowledge_analyzer.assess_value(
            self.salon_session["knowledge_items"]
        )
        
        # 模式识别
        pattern_result = await self.knowledge_analyzer.recognize_patterns(
            self.salon_session["knowledge_items"]
        )
        
        analysis_result = {
            "quality": quality_result,
            "value": value_result,
            "patterns": pattern_result,
            "summary": self._generate_summary()
        }
        
        print("✅ 知识分析完成")
        return analysis_result
    
    def _generate_summary(self):
        """生成沙龙总结"""
        return {
            "total_knowledge_items": len(self.salon_session["knowledge_items"]),
            "main_topics": list(set(item["topic"] for item in self.salon_session["knowledge_items"])),
            "duration_minutes": (datetime.now() - self.salon_session["start_time"]).total_seconds() / 60,
            "participant_count": len(self.salon_session["participants"])
        }
    
    async def generate_content(self, analysis_result):
        """生成内容"""
        if not analysis_result:
            return None
        
        # 基于分析结果生成内容
        content = await self.content_agent.generate_content(
            topic=self.salon_session["topic"],
            brand_info={
                "name": "AI咖啡沙龙",
                "category": "知识分享"
            },
            content_type="knowledge_sharing",
            additional_context={
                "quality_score": analysis_result["quality"]["overall_score"],
                "key_insights": analysis_result["patterns"]["key_insights"]
            }
        )
        
        return content
    
    async def cleanup(self):
        """清理资源"""
        await self.registry.cleanup()
        self.knowledge_analyzer.cleanup()
        await self.content_agent.cleanup()

async def main():
    """主函数"""
    salon = CoffeeSalonWorkflow()
    
    try:
        # 设置沙龙
        await salon.setup_salon("精品咖啡的烘焙工艺", duration=45)
        
        # 运行沙龙
        session_result = await salon.run_salon_session()
        
        # 分析知识
        analysis_result = await salon.analyze_knowledge()
        
        # 生成内容
        content = await salon.generate_content(analysis_result)
        
        # 输出结果
        print("\n" + "="*50)
        print("🎉 咖啡沙龙完成！")
        print("="*50)
        
        print(f"\n📊 知识分析结果:")
        if analysis_result:
            print(f"  质量评分: {analysis_result['quality']['overall_score']:.2f}")
            print(f"  价值评估: {analysis_result['value']['overall_value']}")
            print(f"  识别模式: {len(analysis_result['patterns']['patterns'])}个")
        
        print(f"\n📝 生成的内容:")
        if content:
            print(f"  标题: {content['title']}")
            print(f"  标签: {', '.join(content['hashtags'])}")
        
        print(f"\n💾 沙龙总结:")
        summary = session_result.get("summary", {})
        print(f"  知识项数量: {summary.get('total_knowledge_items', 0)}")
        print(f"  主要话题: {', '.join(summary.get('main_topics', []))}")
        print(f"  参与人数: {summary.get('participant_count', 0)}")
        
    finally:
        await salon.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 企业级部署

展示如何在企业环境中部署和配置系统。

```yaml
# examples/advanced-features/enterprise-deployment/docker-compose.prod.yml
version: '3.8'

services:
  # 应用负载均衡器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

  # 主应用 (多实例)
  app:
    image: ai-tech-suite:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    environment:
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres-cluster:5432/ai_suite
      - REDIS_URL=redis://redis-cluster:6379/0
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - postgres-cluster
      - redis-cluster
      - elasticsearch
      - kafka
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL集群
  postgres-cluster:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_suite
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db-prod.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      postgres 
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
    restart: unless-stopped

  # Redis集群
  redis-cluster:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped

  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper_data:/var/lib/zookeeper/data

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka_data:/var/lib/kafka/data

  # 监控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.prod.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  kafka_data:
  zookeeper_data:
  prometheus_data:
  grafana_data:
```

## 自定义扩展

展示如何创建自定义智能体和功能模块。

```python
# examples/advanced-features/custom_agent.py
from packages.multi_agent_framework.core.agent import BaseAgent
from packages.multi_agent_framework.core.message import Message
from typing import Dict, Any, List

class CustomExpertAgent(BaseAgent):
    """自定义专家智能体"""
    
    def __init__(self, name: str, specialty: str, expertise_areas: List[str]):
        super().__init__(name, "expert")
        self.specialty = specialty
        self.expertise_areas = expertise_areas
        self.knowledge_base = {}
        self.conversation_history = []
    
    async def process_message(self, message: Message) -> Message:
        """处理接收到的消息"""
        # 记录对话历史
        self.conversation_history.append({
            "timestamp": message.timestamp,
            "sender": message.sender,
            "content": message.content,
            "type": "received"
        })
        
        # 分析消息内容
        analysis = await self._analyze_message(message.content)
        
        # 生成回复
        response_content = await self._generate_response(message.content, analysis)
        
        # 记录回复历史
        self.conversation_history.append({
            "timestamp": message.timestamp,
            "sender": self.name,
            "content": response_content,
            "type": "sent"
        })
        
        return Message(
            sender=self.name,
            receiver=message.sender,
            content=response_content,
            message_type="response",
            metadata={
                "specialty": self.specialty,
                "confidence": analysis.get("confidence", 0.8),
                "expertise_areas": self.expertise_areas
            }
        )
    
    async def _analyze_message(self, content: str) -> Dict[str, Any]:
        """分析消息内容"""
        # 简单的关键词分析
        keywords = content.lower().split()
        matched_areas = [area for area in self.expertise_areas 
                        if any(keyword in area.lower() for keyword in keywords)]
        
        return {
            "matched_expertise": matched_areas,
            "confidence": min(len(matched_areas) / len(self.expertise_areas), 1.0),
            "complexity": "high" if len(content) > 200 else "medium"
        }
    
    async def _generate_response(self, content: str, analysis: Dict[str, Any]) -> str:
        """生成回复"""
        if not analysis["matched_expertise"]:
            return f"抱歉，我在{self.specialty}领域有专长，但您的问题似乎不在我的专业范围内。我可以为您推荐相关的专家。"
        
        # 基于专业领域生成回复
        response_parts = []
        response_parts.append(f"作为{self.specialty}专家，我的观点是：")
        
        for area in analysis["matched_expertise"]:
            response_parts.append(f"\n关于{area}：")
            response_parts.append(f"基于我的专业知识，我建议...")
        
        return "\n".join(response_parts)
    
    def add_knowledge(self, topic: str, knowledge: str):
        """添加知识到知识库"""
        if topic not in self.knowledge_base:
            self.knowledge_base[topic] = []
        self.knowledge_base[topic].append(knowledge)
    
    def get_expertise_summary(self) -> Dict[str, Any]:
        """获取专业能力摘要"""
        return {
            "name": self.name,
            "specialty": self.specialty,
            "expertise_areas": self.expertise_areas,
            "knowledge_topics": list(self.knowledge_base.keys()),
            "conversation_count": len(self.conversation_history),
            "expertise_level": "expert"  # 可以根据经验动态调整
        }

# 使用示例
async def main():
    # 创建自定义专家
    coffee_expert = CustomExpertAgent(
        name="咖啡工艺专家",
        specialty="咖啡烘焙与制作",
        expertise_areas=["咖啡烘焙", "咖啡研磨", "萃取技巧", "咖啡品鉴"]
    )
    
    # 添加专业知识
    coffee_expert.add_knowledge("烘焙程度", "浅烘焙保留酸质，深烘焙增加苦味")
    coffee_expert.add_knowledge("研磨粗细", "意式咖啡需要细研磨，手冲需要中等粗细")
    
    # 模拟对话
    from packages.multi_agent_framework.core.message import Message
    
    question = Message(
        sender="user",
        receiver="coffee_expert", 
        content="我想了解手冲咖啡的研磨粗细应该如何选择？",
        message_type="question"
    )
    
    response = await coffee_expert.process_message(question)
    print(f"专家回复: {response.content}")
    
    # 获取专家能力摘要
    summary = coffee_expert.get_expertise_summary()
    print(f"专家摘要: {summary}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 性能优化

展示系统性能优化的配置和最佳实践。

```python
# examples/advanced-features/performance_optimization.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import aioredis
from packages.multi_agent_framework.core.registry import AgentRegistry

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.redis_pool = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.cache = {}
        self.metrics = {
            "requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0
        }
    
    async def setup_optimizations(self):
        """设置性能优化"""
        # 连接池配置
        self.redis_pool = aioredis.ConnectionPool.from_url(
            "redis://localhost:6379/0",
            max_connections=20,
            retry_on_timeout=True
        )
        
        print("✅ 性能优化配置完成")
    
    async def optimize_agent_responses(self, agents: List[str], queries: List[str]):
        """优化智能体响应性能"""
        start_time = time.time()
        
        # 并发处理查询
        tasks = []
        for query in queries:
            for agent in agents:
                task = self._cached_agent_call(agent, query)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"⚡ 性能统计:")
        print(f"  总查询数: {len(queries) * len(agents)}")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  平均响应时间: {total_time / len(tasks):.3f}秒")
        print(f"  吞吐量: {len(tasks) / total_time:.1f} 请求/秒")
        print(f"  缓存命中率: {self.metrics['cache_hits'] / self.metrics['requests'] * 100:.1f}%")
        
        return results
    
    async def _cached_agent_call(self, agent_name: str, query: str):
        """带缓存的智能体调用"""
        self.metrics["requests"] += 1
        
        # 生成缓存键
        cache_key = f"{agent_name}:{hash(query)}"
        
        # 检查缓存
        if cache_key in self.cache:
            self.metrics["cache_hits"] += 1
            return self.cache[cache_key]
        
        self.metrics["cache_misses"] += 1
        
        # 模拟智能体调用
        start_time = time.time()
        result = await self._simulate_agent_call(agent_name, query)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 更新平均响应时间
        self.metrics["avg_response_time"] = (
            (self.metrics["avg_response_time"] * (self.metrics["requests"] - 1) + response_time) 
            / self.metrics["requests"]
        )
        
        # 缓存结果
        self.cache[cache_key] = result
        
        return result
    
    async def _simulate_agent_call(self, agent_name: str, query: str):
        """模拟智能体调用（实际应用中替换为真实调用）"""
        # 模拟处理时间
        await asyncio.sleep(0.1)
        
        return {
            "agent": agent_name,
            "query": query,
            "response": f"来自{agent_name}的回复: {query[:50]}...",
            "timestamp": time.time()
        }
    
    async def batch_process_knowledge(self, knowledge_items: List[Dict[str, Any]]):
        """批量处理知识项"""
        print(f"🔄 开始批量处理{len(knowledge_items)}个知识项...")
        
        start_time = time.time()
        
        # 分批处理
        batch_size = 10
        batches = [knowledge_items[i:i + batch_size] 
                  for i in range(0, len(knowledge_items), batch_size)]
        
        results = []
        for i, batch in enumerate(batches):
            print(f"  处理批次 {i+1}/{len(batches)}")
            
            # 并发处理批次
            batch_tasks = [self._process_knowledge_item(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ 批量处理完成:")
        print(f"  处理时间: {total_time:.2f}秒")
        print(f"  平均每项: {total_time / len(knowledge_items):.3f}秒")
        print(f"  吞吐量: {len(knowledge_items) / total_time:.1f} 项/秒")
        
        return results
    
    async def _process_knowledge_item(self, item: Dict[str, Any]):
        """处理单个知识项"""
        # 模拟处理逻辑
        await asyncio.sleep(0.05)  # 模拟处理时间
        
        return {
            "id": item.get("id"),
            "processed": True,
            "quality_score": 0.85,  # 模拟评分
            "processing_time": 0.05
        }
    
    async def cleanup(self):
        """清理资源"""
        if self.redis_pool:
            await self.redis_pool.disconnect()
        self.executor.shutdown(wait=True)

# 性能测试示例
async def main():
    optimizer = PerformanceOptimizer()
    await optimizer.setup_optimizations()
    
    try:
        # 测试智能体响应性能
        agents = ["agent1", "agent2", "agent3", "agent4", "agent5"]
        queries = [f"问题{i}" for i in range(100)]
        
        await optimizer.optimize_agent_responses(agents, queries)
        
        # 测试知识处理性能
        knowledge_items = [{"id": f"item_{i}", "content": f"知识内容{i}"}
                          for i in range(50)]
        
        await optimizer.batch_process_knowledge(knowledge_items)
        
    finally:
        await optimizer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 安全配置

展示企业级安全配置和最佳实践。

```python
# examples/advanced-features/security_config.py
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from packages.multi_agent_framework.core.auth import AuthenticationManager

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.session_tokens = {}
        self.failed_attempts = {}
        self.rate_limits = {}
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = ".encryption_key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # 限制文件权限
            return key
    
    def create_secure_config(self, config: Dict[str, Any]) -> str:
        """创建安全配置"""
        # 加密敏感信息
        sensitive_fields = ["api_key", "password", "secret", "token"]
        encrypted_config = {}
        
        for key, value in config.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                encrypted_config[key] = self.cipher.encrypt(
                    str(value).encode()
                ).decode()
            else:
                encrypted_config[key] = value
        
        return self.cipher.encrypt(
            str(encrypted_config).encode()
        ).decode()
    
    def decrypt_config(self, encrypted_config: str) -> Dict[str, Any]:
        """解密配置"""
        decrypted_data = self.cipher.decrypt(encrypted_config.encode()).decode()
        config = eval(decrypted_data)  # 注意：实际使用中应使用json.loads
        
        # 解密敏感字段
        sensitive_fields = ["api_key", "password", "secret", "token"]
        for key, value in config.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                try:
                    config[key] = self.cipher.decrypt(value.encode()).decode()
                except:
                    pass  # 如果解密失败，保持原值
        
        return config
    
    def create_session_token(self, user_id: str, permissions: list) -> str:
        """创建会话令牌"""
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16)  # 唯一标识符
        }
        
        token = jwt.encode(payload, self.encryption_key, algorithm="HS256")
        self.session_tokens[token] = payload
        
        return token
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证会话令牌"""
        try:
            payload = jwt.decode(token, self.encryption_key, algorithms=["HS256"])
            
            # 检查令牌是否在会话列表中
            if token not in self.session_tokens:
                return None
            
            # 检查令牌是否过期
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                del self.session_tokens[token]
                return None
            
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 3600):
        """检查速率限制"""
        now = datetime.utcnow()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # 清理过期记录
        self.rate_limits[identifier] = [
            timestamp for timestamp in self.rate_limits[identifier]
            if now - timestamp < timedelta(seconds=window)
        ]
        
        # 检查是否超过限制
        if len(self.rate_limits[identifier]) >= limit:
            return False
        
        # 记录当前请求
        self.rate_limits[identifier].append(now)
        return True
    
    def check_brute_force(self, identifier: str, max_attempts: int = 5, lockout_time: int = 900):
        """检查暴力破解"""
        now = datetime.utcnow()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # 清理过期记录
        self.failed_attempts[identifier] = [
            timestamp for timestamp in self.failed_attempts[identifier]
            if now - timestamp < timedelta(seconds=lockout_time)
        ]
        
        # 检查是否被锁定
        if len(self.failed_attempts[identifier]) >= max_attempts:
            return False
        
        return True
    
    def record_failed_attempt(self, identifier: str):
        """记录失败尝试"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(datetime.utcnow())
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """安全密码哈希"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000  # 迭代次数
        )
        
        return salt, password_hash.hex()
    
    def verify_password(self, password: str, salt: str, password_hash: str) -> bool:
        """验证密码"""
        _, computed_hash = self.hash_password(password, salt)
        return computed_hash == password_hash

# 安全配置示例
async def main():
    security = SecurityManager()
    
    # 创建安全配置
    config = {
        "database_url": "postgresql://user:pass@localhost/db",
        "api_key": "secret_api_key_123",
        "redis_url": "redis://localhost:6379",
        "debug": False
    }
    
    encrypted_config = security.create_secure_config(config)
    print(f"加密配置: {encrypted_config[:50]}...")
    
    decrypted_config = security.decrypt_config(encrypted_config)
    print(f"解密配置: {decrypted_config}")
    
    # 创建会话令牌
    token = security.create_session_token("user123", ["read", "write"])
    print(f"会话令牌: {token}")
    
    # 验证令牌
    payload = security.validate_session_token(token)
    print(f"令牌载荷: {payload}")
    
    # 速率限制测试
    for i in range(105):
        if not security.check_rate_limit("user123", limit=100):
            print(f"速率限制触发在第{i+1}次请求")
            break
    
    print("✅ 安全配置测试完成")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

这些高级示例展示了如何在实际项目中应用 AI Tech Innovation Suite 的高级功能。每个示例都可以独立运行，并提供了完整的代码实现和详细注释。
