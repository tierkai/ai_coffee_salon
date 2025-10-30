#!/usr/bin/env python3
"""
咖啡专家智能体系统使用示例
展示如何使用6大专家智能体进行咖啡相关的查询和咨询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.expert_system import create_expert_system, query_expert_by_question

def main():
    """演示专家智能体系统的使用"""
    print("=" * 60)
    print("咖啡专家智能体系统演示")
    print("=" * 60)
    
    # 创建专家系统
    print("\n1. 初始化专家系统...")
    system = create_expert_system()
    print("✅ 专家系统初始化完成")
    
    # 展示所有专家
    print("\n2. 可用的专家智能体：")
    status = system.get_system_status()
    for agent in status['agents_info']:
        print(f"   • {agent['name']} - {agent['specialty']}")
    
    # 演示不同类型的查询
    queries = [
        {
            "question": "埃塞俄比亚耶加雪菲咖啡有什么特点？",
            "description": "产区专家查询"
        },
        {
            "question": "浅烘和深烘有什么区别？",
            "description": "烘焙专家查询"
        },
        {
            "question": "如何制作一杯完美的意式浓缩？",
            "description": "萃取专家查询"
        },
        {
            "question": "咖啡用水的TDS应该是多少？",
            "description": "水质专家查询"
        },
        {
            "question": "新手应该选择什么样的磨豆机？",
            "description": "器具专家查询"
        },
        {
            "question": "如何描述咖啡的风味特征？",
            "description": "感官专家查询"
        },
        {
            "question": "我想开一家咖啡店，需要什么设备？",
            "description": "复杂问题，需要多专家协作"
        }
    ]
    
    print("\n3. 开始演示查询...")
    for i, query_info in enumerate(queries, 1):
        print(f"\n--- 查询 {i}: {query_info['description']} ---")
        print(f"问题: {query_info['question']}")
        
        # 获取专家推荐
        recommendation = query_expert_by_question(query_info['question'])
        print(f"推荐专家: {recommendation['recommendations'][0]['expert_type']}")
        print(f"推荐理由: {recommendation['recommendations'][0]['reason']}")
        
        # 执行查询
        result = system.process_query(
            query_info['question'],
            preferred_expert=recommendation['recommendations'][0]['expert_type']
        )
        
        if 'response' in result:
            print(f"回答: {result['response']['content'][:200]}...")
        elif 'session_id' in result:
            print("已创建多专家协作讨论...")
    
    # 展示系统状态
    print("\n4. 系统运行状态:")
    final_status = system.get_system_status()
    print(f"   • 总查询数: {final_status['system_info']['total_queries']}")
    print(f"   • 协作会话数: {final_status['system_info']['collaboration_metrics']['total_sessions']}")
    print(f"   • 知识共享次数: {final_status['system_info']['collaboration_metrics']['knowledge_shares']}")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    main()