"""
器具专家智能体
负责咖啡器具、设备选择、使用技巧等专业知识
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import json

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class EquipmentExpertAgent(BaseExpertAgent):
    """器具专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="equipment_expert_001",
            name="器具专家",
            specialty="咖啡器具与设备",
            level=ExpertLevel.EXPERT
        )
        
        # 器具分类
        self.equipment_categories = {
            'brewing': ['手冲壶', '法压壶', '爱乐压', '虹吸壶'],
            'espresso': ['意式咖啡机', '磨豆机', '压粉器', '手柄'],
            'grinding': ['锥刀磨豆机', '平刀磨豆机', '手摇磨豆机'],
            'accessories': ['电子秤', '温度计', '滤纸', '滤网'],
            'storage': ['密封罐', '保鲜盒', '真空罐']
        }
        
        # 价格区间分类
        self.price_ranges = {
            'budget': (0, 500),      # 经济型
            'mid_range': (500, 2000), # 中端
            'premium': (2000, 5000),  # 高端
            'luxury': (5000, float('inf'))  # 奢华型
        }
    
    def _initialize_knowledge_base(self):
        """初始化器具专业知识库"""
        equipment_knowledge = [
            {
                'id': 'espresso_machine_types',
                'content': '意式咖啡机主要分为：1)全自动机：操作简单，适合商用；2)半自动机：需要手动操作，适合专业用户；3)胶囊机：便捷性高，风味相对单一；4)杠杆机：传统工艺，需要技巧。',
                'source': '咖啡设备技术手册',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['意式咖啡机', '全自动', '半自动', '胶囊机', '杠杆机'],
                'references': ['咖啡设备技术手册']
            },
            {
                'id': 'grinder_importance',
                'content': '磨豆机是咖啡制作中最重要的设备，比咖啡机更重要。好的磨豆机应具备：一致的研磨度、广泛的调节范围、低热量产生、耐用的结构。锥刀适合手冲，平刀适合意式。',
                'source': '磨豆机技术指南',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['磨豆机', '最重要', '锥刀', '平刀', '一致性'],
                'references': ['磨豆机技术指南']
            },
            {
                'id': 'pour_over_equipment',
                'content': '手冲器具包括：V60滤杯(快速萃取)、Chemex(干净口感)、Kalita Wave(稳定萃取)、Melitta(经典设计)。每种滤杯都有其独特的流速设计和风味表现。',
                'source': '手冲器具指南',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['手冲器具', 'V60', 'Chemex', 'Kalita', 'Melitta'],
                'references': ['手冲器具指南']
            },
            {
                'id': 'espresso_machine_components',
                'content': '意式咖啡机的关键组件：锅炉(提供热水和蒸汽)、泵(产生压力)、冲泡头(分配热水)、PID温控(精确温度控制)、预浸功能(改善萃取)。每个组件都影响最终咖啡质量。',
                'source': '意式咖啡机结构',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['意式咖啡机', '锅炉', '泵', '冲泡头', 'PID', '预浸'],
                'references': ['意式咖啡机结构分析']
            },
            {
                'id': 'grinder_adjustment',
                'content': '磨豆机调节需要考虑：豆子新鲜度(新鲜豆需要调粗)、烘焙程度(浅烘需要调细)、萃取方法(意式最细，手冲中等，法压最粗)。每次调节后需要测试萃取效果。',
                'source': '磨豆机调节技术',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['磨豆机调节', '新鲜度', '烘焙程度', '萃取方法'],
                'references': ['磨豆机调节技术']
            },
            {
                'id': 'water_quality_equipment',
                'content': '水质处理设备包括：反渗透系统(去除杂质)、软水器(减少硬度)、活性炭过滤(改善口感)、矿物质添加器(调整TDS)。选择取决于水源质量和预算。',
                'source': '水质设备指南',
                'confidence': 0.91,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['水质设备', '反渗透', '软水器', '活性炭', '矿物质'],
                'references': ['水质设备指南']
            },
            {
                'id': 'maintenance_schedule',
                'content': '咖啡器具维护计划：每日清洁(冲泡头、滤网)、每周深度清洁(除垢)、每月保养(更换密封圈)、每季度专业维护(校准、检修)。定期维护保证设备性能和寿命。',
                'source': '设备维护手册',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['设备维护', '每日清洁', '每周除垢', '每月保养', '季度检修'],
                'references': ['设备维护手册']
            },
            {
                'id': 'accessories_importance',
                'content': '咖啡制作配件的重要性：电子秤(精确控制粉水比)、温度计(监控水温)、计时器(控制萃取时间)、布粉器(均匀分布咖啡粉)、压粉器(制作均匀粉饼)。',
                'source': '咖啡配件指南',
                'confidence': 0.89,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['咖啡配件', '电子秤', '温度计', '计时器', '布粉器', '压粉器'],
                'references': ['咖啡配件指南']
            },
            {
                'id': 'equipment_selection',
                'content': '选择咖啡器具的考虑因素：预算范围、使用频率、技术水平、空间限制、维护能力、初学者建议从简单器具开始，逐步升级到更复杂的设备。',
                'source': '器具选择指南',
                'confidence': 0.88,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['器具选择', '预算', '使用频率', '技术水平', '空间', '维护'],
                'references': ['器具选择指南']
            },
            {
                'id': 'storage_solutions',
                'content': '咖啡豆储存解决方案：密封罐(防止氧化)、真空罐(延长保鲜)、单向阀包装(释放CO2)、避光容器(防止光照)、温度稳定环境(避免温度波动)。正确的储存保持咖啡新鲜度。',
                'source': '咖啡储存指南',
                'confidence': 0.87,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['咖啡储存', '密封罐', '真空罐', '单向阀', '避光', '温度'],
                'references': ['咖啡储存指南']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in equipment_knowledge:
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
        
        logger.info(f"器具专家知识库初始化完成，共{len(equipment_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理器具相关查询"""
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
            logger.error(f"器具专家处理查询失败: {e}")
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
        if any(keyword in query_lower for keyword in ['磨豆机', 'grinder']):
            return self._handle_grinder_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['咖啡机', 'espresso machine']):
            return self._handle_espresso_machine_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['手冲', 'pour over', 'v60', 'chemex']):
            return self._handle_pour_over_equipment_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['选择', 'recommend', '购买']):
            return self._handle_equipment_selection_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['维护', 'maintenance', '保养', '清洁']):
            return self._handle_maintenance_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['配件', 'accessories', '工具']):
            return self._handle_accessories_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_grinder_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理磨豆机查询"""
        response = "关于磨豆机，我来为您详细说明：\n\n"
        
        # 查找磨豆机相关知识
        grinder_knowledge = [k for k in knowledge if '磨豆机' in k.tags]
        
        if grinder_knowledge:
            for item in grinder_knowledge:
                response += f"**磨豆机重要性**\n{item.content}\n\n"
        
        response += "磨豆机类型对比：\n\n"
        
        response += "**锥刀磨豆机**\n"
        response += "• 优点：热量产生少、风味干净、适合手冲\n"
        response += "• 缺点：细粉较多、研磨速度慢\n"
        response += "• 适用：手冲、法压、土耳其咖啡\n\n"
        
        response += "**平刀磨豆机**\n"
        response += "• 优点：研磨均匀、细粉少、适合意式\n"
        response += "• 缺点：热量产生多、价格较高\n"
        response += "• 适用：意式浓缩、精品手冲\n\n"
        
        response += "选择建议：\n"
        response += "1. 预算充足：选择平刀磨豆机\n"
        response += "2. 主要手冲：锥刀磨豆机足够\n"
        response += "3. 意式为主：必须选择平刀\n"
        response += "4. 考虑可调节范围和精度\n"
        
        return response
    
    def _handle_espresso_machine_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理意式咖啡机查询"""
        response = "关于意式咖啡机，我来为您详细解释：\n\n"
        
        # 查找意式咖啡机相关知识
        machine_knowledge = [k for k in knowledge if '意式咖啡机' in k.tags]
        
        if machine_knowledge:
            for item in machine_knowledge:
                response += f"**咖啡机类型**\n{item.content}\n\n"
        
        response += "意式咖啡机类型对比：\n\n"
        
        response += "**全自动咖啡机**\n"
        response += "• 优点：操作简单、一键制作、适合商用\n"
        response += "• 缺点：价格高、可调性差、维护成本高\n"
        response += "• 适用：办公室、商业场所\n\n"
        
        response += "**半自动咖啡机**\n"
        response += "• 优点：控制性强、品质高、可玩性大\n"
        response += "• 缺点：需要技巧、学习成本高\n"
        response += "• 适用：家庭咖啡爱好者、专业咖啡师\n\n"
        
        response += "**胶囊咖啡机**\n"
        response += "• 优点：便捷性高、清洁简单、一致性好\n"
        response += "• 缺点：成本高、风味单一、环保问题\n"
        response += "• 适用：快节奏生活、偶尔饮用\n\n"
        
        response += "关键组件重要性：\n"
        response += "• 锅炉：影响温度稳定性\n"
        response += "• 泵：决定压力表现\n"
        response += "• PID：精确温控\n"
        response += "• 预浸：改善萃取均匀性\n"
        
        return response
    
    def _handle_pour_over_equipment_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理手冲器具查询"""
        response = "关于手冲器具，我来为您详细介绍：\n\n"
        
        # 查找手冲器具相关知识
        pour_over_knowledge = [k for k in knowledge if '手冲器具' in k.tags]
        
        if pour_over_knowledge:
            for item in pour_over_knowledge:
                response += f"**手冲器具**\n{item.content}\n\n"
        
        response += "主流滤杯对比：\n\n"
        
        response += "**V60滤杯**\n"
        response += "• 特点：大孔径、快速萃取、螺旋肋条\n"
        response += "• 风味：清晰、明亮、酸质突出\n"
        response += "• 难度：中等，需要一定技巧\n"
        response += "• 适用：单一产区豆、花香果酸型咖啡\n\n"
        
        response += "**Chemex滤杯**\n"
        response += "• 特点：厚滤纸、慢流速、优雅设计\n"
        response += "• 风味：干净、醇厚、低酸质\n"
        response += "• 难度：较难，需要耐心\n"
        response += "• 适用：深烘豆、醇厚口感偏好\n\n"
        
        response += "**Kalita Wave滤杯**\n"
        response += "• 特点：波浪滤纸、平底设计、稳定流速\n"
        response += "• 风味：平衡、稳定、易于复制\n"
        response += "• 难度：较易，适合初学者\n"
        response += "• 适用：日常饮用、稳定品质要求\n\n"
        
        response += "选择建议：\n"
        response += "• 初学者：Kalita Wave\n"
        response += "• 追求酸质：V60\n"
        response += "• 追求醇厚：Chemex\n"
        response += "• 考虑个人风味偏好和使用技巧\n"
        
        return response
    
    def _handle_equipment_selection_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理器具选择查询"""
        response = "关于咖啡器具选择，我来为您提供专业建议：\n\n"
        
        # 查找选择相关知识
        selection_knowledge = [k for k in knowledge if '器具选择' in k.tags]
        
        if selection_knowledge:
            for item in selection_knowledge:
                response += f"**选择考虑因素**\n{item.content}\n\n"
        
        response += "选择步骤：\n\n"
        
        response += "1. **确定预算范围**\n"
        response += "   • 经济型(0-500元)：基础手冲器具\n"
        response += "   • 中端(500-2000元)：优质磨豆机+手冲器具\n"
        response += "   • 高端(2000-5000元)：入门意式设备\n"
        response += "   • 奢华型(5000元以上)：专业级设备\n\n"
        
        response += "2. **评估使用频率**\n"
        response += "   • 偶尔饮用：简单器具即可\n"
        response += "   • 每日饮用：投资优质设备\n"
        response += "   • 商用需求：专业级设备\n\n"
        
        response += "3. **考虑技术水平**\n"
        response += "   • 初学者：操作简单的器具\n"
        response += "   • 有经验：可调性强的设备\n"
        response += "   • 专业用户：高端精密设备\n\n"
        
        response += "4. **评估空间和存储**\n"
        response += "   • 小空间：多功能器具\n"
        response += "   • 大空间：专业设备套装\n"
        response += "   • 移动需求：便携式器具\n\n"
        
        response += "初学者推荐配置：\n"
        response += "• 手摇磨豆机 + V60滤杯 + 手冲壶\n"
        response += "• 电子秤 + 温度计 + 计时器\n"
        response += "• 预算约1000-1500元\n"
        
        return response
    
    def _handle_maintenance_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理维护查询"""
        response = "关于咖啡器具维护，我来为您详细说明：\n\n"
        
        # 查找维护相关知识
        maintenance_knowledge = [k for k in knowledge if '设备维护' in k.tags]
        
        if maintenance_knowledge:
            for item in maintenance_knowledge:
                response += f"**维护计划**\n{item.content}\n\n"
        
        response += "日常维护(每日)：\n"
        response += "• 冲洗冲泡头和手柄\n"
        response += "• 清洁滤网和滤纸\n"
        response += "• 擦拭设备表面\n"
        response += "• 清空废渣盒\n\n"
        
        response += "每周维护：\n"
        response += "• 深度清洁冲泡系统\n"
        response += "• 除垢处理\n"
        response += "• 清洁水箱和供水系统\n"
        response += "• 检查密封件\n\n"
        
        response += "每月维护：\n"
        response += "• 更换滤芯\n"
        response += "• 校准温度和压力\n"
        response += "• 检查电气连接\n"
        response += "• 润滑活动部件\n\n"
        
        response += "季度维护：\n"
        response += "• 专业检修和校准\n"
        response += "• 更换易损件\n"
        response += "• 全面性能测试\n"
        response += "• 记录维护历史\n\n"
        
        response += "维护注意事项：\n"
        response += "• 使用专用清洁剂\n"
        response += "• 避免使用腐蚀性化学品\n"
        response += "• 定期检查电气安全\n"
        response += "• 保持设备干燥\n"
        
        return response
    
    def _handle_accessories_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理配件查询"""
        response = "关于咖啡配件，我来为您详细介绍：\n\n"
        
        # 查找配件相关知识
        accessories_knowledge = [k for k in knowledge if '咖啡配件' in k.tags]
        
        if accessories_knowledge:
            for item in accessories_knowledge:
                response += f"**配件重要性**\n{item.content}\n\n"
        
        response += "必备配件：\n\n"
        
        response += "**电子秤**\n"
        response += "• 功能：精确控制粉水比\n"
        response += "• 精度：0.1g以上\n"
        response += "• 响应速度：快速反应\n"
        response += "• 预算：100-500元\n\n"
        
        response += "**温度计**\n"
        response += "• 功能：监控水温\n"
        response += "• 类型：数字温度计、红外温度计\n"
        response += "• 精度：±1°C\n"
        response += "• 预算：50-200元\n\n"
        
        response += "**计时器**\n"
        response += "• 功能：控制萃取时间\n"
        response += "• 类型：手机APP、机械计时器\n"
        response += "• 精度：秒级\n"
        response += "• 预算：免费-100元\n\n"
        
        response += "**布粉器**\n"
        response += "• 功能：均匀分布咖啡粉\n"
        response += "• 类型：平底布粉器、针式布粉器\n"
        response += "• 尺寸：匹配手柄口径\n"
        response += "• 预算：50-300元\n\n"
        
        response += "**压粉器**\n"
        response += "• 功能：制作均匀粉饼\n"
        response += "• 类型：平底、凸面、木质、金属\n"
        response += "• 重量：2-3磅\n"
        response += "• 预算：100-1000元\n\n"
        
        response += "配件选择建议：\n"
        response += "• 从基础配件开始\n"
        response += "• 优先购买电子秤\n"
        response += "• 根据使用需求逐步添加\n"
        response += "• 选择知名品牌和质量可靠的产品\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为器具专家，我很高兴为您解答关于咖啡器具的问题。\n\n"
        
        if knowledge:
            response += "基于我的器具专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的器具问题，请详细描述，我会为您提供专业的指导和建议。"
        
        return response
    
    def recommend_equipment_setup(self, budget: float, experience_level: str, 
                                coffee_type: str) -> Dict[str, Any]:
        """推荐器具配置"""
        setup = {
            'total_budget': budget,
            'experience_level': experience_level,
            'coffee_type': coffee_type,
            'recommended_equipment': [],
            'priority_order': [],
            'upgrade_path': []
        }
        
        if experience_level == 'beginner':
            if budget <= 500:
                setup['recommended_equipment'] = [
                    {'item': '手摇磨豆机', 'price': 200, 'priority': 1},
                    {'item': 'V60滤杯', 'price': 50, 'priority': 2},
                    {'item': '手冲壶', 'price': 100, 'priority': 3},
                    {'item': '电子秤', 'price': 80, 'priority': 4},
                    {'item': '温度计', 'price': 50, 'priority': 5}
                ]
            elif budget <= 1500:
                setup['recommended_equipment'] = [
                    {'item': '电动磨豆机', 'price': 800, 'priority': 1},
                    {'item': 'V60滤杯套装', 'price': 200, 'priority': 2},
                    {'item': '手冲壶', 'price': 300, 'priority': 3},
                    {'item': '电子秤', 'price': 150, 'priority': 4}
                ]
        elif experience_level == 'intermediate':
            if budget <= 3000:
                setup['recommended_equipment'] = [
                    {'item': '平刀磨豆机', 'price': 1500, 'priority': 1},
                    {'item': '多种滤杯', 'price': 500, 'priority': 2},
                    {'item': '高端手冲壶', 'price': 600, 'priority': 3},
                    {'item': '专业电子秤', 'price': 300, 'priority': 4}
                ]
        
        setup['priority_order'] = [eq['item'] for eq in setup['recommended_equipment']]
        return setup
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem], 
                               context: Dict = None) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['新手', '初学', 'beginner']):
            recommendations.append("建议从手冲器具开始学习")
            recommendations.append("投资一台好的磨豆机比咖啡机更重要")
            recommendations.append("先掌握基础技巧再升级设备")
        
        if any(keyword in query_lower for keyword in ['预算', 'budget', '便宜']):
            recommendations.append("选择性价比高的基础器具")
            recommendations.append("可以先购买二手设备")
            recommendations.append("分阶段投资，逐步升级")
        
        if context and 'space' in context:
            space = context['space']
            recommendations.append(f"针对{space}空间，建议选择{space}适配的器具")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem], 
                       context: Dict = None) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['便宜', '廉价', 'cheap']):
            warnings.append("过于便宜的设备可能质量不佳，影响使用体验")
        
        if any(keyword in query_lower for keyword in ['二手', 'used']):
            warnings.append("购买二手设备需要仔细检查功能状态")
        
        if context and 'budget' in context:
            budget = context['budget']
            if budget < 100:
                warnings.append("预算过低可能无法购买到合适的器具")
        
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
            "磨豆机技术",
            "意式咖啡机",
            "手冲器具",
            "设备选择",
            "维护保养",
            "配件推荐",
            "器具对比",
            "设备升级",
            "空间规划",
            "预算配置"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        content = knowledge_item.content
        
        # 检查价格范围的合理性
        import re
        price_matches = re.findall(r'(\d+)(?:-(\d+))?\s*元', content)
        for match in price_matches:
            start_price = int(match[0])
            end_price = int(match[1]) if match[1] else start_price
            
            if start_price < 0 or end_price > 100000:
                return False, f"价格范围{start_price}-{end_price}元超出合理范围(0-100000元)"
        
        # 检查温度范围的合理性
        temp_matches = re.findall(r'(\d+)[°℃]', content)
        for temp in temp_matches:
            temp_val = int(temp)
            if temp_val < 0 or temp_val > 200:
                return False, f"温度值{temp_val}°C超出合理范围(0-200°C)"
        
        return True, "验证通过"