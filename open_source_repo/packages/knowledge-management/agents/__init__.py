"""
智能体模块

实现多智能体协作系统：
- 研究型智能体：信息检索和收集
- 执行型智能体：知识综合和推理
- 校对型智能体：质量评估和验证
- 编排器：智能体协作管理
"""

from .multi_agent import (
    BaseAgent,
    ResearcherAgent,
    ExecutorAgent, 
    ReviewerAgent,
    MultiAgentOrchestrator
)

__all__ = [
    "BaseAgent",
    "ResearcherAgent",
    "ExecutorAgent",
    "ReviewerAgent", 
    "MultiAgentOrchestrator"
]
