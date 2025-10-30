"""
知识价值评估器
评估知识的经济价值、社会价值和应用价值
"""

import math
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from dataclasses import dataclass
import json


@dataclass
class ValueAssessment:
    """价值评估结果"""
    economic_value: float
    social_value: float
    application_value: float
    innovation_value: float
    overall_value: float
    value_breakdown: Dict[str, Any]
    recommendations: List[str]
    risk_factors: List[str]


class ValueAssessor:
    """知识价值评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 价值评估权重
        self.value_weights = {
            'economic': 0.3,
            'social': 0.25,
            'application': 0.25,
            'innovation': 0.2
        }
        
        # 价值指示词和权重
        self.value_indicators = {
            'economic': {
                'high': ['商业价值', '市场潜力', '经济效益', '投资回报', '成本节约', '收入增长'],
                'medium': ['价值', '收益', '利润', '效率', '优化'],
                'low': ['花费', '成本', '支出', '损失']
            },
            'social': {
                'high': ['社会效益', '公共利益', '民生改善', '教育价值', '文化传承', '社会进步'],
                'medium': ['影响', '意义', '作用', '贡献', '帮助'],
                'low': ['问题', '风险', '挑战', '负面影响']
            },
            'application': {
                'high': ['实用价值', '应用前景', '技术成熟', '可实施', '解决方案', '工具'],
                'medium': ['应用', '使用', '实施', '操作', '实践'],
                'low': ['理论', '概念', '设想', '可能']
            },
            'innovation': {
                'high': ['创新突破', '原创性', '颠覆性', '前沿技术', '新兴领域', '突破性'],
                'medium': ['新颖', '独特', '改进', '优化', '发展'],
                'low': ['传统', '常规', '标准', '常见']
            }
        }
        
        # 行业价值基准
        industry_value_benchmarks = {
            'technology': {'base_value': 0.8, 'growth_potential': 0.9},
            'healthcare': {'base_value': 0.9, 'growth_potential': 0.8},
            'finance': {'base_value': 0.7, 'growth_potential': 0.7},
            'education': {'base_value': 0.6, 'growth_potential': 0.8},
            'manufacturing': {'base_value': 0.7, 'growth_potential': 0.6},
            'energy': {'base_value': 0.8, 'growth_potential': 0.9},
            'environment': {'base_value': 0.7, 'growth_potential': 0.8}
        }
        
        self.industry_benchmarks = config.get('industry_benchmarks', industry_value_benchmarks)
    
    def assess_economic_value(self, knowledge_item: Dict[str, Any], 
                            context: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """评估经济价值"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            economic_score = 0.0
            details = {}
            
            # 1. 商业价值指示词分析
            commercial_indicators = self._analyze_value_indicators(text, 'economic')
            details['commercial_indicators'] = commercial_indicators
            
            commercial_score = (
                commercial_indicators['high'] * 1.0 +
                commercial_indicators['medium'] * 0.6 +
                commercial_indicators['low'] * 0.2
            )
            commercial_score = min(commercial_score / 10, 1.0)  # 标准化
            details['commercial_score'] = round(commercial_score, 3)
            economic_score += commercial_score * 0.3
            
            # 2. 市场潜力评估
            market_potential = self._assess_market_potential(knowledge_item, context)
            details['market_potential'] = market_potential
            economic_score += market_potential * 0.25
            
            # 3. 成本效益分析
            cost_benefit = self._assess_cost_benefit(knowledge_item)
            details['cost_benefit'] = round(cost_benefit, 3)
            economic_score += cost_benefit * 0.2
            
            # 4. 投资价值评估
            investment_value = self._assess_investment_value(knowledge_item)
            details['investment_value'] = round(investment_value, 3)
            economic_score += investment_value * 0.15
            
            # 5. 行业价值基准
            industry_value = self._assess_industry_value(knowledge_item, context)
            details['industry_value'] = round(industry_value, 3)
            economic_score += industry_value * 0.1
            
            economic_score = max(0, min(1, economic_score))
            details['final_score'] = round(economic_score, 3)
            
            return economic_score, details
            
        except Exception as e:
            self.logger.error(f"评估经济价值失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_social_value(self, knowledge_item: Dict[str, Any], 
                          context: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """评估社会价值"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            social_score = 0.0
            details = {}
            
            # 1. 社会效益指示词分析
            social_indicators = self._analyze_value_indicators(text, 'social')
            details['social_indicators'] = social_indicators
            
            social_impact_score = (
                social_indicators['high'] * 1.0 +
                social_indicators['medium'] * 0.6 +
                social_indicators['low'] * 0.2
            )
            social_impact_score = min(social_impact_score / 10, 1.0)
            details['social_impact_score'] = round(social_impact_score, 3)
            social_score += social_impact_score * 0.35
            
            # 2. 公共利益评估
            public_benefit = self._assess_public_benefit(knowledge_item)
            details['public_benefit'] = round(public_benefit, 3)
            social_score += public_benefit * 0.25
            
            # 3. 教育价值评估
            educational_value = self._assess_educational_value(knowledge_item)
            details['educational_value'] = round(educational_value, 3)
            social_score += educational_value * 0.2
            
            # 4. 文化价值评估
            cultural_value = self._assess_cultural_value(knowledge_item)
            details['cultural_value'] = round(cultural_value, 3)
            social_score += cultural_value * 0.1
            
            # 5. 社会影响范围
            impact_scope = self._assess_impact_scope(knowledge_item)
            details['impact_scope'] = round(impact_scope, 3)
            social_score += impact_scope * 0.1
            
            social_score = max(0, min(1, social_score))
            details['final_score'] = round(social_score, 3)
            
            return social_score, details
            
        except Exception as e:
            self.logger.error(f"评估社会价值失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_application_value(self, knowledge_item: Dict[str, Any], 
                               context: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """评估应用价值"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            application_score = 0.0
            details = {}
            
            # 1. 实用性指示词分析
            application_indicators = self._analyze_value_indicators(text, 'application')
            details['application_indicators'] = application_indicators
            
            practicality_score = (
                application_indicators['high'] * 1.0 +
                application_indicators['medium'] * 0.6 +
                application_indicators['low'] * 0.2
            )
            practicality_score = min(practicality_score / 10, 1.0)
            details['practicality_score'] = round(practicality_score, 3)
            application_score += practicality_score * 0.3
            
            # 2. 技术成熟度评估
            tech_maturity = self._assess_technology_maturity(knowledge_item)
            details['tech_maturity'] = round(tech_maturity, 3)
            application_score += tech_maturity * 0.25
            
            # 3. 可实施性评估
            feasibility = self._assess_feasibility(knowledge_item, context)
            details['feasibility'] = round(feasibility, 3)
            application_score += feasibility * 0.25
            
            # 4. 工具化潜力
            tool_potential = self._assess_tool_potential(knowledge_item)
            details['tool_potential'] = round(tool_potential, 3)
            application_score += tool_potential * 0.2
            
            application_score = max(0, min(1, application_score))
            details['final_score'] = round(application_score, 3)
            
            return application_score, details
            
        except Exception as e:
            self.logger.error(f"评估应用价值失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_innovation_value(self, knowledge_item: Dict[str, Any], 
                              context: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """评估创新价值"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            innovation_score = 0.0
            details = {}
            
            # 1. 创新性指示词分析
            innovation_indicators = self._analyze_value_indicators(text, 'innovation')
            details['innovation_indicators'] = innovation_indicators
            
            novelty_score = (
                innovation_indicators['high'] * 1.0 +
                innovation_indicators['medium'] * 0.6 +
                innovation_indicators['low'] * 0.2
            )
            novelty_score = min(novelty_score / 10, 1.0)
            details['novelty_score'] = round(novelty_score, 3)
            innovation_score += novelty_score * 0.3
            
            # 2. 原创性评估
            originality = self._assess_originality(knowledge_item)
            details['originality'] = round(originality, 3)
            innovation_score += originality * 0.25
            
            # 3. 颠覆性潜力
            disruption_potential = self._assess_disruption_potential(knowledge_item)
            details['disruption_potential'] = round(disruption_potential, 3)
            innovation_score += disruption_potential * 0.25
            
            # 4. 前沿性评估
            cutting_edge = self._assess_cutting_edge(knowledge_item, context)
            details['cutting_edge'] = round(cutting_edge, 3)
            innovation_score += cutting_edge * 0.2
            
            innovation_score = max(0, min(1, innovation_score))
            details['final_score'] = round(innovation_score, 3)
            
            return innovation_score, details
            
        except Exception as e:
            self.logger.error(f"评估创新价值失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_comprehensive_value(self, knowledge_item: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> ValueAssessment:
        """综合价值评估"""
        try:
            self.logger.info(f"开始综合评估知识项价值: {knowledge_item.get('title', 'Unknown')}")
            
            # 分别评估各个价值维度
            economic_value, economic_details = self.assess_economic_value(knowledge_item, context)
            social_value, social_details = self.assess_social_value(knowledge_item, context)
            application_value, application_details = self.assess_application_value(knowledge_item, context)
            innovation_value, innovation_details = self.assess_innovation_value(knowledge_item, context)
            
            # 计算加权总分
            overall_value = (
                economic_value * self.value_weights['economic'] +
                social_value * self.value_weights['social'] +
                application_value * self.value_weights['application'] +
                innovation_value * self.value_weights['innovation']
            )
            
            # 生成建议和风险因素
            recommendations = self._generate_recommendations(knowledge_item, {
                'economic': economic_value,
                'social': social_value,
                'application': application_value,
                'innovation': innovation_value,
                'overall': overall_value
            })
            
            risk_factors = self._identify_risk_factors(knowledge_item, {
                'economic': economic_value,
                'social': social_value,
                'application': application_value,
                'innovation': innovation_value
            })
            
            value_assessment = ValueAssessment(
                economic_value=round(economic_value, 3),
                social_value=round(social_value, 3),
                application_value=round(application_value, 3),
                innovation_value=round(innovation_value, 3),
                overall_value=round(overall_value, 3),
                value_breakdown={
                    'economic_details': economic_details,
                    'social_details': social_details,
                    'application_details': application_details,
                    'innovation_details': innovation_details,
                    'weights_used': self.value_weights,
                    'assessment_time': datetime.now().isoformat()
                },
                recommendations=recommendations,
                risk_factors=risk_factors
            )
            
            self.logger.info(f"综合价值评估完成，总体价值: {overall_value:.3f}")
            return value_assessment
            
        except Exception as e:
            self.logger.error(f"综合价值评估失败: {e}")
            return ValueAssessment(0, 0, 0, 0, 0, {"error": str(e)}, [], [])
    
    def assess_batch_value(self, knowledge_items: List[Dict[str, Any]], 
                         context: Dict[str, Any] = None) -> List[ValueAssessment]:
        """批量价值评估"""
        results = []
        
        for i, item in enumerate(knowledge_items):
            try:
                value_assessment = self.assess_comprehensive_value(item, context)
                results.append(value_assessment)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"已评估 {i + 1}/{len(knowledge_items)} 项")
                    
            except Exception as e:
                self.logger.error(f"评估第 {i} 项失败: {e}")
                # 添加默认低分
                results.append(ValueAssessment(0, 0, 0, 0, 0, {"error": str(e)}, [], []))
        
        return results
    
    def compare_value_dimensions(self, value_assessments: List[ValueAssessment]) -> Dict[str, Any]:
        """比较不同价值维度"""
        if not value_assessments:
            return {}
        
        # 提取各维度价值
        economic_values = [va.economic_value for va in value_assessments]
        social_values = [va.social_value for va in value_assessments]
        application_values = [va.application_value for va in value_assessments]
        innovation_values = [va.innovation_value for va in value_assessments]
        overall_values = [va.overall_value for va in value_assessments]
        
        comparison = {
            'dimension_averages': {
                'economic': round(sum(economic_values) / len(economic_values), 3),
                'social': round(sum(social_values) / len(social_values), 3),
                'application': round(sum(application_values) / len(application_values), 3),
                'innovation': round(sum(innovation_values) / len(innovation_values), 3),
                'overall': round(sum(overall_values) / len(overall_values), 3)
            },
            'dimension_ranges': {
                'economic': {'min': min(economic_values), 'max': max(economic_values)},
                'social': {'min': min(social_values), 'max': max(social_values)},
                'application': {'min': min(application_values), 'max': max(application_values)},
                'innovation': {'min': min(innovation_values), 'max': max(innovation_values)},
                'overall': {'min': min(overall_values), 'max': max(overall_values)}
            },
            'value_distribution': self._analyze_value_distribution(value_assessments),
            'high_value_items': len([va for va in value_assessments if va.overall_value >= 0.7]),
            'total_items': len(value_assessments)
        }
        
        return comparison
    
    def get_value_insights(self, value_assessments: List[ValueAssessment]) -> Dict[str, Any]:
        """获取价值洞察"""
        if not value_assessments:
            return {}
        
        insights = {
            'value_patterns': self._identify_value_patterns(value_assessments),
            'value_drivers': self._identify_value_drivers(value_assessments),
            'improvement_opportunities': self._identify_improvement_opportunities(value_assessments),
            'strategic_recommendations': self._generate_strategic_recommendations(value_assessments)
        }
        
        return insights
    
    # 私有方法：价值指标分析
    
    def _analyze_value_indicators(self, text: str, value_type: str) -> Dict[str, int]:
        """分析价值指示词"""
        indicators = {'high': 0, 'medium': 0, 'low': 0}
        
        if value_type not in self.value_indicators:
            return indicators
        
        text_lower = text.lower()
        
        for level, words in self.value_indicators[value_type].items():
            count = sum(1 for word in words if word in text_lower)
            indicators[level] = count
        
        return indicators
    
    def _assess_market_potential(self, knowledge_item: Dict[str, Any], 
                               context: Dict[str, Any] = None) -> float:
        """评估市场潜力"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 市场相关词汇
        market_indicators = ['市场', '需求', '用户', '客户', '商业', '产业', '行业']
        market_score = sum(1 for indicator in market_indicators if indicator in text)
        
        # 目标市场分析
        target_market = context.get('target_market', '') if context else ''
        if target_market:
            market_score += 2
        
        return min(market_score / 10, 1.0)
    
    def _assess_cost_benefit(self, knowledge_item: Dict[str, Any]) -> float:
        """评估成本效益"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 效益相关词汇
        benefit_words = ['效益', '收益', '节约', '效率', '优化', '改善']
        benefit_count = sum(1 for word in benefit_words if word in text)
        
        # 成本相关词汇
        cost_words = ['成本', '费用', '投入', '投资']
        cost_count = sum(1 for word in cost_words if word in text)
        
        if cost_count > 0:
            benefit_ratio = benefit_count / cost_count
            return min(benefit_ratio, 1.0)
        else:
            return min(benefit_count / 5, 1.0)
    
    def _assess_investment_value(self, knowledge_item: Dict[str, Any]) -> float:
        """评估投资价值"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 投资相关词汇
        investment_indicators = ['投资', '融资', '资本', '资金', '回报', '收益']
        investment_score = sum(1 for indicator in investment_indicators if indicator in text)
        
        # 时间因子
        collection_time = knowledge_item.get('_collection_time', '')
        time_factor = 0.5  # 默认时间因子
        
        if collection_time:
            try:
                time_obj = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
                days_old = (datetime.now() - time_obj.replace(tzinfo=None)).days
                # 较新的知识通常有更好的投资价值
                time_factor = max(0.3, 1 - days_old / 365)
            except:
                pass
        
        return min(investment_score / 5 * time_factor, 1.0)
    
    def _assess_industry_value(self, knowledge_item: Dict[str, Any], 
                             context: Dict[str, Any] = None) -> float:
        """评估行业价值"""
        # 检测行业类型
        industry = context.get('industry', 'general') if context else 'general'
        
        if industry in self.industry_benchmarks:
            benchmark = self.industry_benchmarks[industry]
            return benchmark['base_value']
        
        return 0.5  # 默认中等价值
    
    def _assess_public_benefit(self, knowledge_item: Dict[str, Any]) -> float:
        """评估公共利益"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 公共利益相关词汇
        public_indicators = ['公共', '社会', '大众', '全民', '普遍', '广泛']
        public_score = sum(1 for indicator in public_indicators if indicator in text)
        
        return min(public_score / 5, 1.0)
    
    def _assess_educational_value(self, knowledge_item: Dict[str, Any]) -> float:
        """评估教育价值"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 教育相关词汇
        education_indicators = ['教育', '学习', '培训', '知识', '技能', '能力', '理解']
        education_score = sum(1 for indicator in education_indicators if indicator in text)
        
        # 结构化程度
        structured_indicators = ['定义', '概念', '原理', '方法', '步骤', '框架']
        structure_score = sum(1 for indicator in structured_indicators if indicator in text)
        
        return min((education_score + structure_score) / 10, 1.0)
    
    def _assess_cultural_value(self, knowledge_item: Dict[str, Any]) -> float:
        """评估文化价值"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 文化相关词汇
        culture_indicators = ['文化', '传统', '历史', '遗产', '价值观', '精神']
        culture_score = sum(1 for indicator in culture_indicators if indicator in text)
        
        return min(culture_score / 5, 1.0)
    
    def _assess_impact_scope(self, knowledge_item: Dict[str, Any]) -> float:
        """评估影响范围"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 影响范围相关词汇
        scope_indicators = ['全球', '国际', '全国', '广泛', '深远', '重大']
        scope_score = sum(1 for indicator in scope_indicators if indicator in text)
        
        return min(scope_score / 5, 1.0)
    
    def _assess_technology_maturity(self, knowledge_item: Dict[str, Any]) -> float:
        """评估技术成熟度"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 成熟度指示词
        maturity_indicators = {
            'high': ['成熟', '稳定', '标准', '商业化', '规模化'],
            'medium': ['发展中', '改进', '优化', '完善'],
            'low': ['实验', '概念', '原型', '设想']
        }
        
        maturity_score = 0
        for level, indicators in maturity_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text)
            if level == 'high':
                maturity_score += count * 1.0
            elif level == 'medium':
                maturity_score += count * 0.6
            else:
                maturity_score -= count * 0.3
        
        return max(0, min(maturity_score / 5, 1.0))
    
    def _assess_feasibility(self, knowledge_item: Dict[str, Any], 
                          context: Dict[str, Any] = None) -> float:
        """评估可实施性"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 可实施性指示词
        feasibility_positive = ['可行', '容易', '简单', '直接', '立即', '快速']
        feasibility_negative = ['困难', '复杂', '困难', '耗时', '昂贵']
        
        positive_count = sum(1 for word in feasibility_positive if word in text)
        negative_count = sum(1 for word in feasibility_negative if word in text)
        
        feasibility_score = positive_count - negative_count * 0.5
        return max(0, min(feasibility_score / 5, 1.0))
    
    def _assess_tool_potential(self, knowledge_item: Dict[str, Any]) -> float:
        """评估工具化潜力"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 工具化指示词
        tool_indicators = ['工具', '软件', '系统', '平台', '框架', '库', '接口']
        tool_score = sum(1 for indicator in tool_indicators if indicator in text)
        
        return min(tool_score / 5, 1.0)
    
    def _assess_originality(self, knowledge_item: Dict[str, Any]) -> float:
        """评估原创性"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 原创性指示词
        originality_indicators = ['原创', '首创', '独特', '新颖', '首次', '独创']
        originality_score = sum(1 for indicator in originality_indicators if indicator in text)
        
        # 避免常见表述
        common_phrases = ['众所周知', '一般认为', '通常', '常见']
        common_count = sum(1 for phrase in common_phrases if phrase in text)
        
        originality_final = originality_score - common_count * 0.3
        return max(0, min(originality_final / 5, 1.0))
    
    def _assess_disruption_potential(self, knowledge_item: Dict[str, Any]) -> float:
        """评估颠覆性潜力"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 颠覆性指示词
        disruption_indicators = ['颠覆', '革命性', '突破性', '变革', '重新定义', '改变游戏规则']
        disruption_score = sum(1 for indicator in disruption_indicators if indicator in text)
        
        return min(disruption_score / 5, 1.0)
    
    def _assess_cutting_edge(self, knowledge_item: Dict[str, Any], 
                           context: Dict[str, Any] = None) -> float:
        """评估前沿性"""
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        # 前沿性指示词
        cutting_edge_indicators = ['前沿', '先进', '最新', '新兴', '未来', '下一代']
        cutting_edge_score = sum(1 for indicator in cutting_edge_indicators if indicator in text)
        
        # 时间因子
        collection_time = knowledge_item.get('_collection_time', '')
        time_factor = 0.5
        
        if collection_time:
            try:
                time_obj = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
                days_old = (datetime.now() - time_obj.replace(tzinfo=None)).days
                time_factor = max(0.3, 1 - days_old / 180)  # 半年内的知识
            except:
                pass
        
        return min(cutting_edge_score / 5 * time_factor, 1.0)
    
    # 辅助方法
    
    def _generate_recommendations(self, knowledge_item: Dict[str, Any], 
                                values: Dict[str, float]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        overall_value = values.get('overall', 0)
        economic_value = values.get('economic', 0)
        social_value = values.get('social', 0)
        application_value = values.get('application', 0)
        innovation_value = values.get('innovation', 0)
        
        if overall_value >= 0.8:
            recommendations.append("高价值知识，建议优先开发和应用")
        elif overall_value >= 0.6:
            recommendations.append("中等价值知识，可考虑进一步挖掘潜力")
        else:
            recommendations.append("价值较低，建议重新评估或寻找新的应用场景")
        
        if economic_value >= 0.7:
            recommendations.append("经济价值突出，建议寻找商业化机会")
        elif economic_value < 0.3:
            recommendations.append("经济价值有限，建议从其他维度寻找价值")
        
        if social_value >= 0.7:
            recommendations.append("社会价值显著，建议推广到更广泛的应用")
        elif social_value < 0.3:
            recommendations.append("社会价值不足，建议增强社会影响元素")
        
        if application_value >= 0.7:
            recommendations.append("应用价值高，建议快速推进实施")
        elif application_value < 0.3:
            recommendations.append("应用价值低，建议提高实用性")
        
        if innovation_value >= 0.7:
            recommendations.append("创新价值突出，建议保护知识产权")
        elif innovation_value < 0.3:
            recommendations.append("创新价值有限，建议寻找创新突破点")
        
        return recommendations
    
    def _identify_risk_factors(self, knowledge_item: Dict[str, Any], 
                             values: Dict[str, float]) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        overall_value = values.get('overall', 0)
        economic_value = values.get('economic', 0)
        social_value = values.get('social', 0)
        application_value = values.get('application', 0)
        innovation_value = values.get('innovation', 0)
        
        if overall_value < 0.5:
            risk_factors.append("总体价值偏低，存在投入产出不匹配风险")
        
        if economic_value < 0.3:
            risk_factors.append("经济价值不足，商业化风险较高")
        
        if social_value < 0.3:
            risk_factors.append("社会价值有限，公众接受度可能不高")
        
        if application_value < 0.3:
            risk_factors.append("应用价值不足，实施风险较大")
        
        if innovation_value < 0.3:
            risk_factors.append("创新价值有限，竞争力不足")
        
        # 检查文本中的风险提示
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        risk_keywords = ['风险', '挑战', '问题', '困难', '限制', '不足']
        if any(keyword in text for keyword in risk_keywords):
            risk_factors.append("知识内容本身包含风险提示，需要谨慎评估")
        
        return risk_factors
    
    def _analyze_value_distribution(self, value_assessments: List[ValueAssessment]) -> Dict[str, int]:
        """分析价值分布"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for va in value_assessments:
            if va.overall_value >= 0.7:
                distribution['high'] += 1
            elif va.overall_value >= 0.4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def _identify_value_patterns(self, value_assessments: List[ValueAssessment]) -> Dict[str, Any]:
        """识别价值模式"""
        patterns = {}
        
        # 分析价值维度相关性
        economic_values = [va.economic_value for va in value_assessments]
        social_values = [va.social_value for va in value_assessments]
        application_values = [va.application_value for va in value_assessments]
        innovation_values = [va.innovation_value for va in value_assessments]
        
        # 简单的相关性分析
        patterns['value_correlations'] = {
            'economic_social': self._calculate_correlation(economic_values, social_values),
            'economic_application': self._calculate_correlation(economic_values, application_values),
            'social_application': self._calculate_correlation(social_values, application_values)
        }
        
        # 识别价值主导模式
        dimension_strengths = []
        for va in value_assessments:
            strengths = {
                'economic': va.economic_value,
                'social': va.social_value,
                'application': va.application_value,
                'innovation': va.innovation_value
            }
            strongest_dimension = max(strengths, key=strengths.get)
            dimension_strengths.append(strongest_dimension)
        
        patterns['dominant_dimensions'] = dict(Counter(dimension_strengths))
        
        return patterns
    
    def _identify_value_drivers(self, value_assessments: List[ValueAssessment]) -> List[str]:
        """识别价值驱动因素"""
        drivers = []
        
        # 分析高价值项目的共同特征
        high_value_items = [va for va in value_assessments if va.overall_value >= 0.7]
        
        if not high_value_items:
            return ["数据不足，无法识别明确的驱动因素"]
        
        # 简化的驱动因素分析
        avg_economic = sum(va.economic_value for va in high_value_items) / len(high_value_items)
        avg_social = sum(va.social_value for va in high_value_items) / len(high_value_items)
        avg_application = sum(va.application_value for va in high_value_items) / len(high_value_items)
        avg_innovation = sum(va.innovation_value for va in high_value_items) / len(high_value_items)
        
        if avg_economic >= 0.6:
            drivers.append("经济价值是主要驱动因素")
        if avg_social >= 0.6:
            drivers.append("社会价值是主要驱动因素")
        if avg_application >= 0.6:
            drivers.append("应用价值是主要驱动因素")
        if avg_innovation >= 0.6:
            drivers.append("创新价值是主要驱动因素")
        
        return drivers if drivers else ["价值驱动因素不明确"]
    
    def _identify_improvement_opportunities(self, value_assessments: List[ValueAssessment]) -> List[str]:
        """识别改进机会"""
        opportunities = []
        
        # 分析低价值项目的改进空间
        low_value_items = [va for va in value_assessments if va.overall_value < 0.5]
        
        if not low_value_items:
            return ["当前知识价值水平较高，改进空间有限"]
        
        # 分析各维度短板
        avg_economic = sum(va.economic_value for va in low_value_items) / len(low_value_items)
        avg_social = sum(va.social_value for va in low_value_items) / len(low_value_items)
        avg_application = sum(va.application_value for va in low_value_items) / len(low_value_items)
        avg_innovation = sum(va.innovation_value for va in low_value_items) / len(low_value_items)
        
        min_dimension = min([
            ('economic', avg_economic),
            ('social', avg_social),
            ('application', avg_application),
            ('innovation', avg_innovation)
        ], key=lambda x: x[1])
        
        dimension_names = {
            'economic': '经济价值',
            'social': '社会价值',
            'application': '应用价值',
            'innovation': '创新价值'
        }
        
        opportunities.append(f"重点提升{dimension_names[min_dimension[0]]}，当前平均分仅为{min_dimension[1]:.2f}")
        
        return opportunities
    
    def _generate_strategic_recommendations(self, value_assessments: List[ValueAssessment]) -> List[str]:
        """生成战略建议"""
        recommendations = []
        
        if not value_assessments:
            return ["数据不足，无法生成战略建议"]
        
        # 总体价值分析
        overall_values = [va.overall_value for va in value_assessments]
        avg_overall = sum(overall_values) / len(overall_values)
        high_value_count = len([va for va in value_assessments if va.overall_value >= 0.7])
        
        if avg_overall >= 0.7:
            recommendations.append("整体价值水平较高，建议扩大投入规模")
        elif avg_overall >= 0.5:
            recommendations.append("整体价值水平中等，建议优化资源配置")
        else:
            recommendations.append("整体价值水平偏低，建议重新评估战略方向")
        
        if high_value_count / len(value_assessments) >= 0.3:
            recommendations.append("高价值项目占比较高，建议优先发展这些项目")
        else:
            recommendations.append("高价值项目占比较低，建议提高项目筛选标准")
        
        # 价值平衡分析
        dimension_averages = {
            'economic': sum(va.economic_value for va in value_assessments) / len(value_assessments),
            'social': sum(va.social_value for va in value_assessments) / len(value_assessments),
            'application': sum(va.application_value for va in value_assessments) / len(value_assessments),
            'innovation': sum(va.innovation_value for va in value_assessments) / len(value_assessments)
        }
        
        max_dimension = max(dimension_averages, key=dimension_averages.get)
        min_dimension = min(dimension_averages, key=dimension_averages.get)
        
        dimension_names = {
            'economic': '经济价值',
            'social': '社会价值',
            'application': '应用价值',
            'innovation': '创新价值'
        }
        
        recommendations.append(f"优势维度是{dimension_names[max_dimension]}，建议发挥优势")
        recommendations.append(f"薄弱维度是{dimension_names[min_dimension]}，建议加强投入")
        
        return recommendations
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """计算相关系数"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator