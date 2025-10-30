#!/usr/bin/env python3
"""
知识涌现分析工具使用示例
演示如何使用各个模块进行分析
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from knowledge_emergence import (
    KnowledgeEmergenceAnalyzer,
    DataCollector,
    MetricsCalculator,
    QualityAssessor,
    PatternRecognizer,
    ValueAssessor,
    Visualizer,
    ReportGenerator
)


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=== 示例1: 基本使用 ===")
    
    # 创建分析器
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 执行分析
    result = analyzer.analyze(
        data_source="data_example.json",
        output_dir="output_example1"
    )
    
    print(f"分析结果: {result['status']}")
    if result['status'] == 'success':
        print(f"知识项数量: {result['knowledge_items_count']}")
        print(f"可视化文件: {len(result['visualization_files'])}")
        print(f"报告文件: {len(result['report_files'])}")
    else:
        print(f"错误: {result.get('error', 'Unknown error')}")
    
    print()


def example_2_quick_analysis():
    """示例2: 快速分析"""
    print("=== 示例2: 快速分析 ===")
    
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 快速分析
    result = analyzer.quick_analysis(
        data_path="data_example.json",
        output_dir="output_example2"
    )
    
    print(f"快速分析结果: {result['status']}")
    if result['status'] == 'success':
        results = result['results']
        print(f"知识项数量: {results['knowledge_items_count']}")
        if 'output_file' in results:
            print(f"输出文件: {results['output_file']}")
    else:
        print(f"错误: {result.get('error', 'Unknown error')}")
    
    print()


def example_3_individual_modules():
    """示例3: 单独使用各个模块"""
    print("=== 示例3: 单独使用各个模块 ===")
    
    # 1. 数据采集
    print("1. 数据采集...")
    collector = DataCollector()
    knowledge_items = collector.collect_from_file("data_example.json", "json")
    processed_data = collector.preprocess_data(knowledge_items)
    print(f"   采集到 {len(processed_data)} 条数据")
    
    # 2. 指标计算
    print("2. 指标计算...")
    calculator = MetricsCalculator()
    metrics = calculator.calculate_all_metrics(processed_data)
    print(f"   计算了 {len(metrics)} 个维度的指标")
    
    # 3. 质量评估
    print("3. 质量评估...")
    assessor = QualityAssessor()
    quality_scores = assessor.assess_batch_quality(processed_data)
    print(f"   评估了 {len(quality_scores)} 个质量分数")
    
    # 4. 模式识别
    print("4. 模式识别...")
    recognizer = PatternRecognizer()
    patterns = []
    patterns.extend(recognizer.identify_temporal_patterns(processed_data))
    patterns.extend(recognizer.identify_content_patterns(processed_data))
    print(f"   识别了 {len(patterns)} 个模式")
    
    # 5. 价值评估
    print("5. 价值评估...")
    value_assessor = ValueAssessor()
    value_assessments = value_assessor.assess_batch_value(processed_data)
    print(f"   评估了 {len(value_assessments)} 个价值分数")
    
    # 6. 可视化
    print("6. 生成可视化...")
    visualizer = Visualizer()
    viz_file = visualizer.generate_metrics_visualization(
        metrics, 
        "example_metrics.png"
    )
    print(f"   生成可视化文件: {viz_file}")
    
    # 7. 报告生成
    print("7. 生成报告...")
    generator = ReportGenerator()
    analysis_data = {
        'knowledge_items': processed_data,
        'metrics': metrics,
        'quality_scores': quality_scores,
        'patterns': patterns,
        'value_assessments': value_assessments
    }
    report_file = generator.generate_executive_summary(analysis_data)
    print(f"   生成报告文件: {report_file}")
    
    print()


def example_4_custom_config():
    """示例4: 使用自定义配置"""
    print("=== 示例4: 使用自定义配置 ===")
    
    # 创建自定义配置
    custom_config = {
        'data_collector': {
            'data_sources': [
                {
                    'name': 'example_data',
                    'type': 'file',
                    'config': {'path': 'data_example.json'},
                    'enabled': True
                }
            ]
        },
        'metrics_calculator': {
            'min_pattern_strength': 0.5,  # 提高模式识别阈值
            'time_window_days': 3
        },
        'quality_assessor': {
            'quality_weights': {
                'accuracy': 0.3,      # 提高准确性权重
                'completeness': 0.25,
                'consistency': 0.2,
                'credibility': 0.15,
                'relevance': 0.1
            }
        },
        'output': {
            'base_dir': 'output_custom',
            'create_subdirs': True
        }
    }
    
    # 保存配置
    import json
    with open('custom_config.json', 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, ensure_ascii=False, indent=2)
    
    # 使用自定义配置
    analyzer = KnowledgeEmergenceAnalyzer('custom_config.json')
    
    result = analyzer.analyze(
        data_source="data_example.json",
        output_dir="output_custom"
    )
    
    print(f"自定义配置分析结果: {result['status']}")
    
    # 清理临时文件
    if os.path.exists('custom_config.json'):
        os.remove('custom_config.json')
    
    print()


def example_5_batch_analysis():
    """示例5: 批量分析"""
    print("=== 示例5: 批量分析 ===")
    
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 模拟多个数据源
    data_sources = [
        "data_example.json",
        "data_example.json",  # 重复使用示例数据
        "data_example.json"
    ]
    
    results = analyzer.batch_analysis(
        data_sources=data_sources,
        output_dir="output_batch"
    )
    
    print(f"批量分析完成，处理了 {len(results)} 个数据源")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"成功: {success_count}, 失败: {len(results) - success_count}")
    
    print()


def example_6_interactive_mode():
    """示例6: 交互模式演示"""
    print("=== 示例6: 交互模式 ===")
    print("启动交互模式 (输入 'exit' 退出)...")
    
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 模拟交互命令
    commands = [
        "analyze data_example.json output_interactive",
        "quick data_example.json output_quick",
        "config",
        "exit"
    ]
    
    print("模拟交互命令:")
    for cmd in commands:
        print(f"  > {cmd}")
        
        if cmd.startswith('analyze'):
            parts = cmd.split()
            data_source = parts[1]
            output_dir = parts[2]
            result = analyzer.analyze(data_source, output_dir)
            print(f"    结果: {result['status']}")
            
        elif cmd.startswith('quick'):
            parts = cmd.split()
            data_source = parts[1]
            output_dir = parts[2]
            result = analyzer.quick_analysis(data_source, output_dir)
            print(f"    结果: {result['status']}")
            
        elif cmd == 'config':
            print("    配置信息已显示")
            
        elif cmd == 'exit':
            print("    退出交互模式")
            break
    
    print()


def example_7_data_analysis_insights():
    """示例7: 数据分析洞察"""
    print("=== 示例7: 数据分析洞察 ===")
    
    analyzer = KnowledgeEmergenceAnalyzer()
    
    # 执行完整分析
    result = analyzer.analyze(
        data_source="data_example.json",
        output_dir="output_insights"
    )
    
    if result['status'] == 'success':
        # 获取分析数据
        knowledge_items = result['knowledge_items']
        metrics = result['metrics']
        quality_scores = result['quality_scores']
        patterns = result['patterns']
        value_assessments = result['value_assessments']
        
        print("=== 分析洞察 ===")
        
        # 数据概况
        print(f"1. 数据概况:")
        print(f"   - 总知识项: {len(knowledge_items)}")
        
        # 质量分析
        if quality_scores:
            avg_quality = sum(qs.get('overall_score', 0) for qs in quality_scores) / len(quality_scores)
            print(f"   - 平均质量: {avg_quality:.3f}")
            
            high_quality = len([qs for qs in quality_scores if qs.get('overall_score', 0) >= 0.8])
            print(f"   - 高质量项目: {high_quality} ({high_quality/len(quality_scores)*100:.1f}%)")
        
        # 价值分析
        if value_assessments:
            avg_value = sum(va.get('overall_value', 0) for va in value_assessments) / len(value_assessments)
            print(f"   - 平均价值: {avg_value:.3f}")
            
            high_value = len([va for va in value_assessments if va.get('overall_value', 0) >= 0.7])
            print(f"   - 高价值项目: {high_value} ({high_value/len(value_assessments)*100:.1f}%)")
        
        # 模式分析
        print(f"2. 模式识别:")
        print(f"   - 识别模式数: {len(patterns)}")
        
        if patterns:
            pattern_types = {}
            for pattern in patterns:
                ptype = pattern.get('pattern_type', 'unknown')
                pattern_types[ptype] = pattern_types.get(ptype, 0) + 1
            
            print("   - 主要模式类型:")
            for ptype, count in pattern_types.items():
                print(f"     * {ptype}: {count}")
        
        # 指标分析
        print(f"3. 指标分析:")
        if metrics and 'overall' in metrics:
            overall_score = metrics['overall'].get('total_score', 0)
            print(f"   - 总体涌现评分: {overall_score:.1f}")
            
            for dimension, data in metrics.items():
                if isinstance(data, dict) and 'score' in data:
                    print(f"   - {dimension.capitalize()}: {data['score']:.1f}")
        
        # 建议
        print(f"4. 改进建议:")
        if avg_quality < 0.8:
            print("   - 质量有提升空间，建议加强质量控制")
        if avg_value < 0.7:
            print("   - 价值挖掘不足，建议重点关注高价值知识")
        if len(patterns) < 3:
            print("   - 模式识别较少，建议扩大数据范围")
        
    else:
        print(f"分析失败: {result.get('error', 'Unknown error')}")
    
    print()


def main():
    """主函数"""
    print("知识涌现分析工具使用示例")
    print("=" * 50)
    
    # 检查示例数据是否存在
    if not Path("data_example.json").exists():
        print("错误: 示例数据文件 data_example.json 不存在")
        print("请确保在正确的目录下运行此脚本")
        return
    
    try:
        # 运行各个示例
        example_1_basic_usage()
        example_2_quick_analysis()
        example_3_individual_modules()
        example_4_custom_config()
        example_5_batch_analysis()
        example_6_interactive_mode()
        example_7_data_analysis_insights()
        
        print("所有示例运行完成!")
        print("\n生成的文件位于以下目录:")
        print("- output_example1/ - 基本分析结果")
        print("- output_example2/ - 快速分析结果")
        print("- output_custom/ - 自定义配置分析结果")
        print("- output_batch/ - 批量分析结果")
        print("- output_interactive/ - 交互模式分析结果")
        print("- output_insights/ - 洞察分析结果")
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()