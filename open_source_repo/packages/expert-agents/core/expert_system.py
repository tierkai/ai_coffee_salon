"""
专家智能体工厂
统一管理和创建所有专家智能体
"""

from typing import Dict, List, Any, Optional, Type
import logging

from core.base_agent import BaseExpertAgent
from core.collaboration_manager import CollaborationManager
from agents.origin_expert import OriginExpertAgent
from agents.roasting_expert import RoastingExpertAgent
from agents.extraction_expert import ExtractionExpertAgent
from agents.water_expert import WaterExpertAgent
from agents.equipment_expert import EquipmentExpertAgent
from .sensory_expert import SensoryExpertAgent

logger = logging.getLogger(__name__)


class ExpertAgentFactory:
    """专家智能体工厂"""
    
    def __init__(self):
        self.agents: Dict[str, BaseExpertAgent] = {}
        self.agent_classes = {
            'origin': OriginExpertAgent,
            'roasting': RoastingExpertAgent,
            'extraction': ExtractionExpertAgent,
            'water': WaterExpertAgent,
            'equipment': EquipmentExpertAgent,
            'sensory': SensoryExpertAgent
        }
        
        logger.info("专家智能体工厂已初始化")
    
    def create_agent(self, agent_type: str) -> BaseExpertAgent:
        """创建指定类型的专家智能体"""
        if agent_type not in self.agent_classes:
            raise ValueError(f"不支持的智能体类型: {agent_type}")
        
        agent_class = self.agent_classes[agent_type]
        agent = agent_class()
        self.agents[agent.agent_id] = agent
        
        logger.info(f"创建了{agent_type}专家智能体: {agent.name}")
        return agent
    
    def create_all_agents(self) -> Dict[str, BaseExpertAgent]:
        """创建所有专家智能体"""
        agents = {}
        for agent_type in self.agent_classes.keys():
            agent = self.create_agent(agent_type)
            agents[agent_type] = agent
        
        logger.info(f"创建了{len(agents)}个专家智能体")
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[BaseExpertAgent]:
        """获取指定智能体"""
        return self.agents.get(agent_id)
    
    def get_agent_by_type(self, agent_type: str) -> Optional[BaseExpertAgent]:
        """根据类型获取智能体"""
        for agent in self.agents.values():
            if agent_type in agent.agent_id:
                return agent
        return None
    
    def get_all_agents(self) -> Dict[str, BaseExpertAgent]:
        """获取所有智能体"""
        return self.agents.copy()
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """获取所有智能体信息"""
        info = []
        for agent in self.agents.values():
            info.append(agent.get_specialty_info())
        return info
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除智能体"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"移除了智能体: {agent_id}")
            return True
        return False
    
    def reset_factory(self):
        """重置工厂"""
        self.agents.clear()
        logger.info("专家智能体工厂已重置")


