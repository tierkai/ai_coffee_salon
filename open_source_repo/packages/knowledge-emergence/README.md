# 知识涌现数据收集工具

一个完整的知识涌现分析和评估系统，用于收集、分析和评估知识产生过程中的各种指标。

## 功能特性

### 🔍 数据采集 (Data Collector)
- 支持多种数据源：文件、API、数据库、网页
- 自动数据清洗和预处理
- 数据源配置管理
- 数据质量检查

### 📊 指标计算 (Metrics Calculator)
- **多样性指标**: 香农多样性指数、辛普森指数、基尼系数
- **连接性指标**: 网络密度、聚类系数、平均连接度
- **复杂性指标**: 词汇复杂性、句子复杂性、概念密度
- **涌现性指标**: 涌现强度、创新率、知识整合度
- **连贯性指标**: 文本相似性、连贯性稳定性
- **影响力指标**: 影响力评分、重要性评估

### ✅ 质量评估 (Quality Assessor)
- **准确性评估**: 数值一致性、逻辑一致性、来源可信度
- **完整性评估**: 基本要素、结构完整性、上下文完整性
- **一致性评估**: 概念定义一致性、逻辑一致性、数值一致性
- **可信度评估**: 可信度指示词、来源可信度、语言客观性
- **相关性评估**: 主题相关性、信息密度、时效性

### 🎯 模式识别 (Pattern Recognizer)
- **时间模式**: 周期性模式、趋势模式、爆发模式、收敛模式
- **内容模式**: 主题演化、概念关联、领域分布、质量变化
- **结构模式**: 网络结构、层次结构、聚类模式
- **涌现模式**: 自组织、协同效应、相变模式、临界点

### 💎 价值评估 (Value Assessor)
- **经济价值**: 商业价值、市场潜力、成本效益、投资价值
- **社会价值**: 社会效益、公共利益、教育价值、文化价值
- **应用价值**: 实用性、技术成熟度、可实施性、工具化潜力
- **创新价值**: 原创性、颠覆性潜力、前沿性

### 📈 可视化生成 (Visualizer)
- 指标概览雷达图
- 质量分布分析图
- 价值分析图表
- 模式识别可视化
- 综合仪表板
- 交互式HTML报告

### 📋 报告生成 (Report Generator)
- 执行摘要报告
- 技术分析报告
- 综合分析报告
- JSON数据报告
- HTML可视化报告
- 批量报告生成

## 安装要求

```bash
pip install numpy pandas scikit-learn matplotlib seaborn scipy
```

## 快速开始

### 1. 基本使用

```python
from knowledge_emergence import KnowledgeEmergenceAnalyzer

# 创建分析器
analyzer = KnowledgeEmergenceAnalyzer()

# 执行完整分析
result = analyzer.analyze(
    data_source='data/knowledge_base.json',
    output_dir='output'
)

print(f"分析完成: {result['status']}")
print(f"知识项数量: {result['knowledge_items_count']}")
```

### 2. 命令行使用

```bash
# 基本分析
python main.py --data data/knowledge.json --output results/

# 快速分析
python main.py --mode quick --data data/knowledge.json

# 批量分析
python main.py --mode batch --batch-data "data1.json,data2.json,data3.json" --output batch_results/

# 交互模式
python main.py --mode interactive
```

### 3. 配置文件

创建 `config.json` 配置文件：

```json
{
  "data_collector": {
    "data_sources": [
      {
        "name": "knowledge_base",
        "type": "file",
        "config": {
          "path": "data/knowledge_base.json"
        },
        "enabled": true
      }
    ]
  },
  "metrics_calculator": {
    "min_pattern_strength": 0.3,
    "time_window_days": 7
  },
  "quality_assessor": {
    "quality_weights": {
      "accuracy": 0.25,
      "completeness": 0.20,
      "consistency": 0.20,
      "credibility": 0.20,
      "relevance": 0.15
    }
  },
  "output": {
    "base_dir": "output",
    "create_subdirs": true
  }
}
```

然后使用配置文件：

```bash
python main.py --config config.json --data data/knowledge.json
```

## 数据格式

### 输入数据格式

支持JSON、CSV、TXT格式的知识数据：

```json
[
  {
    "title": "人工智能发展趋势",
    "content": "人工智能技术在近年来取得了显著进展，特别是在深度学习、自然语言处理等领域...",
    "source": "科技日报",
    "author": "张研究员",
    "publication_date": "2024-01-15",
    "tags": ["AI", "技术", "发展"],
    "importance": 8,
    "citations": 15
  },
  {
    "title": "机器学习算法优化",
    "content": "机器学习算法的优化是提升模型性能的关键方法...",
    "source": "学术期刊",
    "author": "李博士",
    "publication_date": "2024-01-20",
    "tags": ["ML", "算法", "优化"],
    "importance": 7,
    "citations": 12
  }
]
```

### 输出结果

分析完成后，会在输出目录生成以下文件：

