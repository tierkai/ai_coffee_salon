"""
产区专家智能体
负责咖啡产区、品种、产地特性等专业知识
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..core.base_agent import BaseExpertAgent, ExpertResponse, KnowledgeItem, ExpertLevel, KnowledgeQuality

logger = logging.getLogger(__name__)


class OriginExpertAgent(BaseExpertAgent):
    """产区专家智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="origin_expert_001",
            name="产区专家",
            specialty="咖啡产区与品种",
            level=ExpertLevel.EXPERT
        )
    
    def _initialize_knowledge_base(self):
        """初始化产区专业知识库"""
        # 世界主要咖啡产区知识
        origin_knowledge = [
            {
                'id': 'origin_ethiopia',
                'content': '埃塞俄比亚是咖啡的发源地，拥有丰富的原生品种。主要产区包括耶加雪菲、西达摩、哈拉尔等。耶加雪菲以其花香和果酸闻名，是世界上最优质的咖啡之一。',
                'source': '国际咖啡组织',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['埃塞俄比亚', '耶加雪菲', '发源地', '花香', '果酸'],
                'references': ['SCA咖啡感官词典', '国际咖啡研究']
            },
            {
                'id': 'origin_colombia',
                'content': '哥伦比亚是世界第二大咖啡生产国，以其平衡的风味和优质的口感著称。主要产区包括Huila、Narino、Antioquia等。哥伦比亚咖啡通常具有坚果、巧克力和水果的风味特征。',
                'source': '哥伦比亚咖啡种植者联合会',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['哥伦比亚', 'Huila', 'Narino', '平衡', '坚果', '巧克力'],
                'references': ['哥伦比亚咖啡品质指南']
            },
            {
                'id': 'origin_brazil',
                'content': '巴西是世界最大的咖啡生产国，主要生产阿拉比卡和罗布斯塔咖啡。产区包括Minas Gerais、Sao Paulo、Parana等。巴西咖啡通常口感醇厚，适合制作意式浓缩。',
                'source': '巴西咖啡出口协会',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['巴西', 'Minas Gerais', '醇厚', '意式浓缩', '最大生产国'],
                'references': ['巴西咖啡产业报告']
            },
            {
                'id': 'origin_panama',
                'content': '巴拿马以其独特的Geisha（艺伎）品种闻名于世。巴拿马Geisha具有花香、柑橘和茶-like的风味，在拍卖会上经常创下高价记录。',
                'source': '巴拿马精品咖啡协会',
                'confidence': 0.94,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['巴拿马', 'Geisha', '艺伎', '花香', '柑橘', '高价'],
                'references': ['BOP最佳巴拿马咖啡竞赛']
            },
            {
                'id': 'origin_kenya',
                'content': '肯尼亚咖啡以其强烈的酸质和复杂的果香著称。主要产区包括Nyeri、Kiambu、Murang\\'a等。肯尼亚咖啡通常具有黑加仑、番茄和葡萄酒的风味特征。',
                'source': '肯尼亚咖啡委员会',
                'confidence': 0.91,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['肯尼亚', '酸质', '果香', '黑加仑', '番茄', '葡萄酒'],
                'references': ['肯尼亚咖啡品质标准']
            },
            {
                'id': 'variety_arabica',
                'content': '阿拉比卡咖啡占全球咖啡产量的70%左右，具有优质的风味特征。生长在海拔600-2000米的高地，对气候条件要求较高。主要品种包括Typica、Bourbon、Geisha等。',
                'source': '国际咖啡研究组织',
                'confidence': 0.96,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['阿拉比卡', 'Typica', 'Bourbon', 'Geisha', '高海拔', '优质风味'],
                'references': ['咖啡品种学手册']
            },
            {
                'id': 'variety_robusta',
                'content': '罗布斯塔咖啡占全球产量的30%左右，含有更高的咖啡因，抗病能力强。主要用于制作速溶咖啡和意式浓缩的拼配。风味较为粗糙，酸质较低。',
                'source': '国际咖啡组织',
                'confidence': 0.95,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['罗布斯塔', '咖啡因', '抗病', '速溶咖啡', '拼配'],
                'references': ['咖啡品种比较研究']
            },
            {
                'id': 'processing_washed',
                'content': '水洗法处理能产生干净、明亮的风味特征。过程包括脱皮、发酵、洗涤和干燥。适合在湿度较高的产区使用，能突出咖啡的酸质和香气。',
                'source': '咖啡处理技术手册',
                'confidence': 0.93,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['水洗法', '干净', '明亮', '酸质', '香气'],
                'references': ['咖啡加工技术指南']
            },
            {
                'id': 'processing_natural',
                'content': '日晒法处理能产生甜感丰富、口感醇厚的咖啡。过程包括直接晾晒带壳豆。适合在干燥的产区使用，能增强咖啡的果香和甜味。',
                'source': '咖啡处理技术手册',
                'confidence': 0.92,
                'quality': KnowledgeQuality.HIGH,
                'tags': ['日晒法', '甜感', '醇厚', '果香', '干燥产区'],
                'references': ['咖啡加工技术指南']
            },
            {
                'id': 'processing_honey',
                'content': '蜜处理法是介于水洗和日晒之间的处理方法，能产生独特的甜味和复杂的风味。根据保留果胶的多少分为白蜜、黄蜜、红蜜、黑蜜。',
                'source': '中美洲咖啡研究所',
                'confidence': 0.90,
                'quality': KnowledgeQuality.MEDIUM,
                'tags': ['蜜处理', '甜味', '复杂', '白蜜', '黄蜜', '红蜜', '黑蜜'],
                'references': ['蜜处理技术研究']
            }
        ]
        
        # 添加知识项到知识库
        for item_data in origin_knowledge:
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
        
        logger.info(f"产区专家知识库初始化完成，共{len(origin_knowledge)}个知识项")
    
    def process_query(self, query: str, context: Dict = None) -> ExpertResponse:
        """处理产区相关查询"""
        start_time = datetime.now()
        
        try:
            # 搜索相关知识
            relevant_knowledge = self.search_knowledge(query, limit=10)
            
            # 生成专业回答
            response_content = self._generate_response(query, relevant_knowledge, context)
            
            # 提取推荐建议
            recommendations = self._extract_recommendations(query, relevant_knowledge)
            
            # 检查警告
            warnings = self._check_warnings(query, relevant_knowledge)
            
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
            logger.error(f"产区专家处理查询失败: {e}")
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ExpertResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f抱歉，处理您的查询时出现错误: {str(e)}",
                confidence=0.0,
                processing_time=response_time
            )
    
    def _generate_response(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """生成专业回答"""
        query_lower = query.lower()
        
        # 根据查询类型生成回答
        if any(keyword in query_lower for keyword in ['产区', '产地', 'origin']):
            return self._handle_origin_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['品种', 'variety', 'arabica', 'robusta']):
            return self._handle_variety_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['处理', 'processing', '水洗', '日晒', '蜜处理']):
            return self._handle_processing_query(query, knowledge, context)
        elif any(keyword in query_lower for keyword in ['风味', 'flavor', '特征', '特点']):
            return self._handle_flavor_query(query, knowledge, context)
        else:
            return self._handle_general_query(query, knowledge, context)
    
    def _handle_origin_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理产区查询"""
        response = "关于咖啡产区，我来为您详细介绍：\n\n"
        
        # 查找相关产区知识
        origin_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                          ['埃塞俄比亚', '哥伦比亚', '巴西', '巴拿马', '肯尼亚'])]
        
        for item in origin_knowledge[:3]:  # 最多显示3个产区
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "选择咖啡产区时，建议考虑以下因素：\n"
        response += "1. 风味偏好 - 不同产区具有独特的风味特征\n"
        response += "2. 烘焙程度 - 某些产区更适合特定的烘焙程度\n"
        response += "3. 处理方法 - 产区常用的处理方法影响最终风味\n"
        response += "4. 季节性 - 了解产区的收获季节\n"
        
        return response
    
    def _handle_variety_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理品种查询"""
        response = "关于咖啡品种，我来为您详细说明：\n\n"
        
        # 查找品种相关知识
        variety_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                           ['阿拉比卡', '罗布斯塔', 'Typica', 'Bourbon', 'Geisha'])]
        
        for item in variety_knowledge:
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "品种选择建议：\n"
        response += "1. 阿拉比卡适合精品咖啡，风味更佳\n"
        response += "2. 罗布斯塔咖啡因含量高，适合意式拼配\n"
        response += "3. 了解品种的种植要求和适应性\n"
        response += "4. 考虑品种的市场接受度和价格\n"
        
        return response
    
    def _handle_processing_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理处理方法查询"""
        response = "关于咖啡处理方法，我来为您详细解释：\n\n"
        
        # 查找处理方法相关知识
        processing_knowledge = [k for k in knowledge if any(tag in k.tags for tag in 
                              ['水洗法', '日晒法', '蜜处理'])]
        
        for item in processing_knowledge:
            response += f"**{item.tags[0]}**\n{item.content}\n\n"
        
        response += "处理方法选择指南：\n"
        response += "1. 水洗法 - 产生干净明亮的口感\n"
        response += "2. 日晒法 - 增强甜感和果香\n"
        response += "3. 蜜处理 - 平衡甜味和复杂度\n"
        response += "4. 考虑当地气候条件和设备\n"
        
        return response
    
    def _handle_flavor_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理风味查询"""
        response = "关于咖啡风味特征，我来为您详细描述：\n\n"
        
        # 提取风味描述
        flavor_descriptions = []
        for item in knowledge:
            for tag in item.tags:
                if tag in ['花香', '果酸', '坚果', '巧克力', '柑橘', '黑加仑']:
                    flavor_descriptions.append((tag, item.content))
        
        for flavor, description in flavor_descriptions[:5]:
            response += f"**{flavor}特征**: {description}\n\n"
        
        response += "风味品鉴要点：\n"
        response += "1. 香气 - 干香和湿香的差异\n"
        response += "2. 酸质 - 明亮度、复杂度、愉悦度\n"
        response += "3. 甜感 - 甜味的类型和强度\n"
        response += "4. 醇厚 - 口感和body的感知\n"
        response += "5. 余韵 - 回味的持续性和质量\n"
        
        return response
    
    def _handle_general_query(self, query: str, knowledge: List[KnowledgeItem], context: Dict) -> str:
        """处理一般查询"""
        response = f"作为产区专家，我很高兴为您解答关于咖啡产区、品种和处理方法的问题。\n\n"
        
        if knowledge:
            response += "基于我的专业知识，我为您整理了相关信息：\n\n"
            for item in knowledge[:3]:
                response += f"• {item.content}\n\n"
        
        response += "如果您有具体的产区、品种或处理方法的问题，请详细描述，我会为您提供更专业的指导。"
        
        return response
    
    def _extract_recommendations(self, query: str, knowledge: List[KnowledgeItem]) -> List[str]:
        """提取推荐建议"""
        recommendations = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['推荐', '建议', '选择']):
            recommendations.append("建议选择知名产区的优质咖啡豆")
            recommendations.append("考虑个人风味偏好进行选择")
            recommendations.append("了解产区的处理方法和烘焙程度")
        
        if any(keyword in query_lower for keyword in ['新手', '初学']):
            recommendations.append("新手建议从温和的风味开始")
            recommendations.append("选择处理方法简单的产区")
            recommendations.append("避免过于复杂或极端的风味")
        
        return recommendations
    
    def _check_warnings(self, query: str, knowledge: List[KnowledgeItem]) -> List[str]:
        """检查警告信息"""
        warnings = []
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['便宜', '低价', '廉价']):
            warnings.append("低价咖啡可能存在品质问题，请注意甄别")
        
        if any(keyword in query_lower for keyword in ['保存', '储存']):
            warnings.append("咖啡豆应储存在阴凉干燥处，避免光照和潮湿")
        
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
            "世界咖啡产区",
            "咖啡品种学",
            "咖啡处理方法",
            "产区风味特征",
            "咖啡贸易",
            "可持续种植",
            "产区气候影响",
            "品种适应性",
            "品质评估",
            "市场分析"
        ]
    
    def _validate_domain_specific_knowledge(self, knowledge_item: KnowledgeItem) -> tuple:
        """专业知识验证"""
        # 验证产区信息的准确性
        valid_origins = ['埃塞俄比亚', '哥伦比亚', '巴西', '巴拿马', '肯尼亚', '牙买加', '哥斯达黎加']
        valid_varieties = ['阿拉比卡', '罗布斯塔', 'Typica', 'Bourbon', 'Geisha']
        valid_processing = ['水洗法', '日晒法', '蜜处理法']
        
        content = knowledge_item.content
        
        # 检查是否包含有效的产区、品种或处理方法
        has_valid_info = (
            any(origin in content for origin in valid_origins) or
            any(variety in content for variety in valid_varieties) or
            any(method in content for method in valid_processing)
        )
        
        if not has_valid_info:
            return False, "内容未包含有效的产区、品种或处理方法信息"
        
        # 检查置信度合理性
        if knowledge_item.confidence > 0.98:
            return False, "置信度过高，可能不准确"
        
        return True, "验证通过"