class ExpertAgentCoordinator:
    """专家智能体协调器"""
    
    def __init__(self):
        self.factory = ExpertAgentFactory()
        self.collaboration_manager = CollaborationManager()
        self.active_agents: Dict[str, BaseExpertAgent] = {}
        
        # 注册所有智能体到协作管理器
        self._initialize_system()
        
        logger.info("专家智能体协调器已初始化")
    
    def _initialize_system(self):
        """初始化系统"""
        # 创建所有专家智能体
        self.active_agents = self.factory.create_all_agents()
        
        # 注册到协作管理器
        for agent in self.active_agents.values():
            self.collaboration_manager.register_agent(agent)
        
        logger.info("专家智能体系统初始化完成")
    
    def query_expert(self, agent_type: str, query: str, context: Dict = None) -> Dict[str, Any]:
        """查询指定专家"""
        agent = self.factory.get_agent_by_type(agent_type)
        if not agent:
            return {
                'success': False,
                'error': f'未找到{agent_type}专家'
            }
        
        try:
            response = agent.process_query(query, context)
            return {
                'success': True,
                'agent_info': agent.get_specialty_info(),
                'response': {
                    'content': response.content,
                    'confidence': response.confidence,
                    'processing_time': response.processing_time,
                    'knowledge_items': [
                        {
                            'id': item.id,
                            'content': item.content,
                            'confidence': item.confidence,
                            'quality': item.quality.value
                        }
                        for item in response.knowledge_items
                    ],
                    'recommendations': response.recommendations,
                    'warnings': response.warnings
                }
            }
        except Exception as e:
            logger.error(f"查询{agent_type}专家失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_all_experts(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """查询所有专家"""
        results = {}
        
        for agent_type in self.factory.agent_classes.keys():
            result = self.query_expert(agent_type, query, context)
            results[agent_type] = result
        
        # 统计结果
        successful_queries = sum(1 for r in results.values() if r['success'])
        
        return {
            'success': True,
            'total_experts': len(results),
            'successful_queries': successful_queries,
            'results': results
        }
    
    def collaborative_discussion(self, topic: str, participant_types: List[str] = None) -> Dict[str, Any]:
        """启动协作讨论"""
        if participant_types is None:
            participant_types = list(self.factory.agent_classes.keys())
        
        # 验证参与者
        valid_participants = []
        for agent_type in participant_types:
            agent = self.factory.get_agent_by_type(agent_type)
            if agent:
                valid_participants.append(agent.agent_id)
        
        if not valid_participants:
            return {
                'success': False,
                'error': '没有有效的参与者'
            }
        
        try:
            # 创建协作会话
            session_id = self.collaboration_manager.create_collaboration_session(
                topic, valid_participants
            )
            
            # 启动讨论
            import asyncio
            result = asyncio.run(
                self.collaboration_manager.start_collaborative_discussion(
                    session_id, f"请就'{topic}'发表您的专业见解"
                )
            )
            
            return {
                'success': True,
                'session_id': session_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"协作讨论失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_expert_recommendation(self, question: str) -> Dict[str, Any]:
        """获取专家推荐"""
        # 根据问题类型推荐合适的专家
        question_lower = question.lower()
        
        recommendations = []
        
        # 产区相关
        if any(keyword in question_lower for keyword in ['产区', '产地', 'origin', '国家', '地区']):
            recommendations.append({
                'expert_type': 'origin',
                'reason': '问题涉及咖啡产区信息'
            })
        
        # 烘焙相关
        if any(keyword in question_lower for keyword in ['烘焙', 'roast', '温度', 'curve']):
            recommendations.append({
                'expert_type': 'roasting',
                'reason': '问题涉及咖啡烘焙技术'
            })
        
        # 萃取相关
        if any(keyword in question_lower for keyword in ['萃取', 'extraction', 'espresso', '手冲']):
            recommendations.append({
                'expert_type': 'extraction',
                'reason': '问题涉及咖啡萃取方法'
            })
        
        # 水质相关
        if any(keyword in question_lower for keyword in ['水质', 'water', 'TDS', '硬度', 'pH']):
            recommendations.append({
                'expert_type': 'water',
                'reason': '问题涉及水质对咖啡的影响'
            })
        
        # 器具相关
        if any(keyword in question_lower for keyword in ['器具', 'equipment', '机器', '磨豆机']):
            recommendations.append({
                'expert_type': 'equipment',
                'reason': '问题涉及咖啡器具选择'
            })
        
        # 感官相关
        if any(keyword in question_lower for keyword in ['风味', 'flavor', '杯测', 'sensory', '品鉴']):
            recommendations.append({
                'expert_type': 'sensory',
                'reason': '问题涉及咖啡感官品鉴'
            })
        
        # 如果没有特定推荐，建议协作讨论
        if not recommendations:
            recommendations.append({
                'expert_type': 'collaborative',
                'reason': '问题复杂，建议多专家协作讨论'
            })
        
        return {
            'success': True,
            'question': question,
            'recommendations': recommendations
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        agents_info = self.factory.get_agent_info()
        collaboration_metrics = self.collaboration_manager.get_collaboration_metrics()
        active_sessions = self.collaboration_manager.get_active_sessions()
        
        return {
            'success': True,
            'system_info': {
                'total_agents': len(agents_info),
                'active_agents': len([a for a in agents_info if a['performance_metrics']['total_queries'] > 0]),
                'collaboration_metrics': collaboration_metrics,
                'active_sessions': len(active_sessions)
            },
            'agents': agents_info,
            'active_sessions': active_sessions
        }
    
    def export_knowledge_base(self) -> Dict[str, Any]:
        """导出所有知识库"""
        knowledge_bases = {}
        
        for agent in self.active_agents.values():
            knowledge_bases[agent.agent_id] = agent.export_knowledge_base()
        
        return {
            'success': True,
            'export_time': datetime.now().isoformat(),
            'knowledge_bases': knowledge_bases,
            'collaboration_network': self.collaboration_manager.get_knowledge_sharing_network()
        }
    
    def generate_system_report(self) -> str:
        """生成系统报告"""
        status = self.get_system_status()
        collaboration_report = self.collaboration_manager.generate_collaboration_report()
        
        report = f"""
# AI咖啡专家智能体系统报告

## 系统概览
- 总智能体数: {status['system_info']['total_agents']}
- 活跃智能体数: {status['system_info']['active_agents']}
- 协作会话数: {status['system_info']['collaboration_metrics']['total_sessions']}
- 知识共享次数: {status['system_info']['collaboration_metrics']['knowledge_shares']}

## 智能体状态
"""
        
        for agent in status['agents']:
            metrics = agent['performance_metrics']
            report += f"""
### {agent['name']} ({agent['specialty']})
- 查询数: {metrics['total_queries']}
- 成功率: {metrics['knowledge_accuracy']:.2%}
- 平均响应时间: {metrics['avg_response_time']:.2f}秒
"""
        
        report += f"\n## 协作情况\n{collaboration_report}"
        
        return report


# 便捷函数
def create_expert_system() -> ExpertAgentCoordinator:
    """创建专家系统"""
    return ExpertAgentCoordinator()


def query_expert_by_question(question: str, coordinator: ExpertAgentCoordinator = None) -> Dict[str, Any]:
    """根据问题自动选择专家并查询"""
    if coordinator is None:
        coordinator = create_expert_system()
    
    # 获取专家推荐
    recommendation = coordinator.get_expert_recommendation(question)
    
    if recommendation['recommendations'][0]['expert_type'] == 'collaborative':
        # 启动协作讨论
        return coordinator.collaborative_discussion(question)
    else:
        # 查询指定专家
        expert_type = recommendation['recommendations'][0]['expert_type']
        return coordinator.query_expert(expert_type, question)


# 导入datetime
from datetime import datetime