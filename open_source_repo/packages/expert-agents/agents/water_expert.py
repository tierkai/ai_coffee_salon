"""
水质专家智能体
负责水质对咖啡的影响、矿物成分等专业知识
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import math

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class WaterExpertAgent(BaseExpertAgent):
    """水质专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="water_expert_001",
            name="水质专家",
            specialty="咖啡用水水质",
            level=ExpertLevel.EXPERT
        )
        
        # SCA推荐的水质标准
        self.sca_water_standards = {
            'tds': (75, 250),           # ppm
            'calcium_hardness': (17, 85),  # ppm as CaCO3
            'alkalinity': (40, 70),     # ppm as CaCO3
            'ph': (6.5, 8.5),
            'sodium': (10, 30),         # ppm
            'chloride': (5, 30),        # ppm
            'sulfate': (5, 30)          # ppm
        }
        
        # 常见水质问题
        self.water_problems = {
            'scale_formation': {
                'symptoms': ['设备结垢', '萃取不均', '味道平淡'],
                'causes': ['钙硬度过高', '总溶解固体过高'],
                'solutions': ['使用软水', '安装软水器', '定期除垢']
            },
            'corrosion': {
                'symptoms': ['设备腐蚀', '金属味', '设备损坏'],
                'causes': ['pH过低', '氯离子过高', '总溶解固体过低'],
                'solutions': ['调整pH', '更换水源', '使用反渗透水']
            },
            'poor_extraction': {
                'symptoms': ['萃取不足', '酸质突出', '味道平淡'],
                'causes': ['总溶解固体过低', '钙硬度过低', 'pH不当'],
                'solutions': ['添加矿物质', '调整pH', '使用SCA标准水']
            }
        }
    
    def _initialize_knowledge_base(self):
        """初始化水质专业知识库"""
        water_knowledge = [
            {
                'id': 'water_importance',
                'content': '水是咖啡萃取的主要媒介，占咖啡成分的98-99%。水质直接影响咖啡的风味、萃取率和最终品质。理想的水质应该平衡矿物质含量，不会过度萃取或萃取不足咖啡中的可溶性物质。',
                'source': 'SCA水质指南',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['水质重要性', '98-99%', '萃取媒介', '风味影响'],
                'references': ['SCA水质指南']
            },
            {
                'id': 'sca_water_standards',
                'content': 'SCA推荐的水质标准：TDS 75-250 ppm，钙硬度17-85 ppm，碱度40-70 ppm，pH 6.5-8.5。这些参数确保水既能有效萃取咖啡，又不会对设备造成损害。',
                'source': 'SCA水质标准',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['SCA标准', 'TDS', '钙硬度', '碱度', 'pH'],
                'references': ['SCA水质标准文档']
            },
            {
                'id': 'tds_impact',
                'content': '总溶解固体(TDS)影响水的萃取能力。TDS过低(<75 ppm)会导致过度萃取，产生苦涩味；TDS过高(>250 ppm)会导致萃取不足，产生酸味。理想的TDS范围能确保平衡的萃取。',
                'source': '水质对萃取的影响研究',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['TDS影响', '过度萃取', '萃取不足', '平衡萃取'],
                'references': ['水质萃取影响研究']
            },
            {
                'id': 'calcium_hardness',
                'content': '钙硬度影响水的萃取能力和设备保护。钙硬度17-85 ppm能提供足够的萃取能力，同时不会造成过度结垢。钙硬度不足会导致萃取不足，钙硬度太高会导致严重结垢。',
                'source': '水硬度研究',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['钙硬度', '17-85 ppm', '萃取能力', '设备保护', '结垢'],
                'references': ['水硬度研究报告']
            },
            {
                'id': 'alkalinity_role',
                'content': '碱度是水抵抗pH变化的能力，由碳酸氢盐形成。理想碱度40-70 ppm能提供稳定的pH环境，有助于平衡萃取。碱度过高会抑制萃取，碱度过低会导致pH不稳定。',
                'source': '水化学研究',
                'confidence': 0.91,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['碱度', '40-70 ppm', 'pH稳定', '平衡萃取'],
                'references': ['水化学研究']
            },
            {
                'id': 'ph_effects',
                'content': 'pH值影响水的萃取能力和咖啡的风味表现。理想pH 6.5-8.5能确保有效的萃取和良好的风味。pH过低会产生酸味，pH过高会影响萃取效率。',
                'source': 'pH对咖啡萃取的影响',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['pH影响', '6.5-8.5', '酸味', '萃取效率'],
                'references': ['pH影响研究报告']
            },
            {
                'id': 'mineral_balance',
                'content': '水的矿物质平衡对咖啡风味至关重要。钙和镁离子提供萃取能力，碳酸氢盐提供碱度，钠和氯离子影响风味。理想的矿物质平衡能带来清晰、明亮、甜感平衡的咖啡。',
                'source': '矿物质平衡研究',
                'confidence': 0.89,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['矿物质平衡', '钙镁离子', '碳酸氢盐', '风味表现'],
                'references': ['矿物质平衡研究']
            },
            {
                'id': 'water_treatment',
                'content': '常见的水处理方法包括：反渗透(RO)、去离子、软化、活性炭过滤等。RO水需要重新添加矿物质以达到SCA标准。软化水适合减少结垢，但需要监测钠含量。',
                'source': '水处理技术',
                'confidence': 0.88,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['水处理', '反渗透', '去离子', '软化', '活性炭'],
                'references': ['水处理技术手册']
            },
            {
                'id': 'bottled_vs_tap',
                'content': '瓶装水vs自来水：瓶装水通常更稳定，但需要检查是否达到SCA标准。自来水因地区而异，需要定期检测。许多瓶装水的TDS过低，需要添加矿物质。',
                'source': '水源比较研究',
                'confidence': 0.87,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['瓶装水', '自来水', '稳定性', 'TDS检测'],
                'references': ['水源比较研究']
            },
            {
                'id': 'water_testing',
                'content': '水质检测应包括：TDS、pH、钙硬度、碱度、钠、氯化物、硫酸盐等。建议每3-6个月检测一次，或在发现萃取问题时立即检测。使用专业水质检测工具或送检实验室。',
                'source': '水质检测指南',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['水质检测', 'TDS检测', '定期检测', '专业工具'],
                'references': ['水质检测指南']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in water_knowledge:
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
        
        logger.info(f"水质专家知识库初始化完成，共{len(water_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理水质相关查询"""
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
            logger.error(f"水质专家处理查询失败: {e}")
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
        if any(keyword in query_lower for keyword in ['标准', 'standard', 'sca']):
            return self._handle_water_standards_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['tds', '总溶解固体']):
            return self._handle_tds_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['硬度', 'hardness', '钙', 'calcium']):
            return self._handle_hardness_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['ph', '酸碱度']):
            return self._handle_ph_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['处理', 'treatment', '过滤', 'filter']):
            return self._handle_water_treatment_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['检测', 'test', '测量', 'measure']):
            return self._handle_water_testing_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_water_standards_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理水质标准查询"""
        response = "关于咖啡用水水质标准，我来为您详细说明：\n\n"
        
        # 查找SCA标准相关知识
        standards_knowledge = [k for k in knowledge if 'SCA标准' in k.tags]
        
        if standards_knowledge:
            for item in standards_knowledge:
                response += f"**SCA水质标准**\n{item.content}\n\n"
        
        response += "SCA推荐水质参数：\n"
        for param, (min_val, max_val) in self.sca_water_standards.items():
            param_names = {
                'tds': '总溶解固体(TDS)',
                'calcium_hardness': '钙硬度',
                'alkalinity': '碱度',
                'ph': 'pH值',
                'sodium': '钠',
                'chloride': '氯化物',
                'sulfate': '硫酸盐'
            }
            response += f"• {param_names.get(param, param)}: {min_val}-{max_val} ppm\n"
        
        response += "\n为什么这些标准重要：\n"
        response += "• 确保有效的咖啡萃取\n"
        response += "• 保护咖啡设备\n"
        response += "• 获得最佳的风味表现\n"
        response += "• 避免设备结垢和腐蚀\n"
        
        return response
    
    def _handle_tds_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理TDS查询"""
        response = "关于总溶解固体(TDS)，我来为您详细解释：\n\n"
        
        # 查找TDS相关知识
        tds_knowledge = [k for k in knowledge if 'TDS' in k.tags]
        
        if tds_knowledge:
            for item in tds_knowledge:
                response += f"**TDS影响**\n{item.content}\n\n"
        
        response += "TDS参考标准：\n"
        response += "• 理想范围：75-250 ppm\n"
        response += "• 过低(<75 ppm)：过度萃取，苦涩味\n"
        response += "• 过高(>250 ppm)：萃取不足，酸味\n\n"
        
        response += "TDS对咖啡的影响：\n"
        response += "1. 萃取能力：TDS决定了水的萃取能力\n"
        response += "2. 风味平衡：影响酸甜苦的平衡\n"
        response += "3. 口感：影响咖啡的醇厚感和清晰度\n"
        response += "4. 设备影响：影响设备结垢和腐蚀\n\n"
        
        response += "调整TDS的方法：\n"
        response += "• TDS过低：添加矿物质或使用SCA配方水\n"
        response += "• TDS过高：使用反渗透水或软化水\n"
        response += "• 定期检测TDS变化\n"
        
        return response
    
    def _handle_hardness_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理硬度查询"""
        response = "关于水的硬度，我来为您详细说明：\n\n"
        
        # 查找硬度相关知识
        hardness_knowledge = [k for k in knowledge if '钙硬度' in k.tags]
        
        if hardness_knowledge:
            for item in hardness_knowledge:
                response += f"**钙硬度影响**\n{item.content}\n\n"
        
        response += "硬度分类和影响：\n"
        response += "• 软水(0-17 ppm)：萃取不足，设备腐蚀风险\n"
        response += "• 理想硬度(17-85 ppm)：最佳萃取，保护设备\n"
        response += "• 硬水(85-150 ppm)：萃取过度，结垢风险\n"
        response += "• 极硬水(>150 ppm)：严重结垢，萃取困难\n\n"
        
        response += "硬度的作用：\n"
        response += "1. 提供萃取所需的矿物质\n"
        response += "2. 影响咖啡的甜感和醇厚感\n"
        response += "3. 保护设备金属部件\n"
        response += "4. 防止过度萃取\n\n"
        
        response += "硬度过高/过低的解决方案：\n"
        response += "• 硬度过高：安装软水器或使用RO水\n"
        response += "• 硬度过低：添加钙镁矿物质\n"
        response += "• 定期检测和调整\n"
        
        return response
    
    def _handle_ph_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理pH查询"""
        response = "关于水的pH值，我来为您详细解释：\n\n"
        
        # 查找pH相关知识
        ph_knowledge = [k for k in knowledge if 'pH' in k.tags]
        
        if ph_knowledge:
            for item in ph_knowledge:
                response += f"**pH影响**\n{item.content}\n\n"
        
        response += "pH值参考标准：\n"
        response += "• 理想范围：6.5-8.5\n"
        response += "• 过低(<6.5)：酸性水，腐蚀设备，酸味突出\n"
        response += "• 过高(>8.5)：碱性水，萃取困难，苦味增加\n\n"
        
        response += "pH对咖啡的影响：\n"
        response += "1. 萃取效率：影响可溶性物质的溶解\n"
        response += "2. 风味表现：影响酸质的明亮度\n"
        response += "3. 设备保护：防止腐蚀和结垢\n"
        response += "4. 稳定性：影响水质的长期稳定性\n\n"
        
        response += "调整pH的方法：\n"
        response += "• pH过低：使用碱性滤材或添加碱性矿物质\n"
        response += "• pH过高：使用酸性滤材或添加酸性物质\n"
        response += "• 使用pH调节剂(谨慎使用)\n"
        
        return response
    
    def _handle_water_treatment_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理水处理查询"""
        response = "关于水处理方法，我来为您详细说明：\n\n"
        
        # 查找水处理相关知识
        treatment_knowledge = [k for k in knowledge if '水处理' in k.tags]
        
        if treatment_knowledge:
            for item in treatment_knowledge:
                response += f"**水处理技术**\n{item.content}\n\n"
        
        response += "常见水处理方法：\n\n"
        
        response += "1. **反渗透(RO)**\n"
        response += "   • 去除95-99%的杂质\n"
        response += "   • 产生纯净水，需要重新添加矿物质\n"
        response += "   • 适合严重污染的水源\n\n"
        
        response += "2. **去离子**\n"
        response += "   • 去除所有离子杂质\n"
        response += "   • 产生中性水，需要添加矿物质\n"
        response += "   • 适合实验室环境\n\n"
        
        response += "3. **软化**\n"
        response += "   • 去除钙镁离子\n"
        response += "   • 减少结垢，但增加钠含量\n"
        response += "   • 适合硬水地区\n\n"
        
        response += "4. **活性炭过滤**\n"
        response += "   • 去除氯气和有机物\n"
        response += "   • 改善口感和气味\n"
        response += "   • 不能去除矿物质\n\n"
        
        response += "选择建议：\n"
        response += "• 根据水源质量选择合适的处理方法\n"
        response += "• RO水需要添加SCA标准矿物质\n"
        response += "• 定期更换滤芯和维护设备\n"
        
        return response
    
    def _handle_water_testing_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理水质检测查询"""
        response = "关于水质检测，我来为您详细说明：\n\n"
        
        # 查找检测相关知识
        testing_knowledge = [k for k in knowledge if '水质检测' in k.tags]
        
        if testing_knowledge:
            for item in testing_knowledge:
                response += f"**水质检测**\n{item.content}\n\n"
        
        response += "需要检测的参数：\n"
        response += "1. **TDS(总溶解固体)** - 萃取能力指标\n"
        response += "2. **pH值** - 酸碱度\n"
        response += "3. **钙硬度** - 结垢风险\n"
        response += "4. **碱度** - pH稳定性\n"
        response += "5. **钠含量** - 风味影响\n"
        response += "6. **氯化物** - 腐蚀风险\n"
        response += "7. **硫酸盐** - 风味影响\n\n"
        
        response += "检测方法：\n"
        response += "• **家用测试套件** - 快速检测TDS、pH\n"
        response += "• **专业仪器** - 精确测量各项参数\n"
        response += "• **实验室检测** - 最准确，需要送检\n"
        response += "• **定期检测** - 建议每3-6个月一次\n\n"
        
        response += "检测时机：\n"
        response += "• 新安装设备时\n"
        response += "• 发现萃取问题时\n"
        response += "• 更换水源时\n"
        response += "• 定期维护时\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为水质专家，我很高兴为您解答关于咖啡用水的问题。\n\n"
        
        if knowledge:
            response += "基于我的水质专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的水质问题，请详细描述，我会为您提供专业的指导和建议。"
        
        return response
    
    def analyze_water_quality(self, water_parameters: Dict[str, float]) -> Dict[str, Any]:
        """分析水质质量"""
        analysis = {
            'overall_score': 0,
            'grade': 'Unknown',
            'issues': [],
            'recommendations': [],
            'sca_compliance': {}
        }
        
        score = 0
        max_score = 100
        
        # 检查各项参数
        for param, value in water_parameters.items():
            if param in self.sca_water_standards:
                min_val, max_val = self.sca_water_standards[param]
                
                if min_val <= value <= max_val:
                    analysis['sca_compliance'][param] = 'PASS'
                    score += max_score / len(self.sca_water_standards)
                else:
                    analysis['sca_compliance'][param] = 'FAIL'
                    analysis['issues'].append(f"{param}值{value}超出SCA标准范围({min_val}-{max_val})")
                    
                    if value < min_val:
                        analysis['recommendations'].append(f"增加{param}含量")
                    else:
                        analysis['recommendations'].append(f"减少{param}含量")
        
        analysis['overall_score'] = score
        analysis['grade'] = self._get_water_grade(score)
        
        return analysis
    
    def _get_water_grade(self, score: float) -> str:
        """获取水质等级"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
    
    def recommend_water_treatment(self, current_water: Dict[str, float], 
                                target_quality: str = 'SCA_Standard') -> Dict[str, Any]:
        """推荐水处理方案"""
        recommendations = {
            'treatment_methods': [],
            'cost_estimate': '',
            'pros_cons': {},
            'implementation_steps': []
        }
        
        # 分析当前水质
        analysis = self.analyze_water_quality(current_water)
        
        if analysis['grade'] in ['A+', 'A']:
            recommendations['treatment_methods'] = ['minimal_treatment']
            recommendations['cost_estimate'] = '低成本 - 只需基本过滤'
        elif analysis['grade'] in ['B', 'C']:
            recommendations['treatment_methods'] = ['activated_carbon', 'tds_adjustment']
            recommendations['cost_estimate'] = '中等成本 - 过滤和矿物质调整'
        else:
            recommendations['treatment_methods'] = ['reverse_osmosis', 'mineral_readdition']
            recommendations['cost_estimate'] = '较高成本 - 全面处理系统'
        
        return recommendations
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem], 
                               context: Dict = None) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['新手', '初学', 'beginner']):
            recommendations.append("建议使用瓶装水开始练习")
            recommendations.append("购买TDS测试笔监控水质")
            recommendations.append("了解当地自来水水质情况")
        
        if any(keyword in query_lower for keyword in ['家庭', 'home', '家用']):
            recommendations.append("安装家用水质检测设备")
            recommendations.append("定期更换滤芯")
            recommendations.append("使用SCA标准配方水")
        
        if context and 'equipment' in context:
            equipment = context['equipment']
            recommendations.append(f"针对{equipment}设备，建议使用软化水")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem], 
                       context: Dict = None) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['硬水', 'hard water', '结垢']):
            warnings.append("硬水会导致设备结垢，影响萃取质量")
        
        if any(keyword in query_lower for keyword in ['腐蚀', 'corrosion']):
            warnings.append("腐蚀性水会损坏咖啡设备")
        
        if context and 'tds' in context:
            tds = context['tds']
            if tds > 300:
                warnings.append("TDS过高会严重影响咖啡风味")
            elif tds < 50:
                warnings.append("TDS过低可能导致过度萃取")
        
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
            "SCA水质标准",
            "TDS对萃取的影响",
            "水硬度管理",
            "pH值调节",
            "水处理技术",
            "水质检测方法",
            "矿物质平衡",
            "设备保护",
            "水配方制作",
            "水质问题诊断"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        content = knowledge_item.content
        
        # 检查ppm范围的合理性
        import re
        ppm_matches = re.findall(r'(\d+)(?:-(\d+))?\s*ppm', content)
        for match in ppm_matches:
            start_val = int(match[0])
            end_val = int(match[1]) if match[1] else start_val
            
            if start_val < 0 or end_val > 1000:
                return False, f"ppm值{start_val}-{end_val}超出合理范围(0-1000 ppm)"
        
        # 检查pH范围的合理性
        ph_matches = re.findall(r'pH\s*(\d+(?:\.\d+)?)', content)
        for ph in ph_matches:
            ph_val = float(ph)
            if ph_val < 0 or ph_val > 14:
                return False, f"pH值{ph_val}超出合理范围(0-14)"
        
        return True, "验证通过"