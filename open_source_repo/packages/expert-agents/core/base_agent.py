"""
专家智能体基类
为所有咖啡专家智能体提供基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpertLevel(Enum):
    """专家等级"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家"


class KnowledgeQuality(Enum):
    """知识质量等级"""
    HIGH = "高质量"
    MEDIUM = "中等质量"
    LOW = "低质量"
    UNVERIFIED = "未验证"


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    content: str
    source: str
    confidence: float
    quality: KnowledgeQuality
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    verified: bool = False


@dataclass
class ExpertResponse:
    """专家响应"""
    agent_id: str
    agent_name: str
    content: str
    confidence: float
    knowledge_items: List[KnowledgeItem] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class BaseExpertAgent(ABC):
    """专家智能体基类"""
    
    def __init__(self, agent_id: str, name: str, specialty: str, level: ExpertLevel):
        self.agent_id = agent_id
        self.name = name
        self.specialty = specialty
        self.level = level
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        self.collaboration_history: List[Dict] = []
        self.performance_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'avg_response_time': 0.0,
            'knowledge_accuracy': 0.0
        }
        
        # 初始化知识库
        self._initialize_knowledge_base()
        
        logger.info(f"专家智能体 {self.name} ({self.specialty}) 已初始化")
    
    @abstractmethod
    def _initialize_knowledge_base(self):
        """初始化专业知识库"""
        pass
    
    @abstractmethod
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理查询"""
        pass
    
    def get_specialty_info(self) -> Dict[str, Any]:
        """获取专家信息"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'specialty': self.specialty,
            'level': self.level.value,
            'expertise_areas': self.get_expertise_areas(),
            'performance_metrics': self.performance_metrics
        }
    
    @abstractmethod
    def get_expertise_areas(self) -> List[str]:
        """获取专业领域列表"""
        pass
    
    def add_knowledge_item(self, item: KnowledgeItem):
        """添加知识项"""
        self.knowledge_base[item.id] = item
        logger.debug(f"添加知识项: {item.id}")
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeItem]:
        """搜索知识库"""
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_base.values():
            # 简单的关键词匹配
            if (query_lower in item.content.lower() or 
                any(query_lower in tag.lower() for tag in item.tags)):
                results.append(item)
        
        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:limit]
    
    def validate_knowledge(self, knowledge_item: KnowledgeItem) -> Tuple[bool, str]:
        """验证知识项"""
        # 基本验证规则
        if not knowledge_item.content.strip():
            return False, "内容不能为空"
        
        if knowledge_item.confidence < 0.0 or knowledge_item.confidence > 1.0:
            return False, "置信度必须在0-1之间"
        
        # 专业知识验证
        validation_result = self._validate_domain_specific_knowledge(knowledge_item)
        return validation_result
    
    @abstractmethod
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> Tuple[bool, str]:
        """专业知识验证"""
        pass
    
    def collaborate_with_agent(self, other_agent: 'BaseExpertAgent', topic: str) -> Dict[str, Any]:
        """与其他智能体协作"""
        collaboration_record = {
            'timestamp': datetime.now().isoformat(),
            'partner_agent': other_agent.name,
            'topic': topic,
            'contribution': self.process_query(topic),
            'status': 'completed'
        }
        
        self.collaboration_history.append(collaboration_record)
        logger.info(f"与 {other_agent.name} 协作完成: {topic}")
        
        return collaboration_record
    
    def update_performance_metrics(self, response_time: float, success: bool):
        """更新性能指标"""
        self.performance_metrics['total_queries'] += 1
        
        if success:
            self.performance_metrics['successful_responses'] += 1
        
        # 更新平均响应时间
        current_avg = self.performance_metrics['avg_response_time']
        total_queries = self.performance_metrics['total_queries']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
        # 更新准确率
        success_rate = (
            self.performance_metrics['successful_responses'] / 
            self.performance_metrics['total_queries']
        )
        self.performance_metrics['knowledge_accuracy'] = success_rate
    
    def export_knowledge_base(self) -> Dict[str, Any]:
        """导出知识库"""
        return {
            'agent_info': self.get_specialty_info(),
            'knowledge_items': [
                {
                    'id': item.id,
                    'content': item.content,
                    'source': item.source,
                    'confidence': item.confidence,
                    'quality': item.quality.value,
                    'timestamp': item.timestamp.isoformat(),
                    'tags': item.tags,
                    'references': item.references,
                    'verified': item.verified
                }
                for item in self.knowledge_base.values()
            ],
            'collaboration_history': self.collaboration_history
        }
    
    def generate_report(self) -> str:
        """生成专家报告"""
        info = self.get_specialty_info()
        report = f"""
# {self.name} - {self.specialty}专家报告

## 基本信息
- 专家ID: {info['agent_id']}
- 专业等级: {info['level']}
- 专业领域: {', '.join(info['expertise_areas'])}

## 性能指标
- 总查询数: {info['performance_metrics']['total_queries']}
- 成功响应数: {info['performance_metrics']['successful_responses']}
- 平均响应时间: {info['performance_metrics']['avg_response_time']:.2f}秒
- 知识准确率: {info['performance_metrics']['knowledge_accuracy']:.2%}

## 知识库状态
- 知识项数量: {len(self.knowledge_base)}
- 协作记录数: {len(self.collaboration_history)}

## 最近协作记录
"""
        
        # 添加最近的协作记录
        for record in self.collaboration_history[-5:]:
            report += f"- {record['timestamp']}: 与{record['partner_agent']}讨论{record['topic']}\n"
        
        return report