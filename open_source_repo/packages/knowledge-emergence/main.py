"""
知识涌现数据收集工具主程序
整合所有模块，提供统一的使用接口
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入所有模块
from data_collector import DataCollector, DataSource
from metrics_calculator import MetricsCalculator
from quality_assessor import QualityAssessor, QualityScore
from pattern_recognizer import PatternRecognizer, Pattern
from value_assessor import ValueAssessor, ValueAssessment
from visualizer import Visualizer
from report_generator import ReportGenerator

# 忽略警告
warnings.filterwarnings('ignore')


class KnowledgeEmergenceAnalyzer:
    """知识涌现分析器主类"""
    
    def __init__(self, config_path: str = None):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # 初始化各个模块
        self.data_collector = DataCollector(self.config.get('data_collector', {}))
        self.metrics_calculator = MetricsCalculator(self.config.get('metrics_calculator', {}))
        self.quality_assessor = QualityAssessor(self.config.get('quality_assessor', {}))
        self.pattern_recognizer = PatternRecognizer(self.config.get('pattern_recognizer', {}))
        self.value_assessor = ValueAssessor(self.config.get('value_assessor', {}))
        self.visualizer = Visualizer(self.config.get('visualizer', {}))
        self.report_generator = ReportGenerator(self.config.get('report_generator', {}))
        
        self.logger.info("知识涌现分析器初始化完成")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'data_collector': {
                'data_sources': [
                    {
                        'name': 'sample_data',
                        'type': 'file',
                        'config': {'path': 'data/sample_knowledge.json'},
                        'enabled': True
                    }
                ]
            },
            'metrics_calculator': {
                'min_pattern_strength': 0.3,
                'time_window_days': 7
            },
            'quality_assessor': {
                'quality_weights': {
                    'accuracy': 0.25,
                    'completeness': 0.20,
                    'consistency': 0.20,
                    'credibility': 0.20,
                    'relevance': 0.15
                }
            },
            'pattern_recognizer': {
                'min_pattern_strength': 0.3,
                'time_window_days': 7,
                'clustering': {
                    'n_clusters': 5,
                    'random_state': 42
                }
            },
            'value_assessor': {
                'value_weights': {
                    'economic': 0.3,
                    'social': 0.25,
                    'application': 0.25,
                    'innovation': 0.2
                }
            },
            'visualizer': {
                'output_dir': 'visualizations',
                'figure_size': (12, 8),
                'dpi': 100
            },
            'report_generator': {
                'output_dir': 'reports',
                'template_style': 'professional',
                'include_charts': True,
                'include_recommendations': True,
                'language': 'zh-CN'
            },
            'output': {
                'base_dir': 'output',
                'create_subdirs': True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并配置
                self._deep_merge(default_config, user_config)
                print(f"已加载配置文件: {config_path}")
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        else:
            print("使用默认配置")
        
        return default_config
    
    def _deep_merge(self, base: Dict, update: Dict):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('KnowledgeEmergence')
        logger.setLevel(logging.INFO)
        
        # 创建输出目录
        output_dir = Path(self.config['output']['base_dir'])
        log_dir = output_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件处理器
        log_file = log_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def analyze(self, data_source: str = None, output_dir: str = None) -> Dict[str, Any]:
        """执行完整的知识涌现分析"""
        try:
            self.logger.info("开始知识涌现分析...")
            
            # 设置输出目录
            if output_dir:
                self.config['output']['base_dir'] = output_dir
                # 更新各模块的输出目录
                self.config['visualizer']['output_dir'] = str(Path(output_dir) / 'visualizations')
                self.config['report_generator']['output_dir'] = str(Path(output_dir) / 'reports')
            
            # 创建输出目录结构
            self._create_output_directories()
            
            # 1. 数据采集
            self.logger.info("步骤 1: 数据采集")
            knowledge_items = self._collect_data(data_source)
            
            if not knowledge_items:
                raise ValueError("未能采集到任何数据")
            
            self.logger.info(f"成功采集 {len(knowledge_items)} 条知识项")
            
            # 2. 指标计算
            self.logger.info("步骤 2: 指标计算")
            metrics_results = self._calculate_metrics(knowledge_items)
            
            # 3. 质量评估
            self.logger.info("步骤 3: 质量评估")
            quality_scores = self._assess_quality(knowledge_items)
            
            # 4. 模式识别
            self.logger.info("步骤 4: 模式识别")
            patterns = self._recognize_patterns(knowledge_items)
            
            # 5. 价值评估
            self.logger.info("步骤 5: 价值评估")
            value_assessments = self._assess_value(knowledge_items)
            
            # 6. 可视化生成
            self.logger.info("步骤 6: 生成可视化")
            visualization_files = self._generate_visualizations({
                'metrics': metrics_results,
                'quality_scores': quality_scores,
                'patterns': patterns,
                'value_assessments': value_assessments
            })
            
            # 7. 报告生成
            self.logger.info("步骤 7: 生成报告")
            report_files = self._generate_reports({
                'knowledge_items': knowledge_items,
                'metrics': metrics_results,
                'quality_scores': quality_scores,
                'patterns': patterns,
                'value_assessments': value_assessments
            })
            
            # 8. 保存分析结果
            self.logger.info("步骤 8: 保存分析结果")
            results_file = self._save_analysis_results({
                'knowledge_items': knowledge_items,
                'metrics': metrics_results,
                'quality_scores': quality_scores,
                'patterns': patterns,
                'value_assessments': value_assessments,
                'visualization_files': visualization_files,
                'report_files': report_files
            })
            
            self.logger.info("知识涌现分析完成!")
            
            return {
                'status': 'success',
                'knowledge_items_count': len(knowledge_items),
                'metrics': metrics_results,
                'quality_scores': quality_scores,
                'patterns': patterns,
                'value_assessments': value_assessments,
                'visualization_files': visualization_files,
                'report_files': report_files,
                'results_file': results_file,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"分析过程中发生错误: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'analysis_time': datetime.now().isoformat()
            }
    
    def _collect_data(self, data_source: str = None) -> List[Dict[str, Any]]:
        """采集数据"""
        try:
            if data_source:
                # 从指定数据源采集
                if data_source.startswith('http'):
                    # API数据源
                    knowledge_items = self.data_collector.collect_from_api({'url': data_source})
                elif os.path.isfile(data_source):
                    # 文件数据源
                    file_ext = Path(data_source).suffix.lower()
                    knowledge_items = self.data_collector.collect_from_file(data_source, file_ext)
                else:
                    # 假设是数据库或API配置
                    knowledge_items = self.data_collector.collect_data(data_source)
            else:
                # 使用默认数据源
                knowledge_items = self.data_collector.collect_data()
            
            # 数据预处理
            processed_data = self.data_collector.preprocess_data(knowledge_items)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"数据采集失败: {e}")
            return []
    
    def _calculate_metrics(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算指标"""
        try:
            return self.metrics_calculator.calculate_all_metrics(knowledge_items)
        except Exception as e:
            self.logger.error(f"指标计算失败: {e}")
            return {}
    
    def _assess_quality(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """评估质量"""
        try:
            quality_scores = self.quality_assessor.assess_batch_quality(knowledge_items)
            # 转换为字典格式以便JSON序列化
            return [score.__dict__ if hasattr(score, '__dict__') else score for score in quality_scores]
        except Exception as e:
            self.logger.error(f"质量评估失败: {e}")
            return []
    
    def _recognize_patterns(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别模式"""
        try:
            all_patterns = []
            
            # 时间模式
            temporal_patterns = self.pattern_recognizer.identify_temporal_patterns(knowledge_items)
            all_patterns.extend([p.__dict__ if hasattr(p, '__dict__') else p for p in temporal_patterns])
            
            # 内容模式
            content_patterns = self.pattern_recognizer.identify_content_patterns(knowledge_items)
            all_patterns.extend([p.__dict__ if hasattr(p, '__dict__') else p for p in content_patterns])
            
            # 结构模式
            structural_patterns = self.pattern_recognizer.identify_structural_patterns(knowledge_items)
            all_patterns.extend([p.__dict__ if hasattr(p, '__dict__') else p for p in structural_patterns])
            
            # 涌现模式
            emergence_patterns = self.pattern_recognizer.identify_emergence_patterns(knowledge_items)
            all_patterns.extend([p.__dict__ if hasattr(p, '__dict__') else p for p in emergence_patterns])
            
            return all_patterns
            
        except Exception as e:
            self.logger.error(f"模式识别失败: {e}")
            return []
    
    def _assess_value(self, knowledge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """评估价值"""
        try:
            value_assessments = self.value_assessor.assess_batch_value(knowledge_items)
            # 转换为字典格式以便JSON序列化
            return [va.__dict__ if hasattr(va, '__dict__') else va for va in value_assessments]
        except Exception as e:
            self.logger.error(f"价值评估失败: {e}")
            return []
    
    def _generate_visualizations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """生成可视化"""
        try:
            visualization_files = []
            
            # 指标可视化
            metrics_viz = self.visualizer.generate_metrics_visualization(
                analysis_data.get('metrics', {}),
                "metrics_overview.png"
            )
            if metrics_viz:
                visualization_files.append(metrics_viz)
            
            # 模式可视化
            patterns_viz = self.visualizer.generate_pattern_visualization(
                analysis_data.get('patterns', []),
                "pattern_analysis.png"
            )
            if patterns_viz:
                visualization_files.append(patterns_viz)
            
            # 质量可视化
            quality_viz = self.visualizer.generate_quality_visualization(
                analysis_data.get('quality_scores', []),
                "quality_analysis.png"
            )
            if quality_viz:
                visualization_files.append(quality_viz)
            
            # 价值可视化
            value_viz = self.visualizer.generate_value_visualization(
                analysis_data.get('value_assessments', []),
                "value_analysis.png"
            )
            if value_viz:
                visualization_files.append(value_viz)
            
            # 综合仪表板
            dashboard_viz = self.visualizer.generate_comprehensive_dashboard(
                {
                    'metrics': analysis_data.get('metrics', {}),
                    'quality': analysis_data.get('quality_scores', []),
                    'value': analysis_data.get('value_assessments', []),
                    'patterns': analysis_data.get('patterns', [])
                },
                "comprehensive_dashboard.png"
            )
            if dashboard_viz:
                visualization_files.append(dashboard_viz)
            
            return visualization_files
            
        except Exception as e:
            self.logger.error(f"可视化生成失败: {e}")
            return []
    
    def _generate_reports(self, analysis_data: Dict[str, Any]) -> List[str]:
        """生成报告"""
        try:
            report_files = []
            
            # 执行摘要
            exec_summary = self.report_generator.generate_executive_summary(analysis_data)
            if exec_summary:
                report_files.append(exec_summary)
            
            # 技术报告
            tech_report = self.report_generator.generate_technical_report(analysis_data)
            if tech_report:
                report_files.append(tech_report)
            
            # 综合报告
            comprehensive_report = self.report_generator.generate_comprehensive_report(analysis_data)
            if comprehensive_report:
                report_files.append(comprehensive_report)
            
            # JSON报告
            json_report = self.report_generator.generate_json_report(analysis_data)
            if json_report:
                report_files.append(json_report)
            
            # HTML报告
            html_report = self.report_generator.generate_html_report(analysis_data)
            if html_report:
                report_files.append(html_report)
            
            return report_files
            
        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            return []
    
    def _save_analysis_results(self, analysis_data: Dict[str, Any]) -> str:
        """保存分析结果"""
        try:
            output_dir = Path(self.config['output']['base_dir'])
            results_file = output_dir / 'analysis_results.json'
            
            # 准备保存数据
            save_data = {
                'metadata': {
                    'generation_time': datetime.now().isoformat(),
                    'version': '1.0',
                    'analyzer_version': '1.0.0'
                },
                'summary': {
                    'knowledge_items_count': len(analysis_data.get('knowledge_items', [])),
                    'patterns_count': len(analysis_data.get('patterns', [])),
                    'visualization_files_count': len(analysis_data.get('visualization_files', [])),
                    'report_files_count': len(analysis_data.get('report_files', []))
                },
                'analysis_data': analysis_data
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
            
            return str(results_file)
            
        except Exception as e:
            self.logger.error(f"保存分析结果失败: {e}")
            return ""
    
    def _create_output_directories(self):
        """创建输出目录结构"""
        base_dir = Path(self.config['output']['base_dir'])
        
        if self.config['output']['create_subdirs']:
            (base_dir / 'visualizations').mkdir(parents=True, exist_ok=True)
            (base_dir / 'reports').mkdir(parents=True, exist_ok=True)
            (base_dir / 'data').mkdir(parents=True, exist_ok=True)
            (base_dir / 'logs').mkdir(parents=True, exist_ok=True)
    
    def quick_analysis(self, data_path: str, output_dir: str = None) -> Dict[str, Any]:
        """快速分析"""
        self.logger.info("执行快速分析...")
        
        # 简化的分析流程
        knowledge_items = self._collect_data(data_path)
        
        if not knowledge_items:
            return {'status': 'error', 'error': '无数据'}
        
        # 只计算基本指标
        metrics = self._calculate_metrics(knowledge_items)
        
        # 生成简单报告
        simple_report = {
            'knowledge_items_count': len(knowledge_items),
            'metrics': metrics,
            'analysis_time': datetime.now().isoformat()
        }
        
        if output_dir:
            output_path = Path(output_dir) / 'quick_analysis.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(simple_report, f, ensure_ascii=False, indent=2, default=str)
            simple_report['output_file'] = str(output_path)
        
        return {'status': 'success', 'results': simple_report}
    
    def batch_analysis(self, data_sources: List[str], output_dir: str = None) -> List[Dict[str, Any]]:
        """批量分析"""
        self.logger.info(f"开始批量分析 {len(data_sources)} 个数据源...")
        
        results = []
        
        for i, source in enumerate(data_sources):
            self.logger.info(f"分析数据源 {i+1}/{len(data_sources)}: {source}")
            
            try:
                result = self.analyze(source, output_dir)
                results.append(result)
            except Exception as e:
                self.logger.error(f"分析数据源 {source} 失败: {e}")
                results.append({
                    'status': 'error',
                    'data_source': source,
                    'error': str(e)
                })
        
        return results
    
    def interactive_mode(self):
        """交互模式"""
        print("\n=== 知识涌现分析器 - 交互模式 ===")
        print("可用命令:")
        print("1. analyze [数据源] [输出目录] - 执行完整分析")
        print("2. quick [数据源] [输出目录] - 快速分析")
        print("3. batch [数据源列表] [输出目录] - 批量分析")
        print("4. config - 显示当前配置")
        print("5. help - 显示帮助")
        print("6. exit - 退出")
        
        while True:
            try:
                command = input("\n请输入命令: ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'exit':
                    print("再见!")
                    break
                elif cmd == 'help':
                    print("帮助信息请查看上面可用命令")
                elif cmd == 'config':
                    self._show_config()
                elif cmd == 'analyze':
                    if len(parts) >= 2:
                        data_source = parts[1]
                        output_dir = parts[2] if len(parts) >= 3 else None
                        result = self.analyze(data_source, output_dir)
                        print(f"分析完成: {result['status']}")
                    else:
                        print("用法: analyze [数据源] [输出目录]")
                elif cmd == 'quick':
                    if len(parts) >= 2:
                        data_source = parts[1]
                        output_dir = parts[2] if len(parts) >= 3 else None
                        result = self.quick_analysis(data_source, output_dir)
                        print(f"快速分析完成: {result['status']}")
                    else:
                        print("用法: quick [数据源] [输出目录]")
                elif cmd == 'batch':
                    if len(parts) >= 3:
                        data_sources = parts[1].split(',')
                        output_dir = parts[2]
                        results = self.batch_analysis(data_sources, output_dir)
                        print(f"批量分析完成，处理了 {len(results)} 个数据源")
                    else:
                        print("用法: batch [数据源1,数据源2,...] [输出目录]")
                else:
                    print(f"未知命令: {cmd}")
                    
            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"命令执行失败: {e}")
    
    def _show_config(self):
        """显示配置"""
        print("\n=== 当前配置 ===")
        print(json.dumps(self.config, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='知识涌现数据收集和分析工具')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--data', '-d', type=str, help='数据源路径或URL')
    parser.add_argument('--output', '-o', type=str, help='输出目录')
    parser.add_argument('--mode', '-m', type=str, choices=['analyze', 'quick', 'batch', 'interactive'], 
                       default='analyze', help='运行模式')
    parser.add_argument('--batch-data', type=str, help='批量分析的数据源列表（用逗号分隔）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = KnowledgeEmergenceAnalyzer(args.config)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.mode == 'interactive':
            analyzer.interactive_mode()
        elif args.mode == 'quick':
            if not args.data:
                print("错误: 快速分析模式需要指定数据源")
                return 1
            result = analyzer.quick_analysis(args.data, args.output)
            print(f"分析结果: {result}")
        elif args.mode == 'batch':
            if not args.batch_data:
                print("错误: 批量分析模式需要指定数据源列表")
                return 1
            data_sources = [s.strip() for s in args.batch_data.split(',')]
            results = analyzer.batch_analysis(data_sources, args.output)
            print(f"批量分析完成，处理了 {len(results)} 个数据源")
        else:  # analyze mode
            result = analyzer.analyze(args.data, args.output)
            print(f"分析完成: {result['status']}")
            if result['status'] == 'success':
                print(f"分析了 {result['knowledge_items_count']} 个知识项")
                print(f"生成了 {len(result['visualization_files'])} 个可视化文件")
                print(f"生成了 {len(result['report_files'])} 个报告文件")
            else:
                print(f"分析失败: {result.get('error', 'Unknown error')}")
        
        return 0
        
    except Exception as e:
        print(f"程序执行失败: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)