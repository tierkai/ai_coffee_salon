"""
感官专家智能体
负责感官品鉴、风味描述、杯测等专业知识
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import json

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class SensoryExpertAgent(BaseExpertAgent):
    """感官专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="sensory_expert_001",
            name="感官专家",
            specialty="咖啡感官品鉴",
            level=ExpertLevel.EXPERT
        )
        
        # SCA风味轮主要分类
        self.flavor_wheel = {
            'fruity': ['果香', '花香', '柑橘', '浆果', '热带水果', '核果'],
            'sweet': ['甜味', '焦糖', '蜂蜜', '巧克力', '坚果', '香草'],
            'floral': ['花香', '茉莉', '玫瑰', '薰衣草', '茶香'],
            'spicy': ['香料', '肉桂', '丁香', '胡椒', '薄荷'],
            'earthy': ['泥土', '木质', '烟草', '皮革'],
            'chemical': ['化学味', '药味', '橡胶', '石油']
        }
        
        # 杯测评估标准
        self.cupping_standards = {
            'aroma': {'weight': 0.1, 'scale': (1, 10)},
            'flavor': {'weight': 0.2, 'scale': (1, 10)},
            'aftertaste': {'weight': 0.1, 'scale': (1, 10)},
            'acidity': {'weight': 0.15, 'scale': (1, 10)},
            'body': {'weight': 0.1, 'scale': (1, 10)},
            'uniformity': {'weight': 0.1, 'scale': (1, 10)},
            'clean_cup': {'weight': 0.1, 'scale': (1, 10)},
            'sweetness': {'weight': 0.1, 'scale': (1, 10)},
            'overall': {'weight': 0.05, 'scale': (1, 10)}
        }
    
    def _initialize_knowledge_base(self):
        """初始化感官专业知识库"""
        sensory_knowledge = [
            {
                'id': 'sensory_basics',
                'content': '咖啡感官品鉴基于人的基本感官：嗅觉、味觉、触觉和视觉。SCA(Specialty Coffee Association)制定了标准化的感官评估体系，包括香气、风味、余韵、酸质、醇厚感、均一度、清洁度、甜度和综合评价。',
                'source': 'SCA感官指南',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['感官基础', 'SCA标准', '嗅觉', '味觉', '触觉', '视觉'],
                'references': ['SCA感官指南']
            },
            {
                'id': 'aroma_assessment',
                'content': '香气评估包括干香(咖啡粉的香气)和湿香(萃取后的香气)。香气强度分为1-10级，香气质量需要具体描述。常见香气类型包括花香、果香、香料、坚果、巧克力、焦糖等。',
                'source': '咖啡香气学',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['香气评估', '干香', '湿香', '强度', '花香', '果香'],
                'references': ['咖啡香气学研究']
            },
            {
                'id': 'flavor_profiling',
                'content': '风味是咖啡在口中时的综合感官体验。SCA风味轮将风味分为花果香、甜香、香料香、坚果可可、泥土化学等大类。专业杯测师需要能够准确识别和描述风味特征。',
                'source': '风味轮标准',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['风味描述', 'SCA风味轮', '花果香', '甜香', '香料香'],
                'references': ['SCA风味轮']
            },
            {
                'id': 'acidity_evaluation',
                'content': '酸质是精品咖啡的重要特征，但不是简单的酸味。酸质评估包括酸质类型(明亮、柔和、尖锐等)、酸质质量(愉悦、不愉悦)、酸质强度(1-10级)。好的酸质应该明亮、清晰、令人愉悦。',
                'source': '酸质评估标准',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['酸质评估', '明亮', '柔和', '尖锐', '愉悦'],
                'references': ['酸质评估标准']
            },
            {
                'id': 'body_perception',
                'content': '醇厚感(Body)是指咖啡在口中的重量感和质地感知。评估维度包括醇厚程度(1-10级)、质地(丝绸般、奶油般、水感等)、油润度。醇厚感与咖啡的萃取率、密度、纤维含量有关。',
                'source': '醇厚感研究',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['醇厚感', '重量感', '质地', '丝绸般', '奶油般', '水感'],
                'references': ['醇厚感研究报告']
            },
            {
                'id': 'aftertaste_analysis',
                'content': '余韵是指咖啡咽下后在口中和喉部的持续感受。余韵长度分为短、中、长三个等级，余韵质量分为正面(甜、香)、负面(苦、涩)、中性。优质咖啡应该有持久、愉悦的余韵。',
                'source': '余韵分析',
                'confidence': 0.91,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['余韵分析', '长度', '正面', '负面', '中性', '持续'],
                'references': ['余韵分析研究']
            },
            {
                'id': 'sweetness_detection',
                'content': '甜度是咖啡中天然糖分和美拉德反应的产物。甜度评估包括甜度类型(果糖甜、焦糖甜、蜂蜜甜等)、甜度强度(1-10级)、甜度质量。甜度与烘焙程度、处理方法、品种有关。',
                'source': '甜度检测方法',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['甜度检测', '果糖甜', '焦糖甜', '蜂蜜甜', '天然糖分'],
                'references': ['甜度检测方法']
            },
            {
                'id': 'cupping_protocol',
                'content': '标准杯测流程：1)准备85°C热水和中等研磨咖啡粉；2)闻干香；3)注水浸泡4分钟；4)破渣闻湿香；5)用勺子捞渣；6)趁热品尝；7)记录各项评分。杯测环境应安静、无异味、光线充足。',
                'source': 'SCA杯测标准',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['杯测流程', '85°C', '4分钟', '破渣', '趁热品尝'],
                'references': ['SCA杯测标准']
            },
            {
                'id': 'defect_identification',
                'content': '常见感官缺陷包括：过酸(尖锐刺激)、过苦(烧焦味)、发酵味(酒味、醋味)、霉味(土腥味)、化学味(药味、橡胶味)、木味(过木质化)、青草味(未成熟)。识别缺陷有助于改进加工和烘焙。',
                'source': '缺陷识别手册',
                'confidence': 0.89,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['缺陷识别', '过酸', '过苦', '发酵味', '霉味', '化学味'],
                'references': ['缺陷识别手册']
            },
            {
                'id': 'sensory_training',
                'content': '感官训练方法：1)建立感官记忆库(闻香瓶训练)；2)定期杯测练习；3)风味盲测；4)记录感官日记；5)与他人交流对比。训练需要长期坚持，循序渐进。',
                'source': '感官训练指南',
                'confidence': 0.88,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['感官训练', '闻香瓶', '杯测练习', '盲测', '感官日记'],
                'references': ['感官训练指南']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in sensory_knowledge:
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
        
        logger.info(f"感官专家知识库初始化完成，共{len(sensory_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理感官相关查询"""
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
            logger.error(f"感官专家处理查询失败: {e}")
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
        if any(keyword in query_lower for keyword in ['杯测', 'cupping']):
            return self._handle_cupping_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['风味', 'flavor', '描述']):
            return self._handle_flavor_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['香气', 'aroma', '干香', '湿香']):
            return self._handle_aroma_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['酸质', 'acidity']):
            return self._handle_acidity_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['醇厚', 'body', '口感']):
            return self._handle_body_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['训练', 'training', '练习']):
            return self._handle_training_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['缺陷', 'defect', '问题']):
            return self._handle_defect_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_cupping_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理杯测查询"""
        response = "关于咖啡杯测，我来为您详细说明：\n\n"
        
        # 查找杯测相关知识
        cupping_knowledge = [k for k in knowledge if '杯测' in k.tags]
        
        if cupping_knowledge:
            for item in cupping_knowledge:
                response += f"**杯测流程**\n{item.content}\n\n"
        
        response += "标准杯测步骤：\n\n"
        
        response += "1. **准备阶段**\n"
        response += "   • 咖啡粉：中度研磨，每杯8.25g\n"
        response += "   • 水温：85-90°C\n"
        response += "   • 粉水比：1:15.8\n"
        response += "   • 杯具：专用杯测碗\n\n"
        
        response += "2. **干香评估**\n"
        response += "   • 研磨后立即闻干香\n"
        response += "   • 记录香气强度和质量\n"
        response += "   • 评分范围：1-10分\n\n"
        
        response += "3. **注水和浸泡**\n"
        response += "   • 快速注满热水\n"
        response += "   • 浸泡4分钟\n"
        response += "   • 避免搅拌\n\n"
        
        response += "4. **破渣和湿香**\n"
        response += "   • 用勺子破渣\n"
        response += "   • 立即闻湿香\n"
        response += "   • 记录香气变化\n\n"
        
        response += "5. **捞渣**\n"
        response += "   • 用勺子捞出表面浮渣\n"
        response += "   • 清洁杯沿\n"
        response += "   • 准备品尝\n\n"
        
        response += "6. **品尝评估**\n"
        response += "   • 趁热快速品尝\n"
        response += "   • 用勺子舀取咖啡\n"
        response += "   • 让咖啡在口中充分接触\n"
        response += "   • 记录各项评分\n\n"
        
        response += "杯测评分标准：\n"
        for category, info in self.cupping_standards.items():
            category_names = {
                'aroma': '香气',
                'flavor': '风味',
                'aftertaste': '余韵',
                'acidity': '酸质',
                'body': '醇厚',
                'uniformity': '均一度',
                'clean_cup': '清洁度',
                'sweetness': '甜度',
                'overall': '综合评价'
            }
            response += f"• {category_names.get(category, category)}: {info['weight']*100:.0f}%权重\n"
        
        return response
    
    def _handle_flavor_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理风味查询"""
        response = "关于咖啡风味，我来为您详细描述：\n\n"
        
        # 查找风味相关知识
        flavor_knowledge = [k for k in knowledge if '风味' in k.tags]
        
        if flavor_knowledge:
            for item in flavor_knowledge:
                response += f"**风味描述**\n{item.content}\n\n"
        
        response += "SCA风味轮主要分类：\n\n"
        
        for category, flavors in self.flavor_wheel.items():
            category_names = {
                'fruity': '果香类',
                'sweet': '甜香类',
                'floral': '花香类',
                'spicy': '香料类',
                'earthy': '泥土类',
                'chemical': '化学类'
            }
            
            response += f"**{category_names.get(category, category)}**\n"
            response += f"包括：{', '.join(flavors)}\n\n"
        
        response += "风味描述方法：\n"
        response += "1. **具体化描述**\n"
        response += "   • 不说'好喝'，要说'有黑莓的甜酸味'\n"
        response += "   • 使用熟悉的风味参考\n"
        response += "   • 描述风味层次和变化\n\n"
        
        response += "2. **时间维度**\n"
        response += "   • 前调：初入口的风味\n"
        response += "   • 中调：主要风味体验\n"
        response += "   • 后调：余韵和收尾\n\n"
        
        response += "3. **强度和品质**\n"
        response += "   • 风味强度：1-10级\n"
        response += "   • 风味质量：清晰/模糊、愉悦/不愉悦\n"
        response += "   • 风味平衡：是否和谐\n\n"
        
        response += "常见风味描述示例：\n"
        response += "• 埃塞俄比亚：花香、柑橘、茉莉花茶\n"
        response += "• 哥伦比亚：坚果、巧克力、焦糖\n"
        response += "• 巴拿马Geisha：花香、柑橘、蜂蜜\n"
        response += "• 肯尼亚：黑加仑、番茄、葡萄酒\n"
        
        return response
    
    def _handle_aroma_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理香气查询"""
        response = "关于咖啡香气，我来为您详细解释：\n\n"
        
        # 查找香气相关知识
        aroma_knowledge = [k for k in knowledge if '香气' in k.tags]
        
        if aroma_knowledge:
            for item in aroma_knowledge:
                response += f"**香气评估**\n{item.content}\n\n"
        
        response += "香气分类：\n\n"
        
        response += "**干香(Fragrance)**\n"
        response += "• 定义：咖啡粉释放的香气\n"
        response += "• 评估时机：研磨后立即评估\n"
        response += "• 特点：更集中、更直接\n"
        response += "• 评分：1-10分\n\n"
        
        response += "**湿香(Aroma)**\n"
        response += "• 定义：萃取后咖啡液释放的香气\n"
        response += "• 评估时机：破渣后立即评估\n"
        response += "• 特点：更丰富、更复杂\n"
        response += "• 评分：1-10分\n\n"
        
        response += "香气强度分级：\n"
        response += "• 1-2分：微弱，难以察觉\n"
        response += "• 3-4分：轻微，隐约可闻\n"
        response += "• 5-6分：中等，清晰可辨\n"
        response += "• 7-8分：强烈，持久不散\n"
        response += "• 9-10分：极强，震撼感官\n\n"
        
        response += "常见香气类型：\n"
        response += "• 花香：茉莉、玫瑰、薰衣草\n"
        response += "• 果香：柑橘、浆果、热带水果\n"
        response += "• 香料：肉桂、丁香、胡椒\n"
        response += "• 坚果：榛子、杏仁、花生\n"
        response += "• 巧克力：黑巧克力、牛奶巧克力\n"
        response += "• 甜香：焦糖、蜂蜜、香草\n\n"
        
        response += "香气评估技巧：\n"
        response += "• 保持环境安静无异味\n"
        response += "• 距离适中，避免过近或过远\n"
        response += "• 多次闻香，捕捉不同层次\n"
        response += "• 用熟悉物品建立香气记忆\n"
        
        return response
    
    def _handle_acidity_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理酸质查询"""
        response = "关于咖啡酸质，我来为您详细说明：\n\n"
        
        # 查找酸质相关知识
        acidity_knowledge = [k for k in knowledge if '酸质' in k.tags]
        
        if acidity_knowledge:
            for item in acidity_knowledge:
                response += f"**酸质评估**\n{item.content}\n\n"
        
        response += "酸质类型分类：\n\n"
        
        response += "**明亮酸质(Bright)**\n"
        response += "• 特征：清晰、活泼、令人愉悦\n"
        response += "• 常见于：浅烘单一产区豆\n"
        response += "• 风味：柑橘、苹果、浆果\n"
        response += "• 评价：正面特征\n\n"
        
        response += "**柔和酸质(Mild)**\n"
        response += "• 特征：圆润、温和、不刺激\n"
        response += "• 常见于：中度烘焙豆\n"
        response += "• 风味：核果、热带水果\n"
        response += "• 评价：平衡特征\n\n"
        
        response += "**尖锐酸质(Sharp)**\n"
        response += "• 特征：刺激、刺鼻、不和谐\n"
        response += "• 常见于：过度萃取或未成熟豆\n"
        response += "• 风味：醋酸、柠檬酸\n"
        response += "• 评价：负面特征\n\n"
        
        response += "酸质质量评估：\n"
        response += "1. **愉悦度**\n"
        response += "   • 令人愉悦：正面特征\n"
        response += "   • 中性：平衡特征\n"
        response += "   • 不愉悦：负面特征\n\n"
        
        response += "2. **清晰度**\n"
        response += "   • 清晰：酸质边界明确\n"
        response += "   • 模糊：酸质混浊不清\n\n"
        
        response += "3. **复杂度**\n"
        response += "   • 复杂：多种酸质层次\n"
        response += "   • 简单：单一酸质表现\n\n"
        
        response += "酸质强度评分：\n"
        response += "• 1-3分：微弱酸质\n"
        response += "• 4-6分：适中酸质\n"
        response += "• 7-8分：突出酸质\n"
        response += "• 9-10分：极强酸质\n\n"
        
        response += "影响酸质的因素：\n"
        response += "• 品种：阿拉比卡酸质更丰富\n"
        response += "• 海拔：高海拔豆酸质更明亮\n"
        response += "• 烘焙：浅烘保留更多酸质\n"
        response += "• 处理：水洗法酸质更清晰\n"
        response += "• 萃取：过度萃取会突出苦味而非酸质\n"
        
        return response
    
    def _handle_body_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理醇厚感查询"""
        response = "关于咖啡醇厚感，我来为您详细解释：\n\n"
        
        # 查找醇厚感相关知识
        body_knowledge = [k for k in knowledge if '醇厚感' in k.tags]
        
        if body_knowledge:
            for item in body_knowledge:
                response += f"**醇厚感评估**\n{item.content}\n\n"
        
        response += "醇厚感评估维度：\n\n"
        
        response += "1. **重量感(Weight)**\n"
        response += "• 定义：咖啡在口中的重量感知\n"
        response += "• 评估：1-10分\n"
        response += "• 轻：接近水的质感\n"
        response += "• 重：接近牛奶的质感\n\n"
        
        response += "2. **质地(Texture)**\n"
        response += "• 丝绸般：光滑、细腻\n"
        response += "• 奶油般：浓郁、顺滑\n"
        response += "• 油润：轻微油脂感\n"
        response += "• 水感：清淡、稀薄\n"
        response += "• 粉感：有颗粒感\n\n"
        
        response += "3. **密度(Density)**\n"
        response += "• 高密度：浓郁、饱满\n"
        response += "• 中密度：适中、平衡\n"
        response += "• 低密度：清淡、薄感\n\n"
        
        response += "醇厚感强度分级：\n"
        response += "• 1-2分：水感，几乎无醇厚感\n"
        response += "• 3-4分：轻微，有一定厚度\n"
        response += "• 5-6分：适中，明显的醇厚感\n"
        response += "• 7-8分：突出，强烈的醇厚感\n"
        response += "• 9-10分：极强，油润厚重\n\n"
        
        response += "醇厚感类型：\n"
        response += "• **粘稠型**：如蜂蜜、枫糖浆\n"
        response += "• **丝滑型**：如丝绸、奶油\n"
        response += "• **清爽型**：如绿茶、清汤\n"
        response += "• **厚重型**：如黑巧克力、坚果酱\n\n"
        
        response += "影响醇厚感的因素：\n"
        response += "• 萃取率：高萃取率增加醇厚感\n"
        response += "• 咖啡豆密度：高密度豆醇厚感强\n"
        response += "• 烘焙程度：深烘豆醇厚感更突出\n"
        response += "• 品种：罗布斯塔比阿拉比卡醇厚\n"
        response += "• 处理方法：蜜处理比水洗法醇厚感强\n"
        response += "• 研磨度：细研磨增加萃取从而增加醇厚感\n\n"
        
        response += "醇厚感与风味的关系：\n"
        response += "• 高醇厚感：通常伴随甜味和苦味\n"
        response += "• 低醇厚感：通常酸质更突出\n"
        response += "• 适中醇厚感：酸甜苦平衡\n"
        response += "• 醇厚感过强：可能掩盖其他风味\n"
        response += "• 醇厚感过弱：咖啡显得单薄\n"
        
        return response
    
    def _handle_training_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理训练查询"""
        response = "关于感官训练，我来为您详细说明：\n\n"
        
        # 查找训练相关知识
        training_knowledge = [k for k in knowledge if '感官训练' in k.tags]
        
        if training_knowledge:
            for item in training_knowledge:
                response += f"**感官训练**\n{item.content}\n\n"
        
        response += "训练方法：\n\n"
        
        response += "1. **闻香瓶训练**\n"
        response += "• 使用标准闻香瓶套装\n"
        response += "• 练习识别基本香气类型\n"
        response += "• 建立香气记忆库\n"
        response += "• 每日练习15-30分钟\n\n"
        
        response += "2. **杯测练习**\n"
        response += "• 定期进行标准杯测\n"
        response += "• 对比不同产区咖啡\n"
        response += "• 记录感官评分\n"
        response += "• 与他人交流讨论\n\n"
        
        response += "3. **风味盲测**\n"
        response += "• 盲品不同咖啡样品\n"
        response += "• 训练识别能力\n"
        response += "• 提高准确性\n"
        response += "• 减少偏见影响\n\n"
        
        response += "4. **感官日记**\n"
        response += "• 记录每次品鉴结果\n"
        response += "• 描述详细的风味特征\n"
        response += "• 追踪训练进步\n"
        response += "• 建立个人数据库\n\n"
        
        response += "训练计划：\n\n"
        
        response += "**初级阶段(1-3个月)**\n"
        response += "• 目标：建立基本感官能力\n"
        response += "• 内容：识别基本风味类型\n"
        response += "• 频率：每周3-4次练习\n"
        response += "• 方法：闻香瓶 + 简单杯测\n\n"
        
        response += "**中级阶段(3-6个月)**\n"
        response += "• 目标：提高识别精度\n"
        response += "• 内容：细分风味描述\n"
        response += "• 频率：每周2-3次杯测\n"
        response += "• 方法：盲测 + 对比品鉴\n\n"
        
        response += "**高级阶段(6个月以上)**\n"
        response += "• 目标：专业品鉴能力\n"
        response += "• 内容：复杂风味分析\n"
        response += "• 频率：每日练习\n"
        response += "• 方法：专业杯测 + 比赛训练\n\n"
        
        response += "训练注意事项：\n"
        response += "• 保持身体健康，避免感冒\n"
        response += "• 避免强烈气味干扰\n"
        response += "• 保持规律作息\n"
        response += "• 循序渐进，不要急于求成\n"
        response += "• 坚持长期训练\n"
        
        return response
    
    def _handle_defect_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理缺陷查询"""
        response = "关于咖啡感官缺陷，我来为您详细说明：\n\n"
        
        # 查找缺陷相关知识
        defect_knowledge = [k for k in knowledge if '缺陷' in k.tags]
        
        if defect_knowledge:
            for item in defect_knowledge:
                response += f"**缺陷识别**\n{item.content}\n\n"
        
        response += "常见感官缺陷：\n\n"
        
        response += "**过度萃取缺陷**\n"
        response += "• 特征：过度苦味、烧焦味、涩感\n"
        response += "• 原因：时间过长、温度过高、研磨过细\n"
        response += "• 解决方案：调整萃取参数\n\n"
        
        response += "**发酵过度缺陷**\n"
        response += "• 特征：酒味、醋味、酸败味\n"
        response += "• 原因：发酵时间过长、温度过高\n"
        response += "• 解决方案：控制发酵条件\n\n"
        
        response += "**储存不当缺陷**\n"
        response += "• 特征：霉味、土腥味、陈旧味\n"
        response += "• 原因：潮湿、氧化、光照\n"
        response += "• 解决方案：改善储存条件\n\n"
        
        response += "**未熟豆缺陷**\n"
        response += "• 特征：青草味、植物味、涩感\n"
        response += "• 原因：采摘未成熟豆\n"
        response += "• 解决方案：严格筛选成熟度\n\n"
        
        response += "**烘焙缺陷**\n"
        response += "• 特征：烤焦味、生味、不均匀\n"
        response += "• 原因：温度控制不当、时间掌握不准\n"
        response += "• 解决方案：优化烘焙曲线\n\n"
        
        response += "**化学污染缺陷**\n"
        response += "• 特征：药味、化学味、橡胶味\n"
        response += "• 原因：农药残留、加工污染\n"
        response += "• 解决方案：源头控制\n\n"
        
        response += "缺陷识别方法：\n"
        response += "1. **对比品鉴**：与优质咖啡对比\n"
        response += "2. **多次确认**：避免偶然因素\n"
        response += "3. **记录特征**：详细描述缺陷表现\n"
        response += "4. **追溯原因**：分析缺陷产生的环节\n\n"
        
        response += "避免缺陷的建议：\n"
        response += "• 选择优质咖啡豆\n"
        response += "• 控制加工过程\n"
        response += "• 优化烘焙技术\n"
        response += "• 改善储存条件\n"
        response += "• 精确控制萃取\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为感官专家，我很高兴为您解答关于咖啡感官品鉴的问题。\n\n"
        
        if knowledge:
            response += "基于我的感官专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的感官问题，请详细描述，我会为您提供专业的指导和建议。"
        
        return response
    
    def evaluate_coffee_sensory(self, sensory_scores: Dict[str, float]) -> Dict[str, Any]:
        """评估咖啡感官分数"""
        evaluation = {
            'total_score': 0,
            'grade': 'Unknown',
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        for category, score in sensory_scores.items():
            if category in self.cupping_standards:
                weight = self.cupping_standards[category]['weight']
                total_weighted_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            evaluation['total_score'] = total_weighted_score / total_weight * 10  # 转换为10分制
            evaluation['grade'] = self._get_sensory_grade(evaluation['total_score'])
        
        # 分析优劣势
        for category, score in sensory_scores.items():
            if category in self.cupping_standards:
                if score >= 8:
                    evaluation['strengths'].append(f"{category}表现优秀({score:.1f}分)")
                elif score <= 4:
                    evaluation['weaknesses'].append(f"{category}需要改进({score:.1f}分)")
        
        # 生成建议
        if evaluation['total_score'] >= 8:
            evaluation['recommendations'].append("继续保持当前品质")
        elif evaluation['total_score'] >= 6:
            evaluation['recommendations'].append("针对薄弱环节进行改进")
        else:
            evaluation['recommendations'].append("需要全面提升感官品质")
        
        return evaluation
    
    def _get_sensory_grade(self, score: float) -> str:
        """获取感官等级"""
        if score >= 9.0:
            return 'S'
        elif score >= 8.0:
            return 'A'
        elif score >= 7.0:
            return 'B'
        elif score >= 6.0:
            return 'C'
        elif score >= 5.0:
            return 'D'
        else:
            return 'F'
    
    def generate_flavor_profile(self, flavor_notes: List[str]) -> Dict[str, Any]:
        """生成风味描述"""
        profile = {
            'primary_flavors': [],
            'secondary_flavors': [],
            'flavor_intensity': 'medium',
            'flavor_balance': 'balanced',
            'overall_character': ''
        }
        
        # 分类风味
        for note in flavor_notes:
            found_category = False
            for category, flavors in self.flavor_wheel.items():
                if note in flavors:
                    if not found_category:
                        profile['primary_flavors'].append(note)
                        found_category = True
                    else:
                        profile['secondary_flavors'].append(note)
                    break
        
        # 生成整体特征描述
        if profile['primary_flavors']:
            profile['overall_character'] = f"以{', '.join(profile['primary_flavors'])}为主调"
            if profile['secondary_flavors']:
                profile['overall_character'] += f"，伴有{', '.join(profile['secondary_flavors'])}"
        
        return profile
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem], 
                               context: Dict = None) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['新手', '初学', 'beginner']):
            recommendations.append("建议从基础风味识别开始训练")
            recommendations.append("使用闻香瓶建立风味记忆")
            recommendations.append("定期进行简单杯测练习")
        
        if any(keyword in query_lower for keyword in ['训练', 'training']):
            recommendations.append("制定系统的训练计划")
            recommendations.append("保持训练的连续性")
            recommendations.append("记录训练进度和结果")
        
        if context and 'experience' in context:
            experience = context['experience']
            if experience == 'beginner':
                recommendations.append("从基础感官训练开始")
            elif experience == 'advanced':
                recommendations.append("挑战复杂风味识别")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem], 
                       context: Dict = None) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['感冒', '生病', 'ill']):
            warnings.append("身体不适时感官能力会下降，建议暂停品鉴")
        
        if any(keyword in query_lower for keyword in ['训练过度', 'over training']):
            warnings.append("过度训练可能导致感官疲劳，影响判断力")
        
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
            "SCA感官标准",
            "风味轮应用",
            "杯测技术",
            "香气评估",
            "酸质分析",
            "醇厚感评价",
            "感官训练",
            "缺陷识别",
            "风味描述",
            "感官评分"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        content = knowledge_item.content
        
        # 检查评分范围的合理性
        import re
        score_matches = re.findall(r'(\d+(?:\.\d+)?)\s*分', content)
        for score in score_matches:
            score_val = float(score)
            if score_val < 0 or score_val > 10:
                return False, f"评分{score_val}分超出合理范围(0-10分)"
        
        # 检查温度范围的合理性
        temp_matches = re.findall(r'(\d+)[°℃]', content)
        for temp in temp_matches:
            temp_val = int(temp)
            if temp_val < 0 or temp_val > 200:
                return False, f"温度值{temp_val}°C超出合理范围(0-200°C)"
        
        # 检查时间范围的合理性
        time_matches = re.findall(r'(\d+)\s*分钟', content)
        for time_val in time_matches:
            time_num = int(time_val)
            if time_num < 0 or time_num > 60:
                return False, f"时间值{time_num}分钟超出合理范围(0-60分钟)"
        
        return True, "验证通过"