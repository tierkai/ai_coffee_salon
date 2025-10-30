"""
知识涌现指标计算器
计算知识涌现过程中的各种量化指标
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import math
import logging
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MetricsCalculator:
    """知识涌现指标计算器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.knowledge_graph = {}
        self.temporal_data = []
        
    def calculate_diversity_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算知识多样性指标"""
        try:
            if not knowledge_items:
                return {}
            
            # 提取主题或关键词
            topics = []
            for item in knowledge_items:
                # 简单的关键词提取（实际应用中应使用NLP技术）
                text = item.get('content', '') + ' ' + item.get('title', '')
                words = text.lower().split()
                topics.extend([word for word in words if len(word) > 3])
            
            # 计算主题分布
            topic_counts = Counter(topics)
            total_topics = len(topics)
            
            if total_topics == 0:
                return {"diversity_score": 0.0}
            
            # 香农多样性指数
            shannon_diversity = -sum((count/total_topics) * math.log2(count/total_topics) 
                                   for count in topic_counts.values() if count > 0)
            
            # 辛普森多样性指数
            simpson_diversity = 1 - sum((count/total_topics)**2 for count in topic_counts.values())
            
            # 基尼系数（不平等程度）
            sorted_counts = sorted(topic_counts.values())
            n = len(sorted_counts)
            cumsum = np.cumsum(sorted_counts)
            gini = (2 * sum((i+1) * count for i, count in enumerate(sorted_counts))) / (n * sum(sorted_counts)) - (n+1) / n
            
            return {
                "shannon_diversity": round(shannon_diversity, 4),
                "simpson_diversity": round(simpson_diversity, 4),
                "gini_coefficient": round(gini, 4),
                "unique_topics": len(topic_counts),
                "total_topics": total_topics,
                "diversity_score": round(shannon_diversity / math.log2(len(topic_counts) + 1), 4)
            }
            
        except Exception as e:
            self.logger.error(f"计算多样性指标失败: {e}")
            return {}
    
    def calculate_connectivity_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算知识连接性指标"""
        try:
            if not knowledge_items:
                return {}
            
            # 构建简单的引用网络
            connections = defaultdict(set)
            all_concepts = set()
            
            for i, item in enumerate(knowledge_items):
                text = item.get('content', '') + ' ' + item.get('title', '')
                words = set(word.lower() for word in text.split() if len(word) > 3)
                all_concepts.update(words)
                
                # 简单的概念共现
                for j, other_item in enumerate(knowledge_items):
                    if i != j:
                        other_text = other_item.get('content', '') + ' ' + other_item.get('title', '')
                        other_words = set(word.lower() for word in other_text.split() if len(word) > 3)
                        
                        # 计算概念重叠
                        common_concepts = words.intersection(other_words)
                        if len(common_concepts) > 0:
                            connections[i].update([j] * len(common_concepts))
            
            # 计算网络指标
            n_items = len(knowledge_items)
            if n_items <= 1:
                return {"connectivity_score": 0.0}
            
            # 平均连接度
            total_connections = sum(len(conns) for conns in connections.values())
            avg_connectivity = total_connections / n_items if n_items > 0 else 0
            
            # 网络密度
            max_connections = n_items * (n_items - 1)
            network_density = total_connections / max_connections if max_connections > 0 else 0
            
            # 聚类系数
            clustering_coeffs = []
            for i in range(n_items):
                neighbors = connections[i]
                if len(neighbors) <= 1:
                    continue
                
                # 计算邻居之间的连接
                neighbor_connections = 0
                possible_connections = len(neighbors) * (len(neighbors) - 1) / 2
                
                for neighbor1 in neighbors:
                    for neighbor2 in neighbors:
                        if neighbor1 < neighbor2 and neighbor2 in connections[neighbor1]:
                            neighbor_connections += 1
                
                if possible_connections > 0:
                    clustering_coeffs.append(neighbor_connections / possible_connections)
            
            avg_clustering = np.mean(clustering_coeffs) if clustering_coeffs else 0
            
            return {
                "avg_connectivity": round(avg_connectivity, 4),
                "network_density": round(network_density, 4),
                "avg_clustering_coefficient": round(avg_clustering, 4),
                "total_connections": total_connections,
                "connectivity_score": round(network_density * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"计算连接性指标失败: {e}")
            return {}
    
    def calculate_complexity_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算知识复杂性指标"""
        try:
            if not knowledge_items:
                return {}
            
            complexities = []
            
            for item in knowledge_items:
                text = item.get('content', '') + ' ' + item.get('title', '')
                
                if not text.strip():
                    continue
                
                # 词汇复杂性
                words = text.split()
                unique_words = set(word.lower() for word in words)
                word_diversity = len(unique_words) / len(words) if words else 0
                
                # 句子复杂性
                sentences = text.split('.')
                avg_sentence_length = len(words) / len(sentences) if sentences else 0
                
                # 概念密度
                concept_words = [word for word in words if len(word) > 5]
                concept_density = len(concept_words) / len(words) if words else 0
                
                # 结构复杂性（基于标点符号）
                punctuation_count = sum(1 for char in text if char in '.,;:!?()[]{}')
                structural_complexity = punctuation_count / len(text) if text else 0
                
                item_complexity = (
                    word_diversity * 0.3 +
                    min(avg_sentence_length / 20, 1) * 0.3 +
                    concept_density * 0.2 +
                    structural_complexity * 0.2
                )
                
                complexities.append(item_complexity)
            
            if not complexities:
                return {"complexity_score": 0.0}
            
            return {
                "avg_complexity": round(np.mean(complexities), 4),
                "max_complexity": round(max(complexities), 4),
                "min_complexity": round(min(complexities), 4),
                "complexity_std": round(np.std(complexities), 4),
                "complexity_score": round(np.mean(complexities) * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"计算复杂性指标失败: {e}")
            return {}
    
    def calculate_emergence_metrics(self, knowledge_items: List[Dict[str, Any]], 
                                  temporal_order: bool = True) -> Dict[str, float]:
        """计算涌现性指标"""
        try:
            if not knowledge_items:
                return {}
            
            if temporal_order:
                # 按时间排序
                sorted_items = sorted(knowledge_items, 
                                    key=lambda x: x.get('_collection_time', ''))
            else:
                sorted_items = knowledge_items
            
            # 计算知识增长模式
            knowledge_growth = []
            concept_evolution = []
            
            all_concepts = set()
            window_size = max(1, len(sorted_items) // 10)  # 滑动窗口大小
            
            for i in range(0, len(sorted_items), window_size):
                window_items = sorted_items[i:i + window_size]
                window_concepts = set()
                
                for item in window_items:
                    text = item.get('content', '') + ' ' + item.get('title', '')
                    concepts = set(word.lower() for word in text.split() if len(word) > 3)
                    window_concepts.update(concepts)
                
                knowledge_growth.append(len(window_concepts))
                
                if i > 0:
                    prev_concepts = concept_evolution[-1] if concept_evolution else set()
                    new_concepts = window_concepts - prev_concepts
                    concept_evolution.append(new_concepts)
                else:
                    concept_evolution.append(window_concepts)
            
            # 计算涌现强度
            if len(knowledge_growth) < 2:
                emergence_intensity = 0
            else:
                # 使用变化率来衡量涌现强度
                growth_rates = []
                for i in range(1, len(knowledge_growth)):
                    if knowledge_growth[i-1] > 0:
                        rate = (knowledge_growth[i] - knowledge_growth[i-1]) / knowledge_growth[i-1]
                        growth_rates.append(rate)
                
                emergence_intensity = np.mean(growth_rates) if growth_rates else 0
            
            # 计算概念创新度
            total_new_concepts = sum(len(concepts) for concepts in concept_evolution)
            total_concepts = len(set().union(*concept_evolution)) if concept_evolution else 0
            innovation_rate = total_new_concepts / total_concepts if total_concepts > 0 else 0
            
            # 计算知识整合度（概念重叠程度）
            integration_scores = []
            for i in range(len(concept_evolution)):
                for j in range(i + 1, len(concept_evolution)):
                    overlap = len(concept_evolution[i].intersection(concept_evolution[j]))
                    union = len(concept_evolution[i].union(concept_evolution[j]))
                    if union > 0:
                        jaccard = overlap / union
                        integration_scores.append(jaccard)
            
            avg_integration = np.mean(integration_scores) if integration_scores else 0
            
            return {
                "emergence_intensity": round(emergence_intensity, 4),
                "innovation_rate": round(innovation_rate, 4),
                "avg_integration": round(avg_integration, 4),
                "knowledge_growth_trend": knowledge_growth,
                "total_growth_points": len(knowledge_growth),
                "emergence_score": round((emergence_intensity + innovation_rate + avg_integration) / 3 * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"计算涌现性指标失败: {e}")
            return {}
    
    def calculate_coherence_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算知识连贯性指标"""
        try:
            if not knowledge_items or len(knowledge_items) < 2:
                return {"coherence_score": 0.0}
            
            # 提取所有文本
            texts = []
            for item in knowledge_items:
                text = item.get('content', '') + ' ' + item.get('title', '')
                if text.strip():
                    texts.append(text)
            
            if len(texts) < 2:
                return {"coherence_score": 0.0}
            
            # 使用TF-IDF计算文本相似性
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 计算余弦相似性矩阵
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 计算平均相似性（排除对角线）
            n = len(texts)
            similarities = []
            for i in range(n):
                for j in range(i + 1, n):
                    similarities.append(similarity_matrix[i][j])
            
            avg_similarity = np.mean(similarities) if similarities else 0
            
            # 计算连贯性变化趋势
            coherence_trend = []
            window_size = max(2, len(similarities) // 5)
            
            for i in range(0, len(similarities), window_size):
                window = similarities[i:i + window_size]
                if window:
                    coherence_trend.append(np.mean(window))
            
            # 计算连贯性稳定性
            coherence_std = np.std(coherence_trend) if coherence_trend else 0
            
            return {
                "avg_similarity": round(avg_similarity, 4),
                "coherence_trend": coherence_trend,
                "coherence_stability": round(1 / (1 + coherence_std), 4),  # 转换为稳定性分数
                "max_similarity": round(max(similarities), 4) if similarities else 0,
                "min_similarity": round(min(similarities), 4) if similarities else 0,
                "coherence_score": round(avg_similarity * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"计算连贯性指标失败: {e}")
            return {}
    
    def calculate_impact_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算知识影响力指标"""
        try:
            if not knowledge_items:
                return {"impact_score": 0.0}
            
            impact_scores = []
            
            for item in knowledge_items:
                # 基础影响力指标
                text = item.get('content', '') + ' ' + item.get('title', '')
                word_count = len(text.split())
                
                # 引用次数（如果有）
                citations = item.get('citations', 0)
                
                # 重要性标记
                importance = item.get('importance', 0)
                
                # 时间因子（新知识通常更有影响力）
                collection_time = item.get('_collection_time', '')
                if collection_time:
                    try:
                        time_obj = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
                        days_old = (datetime.now() - time_obj.replace(tzinfo=None)).days
                        time_factor = max(0, 1 - days_old / 365)  # 一年内的知识
                    except:
                        time_factor = 0.5
                else:
                    time_factor = 0.5
                
                # 综合影响力计算
                base_score = min(word_count / 1000, 1) * 0.3  # 文本长度因子
                citation_score = min(citations / 100, 1) * 0.3  # 引用因子
                importance_score = min(importance / 10, 1) * 0.3  # 重要性因子
                time_score = time_factor * 0.1  # 时间因子
                
                item_impact = base_score + citation_score + importance_score + time_score
                impact_scores.append(item_impact)
            
            return {
                "avg_impact": round(np.mean(impact_scores), 4),
                "max_impact": round(max(impact_scores), 4),
                "min_impact": round(min(impact_scores), 4),
                "impact_std": round(np.std(impact_scores), 4),
                "high_impact_count": len([score for score in impact_scores if score > 0.7]),
                "impact_score": round(np.mean(impact_scores) * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"计算影响力指标失败: {e}")
            return {}
    
    def calculate_all_metrics(self, knowledge_items: List[Dict[str, Any]], 
                            temporal_order: bool = True) -> Dict[str, Any]:
        """计算所有指标"""
        self.logger.info("开始计算知识涌现指标...")
        
        results = {}
        
        # 多样性指标
        results['diversity'] = self.calculate_diversity_metrics(knowledge_items)
        
        # 连接性指标
        results['connectivity'] = self.calculate_connectivity_metrics(knowledge_items)
        
        # 复杂性指标
        results['complexity'] = self.calculate_complexity_metrics(knowledge_items)
        
        # 涌现性指标
        results['emergence'] = self.calculate_emergence_metrics(knowledge_items, temporal_order)
        
        # 连贯性指标
        results['coherence'] = self.calculate_coherence_metrics(knowledge_items)
        
        # 影响力指标
        results['impact'] = self.calculate_impact_metrics(knowledge_items)
        
        # 综合评分
        scores = []
        for category in results.values():
            if 'score' in category:
                scores.append(category['score'])
        
        results['overall'] = {
            'total_score': round(np.mean(scores), 2) if scores else 0,
            'score_breakdown': {k: v.get('score', 0) for k, v in results.items() if isinstance(v, dict)},
            'calculation_time': datetime.now().isoformat(),
            'data_points': len(knowledge_items)
        }
        
        self.logger.info("指标计算完成")
        return results
    
    def compare_periods(self, period1_data: List[Dict[str, Any]], 
                       period2_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """比较不同时期的知识涌现指标"""
        try:
            metrics1 = self.calculate_all_metrics(period1_data)
            metrics2 = self.calculate_all_metrics(period2_data)
            
            comparison = {}
            
            for category in ['diversity', 'connectivity', 'complexity', 'emergence', 'coherence', 'impact']:
                if category in metrics1 and category in metrics2:
                    score1 = metrics1[category].get('score', 0)
                    score2 = metrics2[category].get('score', 0)
                    
                    if score1 > 0:
                        change_rate = (score2 - score1) / score1
                    else:
                        change_rate = score2  # 如果基线为0，直接使用新值
                    
                    comparison[f'{category}_change'] = round(change_rate, 4)
                    comparison[f'{category}_improvement'] = score2 > score1
            
            # 总体改善情况
            overall1 = metrics1.get('overall', {}).get('total_score', 0)
            overall2 = metrics2.get('overall', {}).get('total_score', 0)
            
            if overall1 > 0:
                overall_change = (overall2 - overall1) / overall1
            else:
                overall_change = overall2
            
            comparison['overall_change'] = round(overall_change, 4)
            comparison['overall_improvement'] = overall2 > overall1
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"比较时期指标失败: {e}")
            return {}