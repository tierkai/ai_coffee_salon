# Coze平台与KAI智能体集成操作指南

## 🎯 操作目标

将AI咖啡知识沙龙系统与Coze平台的KAI智能体打通，实现无缝的智能对话和工作流自动化。

## 📋 前置准备

### 1. 账号准备
- [ ] 注册Coze平台账号（国际版：coze.com，国内版：coze.cn）
- [ ] 获取开发者权限
- [ ] 准备企业邮箱和手机号

### 2. 技术准备
- [ ] Python 3.8+ 环境
- [ ] 安装依赖包：`pip install cozepy requests PyJWT`
- [ ] 配置HTTPS域名（用于Webhook回调）

## 🔧 第一步：Coze平台配置

### 1.1 创建OAuth应用

1. **登录Coze开发者平台**
   ```
   访问：https://www.coze.com/docs/developer_guides/
   或：https://www.coze.cn/docs/developer_guides/
   ```

2. **创建新应用**
   ```
   路径：开发者控制台 → 我的应用 → 创建应用
   应用类型：OAuth应用
   应用名称：AI咖啡知识沙龙
   ```

3. **配置应用参数**
   ```json
   {
     "app_name": "AI咖啡知识沙龙",
     "app_type": "OAuth",
     "redirect_uri": "https://your-domain.com/auth/callback",
     "scope": ["bot:read", "bot:write", "conversation:read", "conversation:write"]
   }
   ```

4. **生成密钥对**
   ```bash
   # 生成RSA密钥对
   openssl genrsa -out private_key.pem 2048
   openssl rsa -in private_key.pem -pubout -out public_key.pem
   
   # 获取公钥指纹
   openssl rsa -pubin -in public_key.pem -outform DER | openssl dgst -sha256
   ```

### 1.2 获取API凭证

记录以下关键信息：
```python
COZE_CONFIG = {
    "app_id": "coze_app_123456",          # 应用ID
    "kid": "your_public_key_fingerprint", # 公钥指纹
    "private_key": "-----BEGIN PRIVATE KEY-----\n...", # 私钥
    "api_base": "https://api.coze.cn",    # API基础URL
    "webhook_url": "https://your-domain.com/webhook/coze"
}
```

## 🔗 第二步：系统集成开发

### 2.1 部署集成代码

1. **复制集成代码**
   ```bash
   cp -r /workspace/src/coze_integration/ /your/project/
   cd /your/project/coze_integration/
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置参数**
   编辑 `config_manager.py`：
   ```python
   class CozeConfig:
       def __init__(self):
           self.app_id = "your_coze_app_id"
           self.kid = "your_kid"
           self.private_key = "your_private_key"
           self.api_base = "https://api.coze.cn"
           self.webhook_url = "https://your-domain.com/webhook/coze"
   ```

### 2.2 启动集成服务

```bash
# 启动主服务
python main.py

# 验证服务状态
curl http://localhost:8080/health
```

预期输出：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-29T21:00:00Z",
  "services": {
    "auth_manager": "ok",
    "coze_client": "ok",
    "kai_manager": "ok"
  }
}
```

## 🔐 第三步：OAuth JWT认证

### 3.1 生成JWT令牌

```python
from auth_manager import AuthManager

auth = AuthManager()

# 生成JWT
jwt_token = auth.generate_jwt_token(
    app_id="your_app_id",
    kid="your_kid",
    private_key="your_private_key"
)

print(f"JWT Token: {jwt_token}")
```

### 3.2 换取访问令牌

```python
# 使用JWT换取访问令牌
access_token = auth.exchange_jwt_for_token(jwt_token)

print(f"Access Token: {access_token}")
```

### 3.3 验证令牌

```python
# 验证令牌有效性
is_valid = auth.validate_token(access_token)
print(f"Token Valid: {is_valid}")
```

## 💬 第四步：对话测试

### 4.1 创建会话

```python
from coze_client import CozeClient

client = CozeClient(access_token)

# 创建新会话
conversation = client.create_conversation(
    app_key="your_api_key",
    user_id="user_123"
)

print(f"Conversation ID: {conversation['conversation_id']}")
```

### 4.2 发送消息

```python
# 发送测试消息
response = client.send_message(
    conversation_id=conversation['conversation_id'],
    query="你好，我想了解咖啡知识",
    stream=False
)

print(f"Response: {response}")
```

### 4.3 流式响应测试

```python
# 测试流式响应
for chunk in client.stream_message(
    conversation_id=conversation['conversation_id'],
    query="请介绍一下手冲咖啡的技巧"
):
    print(chunk, end="")
```

## 🔄 第五步：Webhook配置

