# 基础设置示例

这个示例将展示如何快速设置和运行 AI Tech Innovation Suite 的核心组件。

## 前置要求

- Python 3.9+
- PostgreSQL 13+
- Redis 6+

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/ai-tech-innovation/suite.git
cd suite

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库设置

```bash
# 创建数据库
createdb ai_suite_demo

# 运行迁移
python scripts/setup/init-db.py
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/ai_suite_demo
REDIS_URL=redis://localhost:6379/0

# API配置
OPENAI_API_KEY=your_openai_api_key
COZE_API_KEY=your_coze_api_key

# 应用配置
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

### 4. 启动服务

```bash
# 启动多智能体框架
python -m packages.multi_agent_framework.run

# 在新终端中启动Web应用
cd web-app/frontend
npm install
npm run dev
```

## 基础示例代码

### 创建简单智能体

```python
# examples/basic-setup/simple_agent.py
import asyncio
from packages.multi_agent_framework.core.agent import Agent
from packages.multi_agent_framework.core.registry import AgentRegistry

async def main():
    # 创建智能体注册表
    registry = AgentRegistry()
    
    # 创建简单智能体
    agent = Agent(
        name="HelloAgent",
        role="greeting",
        system_prompt="你是一个友好的问候助手"
    )
    
    # 注册智能体
    await registry.register_agent("hello", agent)
    
    # 发送消息
    response = await registry.send_message(
        agent_name="hello",
        message="你好，请介绍一下自己"
    )
    
    print(f"智能体回复: {response}")
    
    # 清理
    await registry.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 内容生成示例

```python
# examples/basic-setup/content_generation.py
import asyncio
from packages.xiaohongshu_agent import XiaohongshuAgent

async def main():
    # 创建小红书Agent
    agent = XiaohongshuAgent({
        "content_generator": {
            "provider": "openai",
            "model": "gpt-3.5-turbo"
        },
        "image_processor": {
            "quality": 85,
            "max_size": (1080, 1080)
        }
    })
    
    # 生成内容
    content = await agent.generate_content(
        topic="夏日护肤心得",
        brand_info={
            "name": "美丽日记",
            "category": "护肤"
        },
        content_type="experience_share"
    )
    
    print("生成的内容:")
    print(f"标题: {content['title']}")
    print(f"正文: {content['content'][:100]}...")
    print(f"标签: {', '.join(content['hashtags'])}")
    
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 知识分析示例

```python
# examples/basic-setup/knowledge_analysis.py
import asyncio
from packages.knowledge_emergence import KnowledgeEmergenceAnalyzer

async def main():
    # 创建知识分析器
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 示例知识数据
    knowledge_data = [
        {
            "id": "1",
            "content": "人工智能是计算机科学的一个分支",
            "source": "教科书",
            "timestamp": "2024-01-01"
        },
        {
            "id": "2", 
            "content": "机器学习是AI的重要实现方式",
            "source": "论文",
            "timestamp": "2024-01-02"
        }
    ]
    
    # 分析知识
    result = await analyzer.analyze_knowledge(
        knowledge_items=knowledge_data,
        analysis_type="quality_assessment"
    )
    
    print("知识分析结果:")
    print(f"质量评分: {result['quality_score']:.2f}")
    print(f"价值评估: {result['value_assessment']}")
    print(f"模式识别: {result['patterns']}")
    
    analyzer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 运行示例

```bash
# 运行简单智能体示例
python examples/basic-setup/simple_agent.py

# 运行内容生成示例
python examples/basic-setup/content_generation.py

# 运行知识分析示例
python examples/basic-setup/knowledge_analysis.py
```

## 预期输出

运行上述示例后，您应该看到：

1. **智能体示例**: 显示智能体的友好问候回复
2. **内容生成示例**: 生成包含标题、正文和标签的小红书内容
3. **知识分析示例**: 显示知识质量评分和模式识别结果

## 下一步

- 查看[进阶示例](../advanced-features/)了解更多功能
- 阅读[用户指南](../../guides/)深入了解各个组件
- 尝试[集成示例](../integrations/)了解如何组合使用多个组件

## 故障排除

### 常见问题

**Q: 数据库连接失败**
A: 确保PostgreSQL和Redis服务正在运行，并且DATABASE_URL配置正确

**Q: API密钥错误**
A: 检查.env文件中的API密钥是否正确设置

**Q: 端口被占用**
A: 修改配置文件中的端口号，或停止占用端口的其他服务

### 获取帮助

如果遇到问题，请：
- 查看[故障排除指南](../../guides/troubleshooting.md)
- 在[GitHub Discussions](https://github.com/ai-tech-innovation/suite/discussions)提问
- 加入[Discord社区](https://discord.gg/ai-tech-suite)
