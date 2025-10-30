# Coze集成接口

基于集成架构设计文档开发的Coze平台与AI咖啡知识沙龙系统的集成接口代码。

## 项目概述

本项目实现了Coze平台与AI咖啡知识沙龙系统的完整集成，包括：

- **Coze API客户端** - 与Coze平台进行API交互
- **Kai智能体管理器** - 管理多智能体编排和协作
- **集成网关服务** - 提供统一的API接口
- **消息路由器** - 实现事件驱动架构
- **认证和权限控制** - JWT认证和RBAC权限模型
- **配置管理器** - 统一的系统配置管理

## 架构特性

### 分层设计
```
数据摄取层 → 向量存储层 → 知识图谱层 → 检索与重排层 → 生成与Agent层 → 治理与更新层 → 前端/移动端/打印层 → Coze Loop(Platform/SDK/LLM) → API网关 → 事件总线 → 观测与审计
```

### 核心组件
- **API网关** - 统一入口、路由、限流、鉴权
- **Kai-Agent(CrewAI)** - 多智能体编排与协作
- **RAG平台** - 检索、重排、引用
- **向量DB** - 语义检索与召回
- **知识图谱(KG)** - 结构化约束与解释
- **消息队列(RocketMQ)** - 事件驱动与解耦
- **Coze Loop(Platform/SDK/LLM)** - 数据/评估/观察/提示/LLM/基础

### 安全特性
- OAuth JWT认证（RS256算法）
- RBAC权限模型
- 多租户隔离
- 审计日志
- 数据加密

## 快速开始

### 1. 安装依赖

```bash
pip install requests aiohttp pyjwt cryptography pyyaml
```

### 2. 配置系统

复制配置文件模板：
```bash
cp src/coze_integration/examples/config.yaml ./config.yaml
```

编辑配置文件，设置必要的参数：
```yaml
coze:
  base_url: "https://api.coze.cn"
  jwt_secret_key: "your-jwt-secret-key"

database:
  mysql_host: "localhost"
  mysql_user: "root"
  mysql_password: "your-password"

security:
  jwt_secret_key: "your-jwt-secret-key"
  encryption_key: "your-encryption-key"
```

### 3. 启动系统

```bash
# 方式1: 直接运行主程序
python -m coze_integration.main

# 方式2: 运行演示模式
python -m coze_integration.main --demo

# 方式3: 使用配置文件
python -m coze_integration.main --config ./config.yaml
```

### 4. 运行示例

```bash
# 运行基础使用示例
python src/coze_integration/examples/basic_usage.py

# 运行测试
python src/coze_integration/tests/test_coze_integration.py
```

## 使用指南

### 基础配置

```python
from coze_integration import get_config_manager, get_auth_manager

# 加载配置
config_manager = get_config_manager()
config = config_manager.get_config()

# 初始化认证
auth_manager = get_auth_manager()
```

### 用户管理

```python
from coze_integration import User, Role, Permission

# 创建用户
user = User(
    user_id="user_001",
    username="咖啡师张三",
    email="zhangsan@coffee.com",
    tenant_id="coffee_shop_001",
    roles={Role.RESEARCHER, Role.PRINT_OPERATOR}
)

# 注册用户
auth_manager.register_user(user)

# 检查权限
has_permission = auth_manager.check_permission(
    user, 
    Permission.SEARCH_READ, 
    tenant_id="coffee_shop_001"
)
```

### Coze API调用

```python
from coze_integration import get_coze_client
from coze_integration.coze_client import ChatRequest

# 获取客户端
coze_client = get_coze_client()

# 健康检查
is_healthy = coze_client.health_check()

# 发送聊天消息
request = ChatRequest(
    bot_id="your_bot_id",
    query="请介绍一下阿拉比卡咖啡的特点",
    stream=False
)

response = coze_client.chat(request)
print(f"回答: {response.content}")
```

### 智能体管理

```python
from coze_integration import get_agent_manager, TaskContext, TaskPriority, AgentType

# 获取智能体管理器
agent_manager = get_agent_manager()

# 启动管理器
await agent_manager.start()

# 创建任务上下文
task_context = TaskContext(
    task_id="task_001",
    tenant_id="coffee_shop_001",
    user_id="user_001"
)

# 创建问答任务
task = agent_manager.create_task(
    task_type="qna",
    agent_type=AgentType.QNA_AGENT,
    input_data={
        "question": "什么是手冲咖啡？",
        "context": {"language": "zh-CN"}
    },
    context=task_context,
    priority=TaskPriority.NORMAL
)

# 提交任务
success = await agent_manager.submit_task(task)

# 查看任务状态
task_status = agent_manager.get_task_status(task.task_id)
print(f"任务状态: {task_status.status.value}")
```

### 消息路由