### 5.1 配置Webhook

在Coze开发者控制台中：
1. 进入应用设置
2. 找到"Webhook"配置
3. 设置回调URL：`https://your-domain.com/webhook/coze`
4. 设置Bearer Token：`your_webhook_bearer_token`

### 5.2 测试Webhook

```python
# 模拟Webhook回调
import requests

webhook_url = "https://your-domain.com/webhook/coze"
bearer_token = "your_webhook_bearer_token"

headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

data = {
    "event": "conversation.message",
    "data": {
        "conversation_id": "conv_123",
        "message": "Hello from Coze"
    }
}

response = requests.post(webhook_url, headers=headers, json=data)
print(f"Webhook Response: {response.status_code}")
```

## 🤖 第六步：KAI智能体集成

### 6.1 配置KAI适配器

编辑 `kai_manager.py`：
```python
class KAIManager:
    def __init__(self):
        self.mcp_server_url = "your_mcp_server_url"
        self.api_key = "your_kai_api_key"
    
    async def invoke_tool(self, tool_name: str, payload: dict):
        """调用KAI工具"""
        # 这里实现具体的KAI工具调用逻辑
        pass
```

### 6.2 测试工具调用

```python
# 测试工具调用
result = await kai_manager.invoke_tool(
    tool_name="coffee_knowledge_query",
    payload={"query": "埃塞俄比亚咖啡特点"}
)

print(f"Tool Result: {result}")
```

## 📊 第七步：监控和调试

### 7.1 查看日志

```bash
# 查看实时日志
tail -f logs/coze_integration.log

# 查看错误日志
tail -f logs/error.log
```

### 7.2 健康检查

```bash
# 检查所有服务状态
curl http://localhost:8080/health

# 检查Coze连接
curl http://localhost:8080/diagnostics/coze

# 检查KAI连接
curl http://localhost:8080/diagnostics/kai
```

### 7.3 性能监控

访问监控面板：`http://localhost:8080/monitoring`

查看指标：
- API调用成功率
- 平均响应时间
- 错误率统计
- 资源使用情况

## 🚨 故障排除

### 常见问题

#### 1. JWT认证失败
```
错误：Invalid JWT signature
解决：检查私钥和公钥是否匹配，确认kid正确
```

#### 2. API调用401
```
错误：Unauthorized
解决：检查access_token是否过期，重新获取
```

#### 3. Webhook接收失败
```
错误：Webhook signature verification failed
解决：检查Bearer Token是否正确
```

#### 4. 工具调用超时
```
错误：Tool invocation timeout
解决：检查KAI服务状态，增加超时时间
```

### 调试模式

```python
# 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 或在代码中设置
config.debug_mode = True
```

## 📈 性能优化

### 1. 连接池配置
```python
# 配置连接池
client = CozeClient(
    access_token=token,
    max_connections=100,
    timeout=30
)
```

### 2. 缓存策略
```python
# 启用缓存
cache_config = {
    "token_cache_ttl": 3600,  # 1小时
    "response_cache_ttl": 300  # 5分钟
}
```

### 3. 限流控制
```python
# 配置限流
rate_limit = {
    "requests_per_minute": 60,
    "burst_size": 10
}
```

## ✅ 验收测试

### 测试清单

- [ ] OAuth应用创建成功
- [ ] JWT令牌生成和验证
- [ ] 访问令牌获取
- [ ] 会话创建和消息发送
- [ ] 流式响应正常
- [ ] Webhook配置和测试
- [ ] KAI工具调用
- [ ] 错误处理机制
- [ ] 监控面板正常
- [ ] 性能指标达标

### 验收标准

| 指标 | 目标值 | 验收方法 |
|------|--------|----------|
| API成功率 | ≥99% | 连续测试100次 |
| 平均响应时间 | ≤2秒 | 性能测试 |
| 并发处理能力 | ≥50 QPS | 压力测试 |
| 错误恢复时间 | ≤30秒 | 故障注入测试 |

## 🎉 部署完成

完成以上步骤后，您的AI咖啡知识沙龙系统将与Coze平台成功集成！

### 下一步建议

1. **功能扩展**：添加更多KAI工具和功能
2. **用户体验**：优化对话流程和交互设计
3. **数据分析**：收集用户行为数据，优化系统
4. **安全加固**：加强安全防护和审计日志

### 技术支持

如遇到问题，请：
1. 查看系统日志
2. 检查配置参数
3. 参考故障排除章节
4. 联系技术支持团队

---

**重要提醒**：
- 请妥善保管API密钥和私钥
- 定期轮换访问令牌
- 监控API使用配额
- 遵守平台使用条款