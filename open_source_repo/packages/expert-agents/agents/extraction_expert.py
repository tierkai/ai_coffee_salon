"""
萃取专家智能体
负责咖啡萃取方法、参数控制、萃取理论等专业知识
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import math

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class ExtractionExpertAgent(BaseExpertAgent):
    """萃取专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="extraction_expert_001",
            name="萃取专家",
            specialty="咖啡萃取技术",
            level=ExpertLevel.EXPERT
        )
        
        # 萃取参数标准范围
        self.extraction_parameters = {
            'espresso': {
                'ratio_range': (1:1.5, 1:2.5),
                'time_range': (20, 35),
                'temperature_range': (90, 96),
                'pressure_range': (8, 9)
            },
            'pour_over': {
                'ratio_range': (1:15, 1:17),
                'time_range': (180, 300),
                'temperature_range': (92, 96),
                'grind_size': (medium_fine, medium_coarse)
            },
            'french_press': {
                'ratio_range': (1:12, 1:15),
                'time_range': (240, 360),
                'temperature_range': (93, 96),
                'grind_size': (coarse, medium_coarse)
            }
        }
    
    def _initialize_knowledge_base(self):
        """初始化萃取专业知识库"""
        extraction_knowledge = [
            {
                'id': 'extraction_theory',
                'content': '咖啡萃取是用水溶解咖啡中可溶性物质的过程。理想萃取率在18-22%之间。过度萃取会产生苦味，萃取不足会产生酸味。萃取过程受粉水比、时间、温度、研磨度等因素影响。',
                'source': 'SCA萃取理论',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['萃取理论', '18-22%', '过度萃取', '萃取不足', '萃取率'],
                'references': ['SCA萃取指南']
            },
            {
                'id': 'espresso_extraction',
                'content': '意式浓缩萃取使用高压热水快速通过咖啡粉饼。标准参数：粉水比1:2，时间25-30秒，温度90-96°C，压力9巴。萃取出的咖啡体积约为粉量的2倍。',
                'source': '意式咖啡技术手册',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['意式浓缩', '高压', '1:2', '25-30秒', '9巴'],
                'references': ['意式咖啡技术手册']
            },
            {
                'id': 'pour_over_extraction',
                'content': '手冲咖啡通过重力作用让热水缓慢通过咖啡粉层。关键参数：粉水比1:15-17，萃取时间2-4分钟，水温92-96°C。注水方式影响萃取均匀性。',
                'source': '手冲咖啡指南',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['手冲', '重力', '1:15-17', '2-4分钟', '注水方式'],
                'references': ['手冲咖啡指南']
            },
            {
                'id': 'grind_size_impact',
                'content': '研磨度直接影响萃取速度。细研磨增加表面积，萃取更快；粗研磨减少表面积，萃取更慢。不同萃取方法需要不同的研磨度：意式浓缩需要细研磨，手冲需要中度研磨，法压需要粗研磨。',
                'source': '咖啡研磨学',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['研磨度', '表面积', '萃取速度', '细研磨', '粗研磨'],
                'references': ['咖啡研磨学研究']
            },
            {
                'id': 'water_temperature',
                'content': '水温影响萃取效率。理想水温在90-96°C之间。水温过低萃取不足，产生酸味；水温过高过度萃取，产生苦味。不同烘焙程度的咖啡需要不同水温：浅烘需要更高水温，深烘需要较低水温。',
                'source': '萃取工程学',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['水温', '90-96°C', '萃取效率', '浅烘', '深烘'],
                'references': ['萃取工程学']
            },
            {
                'id': 'extraction_time',
                'content': '萃取时间是影响最终风味的重要因素。萃取时间过长会导致过度萃取，时间过短会导致萃取不足。每种萃取方法都有其理想的萃取时间范围，需要根据咖啡豆特性和个人喜好调整。',
                'source': '萃取时间研究',
                'confidence': 0.91,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['萃取时间', '过长', '过短', '理想时间', '调整'],
                'references': ['萃取时间研究报告']
            },
            {
                'id': 'extraction_yield',
                'content': '萃取率是指溶解在咖啡中的干物质百分比。理想萃取率为18-22%。可以使用折射仪测量萃取率。通过调整研磨度、时间、水温等参数来控制萃取率。',
                'source': 'SCA萃取测量',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['萃取率', '18-22%', '折射仪', '测量', '调整参数'],
                'references': ['SCA萃取测量标准']
            },
            {
                'id': 'channeling_effect',
                'content': '通道效应是指水流在咖啡粉饼中形成不均匀通道的现象，导致部分区域过度萃取，部分区域萃取不足。均匀填粉、适当压粉和正确的注水方式可以减少通道效应。',
                'source': '萃取流体力学',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['通道效应', '不均匀', '填粉', '压粉', '注水'],
                'references': ['萃取流体力学研究']
            },
            {
                'id': 'extraction_phases',
                'content': '咖啡萃取可以分为三个阶段：1)初期快速萃取(前30%):主要提取酸质和香气；2)中期平衡萃取(中间40%):酸甜平衡；3)后期慢速萃取(最后30%):主要提取苦味和醇厚感。',
                'source': '萃取阶段分析',
                'confidence': 0.89,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['萃取阶段', '初期', '中期', '后期', '酸质', '香气', '苦味'],
                'references': ['萃取阶段分析报告']
            },
            {
                'id': 'turbulence_control',
                'content': '湍流控制是手冲咖啡中的关键技术。适度的湍流有助于萃取均匀，但过度湍流会破坏粉层结构。注水时应保持稳定的水流和适当的扰动程度。',
                'source': '手冲技术研究',
                'confidence': 0.88,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['湍流控制', '手冲', '萃取均匀', '注水', '水流'],
                'references': ['手冲技术研究报告']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in extraction_knowledge:
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
        
        logger.info(f"萃取专家知识库初始化完成，共{len(extraction_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理萃取相关查询"""
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
            logger.error(f"萃取专家处理查询失败: {e}")
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
        if any(keyword in query_lower for keyword in ['espresso', '意式', '浓缩']):
            return self._handle_espresso_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['手冲', 'pour over', 'v60', 'chemex']):
            return self._handle_pour_over_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['法压', 'french press', ' plunger']):
            return self._handle_french_press_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['萃取率', 'extraction yield', 'tds']):
            return self._handle_extraction_yield_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['研磨度', 'grind size', '细度']):
            return self._handle_grind_size_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['过萃', 'under', '苦', '酸']):
            return self._handle_extraction_problem_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_espresso_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理意式浓缩查询"""
        response = "关于意式浓缩萃取，我来为您详细说明：\n\n"
        
        # 查找意式相关知识
        espresso_knowledge = [k for k in knowledge if '意式浓缩' in k.tags]
        
        if espresso_knowledge:
            for item in espresso_knowledge:
                response += f"**意式浓缩技术**\n{item.content}\n\n"
        
        response += "意式浓缩关键参数：\n"
        response += "1. 粉水比：1:2 (18g咖啡粉 -> 36g咖啡液)\n"
        response += "2. 萃取时间：25-30秒\n"
        response += "3. 水温：90-96°C\n"
        response += "4. 压力：9巴\n"
        response += "5. 研磨度：细研磨\n\n"
        
        response += "萃取调整指南：\n"
        response += "• 萃取过快 → 调细研磨度\n"
        response += "• 萃取过慢 → 调粗研磨度\n"
        response += "• 味道太酸 → 延长萃取时间\n"
        response += "• 味道太苦 → 缩短萃取时间\n"
        
        return response
    
    def _handle_pour_over_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理手冲查询"""
        response = "关于手冲咖啡萃取，我来为您详细解释：\n\n"
        
        # 查找手冲相关知识
        pour_over_knowledge = [k for k in knowledge if '手冲' in k.tags]
        
        if pour_over_knowledge:
            for item in pour_over_knowledge:
                response += f"**手冲技术**\n{item.content}\n\n"
        
        response += "手冲咖啡参数：\n"
        response += "1. 粉水比：1:15-17\n"
        response += "2. 萃取时间：2-4分钟\n"
        response += "3. 水温：92-96°C\n"
        response += "4. 研磨度：中度\n"
        response += "5. 注水方式：分段注水\n\n"
        
        response += "注水技巧：\n"
        response += "• 第一段：闷蒸30-45秒\n"
        response += "• 第二段：中心注水，避免接触滤纸\n"
        response += "• 保持水流稳定，控制湍流\n"
        response += "• 总注水量分3-4次完成\n"
        
        return response
    
    def _handle_french_press_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理法压查询"""
        response = "关于法式压滤壶萃取，我来为您详细说明：\n\n"
        
        response += "法压壶萃取参数：\n"
        response += "1. 粉水比：1:12-15\n"
        response += "2. 萃取时间：4-6分钟\n"
        response += "3. 水温：93-96°C\n"
        response += "4. 研磨度：粗研磨\n\n"
        
        response += "法压壶操作步骤：\n"
        response += "1. 预热法压壶\n"
        response += "2. 加入咖啡粉，缓慢倒入热水\n"
        response += "3. 搅拌均匀，盖上盖子\n"
        response += "4. 静置4-6分钟\n"
        response += "5. 缓慢按压滤网，倒出咖啡\n\n"
        
        response += "注意事项：\n"
        response += "• 避免过度按压，以免产生细粉\n"
        response += "• 萃取完成后立即分离咖啡渣\n"
        response += "• 不要让咖啡在壶中停留过久\n"
        
        return response
    
    def _handle_extraction_yield_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理萃取率查询"""
        response = "关于咖啡萃取率，我来为您详细解释：\n\n"
        
        # 查找萃取率相关知识
        yield_knowledge = [k for k in knowledge if '萃取率' in k.tags]
        
        if yield_knowledge:
            for item in yield_knowledge:
                response += f"**萃取率概念**\n{item.content}\n\n"
        
        response += "萃取率参考标准：\n"
        response += "• 理想范围：18-22%\n"
        response += "• 萃取不足：< 18% (酸味突出)\n"
        response += "• 萃取过度：> 22% (苦味突出)\n\n"
        
        response += "测量萃取率：\n"
        response += "1. 使用折射仪测量TDS(总溶解固体)\n"
        response += "2. 记录咖啡粉重量和咖啡液重量\n"
        response += "3. 计算公式：萃取率 = (TDS × 咖啡液重量) / 咖啡粉重量\n"
        response += "4. 定期测量，优化萃取参数\n"
        
        return response
    
    def _handle_grind_size_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理研磨度查询"""
        response = "关于咖啡研磨度，我来为您详细说明：\n\n"
        
        # 查找研磨度相关知识
        grind_knowledge = [k for k in knowledge if '研磨度' in k.tags]
        
        if grind_knowledge:
            for item in grind_knowledge:
                response += f"**研磨度影响**\n{item.content}\n\n"
        
        response += "不同萃取方法的研磨度：\n"
        response += "• 意式浓缩：细研磨 (食盐颗粒大小)\n"
        response += "• 手冲：中度 (细砂糖大小)\n"
        response += "• 法压：粗研磨 (粗砂糖大小)\n"
        response += "• 土耳其咖啡：极细研磨 (面粉大小)\n\n"
        
        response += "研磨度调整原则：\n"
        response += "• 萃取太快 → 调细研磨度\n"
        response += "• 萃取太慢 → 调粗研磨度\n"
        response += "• 味道太酸 → 调细研磨度\n"
        response += "• 味道太苦 → 调粗研磨度\n"
        
        return response
    
    def _handle_extraction_problem_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理萃取问题查询"""
        response = "关于咖啡萃取问题，我来为您诊断和解决：\n\n"
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['过萃', '苦', 'bitter']):
            response += "**过度萃取问题**\n"
            response += "症状：咖啡味道苦涩、厚重\n"
            response += "原因：萃取时间过长、研磨度太细、水温过高\n"
            response += "解决方案：\n"
            response += "• 调粗研磨度\n"
            response += "• 缩短萃取时间\n"
            response += "• 降低水温2-3°C\n"
            response += "• 减少粉量或增加水量\n\n"
        
        if any(keyword in query_lower for keyword in ['萃取不足', '酸', 'sour', 'under']):
            response += "**萃取不足问题**\n"
            response += "症状：咖啡味道酸涩、寡淡\n"
            response += "原因：萃取时间过短、研磨度太粗、水温过低\n"
            response += "解决方案：\n"
            response += "• 调细研磨度\n"
            response += "• 延长萃取时间\n"
            response += "• 提高水温2-3°C\n"
            response += "• 增加粉量或减少水量\n\n"
        
        if any(keyword in query_lower for keyword in ['不均', 'channeling', '通道']):
            response += "**萃取不均问题**\n"
            response += "症状：咖啡味道不稳定，有杂味\n"
            response += "原因：通道效应、填粉不均、压粉不当\n"
            response += "解决方案：\n"
            response += "• 改善填粉技术\n"
            response += "• 均匀压粉\n"
            response += "• 调整注水方式\n"
            response += "• 检查设备密封性\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为萃取专家，我很高兴为您解答关于咖啡萃取的问题。\n\n"
        
        if knowledge:
            response += "基于我的萃取专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的萃取问题，请详细描述，我会为您提供专业的指导和建议。"
        
        return response
    
    def calculate_extraction_parameters(self, method: str, bean_type: str = None, 
                                      roast_level: str = None) -> Dict[str, Any]:
        """计算萃取参数"""
        if method not in self.extraction_parameters:
            raise ValueError(f"不支持的萃取方法: {method}")
        
        params = self.extraction_parameters[method].copy()
        
        # 根据豆子类型调整
        if bean_type:
            if bean_type.lower() in ['arabica', '阿拉比卡']:
                params['ratio_adjustment'] = -0.5  # 稍微增加粉量
                params['time_adjustment'] = 5      # 延长萃取时间
            elif bean_type.lower() in ['robusta', '罗布斯塔']:
                params['ratio_adjustment'] = 0.5   # 稍微减少粉量
                params['time_adjustment'] = -5     # 缩短萃取时间
        
        # 根据烘焙程度调整
        if roast_level:
            if roast_level.lower() in ['light', '浅烘']:
                params['temp_adjustment'] = 2      # 提高水温
                params['time_adjustment'] = 10     # 延长萃取时间
            elif roast_level.lower() in ['dark', '深烘']:
                params['temp_adjustment'] = -2     # 降低水温
                params['time_adjustment'] = -10    # 缩短萃取时间
        
        return params
    
    def diagnose_extraction_issues(self, observed_time: float, observed_volume: float,
                                 target_time: float, target_volume: float,
                                 taste_notes: List[str]) -> Dict[str, Any]:
        """诊断萃取问题"""
        issues = []
        solutions = []
        
        # 时间诊断
        time_ratio = observed_time / target_time
        if time_ratio < 0.8:
            issues.append("萃取时间过短")
            solutions.append("调细研磨度或延长萃取时间")
        elif time_ratio > 1.2:
            issues.append("萃取时间过长")
            solutions.append("调粗研磨度或缩短萃取时间")
        
        # 体积诊断
        volume_ratio = observed_volume / target_volume
        if volume_ratio < 0.8:
            issues.append("咖啡液体积不足")
            solutions.append("增加粉量或减少水量")
        elif volume_ratio > 1.2:
            issues.append("咖啡液体积过多")
            solutions.append("减少粉量或增加水量")
        
        # 风味诊断
        if any(note in taste_notes for note in ['酸', 'sour', '酸涩']):
            issues.append("萃取不足")
            solutions.extend(["调细研磨度", "延长萃取时间", "提高水温"])
        
        if any(note in taste_notes for note in ['苦', 'bitter', '苦涩']):
            issues.append("过度萃取")
            solutions.extend(["调粗研磨度", "缩短萃取时间", "降低水温"])
        
        return {
            'issues': issues,
            'solutions': solutions,
            'severity': 'high' if len(issues) > 2 else 'medium' if len(issues) > 0 else 'low',
            'recommendations': solutions[:3]  # 返回前3个最重要的建议
        }
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem], 
                               context: Dict = None) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['新手', '初学', 'beginner']):
            recommendations.append("建议从手冲咖啡开始练习萃取")
            recommendations.append("使用电子秤和计时器精确控制参数")
            recommendations.append("记录每次萃取的参数和结果")
        
        if any(keyword in query_lower for keyword in ['espresso', '意式']):
            recommendations.append("投资一台稳定的意式咖啡机")
            recommendations.append("练习填粉和压粉技术")
            recommendations.append("定期清洁和维护设备")
        
        if context and 'method' in context:
            method = context['method']
            recommendations.append(f"针对{method}萃取方法，建议使用相应粒度的磨豆机")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem], 
                       context: Dict = None) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['高温', '100', '沸腾']):
            warnings.append("避免使用100°C的沸水，会过度萃取咖啡")
        
        if any(keyword in query_lower for keyword in ['极细', '粉末', 'dust']):
            warnings.append("过细的研磨度可能导致过度萃取和通道效应")
        
        if context and 'pressure' in context:
            pressure = context['pressure']
            if pressure > 12:
                warnings.append("过高的压力可能损坏设备和影响风味")
        
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
            "意式浓缩萃取",
            "手冲咖啡技术",
            "萃取参数控制",
            "萃取率测量",
            "研磨度调节",
            "萃取问题诊断",
            "萃取理论",
            "萃取均匀性",
            "水质对萃取的影响",
            "萃取设备优化"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        content = knowledge_item.content
        
        # 检查温度范围的合理性
        import re
        temp_matches = re.findall(r'(\d+)[°℃]C', content)
        for temp in temp_matches:
            temp_val = int(temp)
            if temp_val < 70 or temp_val > 105:
                return False, f"温度值{temp_val}°C超出合理范围(70-105°C)"
        
        # 检查时间范围的合理性
        time_matches = re.findall(r'(\d+)(?:-(\d+))?\s*秒', content)
        for match in time_matches:
            start_time = int(match[0])
            end_time = int(match[1]) if match[1] else start_time
            
            if start_time < 10 or end_time > 600:
                return False, f"时间值{start_time}-{end_time}秒超出合理范围(10-600秒)"
        
        # 检查比例的合理性
        ratio_matches = re.findall(r'1:(\d+(?:\.\d+)?)', content)
        for ratio in ratio_matches:
            ratio_val = float(ratio)
            if ratio_val < 1 or ratio_val > 30:
                return False, f"粉水比1:{ratio_val}超出合理范围(1:1-1:30)"
        
        return True, "验证通过"