"""
知识涌现数据收集工具
一个完整的知识涌现分析和评估系统
"""

from .data_collector import DataCollector, DataSource
from .metrics_calculator import MetricsCalculator
from .quality_assessor import QualityAssessor, QualityScore
from .pattern_recognizer import PatternRecognizer, Pattern
from .value_assessor import ValueAssessor, ValueAssessment
from .visualizer import Visualizer
from .report_generator import ReportGenerator
from .main import KnowledgeEmergenceAnalyzer

__version__ = '1.0.0'
__author__ = 'Knowledge Emergence Analysis Team'
__description__ = 'Knowledge Emergence Data Collection and Analysis Tool'

__all__ = [
    'DataCollector',
    'DataSource', 
    'MetricsCalculator',
    'QualityAssessor',
    'QualityScore',
    'PatternRecognizer',
    'Pattern',
    'ValueAssessor',
    'ValueAssessment',
    'Visualizer',
    'ReportGenerator',
    'KnowledgeEmergenceAnalyzer'
]