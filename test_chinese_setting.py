#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试青石镇中国化配置
"""

import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generative_agents'))

def test_load_agents():
    """测试加载所有中国化角色配置"""
    print("=" * 60)
    print("测试 1: 加载中国化角色配置")
    print("=" * 60)
    
    agents_dir = "generative_agents/frontend/static/assets/qingshi_town/agents"
    agent_names = ["王淑芬", "李建国", "张伟", "陈静", "刘洋"]
    
    for name in agent_names:
        agent_path = os.path.join(agents_dir, name, "agent.json")
        try:
            with open(agent_path, 'r', encoding='utf-8') as f:
                agent_config = json.load(f)
            
            print(f"\n✓ 成功加载: {name}")
            print(f"  年龄: {agent_config['age']}岁")
            print(f"  身份: {agent_config['identity']}")
            print(f"  性格特征:")
            print(f"    - 开放性: {agent_config['personality']['openness']}")
            print(f"    - 外向性: {agent_config['personality']['extraversion']}")
            print(f"  口头禅: {agent_config['catchphrase']}")
            print(f"  文化特质:")
            print(f"    - 面子意识: {agent_config['cultural_traits']['face_consciousness']}")
            print(f"    - 人情观念: {agent_config['cultural_traits']['renqing_orientation']}")
            
        except Exception as e:
            print(f"\n✗ 加载失败: {name}")
            print(f"  错误: {e}")
            return False
    
    return True

def test_load_town_config():
    """测试加载青石镇配置"""
    print("\n" + "=" * 60)
    print("测试 2: 加载青石镇场景配置")
    print("=" * 60)
    
    town_config_path = "generative_agents/frontend/static/assets/qingshi_town/town_config.json"
    
    try:
        with open(town_config_path, 'r', encoding='utf-8') as f:
            town_config = json.load(f)
        
        print(f"\n✓ 成功加载: {town_config['town_name']}")
        print(f"  描述: {town_config['description']}")
        print(f"\n  场景列表:")
        for location in town_config['locations']:
            print(f"    - {location['name']}: {location['description'][:30]}...")
        
        print(f"\n  文化活动:")
        for event in town_config['cultural_events']:
            print(f"    - {event['name']}: {event['time']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 加载失败")
        print(f"  错误: {e}")
        return False

def test_relationships():
    """测试角色之间的关系网络"""
    print("\n" + "=" * 60)
    print("测试 3: 检查角色关系网络")
    print("=" * 60)
    
    agents_dir = "generative_agents/frontend/static/assets/qingshi_town/agents"
    agent_names = ["王淑芬", "李建国", "张伟", "陈静", "刘洋"]
    
    relationships = {}
    
    for name in agent_names:
        agent_path = os.path.join(agents_dir, name, "agent.json")
        with open(agent_path, 'r', encoding='utf-8') as f:
            agent_config = json.load(f)
        relationships[name] = agent_config.get('initial_relationships', {})
    
    print(f"\n关系网络概览:")
    for agent_name, rels in relationships.items():
        print(f"\n{agent_name} 的关系:")
        for other_name, rel_data in rels.items():
            print(f"  → {other_name}:")
            print(f"      社会关系: {rel_data['social']}")
            print(f"      好感度: {rel_data['affection']}, 信任度: {rel_data['trust']}, 亲密度: {rel_data['intimacy']}")
            print(f"      备注: {rel_data['note']}")
    
    return True

def test_prompts():
    """测试中国化提示词模板"""
    print("\n" + "=" * 60)
    print("测试 4: 检查中国化提示词模板")
    print("=" * 60)
    
    prompt_files = [
        "generative_agents/data/prompts/generate_chat_chinese.txt",
        "generative_agents/data/prompts/base_desc_chinese.txt"
    ]
    
    for prompt_file in prompt_files:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n✓ 成功加载: {os.path.basename(prompt_file)}")
            
            # 检查是否包含中国文化关键词
            keywords = ["面子", "人情", "含蓄", "长幼有序", "集体主义"]
            found_keywords = [kw for kw in keywords if kw in content]
            
            if found_keywords:
                print(f"  包含中国文化关键词: {', '.join(found_keywords)}")
            else:
                print(f"  ⚠️  未找到中国文化关键词")
            
        except Exception as e:
            print(f"\n✗ 加载失败: {prompt_file}")
            print(f"  错误: {e}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("青石镇中国化配置测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("角色配置加载", test_load_agents()))
    results.append(("场景配置加载", test_load_town_config()))
    results.append(("关系网络检查", test_relationships()))
    results.append(("提示词模板检查", test_prompts()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！青石镇中国化配置已就绪。")
    else:
        print("部分测试失败，请检查配置文件。")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
