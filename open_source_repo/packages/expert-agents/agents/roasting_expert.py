"""
烘焙专家智能体
负责咖啡烘焙技术、曲线控制、烘焙程度等专业知识
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import math

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class RoastingExpertAgent(BaseExpertAgent):
    """烘焙专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="roasting_expert_001",
            name="烘焙专家",
            specialty="咖啡烘焙技术",
            level=ExpertLevel.EXPERT
        )
        
        # 烘焙曲线数据存储
        self.roasting_curves = {}
        self.temperature_zones = {
            'drying': (0, 150),      # 干燥阶段
            'maillard': (150, 200),  # 梅纳反应阶段
            'development': (200, 230) # 发展阶段
        }
    
    def _initialize_knowledge_base(self):
        """初始化烘焙专业知识库"""
        roasting_knowledge = [
            {
                'id': 'roast_levels_light',
                'content': '浅度烘焙保留了咖啡豆的原始风味特征，酸质明亮，香气清新。烘焙温度通常在180-205°C，烘焙时间较短。适合高质量的单一产区豆。',
                'source': 'SCA烘焙标准',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['浅度烘焙', '酸质明亮', '180-205°C', '单一产区'],
                'references': ['SCA烘焙指南']
            },
            {
                'id': 'roast_levels_medium',
                'content': '中度烘焙平衡了酸质和甜感，是最受欢迎的烘焙程度。温度范围200-220°C，烘焙时间适中。风味平衡，适合多种冲煮方法。',
                'source': 'SCA烘焙标准',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['中度烘焙', '平衡', '200-220°C', '通用'],
                'references': ['SCA烘焙指南']
            },
            {
                'id': 'roast_levels_dark',
                'content': '深度烘焙产生浓郁的焦糖和巧克力风味，酸质较低。温度220-240°C，烘焙时间较长。适合意式浓缩和重度烘焙爱好者。',
                'source': 'SCA烘焙标准',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['深度烘焙', '浓郁', '220-240°C', '意式浓缩'],
                'references': ['SCA烘焙指南']
            },
            {
                'id': 'temperature_curve',
                'content': '烘焙温度曲线是控制烘焙过程的关键。理想的曲线应包含：干燥阶段(室温-150°C)、梅纳反应阶段(150-200°C)、发展阶段(200-230°C)。每个阶段都有特定的升温速率要求。',
                'source': '烘焙工程学',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['温度曲线', '干燥', '梅纳反应', '发展阶段', '升温速率'],
                'references': ['咖啡烘焙工程学']
            },
            {
                'id': 'first_crack',
                'content': '一爆是咖啡烘焙中的重要里程碑，标志着水分蒸发和气体膨胀达到高峰。温度通常在196-205°C，豆子会产生爆裂声。这是发展阶段的开始。',
                'source': '烘焙技术手册',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['一爆', '196-205°C', '里程碑', '发展阶段'],
                'references': ['烘焙技术手册']
            },
            {
                'id': 'second_crack',
                'content': '二爆发生在更深度的烘焙阶段，温度约225-230°C。此时咖啡豆结构进一步破坏，产生更强烈的爆裂声。超过二爆会烧焦咖啡豆。',
                'source': '烘焙技术手册',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['二爆', '225-230°C', '深度烘焙', '烧焦'],
                'references': ['烘焙技术手册']
            },
            {
                'id': 'development_time',
                'content': '发展时间指从一爆开始到烘焙结束的时间。浅度烘焙发展时间较短(1-3分钟)，中度烘焙3-5分钟，深度烘焙5-8分钟。发展时间影响最终风味。',
                'source': '烘焙工艺学',
                'confidence': 0.91,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['发展时间', '1-8分钟', '风味影响', '烘焙阶段'],
                'references': ['烘焙工艺学']
            },
            {
                'id': 'bean_density',
                'content': '咖啡豆密度影响烘焙特性。高密度豆需要更长的烘焙时间和更高的温度。密度受品种、海拔、成熟度影响。烘焙时需要根据密度调整参数。',
                'source': '咖啡物理化学',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['豆密度', '烘焙特性', '品种', '海拔', '成熟度'],
                'references': ['咖啡物理化学研究']
            },
            {
                'id': 'roast_defects',
                'content': '常见烘焙缺陷包括：烤焦(温度过高)、烤不熟(温度过低)、烘焙不均(搅拌不足)、过度发展(时间过长)。每种缺陷都有其特征和避免方法。',
                'source': '烘焙质量控制',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['烘焙缺陷', '烤焦', '烤不熟', '不均', '过度发展'],
                'references': ['烘焙质量控制手册']
            },
            {
                'id': 'cooling_process',
                'content': '烘焙后的冷却过程同样重要。应快速降温至室温，停止继续发展。使用风冷或水冷方式，但要避免过度冷却导致回潮。',
                'source': '烘焙后处理',
                'confidence': 0.89,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['冷却过程', '快速降温', '风冷', '水冷', '回潮'],
                'references': ['烘焙后处理指南']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in roasting_knowledge:
            knowledge_item = KnowledgeItem(
                id=item_data['id'],
                content=item_data['content'],
                source=item_data['source'],
                confidence=item_data['confidence'],
                quality=item_data['quality'],
                timestamp=datetime.now(),
                tags=item_data['tags'],
                references=item_data['references'],
                verified=True
            )
            self.add_knowledge_item(knowledge_item)
        
        logger.info(f"烘焙专家知识库初始化完成，共{len(roasting_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理烘焙相关查询"""
        start_time = datetime.now()
        
        try:
            # 搜索相关知识
            relevant_knowledge = self.search_knowledge(query, limit=10)
            
            # 生成专业回答
            response_content = self._generate_response(query, relevant_knowledge, context)
            
            # 提取推荐建议
            recommendations = self._extract_recommendations(query, relevant_knowledge, context)
            
            # 检查警告
            warnings = self._check_warnings(query, relevant_knowledge, context)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            response = ExpertResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=response_content,
                confidence=self._calculate_confidence(relevant_knowledge),
                knowledge_items=relevant_knowledge,
                recommendations=recommendations,
                warnings=warnings,
                processing_time=response_time
            )
            
            return response
            
        except Exception as e:
            logger.error(f"烘焙专家处理查询失败: {e}")
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ExpertResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"抱歉，处理您的查询时出现错误: {str(e)}",
                confidence=0.0,
                processing_time=response_time
            )
    
    def _generate_response(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """生成专业回答"""
        query_lower = query.lower()
        
        # 根据查询类型生成回答
        if any(keyword in query_lower for keyword in ['烘焙程度', 'roast level', '浅烘', '深烘', '中烘']):
            return self._handle_roast_level_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['温度', 'temperature', '曲线', 'curve']):
            return self._handle_temperature_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['一爆', '二爆', 'first crack', 'second crack']):
            return self._handle_crack_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['发展', 'development', '时间', 'time']):
            return self._handle_development_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['缺陷', 'defect', '问题', 'problem']):
            return self._handle_defect_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_roast_level_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理烘焙程度查询"""
        response = "关于咖啡烘焙程度，我来为您详细说明：\n\n"
        
        # 查找烘焙程度相关知识
        level_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                          ['浅度烘焙', '中度烘焙', '深度烘焙'])]
        
        for item in level_knowledge:
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "烘焙程度选择建议：\n"
        response += "1. 浅度烘焙 - 突出产区特色和酸质\n"
        response += "2. 中度烘焙 - 平衡酸甜，适合日常饮用\n"
        response += "3. 深度烘焙 - 浓郁醇厚，适合意式浓缩\n"
        response += "4. 根据冲煮方法调整烘焙程度\n"
        response += "5. 考虑个人风味偏好\n"
        
        return response
    
    def _handle_temperature_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理温度查询"""
        response = "关于烘焙温度控制，我来为您详细解释：\n\n"
        
        # 查找温度相关知识
        temp_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                         ['温度曲线', '干燥', '梅纳反应', '发展阶段'])]
        
        for item in temp_knowledge:
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "温度控制要点：\n"
        response += "1. 干燥阶段(室温-150°C): 去除水分，升温速率5-10°C/分钟\n"
        response += "2. 梅纳反应阶段(150-200°C): 产生香气和颜色，升温速率3-5°C/分钟\n"
        response += "3. 发展阶段(200-230°C): 控制发展时间，升温速率1-3°C/分钟\n"
        response += "4. 避免温度急剧变化\n"
        response += "5. 根据豆子特性调整升温曲线\n"
        
        return response
    
    def _handle_crack_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理爆裂查询"""
        response = "关于咖啡烘焙爆裂，我来为您详细解释：\n\n"
        
        # 查找爆裂相关知识
        crack_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                          ['一爆', '二爆'])]
        
        for item in crack_knowledge:
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "爆裂阶段指导：\n"
        response += "1. 监听爆裂声音 - 一爆声音密集，二爆声音更响亮\n"
        response += "2. 观察豆子颜色 - 一爆时颜色变深，二爆时接近深棕色\n"
        response += "3. 控制发展时间 - 一爆后根据目标烘焙度决定发展时间\n"
        response += "4. 避免过度烘焙 - 超过二爆会导致烧焦\n"
        response += "5. 记录爆裂时间 - 建立个人烘焙档案\n"
        
        return response
    
    def _handle_development_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理发展查询"""
        response = "关于烘焙发展时间，我来为您详细说明：\n\n"
        
        # 查找发展相关知识
        dev_knowledge = [k for k in knowledge if '发展时间' in k.tags]
        
        if dev_knowledge:
            for item in dev_knowledge:
                response += f"**发展时间**\n{item.content}\n\n"
        
        response += "发展时间控制指南：\n"
        response += "1. 浅度烘焙: 一爆后1-3分钟\n"
        response += "2. 中度烘焙: 一爆后3-5分钟\n"
        response += "3. 深度烘焙: 一爆后5-8分钟\n"
        response += "4. 发展时间影响风味复杂度\n"
        response += "5. 过度发展会产生烧焦味\n"
        response += "6. 发展不足会导致生味和酸涩\n"
        
        return response
    
    def _handle_defect_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理缺陷查询"""
        response = "关于烘焙缺陷识别，我来为您详细说明：\n\n"
        
        # 查找缺陷相关知识
        defect_knowledge = [k for k in knowledge if '烘焙缺陷' in k.tags]
        
        if defect_knowledge:
            for item in defect_knowledge:
                response += f"**常见缺陷**\n{item.content}\n\n"
        
        response += "缺陷预防措施：\n"
        response += "1. 烤焦 - 降低温度，缩短时间\n"
        response += "2. 烤不熟 - 提高温度，延长时间\n"
        response += "3. 烘焙不均 - 加强搅拌，确保受热均匀\n"
        response += "4. 过度发展 - 提前结束烘焙\n"
        response += "5. 定期校准设备\n"
        response += "6. 记录烘焙参数\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为烘焙专家，我很高兴为您解答关于咖啡烘焙的问题。\n\n"
        
        if knowledge:
            response += "基于我的烘焙专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的烘焙问题，请详细描述，我会为您提供专业的指导和建议。"
        
        return response
    
    def calculate_roast_profile(self, bean_type: str, target_roast: str, 
                               batch_size: float = 1000) -> Dict[str, Any]:
        """计算烘焙曲线"""
        base_profiles = {
            'light': {
                'drying_temp': 180,
                'maillard_temp': 195,
                'development_temp': 205,
                'total_time': 8,
                'development_time': 2
            },
            'medium': {
                'drying_temp': 190,
                'maillard_temp': 210,
                'development_temp': 220,
                'total_time': 12,
                'development_time': 4
            },
            'dark': {
                'drying_temp': 200,
                'maillard_temp': 225,
                'development_temp': 235,
                'total_time': 15,
                'development_time': 6
            }
        }
        
        if target_roast not in base_profiles:
            raise ValueError(f"不支持的烘焙程度: {target_roast}")
        
        profile = base_profiles[target_roast].copy()
        
        # 根据豆子类型调整
        if bean_type.lower() in ['arabica', '阿拉比卡']:
            profile['temp_adjustment'] = -5
            profile['time_adjustment'] = 0.5
        elif bean_type.lower() in ['robusta', '罗布斯塔']:
            profile['temp_adjustment'] = 10
            profile['time_adjustment'] = -0.5
        
        # 根据批量调整
        if batch_size > 2000:
            profile['temp_adjustment'] += 10
            profile['time_adjustment'] += 1
        
        return profile
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem], 
                               context: Dict = None) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['新手', '初学', 'beginner']):
            recommendations.append("建议从中度烘焙开始练习")
            recommendations.append("使用小批量烘焙(500-1000g)")
            recommendations.append("记录每次烘焙的参数和结果")
        
        if any(keyword in query_lower for keyword in ['温度', 'temperature']):
            recommendations.append("使用精确的温度计监控烘焙过程")
            recommendations.append("避免急剧的温度变化")
            recommendations.append("根据豆子特性调整升温曲线")
        
        if context and 'equipment' in context:
            equipment = context['equipment']
            recommendations.append(f"针对{equipment}设备，建议调整参数")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem], 
                       context: Dict = None) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['高温', 'high temp', '240', '250']):
            warnings.append("避免超过240°C的高温，可能导致烧焦")
        
        if any(keyword in query_lower for keyword in ['二爆', 'second crack']):
            warnings.append("超过二爆会严重损害咖啡风味")
        
        if context and 'batch_size' in context:
            batch_size = context['batch_size']
            if batch_size > 5000:
                warnings.append("大批量烘焙需要更精确的温度控制")
        
        return warnings
    
    def _calculate_confidence(self, knowledge: List[KnowledgeItem]) -> float:
        """计算回答置信度"""
        if not knowledge:
            return 0.3
        
        # 基于知识项数量和质量计算置信度
        avg_confidence = sum(item.confidence for item in knowledge) / len(knowledge)
        quality_bonus = sum(1 for item in knowledge if item.quality == KnowledgeQuality.HIGH) * 0.1
        
        return min(avg_confidence + quality_bonus, 1.0)
    
    def get_expertise_areas(self) -> List[str]:
        """获取专业领域列表"""
        return [
            "烘焙程度控制",
            "温度曲线管理",
            "烘焙设备操作",
            "爆裂阶段识别",
            "发展时间控制",
            "烘焙缺陷诊断",
            "烘焙曲线设计",
            "豆子密度分析",
            "烘焙质量评估",
            "烘焙参数优化"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        content = knowledge_item.content
        
        # 检查温度范围的合理性
        import re
        temp_matches = re.findall(r'(\d+)[°℃]C', content)
        for temp in temp_matches:
            temp_val = int(temp)
            if temp_val < 100 or temp_val > 300:
                return False, f"温度值{temp}°C超出合理范围(100-300°C)"
        
        # 检查时间范围的合理性
        time_matches = re.findall(r'(\d+)(?:-(\d+))?\s*分钟', content)
        for match in time_matches:
            start_time = int(match[0])
            end_time = int(match[1]) if match[1] else start_time
            
            if start_time < 1 or end_time > 30:
                return False, f"时间值{start_time}-{end_time}分钟超出合理范围(1-30分钟)"
        
        return True, "验证通过"