```python
from coze_integration import get_message_router, Subscription, EventType

# 获取路由器
router = get_message_router()

# 启动路由器
await router.start()

# 定义事件处理器
def knowledge_update_handler(event):
    print(f"知识库更新: {event.payload}")

# 创建订阅
subscription = Subscription(
    subscription_id="kb_sub_001",
    event_types=[EventType.KB_UPDATED],
    callback=knowledge_update_handler
)

# 订阅事件
router.subscribe(subscription)

# 发布事件
await router.publish(
    EventType.KB_UPDATED,
    tenant_id="coffee_shop_001",
    payload={"kb_id": "kb_001", "version": "v1.2"},
    user_id="user_001"
)
```

### API网关使用

```python
from coze_integration import get_gateway, APIRequest, APIEndpoint

# 获取网关
gateway = get_gateway()

# 启动网关
await gateway.start()

# 创建API请求
request = APIRequest(
    request_id="req_001",
    endpoint=APIEndpoint.QUERY,
    method="POST",
    user=user,
    tenant_id="coffee_shop_001",
    data={
        "query": "如何制作拿铁咖啡？",
        "context": {"difficulty": "beginner"}
    },
    headers={"Authorization": "Bearer your-token"}
)

# 处理请求
response = await gateway.handle_request(request)

if response.success:
    print(f"回答: {response.data.get('answer')}")
else:
    print(f"错误: {response.error}")
```

## API端点

### 查询相关
- `POST /v1/query` - 问答查询
- `POST /v1/query/stream` - 流式问答查询

### 智能体相关
- `GET /v1/agents` - 获取智能体列表
- `POST /v1/agents/dispatch` - 调度智能体任务
- `GET /v1/agents/status` - 获取智能体状态

### 检索相关
- `POST /v1/rag/retrieve` - RAG检索
- `POST /v1/rag/search` - 搜索

### 知识库相关
- `POST /v1/kb/create` - 创建知识库
- `POST /v1/kb/update` - 更新知识库
- `POST /v1/kb/query` - 查询知识库

### 打印相关
- `POST /v1/print/ticket` - 打印票据
- `GET /v1/print/status` - 打印状态

### 审稿相关
- `POST /v1/review/submit` - 提交审稿
- `POST /v1/review/approve` - 审稿通过
- `POST /v1/review/query` - 查询审稿

### 系统相关
- `GET /v1/system/health` - 系统健康检查
- `GET /v1/system/metrics` - 系统指标
- `GET /v1/system/audit` - 系统审计

## 智能体类型

### 研究员 (Researcher)
- 专门负责咖啡知识的深入研究和信息收集
- 能力：research, knowledge_collection, fact_checking

### 评估者 (Evaluator)
- 负责评估内容的事实性和逻辑一致性
- 能力：evaluation, quality_check, fact_verification

### 总结者 (Summarizer)
- 负责将研究结果整合为结构化报告
- 能力：summarization, report_generation, content_synthesis

### 问答智能体 (QNA Agent)
- 为用户提供咖啡相关的问答服务
- 能力：question_answering, knowledge_retrieval, chat

### 调度智能体 (Dispatcher)
- 负责智能体任务的智能分配和调度
- 能力：task_routing, agent_coordination, workflow_management

### 打印智能体 (Print Agent)
- 负责处理各种文档和票据的打印任务
- 能力：document_printing, ticket_generation, output_management

## 事件类型

### 知识库事件
- `coffee.salon.knowledge.update` - 知识库更新
- `coffee.salon.knowledge.created` - 知识库创建
- `coffee.salon.knowledge.deleted` - 知识库删除

### 检索事件
- `coffee.salon.rag.completed` - RAG检索完成
- `coffee.salon.rag.failed` - RAG检索失败

### 审稿事件
- `coffee.salon.review.approved` - 审稿通过
- `coffee.salon.review.rejected` - 审稿拒绝
- `coffee.salon.review.submitted` - 审稿提交

### 打印事件
- `coffee.salon.print.completed` - 打印完成
- `coffee.salon.print.failed` - 打印失败
- `coffee.salon.print.started` - 打印开始

### 认证事件
- `coffee.salon.auth.login` - 用户登录
- `coffee.salon.auth.logout` - 用户登出
- `coffee.salon.auth.failed` - 认证失败

### 系统事件
- `coffee.salon.system.error` - 系统错误
- `coffee.salon.system.health` - 系统健康

## 权限模型

### 角色
- `admin` - 管理员
- `researcher` - 研究员
- `evaluator` - 评估者
- `summarizer` - 总结者
- `qna_agent` - 问答智能体
- `print_operator` - 打印操作员
- `auditor` - 审计员

### 权限
- `kb:read` - 知识库读取
- `kb:write` - 知识库写入
- `kb:publish` - 知识库发布
- `search:read` - 检索读取
- `search:write` - 检索写入
- `review:read` - 审稿读取
- `review:write` - 审稿写入
- `review:approve` - 审稿通过
- `print:read` - 打印读取
- `print:write` - 打印写入
- `system:admin` - 系统管理
- `system:audit` - 系统审计

