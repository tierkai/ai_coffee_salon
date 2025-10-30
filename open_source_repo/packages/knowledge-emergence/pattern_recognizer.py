"""
知识涌现模式识别器
识别和分析知识涌现过程中的模式和规律
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.signal import find_peaks
import re


@dataclass
class Pattern:
    """知识涌现模式"""
    pattern_type: str
    description: str
    confidence: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    strength: float = 0.0
    supporting_evidence: List[str] = None
    metadata: Dict[str, Any] = None


class PatternRecognizer:
    """知识涌现模式识别器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 模式识别参数
        self.min_pattern_strength = config.get('min_pattern_strength', 0.3)
        self.time_window_days = config.get('time_window_days', 7)
        self.clustering_params = config.get('clustering', {
            'n_clusters': 5,
            'random_state': 42
        })
        
        # 知识领域关键词
        self.domain_keywords = {
            'science': ['研究', '实验', '理论', '发现', '分析', '数据'],
            'technology': ['技术', '创新', '开发', '系统', '算法', '应用'],
            'business': ['商业', '市场', '企业', '经济', '管理', '策略'],
            'social': ['社会', '文化', '教育', '政策', '影响', '趋势'],
            'health': ['健康', '医疗', '疾病', '治疗', '预防', '研究']
        }
    
    def identify_temporal_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """识别时间模式"""
        try:
            self.logger.info("开始识别时间模式...")
            
            # 按时间排序
            sorted_items = sorted(knowledge_items, 
                                key=lambda x: x.get('_collection_time', ''))
            
            if len(sorted_items) < 2:
                return []
            
            patterns = []
            
            # 1. 识别周期性模式
            periodic_patterns = self._detect_periodic_patterns(sorted_items)
            patterns.extend(periodic_patterns)
            
            # 2. 识别趋势模式
            trend_patterns = self._detect_trend_patterns(sorted_items)
            patterns.extend(trend_patterns)
            
            # 3. 识别爆发模式
            burst_patterns = self._detect_burst_patterns(sorted_items)
            patterns.extend(burst_patterns)
            
            # 4. 识别收敛模式
            convergence_patterns = self._detect_convergence_patterns(sorted_items)
            patterns.extend(convergence_patterns)
            
            self.logger.info(f"识别到 {len(patterns)} 个时间模式")
            return patterns
            
        except Exception as e:
            self.logger.error(f"识别时间模式失败: {e}")
            return []
    
    def identify_content_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """识别内容模式"""
        try:
            self.logger.info("开始识别内容模式...")
            
            patterns = []
            
            # 1. 主题演化模式
            topic_patterns = self._detect_topic_evolution(knowledge_items)
            patterns.extend(topic_patterns)
            
            # 2. 概念关联模式
            concept_patterns = self._detect_concept_associations(knowledge_items)
            patterns.extend(concept_patterns)
            
            # 3. 领域分布模式
            domain_patterns = self._detect_domain_patterns(knowledge_items)
            patterns.extend(domain_patterns)
            
            # 4. 质量变化模式
            quality_patterns = self._detect_quality_patterns(knowledge_items)
            patterns.extend(quality_patterns)
            
            self.logger.info(f"识别到 {len(patterns)} 个内容模式")
            return patterns
            
        except Exception as e:
            self.logger.error(f"识别内容模式失败: {e}")
            return []
    
    def identify_structural_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """识别结构模式"""
        try:
            self.logger.info("开始识别结构模式...")
            
            patterns = []
            
            # 1. 网络结构模式
            network_patterns = self._detect_network_patterns(knowledge_items)
            patterns.extend(network_patterns)
            
            # 2. 层次结构模式
            hierarchy_patterns = self._detect_hierarchy_patterns(knowledge_items)
            patterns.extend(hierarchy_patterns)
            
            # 3. 聚类模式
            cluster_patterns = self._detect_clustering_patterns(knowledge_items)
            patterns.extend(cluster_patterns)
            
            self.logger.info(f"识别到 {len(patterns)} 个结构模式")
            return patterns
            
        except Exception as e:
            self.logger.error(f"识别结构模式失败: {e}")
            return []
    
    def identify_emergence_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """识别涌现模式"""
        try:
            self.logger.info("开始识别涌现模式...")
            
            patterns = []
            
            # 1. 自组织模式
            self_org_patterns = self._detect_self_organization(knowledge_items)
            patterns.extend(self_org_patterns)
            
            # 2. 协同效应模式
            synergy_patterns = self._detect_synergy_effects(knowledge_items)
            patterns.extend(synergy_patterns)
            
            # 3. 相变模式
            phase_patterns = self._detect_phase_transitions(knowledge_items)
            patterns.extend(phase_patterns)
            
            # 4. 临界点模式
            critical_patterns = self._detect_critical_points(knowledge_items)
            patterns.extend(critical_patterns)
            
            self.logger.info(f"识别到 {len(patterns)} 个涌现模式")
            return patterns
            
        except Exception as e:
            self.logger.error(f"识别涌现模式失败: {e}")
            return []
    
    def analyze_pattern_evolution(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """分析模式演化"""
        try:
            if not patterns:
                return {}
            
            evolution_analysis = {
                'pattern_lifecycle': self._analyze_pattern_lifecycle(patterns),
                'pattern_interactions': self._analyze_pattern_interactions(patterns),
                'pattern_succession': self._analyze_pattern_succession(patterns),
                'pattern_strength_changes': self._analyze_strength_changes(patterns)
            }
            
            return evolution_analysis
            
        except Exception as e:
            self.logger.error(f"分析模式演化失败: {e}")
            return {}
    
    def predict_pattern_continuation(self, patterns: List[Pattern], 
                                   current_time: str = None) -> Dict[str, Any]:
        """预测模式延续"""
        try:
            if not patterns:
                return {}
            
            predictions = {}
            
            for pattern in patterns:
                if pattern.confidence >= self.min_pattern_strength:
                    prediction = self._predict_single_pattern(pattern, current_time)
                    predictions[pattern.pattern_type] = prediction
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"预测模式延续失败: {e}")
            return {}
    
    # 私有方法：时间模式检测
    
    def _detect_periodic_patterns(self, sorted_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测周期性模式"""
        patterns = []
        
        # 提取时间序列
        timestamps = []
        for item in sorted_items:
            time_str = item.get('_collection_time', '')
            if time_str:
                try:
                    ts = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    timestamps.append(ts)
                except:
                    continue
        
        if len(timestamps) < 4:
            return patterns
        
        # 计算时间间隔
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return patterns
        
        # 检测周期性
        interval_counts = Counter(intervals)
        most_common_interval = interval_counts.most_common(1)[0]
        
        if most_common_interval[1] >= len(intervals) * 0.3:  # 至少30%的间隔相同
            pattern = Pattern(
                pattern_type="periodic",
                description=f"知识产生呈现周期性，间隔约{most_common_interval[0]}天",
                confidence=most_common_interval[1] / len(intervals),
                strength=most_common_interval[1] / len(intervals),
                supporting_evidence=[f"出现{most_common_interval[1]}次相同间隔"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_trend_patterns(self, sorted_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测趋势模式"""
        patterns = []
        
        # 计算每个时间点的知识量
        time_points = []
        knowledge_counts = []
        
        current_date = None
        count = 0
        
        for item in sorted_items:
            time_str = item.get('_collection_time', '')
            if time_str:
                try:
                    date = datetime.fromisoformat(time_str.replace('Z', '+00:00')).date()
                    
                    if current_date != date:
                        if current_date is not None:
                            time_points.append(current_date)
                            knowledge_counts.append(count)
                        current_date = date
                        count = 1
                    else:
                        count += 1
                        
                except:
                    continue
        
        if current_date is not None:
            time_points.append(current_date)
            knowledge_counts.append(count)
        
        if len(time_points) < 3:
            return patterns
        
        # 使用线性回归检测趋势
        x = np.arange(len(time_points))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, knowledge_counts)
        
        if abs(r_value) >= 0.7 and p_value < 0.05:  # 强相关性且显著
            if slope > 0:
                pattern_type = "increasing_trend"
                description = f"知识产生呈上升趋势，斜率{slope:.3f}"
            else:
                pattern_type = "decreasing_trend"
                description = f"知识产生呈下降趋势，斜率{slope:.3f}"
            
            pattern = Pattern(
                pattern_type=pattern_type,
                description=description,
                confidence=abs(r_value),
                strength=abs(r_value),
                supporting_evidence=[f"相关系数: {r_value:.3f}", f"p值: {p_value:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_burst_patterns(self, sorted_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测爆发模式"""
        patterns = []
        
        # 计算每日知识产生量
        daily_counts = defaultdict(int)
        
        for item in sorted_items:
            time_str = item.get('_collection_time', '')
            if time_str:
                try:
                    date = datetime.fromisoformat(time_str.replace('Z', '+00:00')).date()
                    daily_counts[date] += 1
                except:
                    continue
        
        if not daily_counts:
            return patterns
        
        # 排序日期
        sorted_dates = sorted(daily_counts.keys())
        counts = [daily_counts[date] for date in sorted_dates]
        
        # 检测峰值
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        threshold = mean_count + 2 * std_count  # 2倍标准差阈值
        
        peaks, properties = find_peaks(counts, height=threshold)
        
        for peak in peaks:
            if properties['peak_heights'][list(peaks).index(peak)] >= threshold:
                burst_date = sorted_dates[peak]
                burst_count = counts[peak]
                
                pattern = Pattern(
                    pattern_type="knowledge_burst",
                    description=f"在{burst_date}出现知识爆发，产生{burst_count}条知识",
                    confidence=min(burst_count / (mean_count + std_count), 1.0),
                    strength=burst_count / mean_count,
                    start_time=burst_date.isoformat(),
                    supporting_evidence=[f"当日产生量: {burst_count}", f"平均值: {mean_count:.1f}"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_convergence_patterns(self, sorted_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测收敛模式"""
        patterns = []
        
        # 计算知识多样性的变化
        diversity_scores = []
        
        window_size = max(3, len(sorted_items) // 10)
        
        for i in range(len(sorted_items) - window_size + 1):
            window_items = sorted_items[i:i + window_size]
            diversity = self._calculate_window_diversity(window_items)
            diversity_scores.append(diversity)
        
        if len(diversity_scores) < 3:
            return patterns
        
        # 检测收敛趋势
        x = np.arange(len(diversity_scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, diversity_scores)
        
        if slope < -0.1 and abs(r_value) >= 0.6:  # 下降趋势且相关性较强
            pattern = Pattern(
                pattern_type="convergence",
                description="知识内容逐渐收敛，多样性减少",
                confidence=abs(r_value),
                strength=abs(slope),
                supporting_evidence=[f"多样性下降率: {slope:.3f}", f"相关系数: {r_value:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    # 私有方法：内容模式检测
    
    def _detect_topic_evolution(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测主题演化模式"""
        patterns = []
        
        # 提取主题关键词
        topics_over_time = self._extract_topics_by_time(knowledge_items)
        
        if len(topics_over_time) < 3:
            return patterns
        
        # 检测主题变化
        topic_changes = []
        for i in range(1, len(topics_over_time)):
            prev_topics = set(topics_over_time[i-1]['topics'])
            curr_topics = set(topics_over_time[i]['topics'])
            
            new_topics = curr_topics - prev_topics
            removed_topics = prev_topics - curr_topics
            
            if new_topics or removed_topics:
                topic_changes.append({
                    'time': topics_over_time[i]['time'],
                    'new_topics': list(new_topics),
                    'removed_topics': list(removed_topics),
                    'change_magnitude': len(new_topics) + len(removed_topics)
                })
        
        # 识别主要的主题转换
        if topic_changes:
            major_changes = [change for change in topic_changes if change['change_magnitude'] >= 3]
            
            for change in major_changes:
                pattern = Pattern(
                    pattern_type="topic_evolution",
                    description=f"在{change['time']}发生主题转换，新增: {', '.join(change['new_topics'][:3])}",
                    confidence=min(change['change_magnitude'] / 10, 1.0),
                    strength=change['change_magnitude'] / 10,
                    start_time=change['time'],
                    supporting_evidence=[
                        f"新增主题: {len(change['new_topics'])}",
                        f"移除主题: {len(change['removed_topics'])}"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_concept_associations(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测概念关联模式"""
        patterns = []
        
        # 构建概念共现矩阵
        concept_cooccurrence = defaultdict(lambda: defaultdict(int))
        all_concepts = set()
        
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            concepts = self._extract_concepts_from_text(text)
            
            all_concepts.update(concepts)
            
            # 计算共现
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    concept_cooccurrence[concept1][concept2] += 1
                    concept_cooccurrence[concept2][concept1] += 1
        
        # 识别强关联概念对
        strong_associations = []
        for concept1 in concept_cooccurrence:
            for concept2 in concept_cooccurrence[concept1]:
                if concept1 < concept2:  # 避免重复
                    cooccurrence_count = concept_cooccurrence[concept1][concept2]
                    if cooccurrence_count >= 3:  # 至少共现3次
                        strong_associations.append((concept1, concept2, cooccurrence_count))
        
        # 创建关联模式
        for concept1, concept2, count in strong_associations:
            pattern = Pattern(
                pattern_type="concept_association",
                description=f"概念'{concept1}'与'{concept2}'存在强关联",
                confidence=min(count / 10, 1.0),
                strength=count / 10,
                supporting_evidence=[f"共现次数: {count}"],
                metadata={'concept1': concept1, 'concept2': concept2}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_domain_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测领域分布模式"""
        patterns = []
        
        # 分析领域分布
        domain_distribution = defaultdict(int)
        
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            detected_domains = self._detect_domains(text)
            
            for domain in detected_domains:
                domain_distribution[domain] += 1
        
        if not domain_distribution:
            return patterns
        
        # 识别主导领域
        total_items = sum(domain_distribution.values())
        domain_percentages = {domain: count/total_items for domain, count in domain_distribution.items()}
        
        dominant_domains = [domain for domain, percentage in domain_percentages.items() 
                          if percentage >= 0.3]  # 占比30%以上
        
        for domain in dominant_domains:
            pattern = Pattern(
                pattern_type="domain_dominance",
                description=f"'{domain}'领域在知识中占主导地位",
                confidence=domain_percentages[domain],
                strength=domain_percentages[domain],
                supporting_evidence=[f"占比: {domain_percentages[domain]:.1%}"],
                metadata={'domain': domain, 'percentage': domain_percentages[domain]}
            )
            patterns.append(pattern)
        
        # 识别领域转换
        if len(dominant_domains) > 1:
            pattern = Pattern(
                pattern_type="domain_diversity",
                description=f"知识涉及多个领域: {', '.join(dominant_domains)}",
                confidence=0.8,
                strength=len(dominant_domains) / len(domain_distribution),
                supporting_evidence=[f"涉及领域数: {len(dominant_domains)}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_quality_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测质量变化模式"""
        patterns = []
        
        # 假设每个知识项有质量评分
        quality_scores = []
        for item in knowledge_items:
            score = item.get('quality_score', 0.5)  # 默认中等质量
            quality_scores.append(score)
        
        if len(quality_scores) < 5:
            return patterns
        
        # 检测质量趋势
        x = np.arange(len(quality_scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, quality_scores)
        
        if abs(r_value) >= 0.6:
            if slope > 0.01:  # 明显上升趋势
                pattern_type = "quality_improvement"
                description = "知识质量呈上升趋势"
            elif slope < -0.01:  # 明显下降趋势
                pattern_type = "quality_decline"
                description = "知识质量呈下降趋势"
            else:
                pattern_type = "quality_stability"
                description = "知识质量保持稳定"
            
            pattern = Pattern(
                pattern_type=pattern_type,
                description=description,
                confidence=abs(r_value),
                strength=abs(slope) * 10,  # 放大斜率以便比较
                supporting_evidence=[f"质量变化率: {slope:.4f}", f"相关系数: {r_value:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    # 私有方法：结构模式检测
    
    def _detect_network_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测网络结构模式"""
        patterns = []
        
        # 构建简单的知识网络
        concept_network = self._build_concept_network(knowledge_items)
        
        if not concept_network:
            return patterns
        
        # 计算网络指标
        network_metrics = self._calculate_network_metrics(concept_network)
        
        # 检测小世界特性
        if network_metrics.get('clustering_coefficient', 0) > 0.3:
            pattern = Pattern(
                pattern_type="small_world_network",
                description="知识网络呈现小世界特性",
                confidence=network_metrics['clustering_coefficient'],
                strength=network_metrics['clustering_coefficient'],
                supporting_evidence=[
                    f"聚类系数: {network_metrics['clustering_coefficient']:.3f}"
                ]
            )
            patterns.append(pattern)
        
        # 检测无标度特性
        degree_distribution = network_metrics.get('degree_distribution', {})
        if degree_distribution:
            # 检查是否符合幂律分布
            is_scale_free = self._check_scale_free_distribution(degree_distribution)
            
            if is_scale_free:
                pattern = Pattern(
                    pattern_type="scale_free_network",
                    description="知识网络呈现无标度特性",
                    confidence=0.7,
                    strength=0.7,
                    supporting_evidence=["度分布符合幂律"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_hierarchy_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测层次结构模式"""
        patterns = []
        
        # 分析概念层次
        concept_hierarchy = self._analyze_concept_hierarchy(knowledge_items)
        
        if not concept_hierarchy:
            return patterns
        
        # 检测层次深度
        max_depth = max(concept_hierarchy.values()) if concept_hierarchy else 0
        
        if max_depth >= 3:
            pattern = Pattern(
                pattern_type="deep_hierarchy",
                description=f"知识呈现深层层次结构，最大深度: {max_depth}",
                confidence=min(max_depth / 5, 1.0),
                strength=max_depth / 5,
                supporting_evidence=[f"最大层次深度: {max_depth}"]
            )
            patterns.append(pattern)
        
        # 检测层次均匀性
        depth_distribution = Counter(concept_hierarchy.values())
        if len(depth_distribution) > 1:
            # 计算分布的标准差
            depths = list(depth_distribution.keys())
            counts = list(depth_distribution.values())
            
            if len(depths) > 1:
                std_dev = np.std(depths)
                if std_dev < 1.0:  # 层次分布相对均匀
                    pattern = Pattern(
                        pattern_type="balanced_hierarchy",
                        description="知识层次结构相对平衡",
                        confidence=1 - std_dev,
                        strength=1 - std_dev,
                        supporting_evidence=[f"层次深度标准差: {std_dev:.2f}"]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_clustering_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测聚类模式"""
        patterns = []
        
        if len(knowledge_items) < 10:
            return patterns
        
        # 提取特征
        features = self._extract_features_for_clustering(knowledge_items)
        
        if len(features) < len(knowledge_items):
            return patterns
        
        # 执行聚类
        n_clusters = min(self.clustering_params['n_clusters'], len(knowledge_items) // 3)
        
        if n_clusters >= 2:
            kmeans = KMeans(n_clusters=n_clusters, random_state=self.clustering_params['random_state'])
            cluster_labels = kmeans.fit_predict(features)
            
            # 分析聚类结果
            cluster_sizes = Counter(cluster_labels)
            
            # 检测主要聚类
            max_cluster_size = max(cluster_sizes.values())
            if max_cluster_size >= len(knowledge_items) * 0.3:  # 最大的聚类占比30%以上
                pattern = Pattern(
                    pattern_type="dominant_cluster",
                    description=f"存在主导聚类，包含{max_cluster_size}个知识项",
                    confidence=max_cluster_size / len(knowledge_items),
                    strength=max_cluster_size / len(knowledge_items),
                    supporting_evidence=[f"聚类大小: {dict(cluster_sizes)}"]
                )
                patterns.append(pattern)
            
            # 检测聚类均匀性
            cluster_sizes_list = list(cluster_sizes.values())
            if len(set(cluster_sizes_list)) == 1:  # 所有聚类大小相同
                pattern = Pattern(
                    pattern_type="balanced_clusters",
                    description="知识聚类相对均匀",
                    confidence=0.8,
                    strength=0.8,
                    supporting_evidence=[f"聚类大小: {cluster_sizes_list}"]
                )
                patterns.append(pattern)
        
        return patterns
    
    # 私有方法：涌现模式检测
    
    def _detect_self_organization(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测自组织模式"""
        patterns = []
        
        # 分析知识项的自发组织
        organization_score = self._calculate_organization_score(knowledge_items)
        
        if organization_score >= 0.6:
            pattern = Pattern(
                pattern_type="self_organization",
                description="知识体系呈现自组织特征",
                confidence=organization_score,
                strength=organization_score,
                supporting_evidence=[f"组织化程度: {organization_score:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_synergy_effects(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测协同效应模式"""
        patterns = []
        
        # 分析知识组合效应
        synergy_score = self._calculate_synergy_score(knowledge_items)
        
        if synergy_score >= 0.5:
            pattern = Pattern(
                pattern_type="synergy_effect",
                description="知识之间存在协同效应",
                confidence=synergy_score,
                strength=synergy_score,
                supporting_evidence=[f"协同强度: {synergy_score:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_phase_transitions(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测相变模式"""
        patterns = []
        
        # 分析知识状态的突然变化
        transitions = self._detect_state_transitions(knowledge_items)
        
        for transition in transitions:
            pattern = Pattern(
                pattern_type="phase_transition",
                description=f"在{transition['time']}发生知识状态相变",
                confidence=transition['strength'],
                strength=transition['strength'],
                start_time=transition['time'],
                supporting_evidence=[f"变化幅度: {transition['magnitude']:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_critical_points(self, knowledge_items: List[Dict[str, Any]]) -> List[Pattern]:
        """检测临界点模式"""
        patterns = []
        
        # 识别关键转折点
        critical_points = self._identify_critical_points(knowledge_items)
        
        for point in critical_points:
            pattern = Pattern(
                pattern_type="critical_point",
                description=f"在{point['time']}达到临界状态",
                confidence=point['importance'],
                strength=point['importance'],
                start_time=point['time'],
                supporting_evidence=[f"重要性评分: {point['importance']:.3f}"]
            )
            patterns.append(pattern)
        
        return patterns
    
    # 辅助方法
    
    def _calculate_window_diversity(self, window_items: List[Dict[str, Any]]) -> float:
        """计算窗口内的多样性"""
        if not window_items:
            return 0.0
        
        all_concepts = set()
        for item in window_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            concepts = self._extract_concepts_from_text(text)
            all_concepts.update(concepts)
        
        # 简单的多样性计算
        return min(len(all_concepts) / len(window_items), 1.0)
    
    def _extract_topics_by_time(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按时间提取主题"""
        topics_over_time = []
        
        # 按时间分组
        time_groups = defaultdict(list)
        for item in knowledge_items:
            time_str = item.get('_collection_time', '')
            if time_str:
                try:
                    date = datetime.fromisoformat(time_str.replace('Z', '+00:00')).date()
                    time_groups[date].append(item)
                except:
                    continue
        
        # 提取每个时间点的主题
        for date in sorted(time_groups.keys()):
            items = time_groups[date]
            topics = set()
            
            for item in items:
                text = item.get('content', '') + ' ' + item.get('title', '')
                concepts = self._extract_concepts_from_text(text)
                topics.update(concepts)
            
            topics_over_time.append({
                'time': date.isoformat(),
                'topics': list(topics),
                'count': len(items)
            })
        
        return topics_over_time
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """从文本中提取概念"""
        if not text:
            return []
        
        # 简单的概念提取
        words = text.split()
        concepts = []
        
        for word in words:
            # 过滤短词和常见词
            if len(word) > 3 and word.isalpha():
                concepts.append(word.lower())
        
        return concepts
    
    def _detect_domains(self, text: str) -> List[str]:
        """检测文本涉及的领域"""
        detected_domains = []
        text_lower = text.lower()
        
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_domains.append(domain)
        
        return detected_domains
    
    def _build_concept_network(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建概念网络"""
        network = defaultdict(list)
        
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            concepts = self._extract_concepts_from_text(text)
            
            # 创建概念之间的连接
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    if concept2 not in network[concept1]:
                        network[concept1].append(concept2)
        
        return dict(network)
    
    def _calculate_network_metrics(self, network: Dict[str, List[str]]) -> Dict[str, float]:
        """计算网络指标"""
        if not network:
            return {}
        
        # 计算度分布
        degrees = {node: len(neighbors) for node, neighbors in network.items()}
        degree_distribution = Counter(degrees.values())
        
        # 计算聚类系数
        clustering_coeffs = []
        for node, neighbors in network.items():
            if len(neighbors) < 2:
                continue
            
            # 计算邻居之间的连接
            neighbor_connections = 0
            possible_connections = len(neighbors) * (len(neighbors) - 1) / 2
            
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 < neighbor2 and neighbor2 in network.get(neighbor1, []):
                        neighbor_connections += 1
            
            if possible_connections > 0:
                clustering_coeffs.append(neighbor_connections / possible_connections)
        
        avg_clustering = np.mean(clustering_coeffs) if clustering_coeffs else 0
        
        return {
            'clustering_coefficient': avg_clustering,
            'degree_distribution': dict(degree_distribution),
            'avg_degree': np.mean(list(degrees.values())) if degrees else 0
        }
    
    def _check_scale_free_distribution(self, degree_distribution: Dict[int, int]) -> bool:
        """检查是否符合无标度分布"""
        if len(degree_distribution) < 3:
            return False
        
        degrees = list(degree_distribution.keys())
        counts = list(degree_distribution.values())
        
        # 简单的幂律检验
        try:
            log_degrees = np.log(degrees)
            log_counts = np.log(counts)
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_counts)
            
            # 如果相关系数较高且斜率为负，则可能是无标度网络
            return r_value < -0.7 and abs(r_value) > 0.8
            
        except:
            return False
    
    def _analyze_concept_hierarchy(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析概念层次"""
        concept_depths = {}
        
        # 简化的层次分析
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            concepts = self._extract_concepts_from_text(text)
            
            # 根据概念长度估计层次（简单启发式）
            for concept in concepts:
                if concept not in concept_depths:
                    concept_depths[concept] = len(concept) // 3  # 简单的层次估计
        
        return concept_depths
    
    def _extract_features_for_clustering(self, knowledge_items: List[Dict[str, Any]]) -> np.ndarray:
        """提取聚类特征"""
        features = []
        
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            
            # 简单特征提取
            feature_vector = [
                len(text.split()),  # 词数
                text.count('。'),   # 句号数
                len(set(text.split())),  # 独特词数
                text.count('数据'),  # 数据相关词数
                text.count('研究'),  # 研究相关词数
            ]
            
            features.append(feature_vector)
        
        # 标准化特征
        if features:
            scaler = StandardScaler()
            features = scaler.fit_transform(features)
        
        return np.array(features)
    
    def _calculate_organization_score(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """计算组织化程度"""
        if len(knowledge_items) < 2:
            return 0.0
        
        # 简化的组织化程度计算
        connections = 0
        total_possible = len(knowledge_items) * (len(knowledge_items) - 1) / 2
        
        for i, item1 in enumerate(knowledge_items):
            for j, item2 in enumerate(knowledge_items):
                if i < j:
                    # 检查概念重叠
                    text1 = item1.get('content', '') + ' ' + item1.get('title', '')
                    text2 = item2.get('content', '') + ' ' + item2.get('title', '')
                    
                    concepts1 = set(self._extract_concepts_from_text(text1))
                    concepts2 = set(self._extract_concepts_from_text(text2))
                    
                    if concepts1.intersection(concepts2):
                        connections += 1
        
        return connections / total_possible if total_possible > 0 else 0
    
    def _calculate_synergy_score(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """计算协同效应强度"""
        if len(knowledge_items) < 2:
            return 0.0
        
        # 简化的协同效应计算
        synergy_indicators = ['结合', '整合', '协同', '合作', '配合']
        
        synergy_count = 0
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            if any(indicator in text for indicator in synergy_indicators):
                synergy_count += 1
        
        return synergy_count / len(knowledge_items)
    
    def _detect_state_transitions(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测状态转换"""
        transitions = []
        
        if len(knowledge_items) < 3:
            return transitions
        
        # 计算每个时间点的状态指标
        states = []
        for item in knowledge_items:
            text = item.get('content', '') + ' ' + item.get('title', '')
            # 简单的状态指标：文本复杂度
            state = len(text.split()) / 100  # 标准化
            states.append(state)
        
        # 检测显著变化
        for i in range(1, len(states)):
            change = abs(states[i] - states[i-1])
            if change > 0.5:  # 显著变化阈值
                transition = {
                    'time': knowledge_items[i].get('_collection_time', ''),
                    'magnitude': change,
                    'strength': min(change, 1.0)
                }
                transitions.append(transition)
        
        return transitions
    
    def _identify_critical_points(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别关键转折点"""
        critical_points = []
        
        if len(knowledge_items) < 3:
            return critical_points
        
        # 寻找重要性突然增加的点
        importances = []
        for item in knowledge_items:
            # 简单的重要性指标
            importance = len(item.get('content', '').split()) / 1000
            importances.append(importance)
        
        for i in range(1, len(importances)):
            importance_change = importances[i] - importances[i-1]
            if importance_change > 0.5:  # 重要性显著增加
                critical_point = {
                    'time': knowledge_items[i].get('_collection_time', ''),
                    'importance': min(importance_change, 1.0)
                }
                critical_points.append(critical_point)
        
        return critical_points
    
    # 模式分析辅助方法
    
    def _analyze_pattern_lifecycle(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """分析模式生命周期"""
        lifecycle_analysis = {
            'total_patterns': len(patterns),
            'pattern_types': Counter([p.pattern_type for p in patterns]),
            'avg_lifespan': 0,
            'dominant_patterns': []
        }
        
        # 识别主导模式
        type_counts = lifecycle_analysis['pattern_types']
        if type_counts:
            max_count = max(type_counts.values())
            dominant_types = [ptype for ptype, count in type_counts.items() if count == max_count]
            lifecycle_analysis['dominant_patterns'] = dominant_types
        
        return lifecycle_analysis
    
    def _analyze_pattern_interactions(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """分析模式相互作用"""
        interactions = {
            'cooccurring_types': [],
            'conflicting_types': [],
            'sequential_patterns': []
        }
        
        # 简化的相互作用分析
        pattern_types = [p.pattern_type for p in patterns]
        type_counts = Counter(pattern_types)
        
        # 识别经常一起出现的模式类型
        for ptype1, count1 in type_counts.items():
            for ptype2, count2 in type_counts.items():
                if ptype1 < ptype2 and count1 > 0 and count2 > 0:
                    interactions['cooccurring_types'].append((ptype1, ptype2))
        
        return interactions
    
    def _analyze_pattern_succession(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """分析模式序列"""
        succession = {
            'common_sequences': [],
            'transition_probabilities': {}
        }
        
        # 按时间排序模式
        sorted_patterns = sorted(patterns, key=lambda x: x.start_time or '')
        
        # 分析模式序列
        sequences = []
        for i in range(len(sorted_patterns) - 1):
            current_type = sorted_patterns[i].pattern_type
            next_type = sorted_patterns[i + 1].pattern_type
            sequences.append((current_type, next_type))
        
        # 统计常见序列
        sequence_counts = Counter(sequences)
        common_sequences = sequence_counts.most_common(3)
        
        succession['common_sequences'] = [(seq, count) for seq, count in common_sequences]
        
        return succession
    
    def _analyze_strength_changes(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """分析模式强度变化"""
        strength_analysis = {
            'avg_strength': np.mean([p.strength for p in patterns]) if patterns else 0,
            'strength_distribution': {},
            'strength_trends': []
        }
        
        # 强度分布
        if patterns:
            strengths = [p.strength for p in patterns]
            strength_analysis['strength_distribution'] = {
                'min': min(strengths),
                'max': max(strengths),
                'std': np.std(strengths)
            }
        
        return strength_analysis
    
    def _predict_single_pattern(self, pattern: Pattern, current_time: str = None) -> Dict[str, Any]:
        """预测单个模式的延续"""
        prediction = {
            'pattern_type': pattern.pattern_type,
            'continuation_probability': pattern.confidence,
            'expected_duration': 'unknown',
            'strength_forecast': pattern.strength,
            'confidence_level': pattern.confidence
        }
        
        # 基于模式类型的简单预测
        if pattern.pattern_type == "increasing_trend":
            prediction['expected_duration'] = "持续增长"
            prediction['strength_forecast'] = min(pattern.strength * 1.1, 1.0)
        elif pattern.pattern_type == "knowledge_burst":
            prediction['expected_duration'] = "短期爆发"
            prediction['strength_forecast'] = pattern.strength * 0.8  # 衰减
        elif pattern.pattern_type == "periodic":
            prediction['expected_duration'] = "周期性重复"
            prediction['strength_forecast'] = pattern.strength
        
        return prediction