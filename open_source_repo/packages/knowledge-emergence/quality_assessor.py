"""
知识质量评估器
评估知识内容的质量、准确性和可靠性
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import math
from dataclasses import dataclass


@dataclass
class QualityScore:
    """质量评分结果"""
    overall_score: float
    accuracy_score: float
    completeness_score: float
    consistency_score: float
    credibility_score: float
    relevance_score: float
    details: Dict[str, Any]


class QualityAssessor:
    """知识质量评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 质量评估规则和权重
        self.quality_weights = {
            'accuracy': 0.25,
            'completeness': 0.20,
            'consistency': 0.20,
            'credibility': 0.20,
            'relevance': 0.15
        }
        
        # 可信度指示词
        self.credibility_indicators = {
            'high': ['研究', '实验', '数据', '统计', '证实', '验证', '发现', '分析'],
            'medium': ['认为', '建议', '可能', '似乎', '推测', '估计'],
            'low': ['据说', '听说', '传言', '据说', '可能', '也许']
        }
        
        # 准确性指示词
        self.accuracy_indicators = {
            'positive': ['准确', '正确', '精确', '确实', '的确', '证实'],
            'negative': ['错误', '不准', '虚假', '错误', '误导', '误解']
        }
        
        # 完整性检查项
        self.completeness_elements = [
            '定义', '解释', '原因', '结果', '例子', '数据', '引用'
        ]
    
    def assess_accuracy(self, knowledge_item: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """评估知识准确性"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            accuracy_score = 0.0
            details = {}
            
            # 1. 检查数值和事实的一致性
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                # 检查数字格式是否合理
                valid_numbers = 0
                for num in numbers:
                    try:
                        float(num)
                        valid_numbers += 1
                    except:
                        pass
                
                number_accuracy = valid_numbers / len(numbers) if numbers else 0
                details['number_accuracy'] = round(number_accuracy, 3)
                accuracy_score += number_accuracy * 0.3
            
            # 2. 检查逻辑一致性
            logical_indicators = self._check_logical_consistency(text)
            details.update(logical_indicators)
            accuracy_score += logical_indicators.get('consistency_score', 0) * 0.4
            
            # 3. 检查不确定性标记
            uncertainty_markers = ['可能', '也许', '据说', '传言', '推测']
            uncertainty_count = sum(1 for marker in uncertainty_markers if marker in text)
            uncertainty_penalty = min(uncertainty_count / len(text.split()) * 10, 0.3)
            
            details['uncertainty_penalty'] = round(uncertainty_penalty, 3)
            accuracy_score -= uncertainty_penalty
            
            # 4. 检查引用和来源
            source_quality = self._assess_source_quality(knowledge_item)
            details['source_quality'] = source_quality
            accuracy_score += source_quality * 0.3
            
            # 标准化分数到0-1范围
            accuracy_score = max(0, min(1, accuracy_score))
            details['final_score'] = round(accuracy_score, 3)
            
            return accuracy_score, details
            
        except Exception as e:
            self.logger.error(f"评估准确性失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_completeness(self, knowledge_item: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """评估知识完整性"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            completeness_score = 0.0
            details = {}
            
            # 1. 检查基本要素
            word_count = len(text.split())
            details['word_count'] = word_count
            
            # 文本长度评分
            if word_count >= 500:
                length_score = 1.0
            elif word_count >= 200:
                length_score = 0.7
            elif word_count >= 50:
                length_score = 0.4
            else:
                length_score = 0.1
            
            details['length_score'] = round(length_score, 3)
            completeness_score += length_score * 0.2
            
            # 2. 检查完整性要素
            element_scores = {}
            for element in self.completeness_elements:
                if element in text:
                    element_scores[element] = 1.0
                else:
                    element_scores[element] = 0.0
            
            details['element_scores'] = element_scores
            element_coverage = sum(element_scores.values()) / len(element_scores)
            completeness_score += element_coverage * 0.4
            
            # 3. 检查结构完整性
            structure_score = self._assess_structure_completeness(text)
            details['structure_score'] = round(structure_score, 3)
            completeness_score += structure_score * 0.2
            
            # 4. 检查上下文完整性
            context_score = self._assess_context_completeness(knowledge_item)
            details['context_score'] = round(context_score, 3)
            completeness_score += context_score * 0.2
            
            completeness_score = max(0, min(1, completeness_score))
            details['final_score'] = round(completeness_score, 3)
            
            return completeness_score, details
            
        except Exception as e:
            self.logger.error(f"评估完整性失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_consistency(self, knowledge_items: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """评估知识一致性"""
        try:
            if not knowledge_items:
                return 0.0, {"reason": "无知识项"}
            
            consistency_score = 0.0
            details = {}
            
            # 1. 提取所有关键概念
            all_concepts = set()
            concept_definitions = defaultdict(list)
            
            for item in knowledge_items:
                text = item.get('content', '') + ' ' + item.get('title', '')
                concepts = self._extract_concepts(text)
                
                for concept in concepts:
                    all_concepts.add(concept)
                    concept_definitions[concept].append(text)
            
            # 2. 检查概念定义的一致性
            concept_consistency = {}
            for concept, definitions in concept_definitions.items():
                if len(definitions) > 1:
                    consistency = self._compare_definitions(definitions)
                    concept_consistency[concept] = consistency
            
            details['concept_consistency'] = concept_consistency
            
            # 计算概念一致性平均分
            if concept_consistency:
                avg_concept_consistency = sum(concept_consistency.values()) / len(concept_consistency)
            else:
                avg_concept_consistency = 1.0
            
            consistency_score += avg_concept_consistency * 0.4
            
            # 3. 检查逻辑一致性
            logical_consistency = self._check_cross_item_consistency(knowledge_items)
            details['logical_consistency'] = round(logical_consistency, 3)
            consistency_score += logical_consistency * 0.3
            
            # 4. 检查数值一致性
            numerical_consistency = self._check_numerical_consistency(knowledge_items)
            details['numerical_consistency'] = round(numerical_consistency, 3)
            consistency_score += numerical_consistency * 0.3
            
            consistency_score = max(0, min(1, consistency_score))
            details['final_score'] = round(consistency_score, 3)
            
            return consistency_score, details
            
        except Exception as e:
            self.logger.error(f"评估一致性失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_credibility(self, knowledge_item: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """评估知识可信度"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            credibility_score = 0.0
            details = {}
            
            # 1. 检查可信度指示词
            credibility_indicators = self._check_credibility_indicators(text)
            details['credibility_indicators'] = credibility_indicators
            
            high_cred_words = len([word for word in self.credibility_indicators['high'] if word in text])
            medium_cred_words = len([word for word in self.credibility_indicators['medium'] if word in text])
            low_cred_words = len([word for word in self.credibility_indicators['low'] if word in text])
            
            indicator_score = (high_cred_words * 1.0 + medium_cred_words * 0.5 - low_cred_words * 0.8)
            indicator_score = max(0, min(1, indicator_score / 10))  # 标准化
            details['indicator_score'] = round(indicator_score, 3)
            credibility_score += indicator_score * 0.3
            
            # 2. 检查引用和来源
            source_score = self._assess_source_credibility(knowledge_item)
            details['source_score'] = round(source_score, 3)
            credibility_score += source_score * 0.4
            
            # 3. 检查语言客观性
            objectivity_score = self._assess_objectivity(text)
            details['objectivity_score'] = round(objectivity_score, 3)
            credibility_score += objectivity_score * 0.3
            
            credibility_score = max(0, min(1, credibility_score))
            details['final_score'] = round(credibility_score, 3)
            
            return credibility_score, details
            
        except Exception as e:
            self.logger.error(f"评估可信度失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_relevance(self, knowledge_item: Dict[str, Any], 
                        context: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """评估知识相关性"""
        try:
            text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
            
            if not text.strip():
                return 0.0, {"reason": "空文本内容"}
            
            relevance_score = 0.0
            details = {}
            
            # 1. 检查主题相关性
            if context and 'target_topics' in context:
                target_topics = context['target_topics']
                topic_relevance = self._calculate_topic_relevance(text, target_topics)
                details['topic_relevance'] = round(topic_relevance, 3)
                relevance_score += topic_relevance * 0.4
            else:
                relevance_score += 0.4  # 默认相关性
            
            # 2. 检查信息密度
            info_density = self._calculate_information_density(text)
            details['info_density'] = round(info_density, 3)
            relevance_score += info_density * 0.3
            
            # 3. 检查时效性
            timeliness = self._assess_timeliness(knowledge_item)
            details['timeliness'] = round(timeliness, 3)
            relevance_score += timeliness * 0.2
            
            # 4. 检查独特性
            uniqueness = self._assess_uniqueness(knowledge_item)
            details['uniqueness'] = round(uniqueness, 3)
            relevance_score += uniqueness * 0.1
            
            relevance_score = max(0, min(1, relevance_score))
            details['final_score'] = round(relevance_score, 3)
            
            return relevance_score, details
            
        except Exception as e:
            self.logger.error(f"评估相关性失败: {e}")
            return 0.0, {"error": str(e)}
    
    def assess_quality(self, knowledge_item: Dict[str, Any], 
                      context: Dict[str, Any] = None) -> QualityScore:
        """综合质量评估"""
        try:
            self.logger.info(f"开始评估知识项质量: {knowledge_item.get('title', 'Unknown')}")
            
            # 分别评估各个维度
            accuracy, accuracy_details = self.assess_accuracy(knowledge_item)
            completeness, completeness_details = self.assess_completeness(knowledge_item)
            credibility, credibility_details = self.assess_credibility(knowledge_item)
            relevance, relevance_details = self.assess_relevance(knowledge_item, context)
            
            # 一致性需要多个知识项
            consistency, consistency_details = self.assess_consistency([knowledge_item])
            
            # 计算加权总分
            overall_score = (
                accuracy * self.quality_weights['accuracy'] +
                completeness * self.quality_weights['completeness'] +
                consistency * self.quality_weights['consistency'] +
                credibility * self.quality_weights['credibility'] +
                relevance * self.quality_weights['relevance']
            )
            
            quality_score = QualityScore(
                overall_score=round(overall_score, 3),
                accuracy_score=round(accuracy, 3),
                completeness_score=round(completeness, 3),
                consistency_score=round(consistency, 3),
                credibility_score=round(credibility, 3),
                relevance_score=round(relevance, 3),
                details={
                    'accuracy_details': accuracy_details,
                    'completeness_details': completeness_details,
                    'consistency_details': consistency_details,
                    'credibility_details': credibility_details,
                    'relevance_details': relevance_details,
                    'assessment_time': datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"质量评估完成，总体得分: {overall_score:.3f}")
            return quality_score
            
        except Exception as e:
            self.logger.error(f"综合质量评估失败: {e}")
            return QualityScore(0, 0, 0, 0, 0, 0, {"error": str(e)})
    
    def assess_batch_quality(self, knowledge_items: List[Dict[str, Any]], 
                           context: Dict[str, Any] = None) -> List[QualityScore]:
        """批量质量评估"""
        results = []
        
        for i, item in enumerate(knowledge_items):
            try:
                quality_score = self.assess_quality(item, context)
                results.append(quality_score)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"已评估 {i + 1}/{len(knowledge_items)} 项")
                    
            except Exception as e:
                self.logger.error(f"评估第 {i} 项失败: {e}")
                # 添加默认低分
                results.append(QualityScore(0, 0, 0, 0, 0, 0, {"error": str(e)}))
        
        return results
    
    def get_quality_statistics(self, quality_scores: List[QualityScore]) -> Dict[str, Any]:
        """获取质量统计信息"""
        if not quality_scores:
            return {}
        
        scores = {
            'overall': [score.overall_score for score in quality_scores],
            'accuracy': [score.accuracy_score for score in quality_scores],
            'completeness': [score.completeness_score for score in quality_scores],
            'consistency': [score.consistency_score for score in quality_scores],
            'credibility': [score.credibility_score for score in quality_scores],
            'relevance': [score.relevance_score for score in quality_scores]
        }
        
        stats = {}
        for dimension, values in scores.items():
            if values:
                stats[dimension] = {
                    'mean': round(sum(values) / len(values), 3),
                    'max': max(values),
                    'min': min(values),
                    'std': round(math.sqrt(sum((x - sum(values)/len(values))**2 for x in values) / len(values), 3))
                }
        
        # 质量等级分布
        quality_levels = {'high': 0, 'medium': 0, 'low': 0}
        for score in quality_scores:
            if score.overall_score >= 0.8:
                quality_levels['high'] += 1
            elif score.overall_score >= 0.6:
                quality_levels['medium'] += 1
            else:
                quality_levels['low'] += 1
        
        stats['distribution'] = quality_levels
        stats['total_items'] = len(quality_scores)
        
        return stats
    
    # 辅助方法
    def _check_logical_consistency(self, text: str) -> Dict[str, Any]:
        """检查逻辑一致性"""
        # 简单的逻辑检查
        contradictions = []
        
        # 检查明显的矛盾表述
        contradiction_pairs = [
            ('总是', '从不'), ('所有', '没有'), ('肯定', '不确定'),
            ('绝对', '相对'), ('完全', '部分')
        ]
        
        for word1, word2 in contradiction_pairs:
            if word1 in text and word2 in text:
                contradictions.append((word1, word2))
        
        consistency_score = max(0, 1 - len(contradictions) * 0.2)
        
        return {
            'contradictions': contradictions,
            'consistency_score': consistency_score
        }
    
    def _assess_source_quality(self, knowledge_item: Dict[str, Any]) -> float:
        """评估来源质量"""
        # 检查是否有来源信息
        source = knowledge_item.get('source', '') or knowledge_item.get('author', '')
        
        if not source:
            return 0.3  # 无来源信息
        
        # 简单的来源质量评估
        high_quality_sources = ['研究', '学术', '官方', '权威']
        medium_quality_sources = ['新闻', '报道', '分析']
        
        source_lower = source.lower()
        if any(hq in source_lower for hq in high_quality_sources):
            return 0.9
        elif any(mq in source_lower for mq in medium_quality_sources):
            return 0.6
        else:
            return 0.4
    
    def _assess_structure_completeness(self, text: str) -> float:
        """评估结构完整性"""
        # 检查是否有清晰的结构标记
        structure_markers = ['首先', '其次', '最后', '总结', '结论', '因此', '所以']
        
        marker_count = sum(1 for marker in structure_markers if marker in text)
        structure_score = min(marker_count / 3, 1.0)  # 最多3个标记为满分
        
        return structure_score
    
    def _assess_context_completeness(self, knowledge_item: Dict[str, Any]) -> float:
        """评估上下文完整性"""
        # 检查是否有足够的上下文信息
        context_elements = ['背景', '原因', '结果', '影响', '意义']
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        
        context_count = sum(1 for element in context_elements if element in text)
        return min(context_count / len(context_elements), 1.0)
    
    def _extract_concepts(self, text: str) -> List[str]:
        """提取关键概念"""
        # 简单的概念提取（实际应用中应使用NLP技术）
        words = text.split()
        concepts = []
        
        for word in words:
            if len(word) > 3 and word.isalpha():
                concepts.append(word.lower())
        
        return concepts
    
    def _compare_definitions(self, definitions: List[str]) -> float:
        """比较定义的一致性"""
        if len(definitions) < 2:
            return 1.0
        
        # 简单的相似性比较
        similarities = []
        for i in range(len(definitions)):
            for j in range(i + 1, len(definitions)):
                # 计算共同词汇比例
                words1 = set(definitions[i].lower().split())
                words2 = set(definitions[j].lower().split())
                
                if words1 and words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                    similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0
    
    def _check_cross_item_consistency(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """检查跨项目一致性"""
        if len(knowledge_items) < 2:
            return 1.0
        
        # 提取所有文本
        all_texts = [item.get('content', '') + ' ' + item.get('title', '') for item in knowledge_items]
        
        # 检查重复内容的比例
        total_words = sum(len(text.split()) for text in all_texts)
        unique_words = len(set().union(*[set(text.lower().split()) for text in all_texts]))
        
        if total_words > 0:
            uniqueness = unique_words / total_words
            consistency = 1 - abs(uniqueness - 0.7)  # 期望70%的词汇是独特的
            return max(0, consistency)
        
        return 0
    
    def _check_numerical_consistency(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """检查数值一致性"""
        # 提取所有数值
        all_numbers = []
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            numbers = re.findall(r'\d+\.?\d*', text)
            all_numbers.extend([float(num) for num in numbers])
        
        if len(all_numbers) < 2:
            return 1.0
        
        # 检查数值范围是否合理
        if all_numbers:
            mean_val = sum(all_numbers) / len(all_numbers)
            std_val = math.sqrt(sum((x - mean_val)**2 for x in all_numbers) / len(all_numbers))
            
            # 变异系数
            cv = std_val / mean_val if mean_val > 0 else 0
            
            # 变异系数在0-1之间认为是一致的
            consistency = max(0, 1 - cv)
            return consistency
        
        return 0
    
    def _check_credibility_indicators(self, text: str) -> Dict[str, int]:
        """检查可信度指示词"""
        return {
            'high_credibility': len([word for word in self.credibility_indicators['high'] if word in text]),
            'medium_credibility': len([word for word in self.credibility_indicators['medium'] if word in text]),
            'low_credibility': len([word for word in self.credibility_indicators['low'] if word in text])
        }
    
    def _assess_source_credibility(self, knowledge_item: Dict[str, Any]) -> float:
        """评估来源可信度"""
        source = knowledge_item.get('source', '') or knowledge_item.get('author', '')
        
        if not source:
            return 0.3
        
        # 简化的来源可信度评估
        credible_patterns = ['大学', '研究所', '政府', '.org', '.edu', '研究']
        
        if any(pattern in source for pattern in credible_patterns):
            return 0.8
        else:
            return 0.4
    
    def _assess_objectivity(self, text: str) -> float:
        """评估客观性"""
        # 检查主观性词汇
        subjective_words = ['我认为', '我觉得', '相信', '认为', '应该', '可能']
        objective_indicators = ['数据', '研究', '实验', '统计', '分析', '显示']
        
        subjective_count = sum(1 for word in subjective_words if word in text)
        objective_count = sum(1 for word in objective_indicators if word in text)
        
        if subjective_count + objective_count > 0:
            objectivity = objective_count / (subjective_count + objective_count)
        else:
            objectivity = 0.5
        
        return objectivity
    
    def _calculate_topic_relevance(self, text: str, target_topics: List[str]) -> float:
        """计算主题相关性"""
        if not target_topics:
            return 0.5
        
        text_lower = text.lower()
        topic_matches = sum(1 for topic in target_topics if topic.lower() in text_lower)
        
        return topic_matches / len(target_topics)
    
    def _calculate_information_density(self, text: str) -> float:
        """计算信息密度"""
        words = text.split()
        if not words:
            return 0
        
        # 关键信息词汇比例
        info_words = ['数据', '研究', '发现', '结果', '分析', '统计', '实验']
        info_count = sum(1 for word in words if any(info_word in word for info_word in info_words))
        
        return min(info_count / len(words) * 5, 1.0)  # 标准化
    
    def _assess_timeliness(self, knowledge_item: Dict[str, Any]) -> float:
        """评估时效性"""
        collection_time = knowledge_item.get('_collection_time', '')
        
        if not collection_time:
            return 0.5
        
        try:
            time_obj = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
            days_old = (datetime.now() - time_obj.replace(tzinfo=None)).days
            
            # 一周内为1分，一个月内为0.8分，一年内为0.5分
            if days_old <= 7:
                return 1.0
            elif days_old <= 30:
                return 0.8
            elif days_old <= 365:
                return 0.5
            else:
                return 0.2
                
        except:
            return 0.5
    
    def _assess_uniqueness(self, knowledge_item: Dict[str, Any]) -> float:
        """评估独特性"""
        # 简单的独特性评估
        text = knowledge_item.get('content', '') + ' ' + knowledge_item.get('title', '')
        words = text.lower().split()
        
        # 检查不常见词汇比例
        if not words:
            return 0
        
        # 假设长度超过6的词汇为相对独特的
        unique_words = [word for word in words if len(word) > 6]
        uniqueness = len(unique_words) / len(words)
        
        return min(uniqueness * 2, 1.0)  # 标准化