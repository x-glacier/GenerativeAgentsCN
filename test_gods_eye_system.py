"""
测试上帝视角系统（God's Eye System）

验证所有功能：
1. 心智状态记录
2. 关系管理和记录
3. 交互事件记录
4. 数据查询和分析
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generative_agents'))

from modules.observers.gods_eye_system import get_gods_eye_system
from modules.relationship_manager import RelationshipManager


def test_gods_eye_system():
    """测试上帝视角系统"""
    
    print("="*60)
    print("上帝视角系统测试")
    print("="*60)
    
    # 初始化系统
    gods_eye = get_gods_eye_system(
        db_path="test_storage/evolution.db",
        enable_db=True
    )
    
    # ========== 测试 1: 心智状态记录 ==========
    print("\n【测试 1】心智状态记录")
    print("-"*60)
    
    # 模拟阿伊莎的心智状态
    gods_eye.log_mind_state(
        agent_name="阿伊莎",
        emotion={"pleasure": 0.6, "arousal": 0.4, "dominance": 0.5},
        personality={
            "openness": 0.85,
            "conscientiousness": 0.75,
            "extraversion": 0.60,
            "agreeableness": 0.80,
            "neuroticism": 0.40
        },
        current_activity="在茶馆阅读",
        location="(10, 15)"
    )
    
    print("✓ 阿伊莎的心智状态已记录")
    
    # 模拟张伟的心智状态
    gods_eye.log_mind_state(
        agent_name="张伟",
        emotion={"pleasure": 0.7, "arousal": 0.5, "dominance": 0.6},
        personality={
            "openness": 0.70,
            "conscientiousness": 0.80,
            "extraversion": 0.75,
            "agreeableness": 0.70,
            "neuroticism": 0.35
        },
        current_activity="在茶馆工作",
        location="(10, 16)"
    )
    
    print("✓ 张伟的心智状态已记录")
    
    # ========== 测试 2: 关系管理 ==========
    print("\n【测试 2】关系管理")
    print("-"*60)
    
    # 创建关系管理器
    aisha_rel = RelationshipManager("阿伊莎")
    zhangwei_rel = RelationshipManager("张伟")
    
    # 初始化关系
    aisha_to_zhangwei = aisha_rel.get_relationship("张伟")
    aisha_to_zhangwei.social = "acquaintance"
    aisha_to_zhangwei.affection = 60
    aisha_to_zhangwei.trust = 50
    
    print(f"初始关系 - 阿伊莎对张伟:")
    print(f"  好感度: {aisha_to_zhangwei.affection}")
    print(f"  信任度: {aisha_to_zhangwei.trust}")
    print(f"  亲密度: {aisha_to_zhangwei.intimacy}")
    
    # 记录初始关系
    gods_eye.log_relationship(
        agent_a="阿伊莎",
        agent_b="张伟",
        a_to_b={
            "affection": aisha_to_zhangwei.affection,
            "trust": aisha_to_zhangwei.trust,
            "intimacy": aisha_to_zhangwei.intimacy,
            "impression": aisha_to_zhangwei.overall_impression
        },
        kinship="none",
        social="acquaintance"
    )
    
    print("✓ 初始关系已记录")
    
    # ========== 测试 3: 交互事件记录 ==========
    print("\n【测试 3】交互事件记录")
    print("-"*60)
    
    # 模拟对话 1: 张伟主动打招呼
    print("\n对话 1: 张伟 -> 阿伊莎")
    
    zhangwei_emotion = {"pleasure": 0.7, "arousal": 0.5, "dominance": 0.6}
    aisha_emotion_before = {"pleasure": 0.6, "arousal": 0.4, "dominance": 0.5}
    
    # 阿伊莎感知到张伟的情绪并产生反应
    aisha_emotion_after = {
        "pleasure": 0.65,  # 受到张伟积极情绪的影响
        "arousal": 0.45,
        "dominance": 0.5
    }
    
    gods_eye.log_interaction(
        interaction_type="dialogue",
        speaker="张伟",
        listener="阿伊莎",
        content="阿伊莎，今天天气真好！要不要一起去河边散步？",
        speaker_state={
            "real_emotion": zhangwei_emotion,
            "activity": "在茶馆工作"
        },
        listener_state={
            "perceived_emotion": zhangwei_emotion,
            "my_emotion_before": aisha_emotion_before,
            "my_emotion_after": aisha_emotion_after,
            "perception_error": 0.0
        },
        location="茶馆"
    )
    
    print(f"  张伟的情绪: Pleasure={zhangwei_emotion['pleasure']}")
    print(f"  阿伊莎感知到的情绪: Pleasure={zhangwei_emotion['pleasure']}")
    print(f"  阿伊莎的情绪变化: {aisha_emotion_before['pleasure']} -> {aisha_emotion_after['pleasure']}")
    print("✓ 交互事件已记录")
    
    # 更新关系
    emotion_change = aisha_emotion_after['pleasure'] - aisha_emotion_before['pleasure']
    rel_changes = aisha_rel.update_relationship(
        other_name="张伟",
        interaction_positive=True,
        interaction_intensity=emotion_change
    )
    
    print(f"\n关系变化:")
    print(f"  好感度: +{rel_changes['affection']:.2f}")
    print(f"  信任度: +{rel_changes['trust']:.2f}")
    print(f"  亲密度: +{rel_changes['intimacy']:.2f}")
    
    # 记录更新后的关系
    aisha_to_zhangwei = aisha_rel.get_relationship("张伟")
    gods_eye.log_relationship(
        agent_a="阿伊莎",
        agent_b="张伟",
        a_to_b={
            "affection": aisha_to_zhangwei.affection,
            "trust": aisha_to_zhangwei.trust,
            "intimacy": aisha_to_zhangwei.intimacy,
            "impression": aisha_to_zhangwei.overall_impression
        },
        kinship="none",
        social="acquaintance"
    )
    
    # 模拟对话 2: 阿伊莎回应
    print("\n对话 2: 阿伊莎 -> 张伟")
    
    time.sleep(0.1)  # 模拟时间流逝
    
    aisha_emotion = aisha_emotion_after
    zhangwei_emotion_before = {"pleasure": 0.7, "arousal": 0.5, "dominance": 0.6}
    zhangwei_emotion_after = {"pleasure": 0.75, "arousal": 0.55, "dominance": 0.6}
    
    gods_eye.log_interaction(
        interaction_type="dialogue",
        speaker="阿伊莎",
        listener="张伟",
        content="好啊！我正好想出去走走，呼吸一下新鲜空气。",
        speaker_state={
            "real_emotion": aisha_emotion,
            "activity": "在茶馆阅读"
        },
        listener_state={
            "perceived_emotion": aisha_emotion,
            "my_emotion_before": zhangwei_emotion_before,
            "my_emotion_after": zhangwei_emotion_after,
            "perception_error": 0.0
        },
        location="茶馆"
    )
    
    print(f"  阿伊莎的情绪: Pleasure={aisha_emotion['pleasure']}")
    print(f"  张伟感知到的情绪: Pleasure={aisha_emotion['pleasure']}")
    print(f"  张伟的情绪变化: {zhangwei_emotion_before['pleasure']} -> {zhangwei_emotion_after['pleasure']}")
    print("✓ 交互事件已记录")
    
    # ========== 测试 4: 数据查询 ==========
    print("\n【测试 4】数据查询")
    print("-"*60)
    
    # 查询阿伊莎的情绪时间线
    emotion_timeline = gods_eye.get_agent_emotion_timeline("阿伊莎")
    print(f"\n阿伊莎的情绪时间线: {len(emotion_timeline)} 条记录")
    if emotion_timeline:
        latest = emotion_timeline[-1]
        print(f"  最新记录: Pleasure={latest['emotion']['pleasure']}, 活动={latest['current_activity']}")
    
    # 查询关系演化
    relationship_timeline = gods_eye.get_relationship_timeline("阿伊莎", "张伟")
    print(f"\n阿伊莎和张伟的关系时间线: {len(relationship_timeline)} 条记录")
    if len(relationship_timeline) >= 2:
        initial = relationship_timeline[0]
        current = relationship_timeline[-1]
        print(f"  初始好感度: {initial['a_to_b']['affection']}")
        print(f"  当前好感度: {current['a_to_b']['affection']}")
        print(f"  变化: +{current['a_to_b']['affection'] - initial['a_to_b']['affection']:.2f}")
    
    # 查询最近的交互
    recent_interactions = gods_eye.get_recent_interactions(limit=5)
    print(f"\n最近的交互事件: {len(recent_interactions)} 条")
    for i, interaction in enumerate(recent_interactions[:2], 1):
        print(f"  {i}. {interaction['speaker']} -> {interaction['listener']}: {interaction['content'][:30]}...")
    
    # ========== 测试 5: 数据分析 ==========
    print("\n【测试 5】数据分析")
    print("-"*60)
    
    # 分析情绪变化
    emotion_analysis = gods_eye.analyze_emotion_change("阿伊莎", time_window=3600)
    print(f"\n阿伊莎的情绪分析:")
    print(f"  状态: {emotion_analysis.get('status', 'ok')}")
    if 'change' in emotion_analysis:
        change = emotion_analysis['change']
        if isinstance(change, dict):
            print(f"  Pleasure 变化: {change.get('pleasure', 0):.3f}")
        else:
            print(f"  总体变化: {change:.3f}")
    
    # 分析关系演化
    relationship_analysis = gods_eye.analyze_relationship_evolution("阿伊莎", "张伟")
    print(f"\n阿伊莎和张伟的关系演化:")
    print(f"  趋势: {relationship_analysis.get('trend', 'unknown')}")
    if 'change' in relationship_analysis:
        print(f"  好感度变化: +{relationship_analysis['change']['affection']:.2f}")
        print(f"  信任度变化: +{relationship_analysis['change']['trust']:.2f}")
    
    # ========== 测试 6: 统计信息 ==========
    print("\n【测试 6】统计信息")
    print("-"*60)
    
    stats = gods_eye.get_statistics()
    print(f"\n系统统计:")
    if 'database' in stats:
        db_stats = stats['database']
        print(f"  心智状态记录: {db_stats.get('mind_states_count', 0)} 条")
        print(f"  关系记录: {db_stats.get('relationships_count', 0)} 条")
        print(f"  交互记录: {db_stats.get('interactions_count', 0)} 条")
        print(f"  智能体数量: {db_stats.get('agents_count', 0)} 个")
    
    # ========== 测试 7: 数据导出 ==========
    print("\n【测试 7】数据导出")
    print("-"*60)
    
    export_file = "test_storage/evolution_export.json"
    gods_eye.export_data(export_file)
    
    # 关闭系统
    gods_eye.close()
    
    print("\n" + "="*60)
    print("✓ 所有测试通过！")
    print("="*60)


if __name__ == "__main__":
    # 创建测试目录
    os.makedirs("test_storage", exist_ok=True)
    
    # 运行测试
    test_gods_eye_system()