```
output/
├── analysis_results.json          # 完整分析结果
├── visualizations/                # 可视化图表
│   ├── metrics_overview.png
│   ├── pattern_analysis.png
│   ├── quality_analysis.png
│   ├── value_analysis.png
│   └── comprehensive_dashboard.png
├── reports/                       # 分析报告
│   ├── executive_summary.md
│   ├── technical_report.md
│   ├── comprehensive_report.md
│   ├── analysis_results.json
│   └── report.html
└── logs/                         # 日志文件
    └── analysis_20241201_143022.log
```

## 核心类说明

### KnowledgeEmergenceAnalyzer
主分析器类，整合所有功能模块。

```python
analyzer = KnowledgeEmergenceAnalyzer(config_path=None)
result = analyzer.analyze(data_source=None, output_dir=None)
```

### DataCollector
数据采集器，支持多种数据源。

```python
collector = DataCollector(config)
data = collector.collect_data()
processed_data = collector.preprocess_data(data)
```

### MetricsCalculator
指标计算器，计算知识涌现的各种指标。

```python
calculator = MetricsCalculator(config)
metrics = calculator.calculate_all_metrics(knowledge_items)
```

### QualityAssessor
质量评估器，评估知识的质量属性。

```python
assessor = QualityAssessor(config)
quality_score = assessor.assess_quality(knowledge_item)
quality_scores = assessor.assess_batch_quality(knowledge_items)
```

### PatternRecognizer
模式识别器，识别知识涌现的模式。

```python
recognizer = PatternRecognizer(config)
patterns = recognizer.identify_temporal_patterns(knowledge_items)
patterns += recognizer.identify_content_patterns(knowledge_items)
```

### ValueAssessor
价值评估器，评估知识的经济和社会价值。

```python
assessor = ValueAssessor(config)
value_assessment = assessor.assess_comprehensive_value(knowledge_item)
value_assessments = assessor.assess_batch_value(knowledge_items)
```

### Visualizer
可视化生成器，生成各种图表。

```python
visualizer = Visualizer(config)
viz_file = visualizer.generate_metrics_visualization(metrics_data)
```

### ReportGenerator
报告生成器，生成详细的分析报告。

```python
generator = ReportGenerator(config)
report_file = generator.generate_comprehensive_report(analysis_results)
```

## 高级功能

### 1. 自定义指标

可以扩展指标计算器来添加自定义指标：

```python
class CustomMetricsCalculator(MetricsCalculator):
    def calculate_custom_metric(self, knowledge_items):
        # 实现自定义指标计算
        pass
```

### 2. 自定义质量评估

可以扩展质量评估器来添加自定义质量维度：

```python
class CustomQualityAssessor(QualityAssessor):
    def assess_custom_dimension(self, knowledge_item):
        # 实现自定义质量维度评估
        pass
```

### 3. 自定义模式识别

可以扩展模式识别器来识别自定义模式：

```python
class CustomPatternRecognizer(PatternRecognizer):
    def identify_custom_patterns(self, knowledge_items):
        # 实现自定义模式识别
        pass
```

## 性能优化

### 1. 大数据处理
- 使用分批处理来处理大规模数据
- 启用并行计算来提高处理速度
- 缓存中间结果来避免重复计算

### 2. 内存优化
- 使用生成器来处理大量数据
- 及时释放不需要的中间变量
- 使用适当的数据结构

### 3. 计算优化
- 使用向量化操作代替循环
- 利用NumPy和Pandas的优化函数
- 避免重复的计算操作

## 故障排除

### 常见问题

1. **数据采集失败**
   - 检查数据源路径是否正确
   - 确认数据格式是否符合要求
   - 检查网络连接（对于API数据源）

2. **指标计算错误**
   - 确认输入数据包含必要的字段
   - 检查数据预处理是否正确
   - 验证算法参数设置

3. **可视化生成失败**
   - 检查matplotlib配置
   - 确认输出目录有写入权限
   - 验证数据格式是否正确

4. **报告生成问题**
   - 检查模板文件是否存在
   - 确认输出目录有写入权限
   - 验证数据序列化是否成功

### 日志调试

系统会生成详细的日志文件，位于 `output/logs/` 目录下。通过查看日志可以了解详细的执行过程和错误信息。

```bash
# 查看最新日志
tail -f output/logs/analysis_*.log

# 搜索错误信息
grep "ERROR" output/logs/analysis_*.log
```

## 扩展开发

### 1. 添加新的数据源

继承 `DataCollector` 类并实现新的采集方法：

```python
class CustomDataCollector(DataCollector):
    def collect_from_custom_source(self, source_config):
        # 实现自定义数据源采集
        pass
```

### 2. 添加新的指标

继承 `MetricsCalculator` 类并实现新的指标计算：

```python
class CustomMetricsCalculator(MetricsCalculator):
    def calculate_custom_metric(self, knowledge_items):
        # 实现自定义指标
        pass
```

### 3. 添加新的可视化

继承 `Visualizer` 类并实现新的可视化方法：

```python
class CustomVisualizer(Visualizer):
    def generate_custom_chart(self, data, output_filename):
        # 实现自定义图表
        pass
```

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: knowledge-emergence@example.com
- 项目主页: https://github.com/knowledge-emergence/tool

---

*本工具旨在帮助研究人员和从业者更好地理解和分析知识涌现过程。*