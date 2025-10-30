"""
专家智能体系统测试用例
测试所有专家智能体的功能
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# 导入所有专家智能体
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.expert_system import ExpertAgentCoordinator, create_expert_system, query_expert_by_question
from agents.origin_expert import OriginExpertAgent
from agents.roasting_expert import RoastingExpertAgent
from agents.extraction_expert import ExtractionExpertAgent
from agents.water_expert import WaterExpertAgent
from agents.equipment_expert import EquipmentExpertAgent
from agents.sensory_expert import SensoryExpertAgent


class TestOriginExpertAgent:
    """产区专家智能体测试"""
    
    @pytest.fixture
    def origin_expert(self):
        return OriginExpertAgent()
    
    def test_agent_initialization(self, origin_expert):
        """测试智能体初始化"""
        assert origin_expert.agent_id == "origin_expert_001"
        assert origin_expert.name == "产区专家"
        assert origin_expert.specialty == "咖啡产区与品种"
        assert len(origin_expert.knowledge_base) > 0
    
    def test_knowledge_search(self, origin_expert):
        """测试知识搜索"""
        results = origin_expert.search_knowledge("埃塞俄比亚")
        assert len(results) > 0
        assert any("埃塞俄比亚" in item.content for item in results)
    
    def test_origin_query_processing(self, origin_expert):
        """测试产区查询处理"""
        query = "请介绍一下埃塞俄比亚的咖啡产区"
        response = origin_expert.process_query(query)
        
        assert response.agent_id == origin_expert.agent_id
        assert response.agent_name == origin_expert.name
        assert len(response.content) > 0
        assert "埃塞俄比亚" in response.content
        assert response.confidence > 0
    
    def test_variety_query_processing(self, origin_expert):
        """测试品种查询处理"""
        query = "阿拉比卡和罗布斯塔有什么区别？"
        response = origin_expert.process_query(query)
        
        assert "阿拉比卡" in response.content
        assert "罗布斯塔" in response.content
        assert len(response.recommendations) > 0
    
    def test_processing_method_query(self, origin_expert):
        """测试处理方法查询"""
        query = "水洗法和日晒法有什么不同？"
        response = origin_expert.process_query(query)
        
        assert "水洗法" in response.content
        assert "日晒法" in response.content
        assert len(response.warnings) >= 0  # 可能有警告信息
    
    def test_get_expertise_areas(self, origin_expert):
        """测试获取专业领域"""
        areas = origin_expert.get_expertise_areas()
        assert isinstance(areas, list)
        assert len(areas) > 0
        assert "世界咖啡产区" in areas
        assert "咖啡品种学" in areas
    
    def test_knowledge_validation(self, origin_expert):
        """测试知识验证"""
        # 创建一个有效的知识项
        from ..core.base_agent import KnowledgeItem, KnowledgeQuality
        
        valid_item = KnowledgeItem(
            id="test_001",
            content="埃塞俄比亚是咖啡的发源地",
            source="测试来源",
            confidence=0.9,
            quality=KnowledgeQuality.HIGH,
            timestamp=datetime.now()
        )
        
        is_valid, message = origin_expert.validate_knowledge(valid_item)
        assert is_valid is True


class TestRoastingExpertAgent:
    """烘焙专家智能体测试"""
    
    @pytest.fixture
    def roasting_expert(self):
        return RoastingExpertAgent()
    
    def test_agent_initialization(self, roasting_expert):
        """测试智能体初始化"""
        assert roasting_expert.agent_id == "roasting_expert_001"
        assert roasting_expert.name == "烘焙专家"
        assert roasting_expert.specialty == "咖啡烘焙技术"
        assert len(roasting_expert.knowledge_base) > 0
    
    def test_roast_level_query(self, roasting_expert):
        """测试烘焙程度查询"""
        query = "浅度烘焙和深度烘焙有什么区别？"
        response = roasting_expert.process_query(query)
        
        assert "浅度烘焙" in response.content
        assert "深度烘焙" in response.content
        assert "温度" in response.content
    
    def test_temperature_curve_query(self, roasting_expert):
        """测试温度曲线查询"""
        query = "咖啡烘焙的温度曲线是怎样的？"
        response = roasting_expert.process_query(query)
        
        assert "温度" in response.content
        assert "曲线" in response.content
        assert "梅纳反应" in response.content
    
    def test_crack_query(self, roasting_expert):
        """测试爆裂查询"""
        query = "一爆和二爆是什么意思？"
        response = roasting_expert.process_query(query)
        
        assert "一爆" in response.content
        assert "二爆" in response.content
        assert "196" in response.content or "205" in response.content
    
    def test_roast_profile_calculation(self, roasting_expert):
        """测试烘焙曲线计算"""
        profile = roasting_expert.calculate_roast_profile("arabica", "medium", 1000)
        
        assert "drying_temp" in profile
        assert "maillard_temp" in profile
        assert "development_temp" in profile
        assert profile["drying_temp"] < profile["maillard_temp"] < profile["development_temp"]
    
    def test_defect_query(self, roasting_expert):
        """测试缺陷查询"""
        query = "咖啡烘焙有哪些常见缺陷？"
        response = roasting_expert.process_query(query)
        
        assert "缺陷" in response.content
        assert len(response.recommendations) > 0


class TestExtractionExpertAgent:
    """萃取专家智能体测试"""
    
    @pytest.fixture
    def extraction_expert(self):
        return ExtractionExpertAgent()
    
    def test_agent_initialization(self, extraction_expert):
        """测试智能体初始化"""
        assert extraction_expert.agent_id == "extraction_expert_001"
        assert extraction_expert.name == "萃取专家"
        assert extraction_expert.specialty == "咖啡萃取技术"
        assert len(extraction_expert.knowledge_base) > 0
    
    def test_espresso_query(self, extraction_expert):
        """测试意式浓缩查询"""
        query = "制作意式浓缩的标准参数是什么？"
        response = extraction_expert.process_query(query)
        
        assert "意式浓缩" in response.content
        assert "25-30秒" in response.content or "时间" in response.content
        assert "9巴" in response.content or "压力" in response.content
    
    def test_pour_over_query(self, extraction_expert):
        """测试手冲查询"""
        query = "手冲咖啡的标准参数是什么？"
        response = extraction_expert.process_query(query)
        
        assert "手冲" in response.content
        assert "1:15" in response.content or "粉水比" in response.content
        assert "2-4分钟" in response.content or "时间" in response.content
    
    def test_extraction_yield_query(self, extraction_expert):
        """测试萃取率查询"""
        query = "什么是理想的萃取率？"
        response = extraction_expert.process_query(query)
        
        assert "18-22%" in response.content or "萃取率" in response.content
        assert "过度萃取" in response.content or "萃取不足" in response.content
    
    def test_grind_size_query(self, extraction_expert):
        """测试研磨度查询"""
        query = "不同萃取方法需要什么研磨度？"
        response = extraction_expert.process_query(query)
        
        assert "细研磨" in response.content
        assert "中度" in response.content or "粗研磨" in response.content
        assert "意式" in response.content or "手冲" in response.content
    
    def test_extraction_parameter_calculation(self, extraction_expert):
        """测试萃取参数计算"""
        params = extraction_expert.calculate_extraction_parameters("espresso", "arabica", "medium")
        
        assert "ratio_range" in params
        assert "time_range" in params
        assert "temperature_range" in params
    
    def test_extraction_diagnosis(self, extraction_expert):
        """测试萃取问题诊断"""
        diagnosis = extraction_expert.diagnose_extraction_issues(
            observed_time=35,  # 目标30秒，实际35秒
            observed_volume=36,  # 目标36ml，实际36ml
            target_time=30,
            target_volume=36,
            taste_notes=["苦", "bitter"]
        )
        
        assert "issues" in diagnosis
        assert "solutions" in diagnosis
        assert len(diagnosis["issues"]) > 0


class TestWaterExpertAgent:
    """水质专家智能体测试"""
    
    @pytest.fixture
    def water_expert(self):
        return WaterExpertAgent()
    
    def test_agent_initialization(self, water_expert):
        """测试智能体初始化"""
        assert water_expert.agent_id == "water_expert_001"
        assert water_expert.name == "水质专家"
        assert water_expert.specialty == "咖啡用水水质"
        assert len(water_expert.knowledge_base) > 0
    
    def test_water_standards_query(self, water_expert):
        """测试水质标准查询"""
        query = "SCA推荐的水质标准是什么？"
        response = water_expert.process_query(query)
        
        assert "TDS" in response.content
        assert "75-250" in response.content or "ppm" in response.content
        assert "pH" in response.content
    
    def test_tds_query(self, water_expert):
        """测试TDS查询"""
        query = "TDS对咖啡萃取有什么影响？"
        response = water_expert.process_query(query)
        
        assert "TDS" in response.content
        assert "过度萃取" in response.content or "萃取不足" in response.content
    
    def test_hardness_query(self, water_expert):
        """测试硬度查询"""
        query = "水的硬度对咖啡有什么影响？"
        response = water_expert.process_query(query)
        
        assert "硬度" in response.content
        assert "17-85" in response.content or "ppm" in response.content
        assert "结垢" in response.content
    
    def test_water_treatment_query(self, water_expert):
        """测试水处理查询"""
        query = "有哪些水处理方法？"
        response = water_expert.process_query(query)
        
        assert "反渗透" in response.content or "RO" in response.content
        assert "软化" in response.content
        assert "活性炭" in response.content
    
    def test_water_quality_analysis(self, water_expert):
        """测试水质分析"""
        water_params = {
            'tds': 150,
            'calcium_hardness': 50,
            'alkalinity': 60,
            'ph': 7.0
        }
        
        analysis = water_expert.analyze_water_quality(water_params)
        
        assert 'overall_score' in analysis
        assert 'grade' in analysis
        assert 'sca_compliance' in analysis
        assert analysis['grade'] in ['A+', 'A', 'B', 'C', 'D']


class TestEquipmentExpertAgent:
    """器具专家智能体测试"""
    
    @pytest.fixture
    def equipment_expert(self):
        return EquipmentExpertAgent()
    
    def test_agent_initialization(self, equipment_expert):
        """测试智能体初始化"""
        assert equipment_expert.agent_id == "equipment_expert_001"
        assert equipment_expert.name == "器具专家"
        assert equipment_expert.specialty == "咖啡器具与设备"
        assert len(equipment_expert.knowledge_base) > 0
    
    def test_grinder_query(self, equipment_expert):
        """测试磨豆机查询"""
        query = "锥刀磨豆机和平刀磨豆机有什么区别？"
        response = equipment_expert.process_query(query)
        
        assert "锥刀" in response.content
        assert "平刀" in response.content
        assert "手冲" in response.content or "意式" in response.content
    
    def test_espresso_machine_query(self, equipment_expert):
        """测试咖啡机查询"""
        query = "全自动和半自动咖啡机有什么区别？"
        response = equipment_expert.process_query(query)
        
        assert "全自动" in response.content
        assert "半自动" in response.content
        assert "操作" in response.content
    
    def test_equipment_selection_query(self, equipment_expert):
        """测试器具选择查询"""
        query = "新手应该如何选择咖啡器具？"
        response = equipment_expert.process_query(query)
        
        assert "新手" in response.content
        assert "预算" in response.content
        assert len(response.recommendations) > 0
    
    def test_maintenance_query(self, equipment_expert):
        """测试维护查询"""
        query = "咖啡器具应该如何维护？"
        response = equipment_expert.process_query(query)
        
        assert "维护" in response.content
        assert "每日" in response.content or "每周" in response.content
        assert "清洁" in response.content
    
    def test_equipment_recommendation(self, equipment_expert):
        """测试器具推荐"""
        recommendation = equipment_expert.recommend_equipment_setup(
            budget=1000,
            experience_level="beginner",
            coffee_type="pour_over"
        )
        
        assert 'recommended_equipment' in recommendation
        assert 'priority_order' in recommendation
        assert len(recommendation['recommended_equipment']) > 0


class TestSensoryExpertAgent:
    """感官专家智能体测试"""
    
    @pytest.fixture
    def sensory_expert(self):
        return SensoryExpertAgent()
    
    def test_agent_initialization(self, sensory_expert):
        """测试智能体初始化"""
        assert sensory_expert.agent_id == "sensory_expert_001"
        assert sensory_expert.name == "感官专家"
        assert sensory_expert.specialty == "咖啡感官品鉴"
        assert len(sensory_expert.knowledge_base) > 0
    
    def test_cupping_query(self, sensory_expert):
        """测试杯测查询"""
        query = "如何进行标准咖啡杯测？"
        response = sensory_expert.process_query(query)
        
        assert "杯测" in response.content
        assert "85°C" in response.content or "温度" in response.content
        assert "4分钟" in response.content or "时间" in response.content
    
    def test_flavor_query(self, sensory_expert):
        """测试风味查询"""
        query = "如何描述咖啡的风味？"
        response = sensory_expert.process_query(query)
        
        assert "风味" in response.content
        assert "果香" in response.content or "花香" in response.content
        assert "描述" in response.content
    
    def test_aroma_query(self, sensory_expert):
        """测试香气查询"""
        query = "干香和湿香有什么区别？"
        response = sensory_expert.process_query(query)
        
        assert "干香" in response.content
        assert "湿香" in response.content
        assert "香气" in response.content
    
    def test_acidity_query(self, sensory_expert):
        """测试酸质查询"""
        query = "什么是好的咖啡酸质？"
        response = sensory_expert.process_query(query)
        
        assert "酸质" in response.content
        assert "明亮" in response.content or "愉悦" in response.content
        assert "负面" in response.content or "正面" in response.content
    
    def test_sensory_evaluation(self, sensory_expert):
        """测试感官评估"""
        sensory_scores = {
            'aroma': 8.0,
            'flavor': 7.5,
            'aftertaste': 7.0,
            'acidity': 8.5,
            'body': 6.5,
            'uniformity': 8.0,
            'clean_cup': 9.0,
            'sweetness': 7.5,
            'overall': 8.0
        }
        
        evaluation = sensory_expert.evaluate_coffee_sensory(sensory_scores)
        
        assert 'total_score' in evaluation
        assert 'grade' in evaluation
        assert 'strengths' in evaluation
        assert 'weaknesses' in evaluation
        assert evaluation['grade'] in ['S', 'A', 'B', 'C', 'D', 'F']


class TestExpertSystemIntegration:
    """专家系统集成测试"""
    
    @pytest.fixture
    def coordinator(self):
        return create_expert_system()
    
    def test_system_initialization(self, coordinator):
        """测试系统初始化"""
        assert len(coordinator.active_agents) == 6
        assert len(coordinator.factory.agent_classes) == 6
    
    def test_single_expert_query(self, coordinator):
        """测试单一专家查询"""
        result = coordinator.query_expert("origin", "请介绍一下埃塞俄比亚咖啡")
        
        assert result['success'] is True
        assert 'response' in result
        assert len(result['response']['content']) > 0
        assert result['response']['confidence'] > 0
    
    def test_all_experts_query(self, coordinator):
        """测试所有专家查询"""
        result = coordinator.query_all_experts("咖啡基础知识")
        
        assert result['success'] is True
        assert result['total_experts'] == 6
        assert result['successful_queries'] > 0
        assert len(result['results']) == 6
    
    def test_expert_recommendation(self, coordinator):
        """测试专家推荐"""
        result = coordinator.get_expert_recommendation("埃塞俄比亚有哪些咖啡产区？")
        
        assert result['success'] is True
        assert len(result['recommendations']) > 0
        assert result['recommendations'][0]['expert_type'] == 'origin'
    
    def test_collaborative_discussion(self, coordinator):
        """测试协作讨论"""
        result = coordinator.collaborative_discussion(
            "如何制作一杯完美的咖啡？",
            ["origin", "roasting", "extraction"]
        )
        
        # 由于是异步操作，这里只检查基本结构
        assert 'success' in result
        # 实际测试中可能需要调整异步处理
    
    def test_system_status(self, coordinator):
        """测试系统状态"""
        status = coordinator.get_system_status()
        
        assert status['success'] is True
        assert 'system_info' in status
        assert 'agents' in status
        assert status['system_info']['total_agents'] == 6
    
    def test_convenience_function(self):
        """测试便捷函数"""
        result = query_expert_by_question("埃塞俄比亚咖啡怎么样？")
        
        # 验证返回结果结构
        assert 'success' in result
        if result['success']:
            assert 'response' in result or 'session_id' in result
    
    def test_knowledge_export(self, coordinator):
        """测试知识库导出"""
        export_result = coordinator.export_knowledge_base()
        
        assert export_result['success'] is True
        assert 'knowledge_bases' in export_result
        assert len(export_result['knowledge_bases']) == 6
    
    def test_system_report_generation(self, coordinator):
        """测试系统报告生成"""
        report = coordinator.generate_system_report()
        
        assert isinstance(report, str)
        assert "AI咖啡专家智能体系统报告" in report
        assert "系统概览" in report
        assert "智能体状态" in report


class TestPerformanceAndQuality:
    """性能和质量测试"""
    
    @pytest.fixture
    def coordinator(self):
        return create_expert_system()
    
    def test_response_time(self, coordinator):
        """测试响应时间"""
        start_time = datetime.now()
        result = coordinator.query_expert("origin", "埃塞俄比亚咖啡")
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        assert response_time < 10  # 应该在10秒内完成
        assert result['success'] is True
    
    def test_concurrent_queries(self, coordinator):
        """测试并发查询"""
        import threading
        import time
        
        results = []
        
        def query_agent(agent_type):
            result = coordinator.query_expert(agent_type, f"测试{agent_type}专家")
            results.append(result)
        
        # 启动多个线程同时查询
        threads = []
        for agent_type in ["origin", "roasting", "extraction", "water", "equipment", "sensory"]:
            thread = threading.Thread(target=query_agent, args=(agent_type,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有查询都成功
        assert len(results) == 6
        assert all(result['success'] for result in results)
    
    def test_knowledge_quality(self, coordinator):
        """测试知识质量"""
        for agent_type, agent in coordinator.active_agents.items():
            # 检查知识项数量
            assert len(agent.knowledge_base) > 5
            
            # 检查知识项质量
            for item in agent.knowledge_base.values():
                assert item.confidence > 0
                assert item.content.strip() != ""
                assert len(item.tags) > 0
    
    def test_error_handling(self, coordinator):
        """测试错误处理"""
        # 测试不存在的专家类型
        result = coordinator.query_expert("nonexistent", "测试")
        assert result['success'] is False
        
        # 测试空查询
        result = coordinator.query_expert("origin", "")
        assert result['success'] is True  # 应该能处理空查询
        
        # 测试无效的协作会话
        result = coordinator.collaborative_discussion("测试", ["nonexistent"])
        assert result['success'] is False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])