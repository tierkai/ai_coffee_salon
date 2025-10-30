"""
智能体协作管理器
负责管理专家智能体间的协作和知识共享
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import logging
from collections import defaultdict

from core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem

logger = logging.getLogger(__name__)


@dataclass
class CollaborationSession:
    """协作会话"""
    session_id: str
    topic: str
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    contributions: List[Dict] = field(default_factory=list)
    knowledge_sharing: List[Dict] = field(default_factory=list)
    consensus_reached: bool = False
    final_output: Optional[str] = None


@dataclass
class KnowledgeSharing:
    """知识共享记录"""
    from_agent: str
    to_agent: str
    knowledge_item: KnowledgeItem
    timestamp: datetime
    shared_successfully: bool = False


class CollaborationManager:
    """协作管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseExpertAgent] = {}
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.knowledge_sharing_history: List[KnowledgeSharing] = []
        self.collaboration_metrics = {
            'total_sessions': 0,
            'successful_collaborations': 0,
            'knowledge_shares': 0,
            'consensus_rate': 0.0
        }
        
        logger.info("协作管理器已初始化")
    
    def register_agent(self, agent: BaseExpertAgent):
        """注册智能体"""
        self.agents[agent.agent_id] = agent
        logger.info(f"智能体 {agent.name} 已注册")
    
    def create_collaboration_session(self, topic: str, participant_ids: List[str]) -> str:
        """创建协作会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 验证参与者
        valid_participants = []
        for agent_id in participant_ids:
            if agent_id in self.agents:
                valid_participants.append(agent_id)
            else:
                logger.warning(f"智能体 {agent_id} 未注册，跳过")
        
        if not valid_participants:
            raise ValueError("没有有效的参与者")
        
        session = CollaborationSession(
            session_id=session_id,
            topic=topic,
            participants=valid_participants,
            start_time=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        self.collaboration_metrics['total_sessions'] += 1
        
        logger.info(f"创建协作会话: {session_id}, 主题: {topic}")
        return session_id
    
    async def start_collaborative_discussion(self, session_id: str, initial_query: str = None) -> Dict[str, Any]:
        """开始协作讨论"""
        if session_id not in self.active_sessions:
            raise ValueError(f"会话 {session_id} 不存在")
        
        session = self.active_sessions[session_id]
        logger.info(f"开始协作讨论: {session.topic}")
        
        try:
            # 并发获取各专家的观点
            tasks = []
            for agent_id in session.participants:
                agent = self.agents[agent_id]
                query = initial_query or f"请就'{session.topic}'发表您的专业见解"
                tasks.append(self._get_agent_response(agent, query))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理响应
            contributions = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"智能体 {session.participants[i]} 响应错误: {response}")
                    continue
                
                contribution = {
                    'agent_id': session.participants[i],
                    'agent_name': self.agents[session.participants[i]].name,
                    'response': response.content,
                    'confidence': response.confidence,
                    'timestamp': response.timestamp.isoformat(),
                    'knowledge_items': [
                        {
                            'id': item.id,
                            'content': item.content,
                            'confidence': item.confidence
                        }
                        for item in response.knowledge_items
                    ]
                }
                contributions.append(contribution)
            
            session.contributions = contributions
            
            # 知识共享阶段
            await self._facilitate_knowledge_sharing(session)
            
            # 达成共识
            consensus = await self._reach_consensus(session)
            
            session.end_time = datetime.now()
            session.consensus_reached = consensus['reached']
            session.final_output = consensus['output']
            
            # 更新指标
            if session.consensus_reached:
                self.collaboration_metrics['successful_collaborations'] += 1
            
            result = {
                'session_id': session_id,
                'topic': session.topic,
                'participants': [
                    {
                        'agent_id': pid,
                        'agent_name': self.agents[pid].name
                    }
                    for pid in session.participants
                ],
                'contributions': contributions,
                'knowledge_sharing': session.knowledge_sharing,
                'consensus_reached': session.consensus_reached,
                'final_output': session.final_output,
                'duration': (session.end_time - session.start_time).total_seconds()
            }
            
            logger.info(f"协作讨论完成: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"协作讨论失败: {e}")
            raise
    
    async def _get_agent_response(self, agent: BaseExpertAgent, query: str) -> ExpertResponse:
        """获取智能体响应"""
        start_time = datetime.now()
        try:
            response = agent.process_query(query)
            response_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = response_time
            
            # 更新性能指标
            agent.update_performance_metrics(response_time, True)
            
            return response
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            agent.update_performance_metrics(response_time, False)
            logger.error(f"智能体 {agent.name} 处理查询失败: {e}")
            raise
    
    async def _facilitate_knowledge_sharing(self, session: CollaborationSession):
        """促进知识共享"""
        logger.info("开始知识共享阶段")
        
        # 分析所有贡献，识别可共享的知识
        all_knowledge = []
        for contribution in session.contributions:
            all_knowledge.extend(contribution['knowledge_items'])
        
        # 智能体间的知识共享
        for i, contributor_id in enumerate(session.participants):
            contributor = self.agents[contributor_id]
            
            for j, recipient_id in enumerate(session.participants):
                if i == j:  # 不与自己共享
                    continue
                
                recipient = self.agents[recipient_id]
                
                # 找到适合共享的知识项
                for knowledge in contribution['knowledge_items']:
                    if self._should_share_knowledge(contributor, recipient, knowledge):
                        sharing_record = KnowledgeSharing(
                            from_agent=contributor_id,
                            to_agent=recipient_id,
                            knowledge_item=KnowledgeItem(
                                id=f"{knowledge['id']}_shared_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                content=knowledge['content'],
                                source=f"{contributor.name}共享",
                                confidence=knowledge['confidence'],
                                quality=contributor.knowledge_base[knowledge['id']].quality,
                                timestamp=datetime.now(),
                                tags=[f"shared_from_{contributor_id}"]
                            ),
                            timestamp=datetime.now()
                        )
                        
                        # 执行知识共享
                        success = await self._execute_knowledge_sharing(sharing_record)
                        sharing_record.shared_successfully = success
                        
                        session.knowledge_sharing.append({
                            'from_agent': contributor_id,
                            'to_agent': recipient_id,
                            'knowledge_content': knowledge['content'],
                            'shared_successfully': success,
                            'timestamp': sharing_record.timestamp.isoformat()
                        })
                        
                        self.knowledge_sharing_history.append(sharing_record)
                        self.collaboration_metrics['knowledge_shares'] += 1
        
        logger.info(f"知识共享完成，共{len(session.knowledge_sharing)}次共享")
    
    def _should_share_knowledge(self, contributor: BaseExpertAgent, 
                               recipient: BaseExpertAgent, knowledge: Dict) -> bool:
        """判断是否应该共享知识"""
        # 简单的启发式规则
        # 1. 知识置信度较高
        if knowledge['confidence'] < 0.7:
            return False
        
        # 2. recipient的知识库中不包含相关内容
        existing_knowledge = recipient.search_knowledge(knowledge['content'], limit=1)
        if existing_knowledge:
            return False
        
        # 3. 专家领域互补
        contributor_areas = set(contributor.get_expertise_areas())
        recipient_areas = set(recipient.get_expertise_areas())
        
        # 如果recipient在某个领域知识较少，而contributor有相关知识
        if not contributor_areas.intersection(recipient_areas):
            return True
        
        return False
    
    async def _execute_knowledge_sharing(self, sharing: KnowledgeSharing) -> bool:
        """执行知识共享"""
        try:
            recipient = self.agents[sharing.to_agent]
            
            # 添加知识项到recipient的知识库
            recipient.add_knowledge_item(sharing.knowledge_item)
            
            logger.info(f"知识共享成功: {sharing.from_agent} -> {sharing.to_agent}")
            return True
            
        except Exception as e:
            logger.error(f"知识共享失败: {e}")
            return False
    
    async def _reach_consensus(self, session: CollaborationSession) -> Dict[str, Any]:
        """达成共识"""
        logger.info("开始共识达成阶段")
        
        # 收集所有观点
        all_views = []
        for contribution in session.contributions:
            all_views.append({
                'agent': contribution['agent_name'],
                'view': contribution['response'],
                'confidence': contribution['confidence']
            })
        
        # 使用主持人智能体（或第一个智能体）来综合观点
        if session.participants:
            facilitator = self.agents[session.participants[0]]
            
            # 构建共识查询
            consensus_query = f"""