## 配置说明

### Coze配置
```yaml
coze:
  base_url: "https://api.coze.cn"  # Coze API基础URL
  api_version: "v3"                # API版本
  timeout: 30                      # 请求超时时间
  max_retries: 3                   # 最大重试次数
  rate_limit: 1000                 # 速率限制 (QPS/小时)
  jwt_algorithm: "RS256"           # JWT算法
  jwt_expiry: 3600                 # JWT过期时间 (秒)
  access_token_expiry: 86400       # 访问令牌过期时间 (秒)
```

### 数据库配置
```yaml
database:
  mysql_host: "localhost"          # MySQL主机
  mysql_port: 3306                 # MySQL端口
  mysql_user: "root"               # MySQL用户
  mysql_password: "password"       # MySQL密码
  mysql_database: "coffee_salon"   # 数据库名
  redis_host: "localhost"          # Redis主机
  redis_port: 6379                 # Redis端口
  redis_password: ""               # Redis密码
  redis_db: 0                      # Redis数据库编号
```

### 安全配置
```yaml
security:
  jwt_secret_key: "your-secret-key"    # JWT密钥
  jwt_algorithm: "HS256"               # JWT算法
  jwt_expiry: 3600                     # JWT过期时间
  encryption_key: "your-encryption-key" # 加密密钥
  audit_enabled: true                  # 启用审计
  audit_retention_days: 365            # 审计保留天数
```

## 监控和日志

### 日志级别
- `DEBUG` - 调试信息
- `INFO` - 一般信息
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 监控指标
- 请求总数和成功率
- 平均响应时间
- 智能体任务统计
- 消息队列状态
- 系统资源使用情况

### 健康检查
```python
from coze_integration import health_check

is_healthy = await health_check()
print(f"系统健康状态: {'正常' if is_healthy else '异常'}")
```

## 故障排除

### 常见问题

1. **认证失败**
   - 检查JWT密钥配置
   - 验证访问令牌是否过期
   - 确认用户权限设置

2. **API调用失败**
   - 检查Coze API配置
   - 验证网络连接
   - 查看速率限制

3. **智能体任务失败**
   - 检查智能体配置
   - 查看任务日志
   - 验证Coze机器人ID

4. **消息路由问题**
   - 确认消息队列配置
   - 检查订阅设置
   - 查看事件处理器

### 调试模式

启用调试模式：
```yaml
environment: "development"
debug: true
log_level: "DEBUG"
```

### 日志分析

查看详细日志：
```bash
# 实时查看日志
tail -f logs/coze_integration.log

# 搜索错误
grep "ERROR" logs/coze_integration.log

# 分析性能
grep "execution_time" logs/coze_integration.log
```

## 开发指南

### 添加新的智能体

1. 继承 `BaseAgent` 类
2. 实现 `process_task` 方法
3. 在 `KaiAgentManager` 中注册

```python
class CustomAgent(BaseAgent):
    async def process_task(self, task):
        # 实现自定义逻辑
        result = {"custom_result": "success"}
        return result

# 注册智能体
agent_manager.register_agent(CustomAgent(config, coze_client, router))
```

### 添加新的API端点

1. 在 `APIEndpoint` 枚举中添加端点
2. 在 `IntegrationGateway` 中实现处理器
3. 添加权限检查

```python
class APIEndpoint(Enum):
    CUSTOM_ENDPOINT = "/v1/custom"

async def _handle_custom_endpoint(self, request):
    # 实现自定义逻辑
    return {"result": "success"}
```

### 扩展事件类型

1. 在 `EventType` 枚举中添加新类型
2. 在 `EventPublisher` 中添加发布方法
3. 创建相应的订阅者

```python
class EventType(Enum):
    CUSTOM_EVENT = "coffee.salon.custom.event"

# 添加发布方法
async def publish_custom_event(self, tenant_id, data, user_id=None):
    await self.router.publish(
        EventType.CUSTOM_EVENT,
        tenant_id,
        data,
        user_id
    )
```

## 性能优化

### 配置优化
- 调整工作线程数量
- 优化缓存设置
- 配置合适的超时时间

### 监控优化
- 启用结构化日志
- 配置指标收集
- 设置告警阈值

### 扩展性
- 水平扩展智能体实例
- 使用消息队列解耦
- 配置负载均衡

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题，请通过以下方式联系：
- 邮箱: support@coffee-salon.com
- 项目地址: https://github.com/coffee-salon/coze-integration

---

**注意**: 本项目基于 Coze 平台 API 和 AI 咖啡知识沙龙系统的集成架构设计文档开发，请确保遵循相关使用条款和最佳实践。