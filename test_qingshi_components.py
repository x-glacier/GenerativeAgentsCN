#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
青石镇组件测试脚本
测试各个核心组件的功能
"""

import json
import os
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / 'generative_agents'))

def test_1_config_files():
    """测试1: 配置文件完整性"""
    print("\n" + "=" * 60)
    print("测试 1: 配置文件完整性")
    print("=" * 60)
    
    agents_dir = Path('generative_agents/frontend/static/assets/qingshi_town/agents')
    
    if not agents_dir.exists():
        print(f"✗ 角色目录不存在: {agents_dir}")
        return False
    
    agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir()]
    print(f"✓ 找到 {len(agent_dirs)} 个角色目录")
    
    success_count = 0
    for agent_dir in sorted(agent_dirs):
        agent_name = agent_dir.name
        agent_config_path = agent_dir / 'agent.json'
        
        if not agent_config_path.exists():
            print(f"  ✗ {agent_name}: 缺少 agent.json")
            continue
        
        try:
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必需字段
            required_fields = ['name', 'coord', 'currently', 'scratch', 'spatial']
            missing_fields = [f for f in required_fields if f not in config]
            
            if missing_fields:
                print(f"  ✗ {agent_name}: 缺少字段 {missing_fields}")
                continue
            
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ {agent_name}: {e}")
    
    print(f"\n✓ 成功: {success_count}/{len(agent_dirs)}")
    return success_count == len(agent_dirs)

def test_2_maze_config():
    """测试2: 地图配置"""
    print("\n" + "=" * 60)
    print("测试 2: 地图配置")
    print("=" * 60)
    
    maze_path = 'generative_agents/frontend/static/assets/qingshi_town/maze.json'
    
    try:
        with open(maze_path, 'r', encoding='utf-8') as f:
            maze = json.load(f)
        
        print(f"✓ World: {maze['world']}")
        print(f"✓ Size: {maze['size']}")
        print(f"✓ Tiles: {len(maze['tiles'])}")
        
        # 提取场景
        locations = set()
        for tile in maze['tiles']:
            if 'address' in tile and len(tile['address']) > 0:
                locations.add(tile['address'][0])
        
        print(f"✓ 场景数量: {len(locations)}")
        print("✓ 主要场景:")
        for loc in sorted(locations)[:10]:
            print(f"    - {loc}")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_3_mind_adapter():
    """测试3: 情感记忆系统"""
    print("\n" + "=" * 60)
    print("测试 3: 情感记忆系统 (memos-mind)")
    print("=" * 60)
    
    try:
        from modules.mind_adapter import AgentMindAdapter
        
        # 创建测试实例
        mind = AgentMindAdapter(
            agent_name="测试角色",
            personality={
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.5,
                "agreeableness": 0.8,
                "neuroticism": 0.3
            },
            values={
                "self_direction": 0.7,
                "stimulation": 0.5,
                "hedonism": 0.6,
                "achievement": 0.7,
                "power": 0.4,
                "security": 0.6,
                "conformity": 0.5,
                "tradition": 0.4,
                "benevolence": 0.8,
                "universalism": 0.7
            },
            cultural_traits={
                "face": 0.7,
                "renqing": 0.8,
                "collectivism": 0.6
            }
        )
        
        print("✓ AgentMindAdapter 创建成功")
        
        # 测试情绪更新
        mind.update_emotion(
            event_description="在茶馆里和老朋友聊天",
            social_context="友好的社交场合"
        )
        
        emotion = mind.get_emotion_state()
        print(f"✓ 情绪状态: Pleasure={emotion['pleasure']:.2f}, Arousal={emotion['arousal']:.2f}, Dominance={emotion['dominance']:.2f}")
        
        # 测试情绪记忆
        mind.store_emotional_memory(
            event_description="在茶馆里和老朋友聊天",
            emotion_state=emotion
        )
        
        print("✓ 情绪记忆存储成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_gods_eye():
    """测试4: 上帝之眼观察系统"""
    print("\n" + "=" * 60)
    print("测试 4: 上帝之眼观察系统")
    print("=" * 60)
    
    try:
        from modules.observers.gods_eye_system import GodsEyeSystem
        
        # 创建测试实例
        storage_dir = "/tmp/test_gods_eye"
        os.makedirs(storage_dir, exist_ok=True)
        
        gods_eye = GodsEyeSystem(storage_dir)
        
        print("✓ GodsEyeSystem 创建成功")
        
        # 测试记录心理状态
        gods_eye.log_mind_state(
            agent_name="李建国",
            emotion={
                "pleasure": 0.6,
                "arousal": 0.4,
                "dominance": 0.5
            },
            personality={
                "openness": 0.7,
                "conscientiousness": 0.8,
                "extraversion": 0.5,
                "agreeableness": 0.9,
                "neuroticism": 0.2
            }
        )
        
        print("✓ 心理状态记录成功")
        
        # 测试记录互动
        gods_eye.log_interaction(
            agent_a="李建国",
            agent_b="王淑芬",
            interaction_type="对话",
            content="讨论社区活动",
            location="青石茶馆"
        )
        
        print("✓ 互动记录成功")
        
        # 测试查询
        states = gods_eye.query_mind_states("李建国", limit=1)
        print(f"✓ 查询到 {len(states)} 条心理状态记录")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_relationship_manager():
    """测试5: 关系管理系统"""
    print("\n" + "=" * 60)
    print("测试 5: 关系管理系统")
    print("=" * 60)
    
    try:
        from modules.relationship_manager import RelationshipManager
        
        # 创建测试实例
        rm = RelationshipManager("李建国")
        
        print("✓ RelationshipManager 创建成功")
        
        # 测试更新关系
        rm.update_relationship(
            other_agent="王淑芬",
            interaction_type="友好对话",
            sentiment=0.8
        )
        
        print("✓ 关系更新成功")
        
        # 测试获取关系
        relationship = rm.get_relationship("王淑芬")
        print(f"✓ 关系强度: {relationship['strength']:.2f}, 情感: {relationship['sentiment']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "青石镇组件测试" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 运行所有测试
    results.append(("配置文件完整性", test_1_config_files()))
    results.append(("地图配置", test_2_maze_config()))
    results.append(("情感记忆系统", test_3_mind_adapter()))
    results.append(("上帝之眼系统", test_4_gods_eye()))
    results.append(("关系管理系统", test_5_relationship_manager()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！系统组件正常工作。")
    else:
        print("⚠ 部分测试失败，请检查上述错误信息。")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