基于以下关于"{session.topic}"的专家观点，请生成一个综合性的共识报告：

{json.dumps(all_views, ensure_ascii=False, indent=2)}

请整合各方观点，识别共识点，标注分歧点，并提供最终建议。
            """
            
            try:
                consensus_response = facilitator.process_query(consensus_query)
                
                return {
                    'reached': True,
                    'output': consensus_response.content,
                    'confidence': consensus_response.confidence
                }
            except Exception as e:
                logger.error(f"共识达成失败: {e}")
                return {
                    'reached': False,
                    'output': "无法达成共识",
                    'confidence': 0.0
                }
        
        return {
            'reached': False,
            'output': "没有足够的参与者",
            'confidence': 0.0
        }
    
    def get_collaboration_metrics(self) -> Dict[str, Any]:
        """获取协作指标"""
        metrics = self.collaboration_metrics.copy()
        
        # 计算共识率
        if metrics['total_sessions'] > 0:
            metrics['consensus_rate'] = (
                metrics['successful_collaborations'] / metrics['total_sessions']
            )
        
        return metrics
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活跃会话"""
        sessions = []
        for session_id, session in self.active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'topic': session.topic,
                'participants': session.participants,
                'start_time': session.start_time.isoformat(),
                'duration': (datetime.now() - session.start_time).total_seconds(),
                'contributions_count': len(session.contributions)
            })
        
        return sessions
    
    def get_knowledge_sharing_network(self) -> Dict[str, Any]:
        """获取知识共享网络"""
        network = defaultdict(list)
        
        for sharing in self.knowledge_sharing_history:
            network[sharing.from_agent].append({
                'to': sharing.to_agent,
                'knowledge_id': sharing.knowledge_item.id,
                'confidence': sharing.knowledge_item.confidence,
                'timestamp': sharing.timestamp.isoformat()
            })
        
        return dict(network)
    
    def generate_collaboration_report(self) -> str:
        """生成协作报告"""
        metrics = self.get_collaboration_metrics()
        active_sessions = self.get_active_sessions()
        sharing_network = self.get_knowledge_sharing_network()
        
        report = f"""
# 智能体协作报告

## 总体指标
- 总协作会话数: {metrics['total_sessions']}
- 成功协作数: {metrics['successful_collaborations']}
- 知识共享次数: {metrics['knowledge_shares']}
- 共识达成率: {metrics['consensus_rate']:.2%}

## 活跃会话
"""
        
        for session in active_sessions:
            report += f"- {session['session_id']}: {session['topic']} ({len(session['participants'])}人参与)\n"
        
        report += "\n## 知识共享网络\n"
        for agent_id, shares in sharing_network.items():
            agent_name = self.agents[agent_id].name if agent_id in self.agents else agent_id
            report += f"- {agent_name}: 共享给 {len(shares)} 个智能体\n"
        
        return report