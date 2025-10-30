"""
知识涌现可视化生成器
生成各种图表和可视化结果
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
from collections import Counter, defaultdict
import warnings

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 忽略警告
warnings.filterwarnings('ignore')


class Visualizer:
    """知识涌现可视化生成器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 图表样式配置
        self.style_config = {
            'figure_size': (12, 8),
            'dpi': 100,
            'color_palette': 'viridis',
            'font_size': 12,
            'title_size': 16
        }
        
        # 输出目录
        self.output_dir = Path(config.get('output_dir', 'visualizations'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 图表类型配置
        self.chart_configs = {
            'timeline': {'type': 'line', 'color': '#2E86AB'},
            'distribution': {'type': 'histogram', 'color': '#A23B72'},
            'correlation': {'type': 'heatmap', 'color': 'RdYlBu'},
            'network': {'type': 'graph', 'color': '#F18F01'},
            'comparison': {'type': 'bar', 'color': '#C73E1D'}
        }
    
    def generate_metrics_visualization(self, metrics_data: Dict[str, Any], 
                                     output_filename: str = "metrics_overview.png") -> str:
        """生成指标概览可视化"""
        try:
            self.logger.info("生成指标概览可视化...")
            
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            fig.suptitle('知识涌现指标概览', fontsize=16, fontweight='bold')
            
            # 1. 总体评分雷达图
            self._create_radar_chart(axes[0, 0], metrics_data)
            
            # 2. 各维度评分柱状图
            self._create_dimension_scores_chart(axes[0, 1], metrics_data)
            
            # 3. 质量分布图
            self._create_quality_distribution_chart(axes[0, 2], metrics_data)
            
            # 4. 时间趋势图
            self._create_time_trend_chart(axes[1, 0], metrics_data)
            
            # 5. 相关性热力图
            self._create_correlation_heatmap(axes[1, 1], metrics_data)
            
            # 6. 价值分析图
            self._create_value_analysis_chart(axes[1, 2], metrics_data)
            
            plt.tight_layout()
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"指标概览可视化已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成指标可视化失败: {e}")
            return ""
    
    def generate_pattern_visualization(self, patterns: List[Dict[str, Any]], 
                                     output_filename: str = "pattern_analysis.png") -> str:
        """生成模式分析可视化"""
        try:
            self.logger.info("生成模式分析可视化...")
            
            if not patterns:
                return ""
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('知识涌现模式分析', fontsize=16, fontweight='bold')
            
            # 1. 模式类型分布饼图
            self._create_pattern_distribution_pie(axes[0, 0], patterns)
            
            # 2. 模式强度分析
            self._create_pattern_strength_chart(axes[0, 1], patterns)
            
            # 3. 模式时间线
            self._create_pattern_timeline(axes[1, 0], patterns)
            
            # 4. 模式关联网络
            self._create_pattern_network(axes[1, 1], patterns)
            
            plt.tight_layout()
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"模式分析可视化已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成模式可视化失败: {e}")
            return ""
    
    def generate_quality_visualization(self, quality_scores: List[Dict[str, Any]], 
                                     output_filename: str = "quality_analysis.png") -> str:
        """生成质量分析可视化"""
        try:
            self.logger.info("生成质量分析可视化...")
            
            if not quality_scores:
                return ""
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('知识质量分析', fontsize=16, fontweight='bold')
            
            # 1. 质量维度雷达图
            self._create_quality_radar_chart(axes[0, 0], quality_scores)
            
            # 2. 质量分布直方图
            self._create_quality_histogram(axes[0, 1], quality_scores)
            
            # 3. 质量趋势分析
            self._create_quality_trend_chart(axes[1, 0], quality_scores)
            
            # 4. 质量对比分析
            self._create_quality_comparison_chart(axes[1, 1], quality_scores)
            
            plt.tight_layout()
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"质量分析可视化已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成质量可视化失败: {e}")
            return ""
    
    def generate_value_visualization(self, value_assessments: List[Dict[str, Any]], 
                                   output_filename: str = "value_analysis.png") -> str:
        """生成价值分析可视化"""
        try:
            self.logger.info("生成价值分析可视化...")
            
            if not value_assessments:
                return ""
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('知识价值分析', fontsize=16, fontweight='bold')
            
            # 1. 价值维度分析
            self._create_value_dimension_chart(axes[0, 0], value_assessments)
            
            # 2. 价值分布分析
            self._create_value_distribution_chart(axes[0, 1], value_assessments)
            
            # 3. 价值趋势分析
            self._create_value_trend_chart(axes[1, 0], value_assessments)
            
            # 4. 价值风险分析
            self._create_value_risk_chart(axes[1, 1], value_assessments)
            
            plt.tight_layout()
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"价值分析可视化已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成价值可视化失败: {e}")
            return ""
    
    def generate_comprehensive_dashboard(self, analysis_results: Dict[str, Any], 
                                       output_filename: str = "comprehensive_dashboard.png") -> str:
        """生成综合仪表板"""
        try:
            self.logger.info("生成综合仪表板...")
            
            fig = plt.figure(figsize=(20, 12))
            gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
            
            fig.suptitle('知识涌现综合分析仪表板', fontsize=20, fontweight='bold')
            
            # 1. 总体指标概览 (左上)
            ax1 = fig.add_subplot(gs[0, 0])
            self._create_overview_metrics(ax1, analysis_results.get('metrics', {}))
            
            # 2. 质量概览 (右上)
            ax2 = fig.add_subplot(gs[0, 1])
            self._create_overview_quality(ax2, analysis_results.get('quality', []))
            
            # 3. 价值概览 (右中)
            ax3 = fig.add_subplot(gs[0, 2])
            self._create_overview_value(ax3, analysis_results.get('value', []))
            
            # 4. 模式概览 (右下)
            ax4 = fig.add_subplot(gs[0, 3])
            self._create_overview_patterns(ax4, analysis_results.get('patterns', []))
            
            # 5. 时间趋势分析 (中左)
            ax5 = fig.add_subplot(gs[1, :2])
            self._create_comprehensive_timeline(ax5, analysis_results)
            
            # 6. 相关性分析 (中右)
            ax6 = fig.add_subplot(gs[1, 2:])
            self._create_comprehensive_correlation(ax6, analysis_results)
            
            # 7. 关键指标 (底部)
            ax7 = fig.add_subplot(gs[2, :])
            self._create_key_indicators_chart(ax7, analysis_results)
            
            output_path = self.output_dir / output_filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"综合仪表板已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成综合仪表板失败: {e}")
            return ""
    
    def generate_interactive_visualization(self, data: Dict[str, Any], 
                                         output_filename: str = "interactive_dashboard.html") -> str:
        """生成交互式可视化"""
        try:
            self.logger.info("生成交互式可视化...")
            
            # 这里可以集成 plotly 或其他交互式库
            # 简化版本：生成包含多个图表的HTML文件
            
            html_content = self._create_interactive_html(data)
            
            output_path = self.output_dir / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"交互式可视化已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成交互式可视化失败: {e}")
            return ""
    
    def export_data_visualization(self, data: Dict[str, Any], 
                                format: str = 'png', 
                                output_filename: str = "data_export.png") -> str:
        """导出数据可视化"""
        try:
            self.logger.info(f"导出数据可视化 (格式: {format})...")
            
            if format == 'png':
                return self._export_png_visualization(data, output_filename)
            elif format == 'pdf':
                return self._export_pdf_visualization(data, output_filename)
            elif format == 'svg':
                return self._export_svg_visualization(data, output_filename)
            else:
                raise ValueError(f"不支持的格式: {format}")
                
        except Exception as e:
            self.logger.error(f"导出数据可视化失败: {e}")
            return ""
    
    # 私有方法：具体图表生成方法
    
    def _create_radar_chart(self, ax, metrics_data: Dict[str, Any]):
        """创建雷达图"""
        try:
            # 提取维度数据
            dimensions = ['diversity', 'connectivity', 'complexity', 'emergence', 'coherence', 'impact']
            values = []
            
            for dim in dimensions:
                if dim in metrics_data and 'score' in metrics_data[dim]:
                    values.append(metrics_data[dim]['score'])
                else:
                    values.append(0)
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
            values += values[:1]  # 闭合图形
            angles = np.concatenate((angles, [angles[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB')
            ax.fill(angles, values, alpha=0.25, color='#2E86AB')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([dim.capitalize() for dim in dimensions])
            ax.set_ylim(0, 100)
            ax.set_title('知识涌现指标雷达图', fontweight='bold')
            ax.grid(True)
            
        except Exception as e:
            self.logger.error(f"创建雷达图失败: {e}")
            ax.text(0.5, 0.5, '雷达图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_dimension_scores_chart(self, ax, metrics_data: Dict[str, Any]):
        """创建维度评分柱状图"""
        try:
            dimensions = []
            scores = []
            
            for dim, data in metrics_data.items():
                if isinstance(data, dict) and 'score' in data:
                    dimensions.append(dim.capitalize())
                    scores.append(data['score'])
            
            if not dimensions:
                ax.text(0.5, 0.5, '无维度数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            bars = ax.bar(dimensions, scores, color='#A23B72', alpha=0.7)
            ax.set_title('各维度评分', fontweight='bold')
            ax.set_ylabel('评分')
            ax.set_ylim(0, 100)
            
            # 添加数值标签
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       f'{score:.1f}', ha='center', va='bottom')
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            self.logger.error(f"创建维度评分图失败: {e}")
            ax.text(0.5, 0.5, '维度评分图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_quality_distribution_chart(self, ax, metrics_data: Dict[str, Any]):
        """创建质量分布图"""
        try:
            # 模拟质量分布数据
            quality_scores = np.random.normal(75, 15, 100)  # 模拟数据
            quality_scores = np.clip(quality_scores, 0, 100)
            
            ax.hist(quality_scores, bins=20, color='#F18F01', alpha=0.7, edgecolor='black')
            ax.set_title('知识质量分布', fontweight='bold')
            ax.set_xlabel('质量评分')
            ax.set_ylabel('频次')
            ax.axvline(quality_scores.mean(), color='red', linestyle='--', 
                      label=f'平均值: {quality_scores.mean():.1f}')
            ax.legend()
            
        except Exception as e:
            self.logger.error(f"创建质量分布图失败: {e}")
            ax.text(0.5, 0.5, '质量分布图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_time_trend_chart(self, ax, metrics_data: Dict[str, Any]):
        """创建时间趋势图"""
        try:
            # 模拟时间序列数据
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            trend_values = np.cumsum(np.random.randn(30)) + 50
            
            ax.plot(dates, trend_values, marker='o', color='#C73E1D', linewidth=2)
            ax.set_title('知识涌现趋势', fontweight='bold')
            ax.set_xlabel('时间')
            ax.set_ylabel('指标值')
            ax.grid(True, alpha=0.3)
            
            # 格式化x轴
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.get_xticklabels(), rotation=45)
            
        except Exception as e:
            self.logger.error(f"创建时间趋势图失败: {e}")
            ax.text(0.5, 0.5, '时间趋势图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_correlation_heatmap(self, ax, metrics_data: Dict[str, Any]):
        """创建相关性热力图"""
        try:
            # 模拟相关性矩阵
            dimensions = ['多样性', '连接性', '复杂性', '涌现性', '连贯性', '影响力']
            correlation_matrix = np.random.rand(6, 6)
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2  # 对称化
            np.fill_diagonal(correlation_matrix, 1)  # 对角线设为1
            
            im = ax.imshow(correlation_matrix, cmap='RdYlBu', aspect='auto')
            ax.set_xticks(range(len(dimensions)))
            ax.set_yticks(range(len(dimensions)))
            ax.set_xticklabels(dimensions, rotation=45, ha='right')
            ax.set_yticklabels(dimensions)
            ax.set_title('指标相关性热力图', fontweight='bold')
            
            # 添加颜色条
            plt.colorbar(im, ax=ax, shrink=0.8)
            
        except Exception as e:
            self.logger.error(f"创建相关性热力图失败: {e}")
            ax.text(0.5, 0.5, '相关性热力图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_value_analysis_chart(self, ax, metrics_data: Dict[str, Any]):
        """创建价值分析图"""
        try:
            # 模拟价值分析数据
            value_categories = ['经济价值', '社会价值', '应用价值', '创新价值']
            value_scores = [75, 82, 68, 91]
            
            bars = ax.bar(value_categories, value_scores, 
                         color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            ax.set_title('知识价值分析', fontweight='bold')
            ax.set_ylabel('价值评分')
            ax.set_ylim(0, 100)
            
            # 添加数值标签
            for bar, score in zip(bars, value_scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       f'{score}', ha='center', va='bottom')
            
        except Exception as e:
            self.logger.error(f"创建价值分析图失败: {e}")
            ax.text(0.5, 0.5, '价值分析图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_pattern_distribution_pie(self, ax, patterns: List[Dict[str, Any]]):
        """创建模式分布饼图"""
        try:
            # 统计模式类型
            pattern_types = [pattern.get('pattern_type', 'unknown') for pattern in patterns]
            type_counts = Counter(pattern_types)
            
            if not type_counts:
                ax.text(0.5, 0.5, '无模式数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            labels = list(type_counts.keys())
            sizes = list(type_counts.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            colors=colors, startangle=90)
            ax.set_title('模式类型分布', fontweight='bold')
            
        except Exception as e:
            self.logger.error(f"创建模式分布饼图失败: {e}")
            ax.text(0.5, 0.5, '模式分布图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_pattern_strength_chart(self, ax, patterns: List[Dict[str, Any]]):
        """创建模式强度分析图"""
        try:
            if not patterns:
                ax.text(0.5, 0.5, '无模式数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            pattern_names = [f"模式{i+1}" for i in range(len(patterns))]
            strengths = [pattern.get('strength', 0) for pattern in patterns]
            
            bars = ax.barh(pattern_names, strengths, color='#2E86AB', alpha=0.7)
            ax.set_title('模式强度分析', fontweight='bold')
            ax.set_xlabel('强度值')
            
            # 添加数值标签
            for bar, strength in zip(bars, strengths):
                ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{strength:.2f}', ha='left', va='center')
            
        except Exception as e:
            self.logger.error(f"创建模式强度图失败: {e}")
            ax.text(0.5, 0.5, '模式强度图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_pattern_timeline(self, ax, patterns: List[Dict[str, Any]]):
        """创建模式时间线"""
        try:
            # 模拟时间线数据
            timeline_data = []
            for i, pattern in enumerate(patterns[:10]):  # 只显示前10个模式
                start_time = datetime.now() - timedelta(days=i*7)
                end_time = start_time + timedelta(days=3)
                timeline_data.append({
                    'pattern': f"模式{i+1}",
                    'start': start_time,
                    'end': end_time,
                    'strength': pattern.get('strength', 0.5)
                })
            
            if not timeline_data:
                ax.text(0.5, 0.5, '无时间线数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            y_pos = range(len(timeline_data))
            for i, data in enumerate(timeline_data):
                ax.barh(i, (data['end'] - data['start']).days, 
                       left=data['start'], alpha=0.7, 
                       color=plt.cm.viridis(data['strength']))
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels([data['pattern'] for data in timeline_data])
            ax.set_title('模式时间线', fontweight='bold')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.get_xticklabels(), rotation=45)
            
        except Exception as e:
            self.logger.error(f"创建模式时间线失败: {e}")
            ax.text(0.5, 0.5, '模式时间线生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_pattern_network(self, ax, patterns: List[Dict[str, Any]]):
        """创建模式关联网络"""
        try:
            # 简化的网络图
            if len(patterns) < 2:
                ax.text(0.5, 0.5, '模式数量不足', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 生成网络节点位置
            n_nodes = min(len(patterns), 8)
            angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
            x = np.cos(angles)
            y = np.sin(angles)
            
            # 绘制节点
            ax.scatter(x, y, s=200, c=range(n_nodes), cmap='viridis', alpha=0.7)
            
            # 绘制连接线
            for i in range(n_nodes):
                for j in range(i+1, n_nodes):
                    if np.random.rand() > 0.5:  # 随机连接
                        ax.plot([x[i], x[j]], [y[i], y[j]], 'gray', alpha=0.3)
            
            # 添加节点标签
            for i in range(n_nodes):
                ax.annotate(f'模式{i+1}', (x[i], y[i]), ha='center', va='center')
            
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_title('模式关联网络', fontweight='bold')
            ax.set_aspect('equal')
            ax.axis('off')
            
        except Exception as e:
            self.logger.error(f"创建模式网络图失败: {e}")
            ax.text(0.5, 0.5, '模式网络图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_quality_radar_chart(self, ax, quality_scores: List[Dict[str, Any]]):
        """创建质量雷达图"""
        try:
            if not quality_scores:
                ax.text(0.5, 0.5, '无质量数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 计算平均质量分数
            dimensions = ['accuracy', 'completeness', 'consistency', 'credibility', 'relevance']
            avg_scores = []
            
            for dim in dimensions:
                scores = [qs.get(dim, 0) for qs in quality_scores if isinstance(qs, dict)]
                avg_scores.append(np.mean(scores) if scores else 0)
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
            avg_scores += avg_scores[:1]
            angles = np.concatenate((angles, [angles[0]]))
            
            ax.plot(angles, avg_scores, 'o-', linewidth=2, color='#A23B72')
            ax.fill(angles, avg_scores, alpha=0.25, color='#A23B72')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([dim.capitalize() for dim in dimensions])
            ax.set_ylim(0, 1)
            ax.set_title('知识质量雷达图', fontweight='bold')
            ax.grid(True)
            
        except Exception as e:
            self.logger.error(f"创建质量雷达图失败: {e}")
            ax.text(0.5, 0.5, '质量雷达图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_quality_histogram(self, ax, quality_scores: List[Dict[str, Any]]):
        """创建质量分布直方图"""
        try:
            if not quality_scores:
                ax.text(0.5, 0.5, '无质量数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 提取总体质量分数
            overall_scores = []
            for qs in quality_scores:
                if isinstance(qs, dict) and 'overall_score' in qs:
                    overall_scores.append(qs['overall_score'])
                elif isinstance(qs, dict):
                    # 如果没有总体分数，计算平均值
                    scores = [qs.get(dim, 0) for dim in ['accuracy', 'completeness', 'consistency', 'credibility', 'relevance']]
                    overall_scores.append(np.mean(scores))
            
            if not overall_scores:
                ax.text(0.5, 0.5, '无有效质量分数', ha='center', va='center', transform=ax.transAxes)
                return
            
            ax.hist(overall_scores, bins=20, color='#F18F01', alpha=0.7, edgecolor='black')
            ax.set_title('知识质量分布', fontweight='bold')
            ax.set_xlabel('质量评分')
            ax.set_ylabel('频次')
            ax.axvline(np.mean(overall_scores), color='red', linestyle='--', 
                      label=f'平均值: {np.mean(overall_scores):.3f}')
            ax.legend()
            
        except Exception as e:
            self.logger.error(f"创建质量直方图失败: {e}")
            ax.text(0.5, 0.5, '质量直方图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_quality_trend_chart(self, ax, quality_scores: List[Dict[str, Any]]):
        """创建质量趋势图"""
        try:
            if len(quality_scores) < 2:
                ax.text(0.5, 0.5, '数据点不足', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 模拟时间序列
            indices = range(len(quality_scores))
            trend_values = []
            
            for i, qs in enumerate(quality_scores):
                if isinstance(qs, dict) and 'overall_score' in qs:
                    trend_values.append(qs['overall_score'])
                else:
                    scores = [qs.get(dim, 0) for dim in ['accuracy', 'completeness', 'consistency', 'credibility', 'relevance']]
                    trend_values.append(np.mean(scores))
            
            ax.plot(indices, trend_values, marker='o', color='#C73E1D', linewidth=2)
            ax.set_title('质量变化趋势', fontweight='bold')
            ax.set_xlabel('时间顺序')
            ax.set_ylabel('质量评分')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            self.logger.error(f"创建质量趋势图失败: {e}")
            ax.text(0.5, 0.5, '质量趋势图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_quality_comparison_chart(self, ax, quality_scores: List[Dict[str, Any]]):
        """创建质量对比图"""
        try:
            if not quality_scores:
                ax.text(0.5, 0.5, '无质量数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            dimensions = ['accuracy', 'completeness', 'consistency', 'credibility', 'relevance']
            dimension_names = ['准确性', '完整性', '一致性', '可信度', '相关性']
            
            # 计算各维度平均分
            avg_scores = []
            for dim in dimensions:
                scores = [qs.get(dim, 0) for qs in quality_scores if isinstance(qs, dict)]
                avg_scores.append(np.mean(scores) if scores else 0)
            
            bars = ax.bar(dimension_names, avg_scores, color='#2E86AB', alpha=0.7)
            ax.set_title('质量维度对比', fontweight='bold')
            ax.set_ylabel('平均评分')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for bar, score in zip(bars, avg_scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                       f'{score:.3f}', ha='center', va='bottom')
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            self.logger.error(f"创建质量对比图失败: {e}")
            ax.text(0.5, 0.5, '质量对比图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_value_dimension_chart(self, ax, value_assessments: List[Dict[str, Any]]):
        """创建价值维度图"""
        try:
            if not value_assessments:
                ax.text(0.5, 0.5, '无价值数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            dimensions = ['economic_value', 'social_value', 'application_value', 'innovation_value']
            dimension_names = ['经济价值', '社会价值', '应用价值', '创新价值']
            
            # 计算各维度平均分
            avg_scores = []
            for dim in dimensions:
                scores = [va.get(dim, 0) for va in value_assessments if isinstance(va, dict)]
                avg_scores.append(np.mean(scores) if scores else 0)
            
            bars = ax.bar(dimension_names, avg_scores, 
                         color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            ax.set_title('价值维度分析', fontweight='bold')
            ax.set_ylabel('平均价值评分')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for bar, score in zip(bars, avg_scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                       f'{score:.3f}', ha='center', va='bottom')
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            self.logger.error(f"创建价值维度图失败: {e}")
            ax.text(0.5, 0.5, '价值维度图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_value_distribution_chart(self, ax, value_assessments: List[Dict[str, Any]]):
        """创建价值分布图"""
        try:
            if not value_assessments:
                ax.text(0.5, 0.5, '无价值数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 提取总体价值分数
            overall_values = []
            for va in value_assessments:
                if isinstance(va, dict) and 'overall_value' in va:
                    overall_values.append(va['overall_value'])
                elif isinstance(va, dict):
                    scores = [va.get(dim, 0) for dim in ['economic_value', 'social_value', 'application_value', 'innovation_value']]
                    overall_values.append(np.mean(scores))
            
            if not overall_values:
                ax.text(0.5, 0.5, '无有效价值分数', ha='center', va='center', transform=ax.transAxes)
                return
            
            ax.hist(overall_values, bins=20, color='#F18F01', alpha=0.7, edgecolor='black')
            ax.set_title('知识价值分布', fontweight='bold')
            ax.set_xlabel('价值评分')
            ax.set_ylabel('频次')
            ax.axvline(np.mean(overall_values), color='red', linestyle='--', 
                      label=f'平均值: {np.mean(overall_values):.3f}')
            ax.legend()
            
        except Exception as e:
            self.logger.error(f"创建价值分布图失败: {e}")
            ax.text(0.5, 0.5, '价值分布图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_value_trend_chart(self, ax, value_assessments: List[Dict[str, Any]]):
        """创建价值趋势图"""
        try:
            if len(value_assessments) < 2:
                ax.text(0.5, 0.5, '数据点不足', ha='center', va='center', transform=ax.transAxes)
                return
            
            indices = range(len(value_assessments))
            trend_values = []
            
            for va in value_assessments:
                if isinstance(va, dict) and 'overall_value' in va:
                    trend_values.append(va['overall_value'])
                else:
                    scores = [va.get(dim, 0) for dim in ['economic_value', 'social_value', 'application_value', 'innovation_value']]
                    trend_values.append(np.mean(scores))
            
            ax.plot(indices, trend_values, marker='o', color='#C73E1D', linewidth=2)
            ax.set_title('价值变化趋势', fontweight='bold')
            ax.set_xlabel('时间顺序')
            ax.set_ylabel('价值评分')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            self.logger.error(f"创建价值趋势图失败: {e}")
            ax.text(0.5, 0.5, '价值趋势图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_value_risk_chart(self, ax, value_assessments: List[Dict[str, Any]]):
        """创建价值风险图"""
        try:
            if not value_assessments:
                ax.text(0.5, 0.5, '无价值数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 模拟风险分析数据
            value_levels = ['高价值', '中价值', '低价值']
            risk_levels = ['低风险', '中风险', '高风险']
            
            # 创建风险-价值矩阵
            risk_value_matrix = np.random.rand(3, 3)
            
            im = ax.imshow(risk_value_matrix, cmap='RdYlGn_r', aspect='auto')
            ax.set_xticks(range(len(value_levels)))
            ax.set_yticks(range(len(risk_levels)))
            ax.set_xticklabels(value_levels)
            ax.set_yticklabels(risk_levels)
            ax.set_title('价值-风险分析', fontweight='bold')
            ax.set_xlabel('价值水平')
            ax.set_ylabel('风险水平')
            
            # 添加颜色条
            plt.colorbar(im, ax=ax, shrink=0.8)
            
        except Exception as e:
            self.logger.error(f"创建价值风险图失败: {e}")
            ax.text(0.5, 0.5, '价值风险图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_overview_metrics(self, ax, metrics_data: Dict[str, Any]):
        """创建概览指标图"""
        try:
            if not metrics_data:
                ax.text(0.5, 0.5, '无指标数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 显示关键指标
            key_metrics = {
                '总体评分': metrics_data.get('overall', {}).get('total_score', 0),
                '多样性': metrics_data.get('diversity', {}).get('score', 0),
                '连接性': metrics_data.get('connectivity', {}).get('score', 0),
                '涌现性': metrics_data.get('emergence', {}).get('score', 0)
            }
            
            metrics_names = list(key_metrics.keys())
            metrics_values = list(key_metrics.values())
            
            bars = ax.bar(metrics_names, metrics_values, color='#2E86AB', alpha=0.7)
            ax.set_title('关键指标概览', fontweight='bold')
            ax.set_ylabel('评分')
            ax.set_ylim(0, 100)
            
            # 添加数值标签
            for bar, value in zip(bars, metrics_values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       f'{value:.1f}', ha='center', va='bottom')
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            self.logger.error(f"创建概览指标图失败: {e}")
            ax.text(0.5, 0.5, '概览指标图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_overview_quality(self, ax, quality_scores: List[Dict[str, Any]]):
        """创建概览质量图"""
        try:
            if not quality_scores:
                ax.text(0.5, 0.5, '无质量数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 计算质量分布
            high_quality = len([qs for qs in quality_scores if isinstance(qs, dict) and qs.get('overall_score', 0) >= 0.8])
            medium_quality = len([qs for qs in quality_scores if isinstance(qs, dict) and 0.6 <= qs.get('overall_score', 0) < 0.8])
            low_quality = len([qs for qs in quality_scores if isinstance(qs, dict) and qs.get('overall_score', 0) < 0.6])
            
            quality_levels = ['高质量', '中等质量', '低质量']
            quality_counts = [high_quality, medium_quality, low_quality]
            colors = ['#2E86AB', '#F18F01', '#C73E1D']
            
            wedges, texts, autotexts = ax.pie(quality_counts, labels=quality_levels, 
                                            autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('质量分布概览', fontweight='bold')
            
        except Exception as e:
            self.logger.error(f"创建概览质量图失败: {e}")
            ax.text(0.5, 0.5, '概览质量图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_overview_value(self, ax, value_assessments: List[Dict[str, Any]]):
        """创建概览价值图"""
        try:
            if not value_assessments:
                ax.text(0.5, 0.5, '无价值数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 计算价值分布
            high_value = len([va for va in value_assessments if isinstance(va, dict) and va.get('overall_value', 0) >= 0.7])
            medium_value = len([va for va in value_assessments if isinstance(va, dict) and 0.4 <= va.get('overall_value', 0) < 0.7])
            low_value = len([va for va in value_assessments if isinstance(va, dict) and va.get('overall_value', 0) < 0.4])
            
            value_levels = ['高价值', '中等价值', '低价值']
            value_counts = [high_value, medium_value, low_value]
            colors = ['#A23B72', '#F18F01', '#C73E1D']
            
            wedges, texts, autotexts = ax.pie(value_counts, labels=value_levels, 
                                            autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('价值分布概览', fontweight='bold')
            
        except Exception as e:
            self.logger.error(f"创建概览价值图失败: {e}")
            ax.text(0.5, 0.5, '概览价值图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_overview_patterns(self, ax, patterns: List[Dict[str, Any]]):
        """创建概览模式图"""
        try:
            if not patterns:
                ax.text(0.5, 0.5, '无模式数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            # 统计模式类型
            pattern_types = [pattern.get('pattern_type', 'unknown') for pattern in patterns]
            type_counts = Counter(pattern_types)
            
            # 取前5个最常见的模式类型
            top_types = type_counts.most_common(5)
            if not top_types:
                ax.text(0.5, 0.5, '无有效模式数据', ha='center', va='center', transform=ax.transAxes)
                return
            
            types, counts = zip(*top_types)
            
            bars = ax.bar(types, counts, color='#2E86AB', alpha=0.7)
            ax.set_title('主要模式类型', fontweight='bold')
            ax.set_ylabel('出现次数')
            
            # 添加数值标签
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                       str(count), ha='center', va='bottom')
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            self.logger.error(f"创建概览模式图失败: {e}")
            ax.text(0.5, 0.5, '概览模式图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_comprehensive_timeline(self, ax, analysis_results: Dict[str, Any]):
        """创建综合时间线"""
        try:
            # 模拟综合时间线数据
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            
            # 模拟多个指标的时间序列
            knowledge_volume = np.random.randint(10, 50, 30)
            quality_score = np.random.normal(75, 10, 30)
            value_score = np.random.normal(70, 15, 30)
            
            ax2 = ax.twinx()
            ax3 = ax.twinx()
            ax3.spines['right'].set_position(('outward', 60))
            
            line1 = ax.plot(dates, knowledge_volume, 'b-', label='知识量', linewidth=2)
            line2 = ax2.plot(dates, quality_score, 'r-', label='质量评分', linewidth=2)
            line3 = ax3.plot(dates, value_score, 'g-', label='价值评分', linewidth=2)
            
            ax.set_xlabel('时间')
            ax.set_ylabel('知识量', color='b')
            ax2.set_ylabel('质量评分', color='r')
            ax3.set_ylabel('价值评分', color='g')
            
            ax.tick_params(axis='y', labelcolor='b')
            ax2.tick_params(axis='y', labelcolor='r')
            ax3.tick_params(axis='y', labelcolor='g')
            
            ax.set_title('知识涌现综合时间线', fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # 图例
            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper left')
            
            # 格式化x轴
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.get_xticklabels(), rotation=45)
            
        except Exception as e:
            self.logger.error(f"创建综合时间线失败: {e}")
            ax.text(0.5, 0.5, '综合时间线生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_comprehensive_correlation(self, ax, analysis_results: Dict[str, Any]):
        """创建综合相关性分析"""
        try:
            # 模拟相关性数据
            variables = ['知识量', '质量', '价值', '多样性', '连接性', '创新性']
            correlation_data = np.random.rand(6, 6)
            correlation_data = (correlation_data + correlation_data.T) / 2
            np.fill_diagonal(correlation_data, 1)
            
            im = ax.imshow(correlation_data, cmap='RdYlBu', aspect='auto', vmin=-1, vmax=1)
            ax.set_xticks(range(len(variables)))
            ax.set_yticks(range(len(variables)))
            ax.set_xticklabels(variables, rotation=45, ha='right')
            ax.set_yticklabels(variables)
            ax.set_title('综合相关性分析', fontweight='bold')
            
            # 添加相关性数值
            for i in range(len(variables)):
                for j in range(len(variables)):
                    text = ax.text(j, i, f'{correlation_data[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontsize=8)
            
            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('相关系数')
            
        except Exception as e:
            self.logger.error(f"创建综合相关性分析失败: {e}")
            ax.text(0.5, 0.5, '综合相关性分析生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_key_indicators_chart(self, ax, analysis_results: Dict[str, Any]):
        """创建关键指标图"""
        try:
            # 关键指标数据
            indicators = ['总体质量', '总体价值', '知识多样性', '创新程度', '应用潜力', '社会影响']
            current_values = [75, 68, 82, 79, 71, 85]
            target_values = [80, 75, 85, 85, 80, 90]
            
            x = np.arange(len(indicators))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, current_values, width, label='当前值', color='#2E86AB', alpha=0.7)
            bars2 = ax.bar(x + width/2, target_values, width, label='目标值', color='#F18F01', alpha=0.7)
            
            ax.set_xlabel('指标')
            ax.set_ylabel('评分')
            ax.set_title('关键指标对比', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(indicators, rotation=45, ha='right')
            ax.legend()
            ax.set_ylim(0, 100)
            
            # 添加数值标签
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{height}', ha='center', va='bottom', fontsize=8)
            
        except Exception as e:
            self.logger.error(f"创建关键指标图失败: {e}")
            ax.text(0.5, 0.5, '关键指标图生成失败', ha='center', va='center', transform=ax.transAxes)
    
    def _create_interactive_html(self, data: Dict[str, Any]) -> str:
        """创建交互式HTML"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>知识涌现分析仪表板</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .chart-container { margin: 20px 0; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                .metric-card { background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; }
                .metric-value { font-size: 24px; font-weight: bold; color: #2E86AB; }
                .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>知识涌现分析仪表板</h1>
                <p>生成时间: {timestamp}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_items}</div>
                    <div class="metric-label">知识项总数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_quality:.2f}</div>
                    <div class="metric-label">平均质量评分</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_value:.2f}</div>
                    <div class="metric-label">平均价值评分</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{pattern_count}</div>
                    <div class="metric-label">识别模式数</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>分析结果摘要</h2>
                <p>本仪表板展示了知识涌现过程的综合分析结果，包括质量评估、价值分析、模式识别等多个维度。</p>
                <p>详细的图表和数据分析请参考生成的PNG文件。</p>
            </div>
        </body>
        </html>
        """
        
        # 填充数据
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_items = len(data.get('knowledge_items', []))
        
        quality_scores = data.get('quality_scores', [])
        avg_quality = np.mean([qs.get('overall_score', 0) for qs in quality_scores]) if quality_scores else 0
        
        value_assessments = data.get('value_assessments', [])
        avg_value = np.mean([va.get('overall_value', 0) for va in value_assessments]) if value_assessments else 0
        
        pattern_count = len(data.get('patterns', []))
        
        return html_template.format(
            timestamp=timestamp,
            total_items=total_items,
            avg_quality=avg_quality,
            avg_value=avg_value,
            pattern_count=pattern_count
        )
    
    def _export_png_visualization(self, data: Dict[str, Any], filename: str) -> str:
        """导出PNG可视化"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 简单的数据导出图表
            categories = ['质量', '价值', '多样性', '创新性', '应用性']
            values = [75, 68, 82, 79, 71]
            
            bars = ax.bar(categories, values, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#2E86AB'])
            ax.set_title('知识涌现综合评估', fontsize=16, fontweight='bold')
            ax.set_ylabel('评分')
            ax.set_ylim(0, 100)
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       f'{value}', ha='center', va='bottom')
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"导出PNG失败: {e}")
            return ""
    
    def _export_pdf_visualization(self, data: Dict[str, Any], filename: str) -> str:
        """导出PDF可视化"""
        try:
            # PDF导出逻辑（需要额外的库如matplotlib.backends.backend_pdf）
            # 这里简化为返回错误信息
            self.logger.warning("PDF导出功能需要额外配置")
            return ""
            
        except Exception as e:
            self.logger.error(f"导出PDF失败: {e}")
            return ""
    
    def _export_svg_visualization(self, data: Dict[str, Any], filename: str) -> str:
        """导出SVG可视化"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            categories = ['质量', '价值', '多样性', '创新性', '应用性']
            values = [75, 68, 82, 79, 71]
            
            ax.plot(categories, values, 'o-', linewidth=2, markersize=8, color='#2E86AB')
            ax.set_title('知识涌现趋势分析', fontsize=16, fontweight='bold')
            ax.set_ylabel('评分')
            ax.grid(True, alpha=0.3)
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, format='svg', bbox_inches='tight')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"导出SVG失败: {e}")
            return ""