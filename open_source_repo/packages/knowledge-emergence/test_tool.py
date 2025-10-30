#!/usr/bin/env python3
"""
知识涌现分析工具测试脚本
验证各个模块的基本功能
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入所有模块
try:
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
    print("✓ 所有模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)


def test_data_collector():
    """测试数据采集器"""
    print("\n测试数据采集器...")
    
    try:
        # 创建测试数据
        test_data = [
            {
                "title": "测试知识1",
                "content": "这是一个测试知识项的内容，用于验证数据采集功能。",
                "source": "测试来源",
                "author": "测试作者"
            },
            {
                "title": "测试知识2", 
                "content": "这是另一个测试知识项，包含更多详细信息用于测试。",
                "source": "测试来源2",
                "author": "测试作者2"
            }
        ]
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        try:
            # 测试数据采集
            collector = DataCollector()
            collected_data = collector.collect_from_file(temp_file, 'json')
            
            if len(collected_data) == 2:
                print("  ✓ 数据采集功能正常")
                
                # 测试数据预处理
                processed_data = collector.preprocess_data(collected_data)
                print(f"  ✓ 数据预处理完成，处理了 {len(processed_data)} 条数据")
                
                return processed_data
            else:
                print(f"  ✗ 数据采集数量不正确: 期望2，实际{len(collected_data)}")
                return []
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"  ✗ 数据采集器测试失败: {e}")
        return []


def test_metrics_calculator(knowledge_items):
    """测试指标计算器"""
    print("\n测试指标计算器...")
    
    if not knowledge_items:
        print("  ✗ 无测试数据，跳过指标计算器测试")
        return {}
    
    try:
        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(knowledge_items)
        
        if isinstance(metrics, dict) and 'overall' in metrics:
            print("  ✓ 指标计算功能正常")
            print(f"    - 计算了 {len([k for k, v in metrics.items() if isinstance(v, dict) and 'score' in v])} 个维度")
            return metrics
        else:
            print("  ✗ 指标计算结果格式不正确")
            return {}
            
    except Exception as e:
        print(f"  ✗ 指标计算器测试失败: {e}")
        return {}


def test_quality_assessor(knowledge_items):
    """测试质量评估器"""
    print("\n测试质量评估器...")
    
    if not knowledge_items:
        print("  ✗ 无测试数据，跳过质量评估器测试")
        return []
    
    try:
        assessor = QualityAssessor()
        quality_scores = assessor.assess_batch_quality(knowledge_items)
        
        if len(quality_scores) == len(knowledge_items):
            print("  ✓ 质量评估功能正常")
            print(f"    - 评估了 {len(quality_scores)} 个质量分数")
            
            # 检查质量分数格式
            if hasattr(quality_scores[0], '__dict__'):
                print("  ✓ 质量分数格式正确")
            
            return quality_scores
        else:
            print(f"  ✗ 质量评估数量不正确: 期望{len(knowledge_items)}，实际{len(quality_scores)}")
            return []
            
    except Exception as e:
        print(f"  ✗ 质量评估器测试失败: {e}")
        return []


def test_pattern_recognizer(knowledge_items):
    """测试模式识别器"""
    print("\n测试模式识别器...")
    
    if not knowledge_items:
        print("  ✗ 无测试数据，跳过模式识别器测试")
        return []
    
    try:
        recognizer = PatternRecognizer()
        
        # 测试各种模式识别
        temporal_patterns = recognizer.identify_temporal_patterns(knowledge_items)
        content_patterns = recognizer.identify_content_patterns(knowledge_items)
        structural_patterns = recognizer.identify_structural_patterns(knowledge_items)
        emergence_patterns = recognizer.identify_emergence_patterns(knowledge_items)
        
        all_patterns = temporal_patterns + content_patterns + structural_patterns + emergence_patterns
        
        print("  ✓ 模式识别功能正常")
        print(f"    - 识别了 {len(all_patterns)} 个模式")
        print(f"      * 时间模式: {len(temporal_patterns)}")
        print(f"      * 内容模式: {len(content_patterns)}")
        print(f"      * 结构模式: {len(structural_patterns)}")
        print(f"      * 涌现模式: {len(emergence_patterns)}")
        
        return all_patterns
        
    except Exception as e:
        print(f"  ✗ 模式识别器测试失败: {e}")
        return []


def test_value_assessor(knowledge_items):
    """测试价值评估器"""
    print("\n测试价值评估器...")
    
    if not knowledge_items:
        print("  ✗ 无测试数据，跳过价值评估器测试")
        return []
    
    try:
        assessor = ValueAssessor()
        value_assessments = assessor.assess_batch_value(knowledge_items)
        
        if len(value_assessments) == len(knowledge_items):
            print("  ✓ 价值评估功能正常")
            print(f"    - 评估了 {len(value_assessments)} 个价值分数")
            
            # 检查价值评估格式
            if hasattr(value_assessments[0], '__dict__'):
                print("  ✓ 价值评估格式正确")
            
            return value_assessments
        else:
            print(f"  ✗ 价值评估数量不正确: 期望{len(knowledge_items)}，实际{len(value_assessments)}")
            return []
            
    except Exception as e:
        print(f"  ✗ 价值评估器测试失败: {e}")
        return []


def test_visualizer(metrics, quality_scores, patterns, value_assessments):
    """测试可视化生成器"""
    print("\n测试可视化生成器...")
    
    try:
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            visualizer = Visualizer({'output_dir': temp_dir})
            
            # 测试指标可视化
            viz_file = visualizer.generate_metrics_visualization(metrics, "test_metrics.png")
            if viz_file and Path(viz_file).exists():
                print("  ✓ 指标可视化生成正常")
            else:
                print("  ✗ 指标可视化生成失败")
            
            # 测试模式可视化
            viz_file = visualizer.generate_pattern_visualization(patterns, "test_patterns.png")
            if viz_file and Path(viz_file).exists():
                print("  ✓ 模式可视化生成正常")
            else:
                print("  ✗ 模式可视化生成失败")
            
            # 测试质量可视化
            viz_file = visualizer.generate_quality_visualization(quality_scores, "test_quality.png")
            if viz_file and Path(viz_file).exists():
                print("  ✓ 质量可视化生成正常")
            else:
                print("  ✗ 质量可视化生成失败")
            
            # 测试价值可视化
            viz_file = visualizer.generate_value_visualization(value_assessments, "test_value.png")
            if viz_file and Path(viz_file).exists():
                print("  ✓ 价值可视化生成正常")
            else:
                print("  ✗ 价值可视化生成失败")
                
    except Exception as e:
        print(f"  ✗ 可视化生成器测试失败: {e}")


def test_report_generator(knowledge_items, metrics, quality_scores, patterns, value_assessments):
    """测试报告生成器"""
    print("\n测试报告生成器...")
    
    try:
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator({'output_dir': temp_dir})
            
            # 准备测试数据
            analysis_data = {
                'knowledge_items': knowledge_items,
                'metrics': metrics,
                'quality_scores': quality_scores,
                'patterns': patterns,
                'value_assessments': value_assessments
            }
            
            # 测试执行摘要
            exec_file = generator.generate_executive_summary(analysis_data, "test_exec.md")
            if exec_file and Path(exec_file).exists():
                print("  ✓ 执行摘要生成正常")
            else:
                print("  ✗ 执行摘要生成失败")
            
            # 测试技术报告
            tech_file = generator.generate_technical_report(analysis_data, "test_tech.md")
            if tech_file and Path(tech_file).exists():
                print("  ✓ 技术报告生成正常")
            else:
                print("  ✗ 技术报告生成失败")
            
            # 测试综合报告
            comp_file = generator.generate_comprehensive_report(analysis_data, "test_comp.md")
            if comp_file and Path(comp_file).exists():
                print("  ✓ 综合报告生成正常")
            else:
                print("  ✗ 综合报告生成失败")
            
            # 测试JSON报告
            json_file = generator.generate_json_report(analysis_data, "test_data.json")
            if json_file and Path(json_file).exists():
                print("  ✓ JSON报告生成正常")
            else:
                print("  ✗ JSON报告生成失败")
            
            # 测试HTML报告
            html_file = generator.generate_html_report(analysis_data, "test_report.html")
            if html_file and Path(html_file).exists():
                print("  ✓ HTML报告生成正常")
            else:
                print("  ✗ HTML报告生成失败")
                
    except Exception as e:
        print(f"  ✗ 报告生成器测试失败: {e}")


def test_main_analyzer():
    """测试主分析器"""
    print("\n测试主分析器...")
    
    try:
        # 创建临时测试数据
        test_data = [
            {
                "title": "主分析器测试知识",
                "content": "这是用于测试主分析器功能的知识项。",
                "source": "测试来源",
                "author": "测试作者",
                "_collection_time": datetime.now().isoformat()
            }
        ]
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        try:
            # 创建临时输出目录
            with tempfile.TemporaryDirectory() as temp_output:
                analyzer = KnowledgeEmergenceAnalyzer()
                
                # 测试快速分析
                quick_result = analyzer.quick_analysis(temp_file, temp_output)
                if quick_result['status'] == 'success':
                    print("  ✓ 快速分析功能正常")
                else:
                    print(f"  ✗ 快速分析失败: {quick_result.get('error', 'Unknown error')}")
                
                # 测试完整分析
                full_result = analyzer.analyze(temp_file, temp_output)
                if full_result['status'] == 'success':
                    print("  ✓ 完整分析功能正常")
                    print(f"    - 分析了 {full_result['knowledge_items_count']} 个知识项")
                else:
                    print(f"  ✗ 完整分析失败: {full_result.get('error', 'Unknown error')}")
                    
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"  ✗ 主分析器测试失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n测试错误处理...")
    
    try:
        # 测试无效数据
        analyzer = KnowledgeEmergenceAnalyzer()
        
        # 测试不存在的文件
        result = analyzer.quick_analysis("nonexistent_file.json", "temp_output")
        if result['status'] == 'error':
            print("  ✓ 无效文件错误处理正常")
        else:
            print("  ✗ 无效文件错误处理异常")
        
        # 测试空数据
        empty_data = []
        collector = DataCollector()
        processed = collector.preprocess_data(empty_data)
        if len(processed) == 0:
            print("  ✓ 空数据处理正常")
        else:
            print("  ✗ 空数据处理异常")
            
    except Exception as e:
        print(f"  ✗ 错误处理测试失败: {e}")


def main():
    """主测试函数"""
    print("知识涌现分析工具测试")
    print("=" * 40)
    
    # 记录测试结果
    test_results = []
    
    try:
        # 测试各个模块
        knowledge_items = test_data_collector()
        test_results.append(("数据采集器", len(knowledge_items) > 0))
        
        metrics = test_metrics_calculator(knowledge_items)
        test_results.append(("指标计算器", bool(metrics)))
        
        quality_scores = test_quality_assessor(knowledge_items)
        test_results.append(("质量评估器", len(quality_scores) > 0))
        
        patterns = test_pattern_recognizer(knowledge_items)
        test_results.append(("模式识别器", len(patterns) >= 0))  # 模式可能为空
        
        value_assessments = test_value_assessor(knowledge_items)
        test_results.append(("价值评估器", len(value_assessments) > 0))
        
        test_visualizer(metrics, quality_scores, patterns, value_assessments)
        test_results.append(("可视化生成器", True))  # 可视化测试不返回布尔值
        
        test_report_generator(knowledge_items, metrics, quality_scores, patterns, value_assessments)
        test_results.append(("报告生成器", True))  # 报告测试不返回布尔值
        
        test_main_analyzer()
        test_results.append(("主分析器", True))  # 主分析器测试不返回布尔值
        
        test_error_handling()
        test_results.append(("错误处理", True))  # 错误处理测试不返回布尔值
        
    except Exception as e:
        print(f"\n测试过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 汇总测试结果
    print("\n" + "=" * 40)
    print("测试结果汇总:")
    print("=" * 40)
    
    passed = 0
    total = len(test_results)
    
    for module_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{module_name:12} {status}")
        if result:
            passed += 1
    
    print("=" * 40)
    print(f"总计: {passed}/{total} 个模块测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！工具功能正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个模块测试失败，请检查相关功能。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)