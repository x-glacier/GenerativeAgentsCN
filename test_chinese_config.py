#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
测试中国化配置的完整性和兼容性
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def test_maze_config():
    """测试 maze.json 配置"""
    print("=" * 60)
    print("测试 maze.json 配置")
    print("=" * 60)
    
    maze_path = 'generative_agents/frontend/static/assets/qingshi_town/maze.json'
    
    try:
        with open(maze_path, 'r', encoding='utf-8') as f:
            maze = json.load(f)
        
        # 检查基本字段
        assert 'world' in maze, "缺少 world 字段"
        assert maze['world'] == '青石镇', f"world 名称错误: {maze['world']}"
        assert 'size' in maze, "缺少 size 字段"
        assert maze['size'] == [100, 140], f"地图尺寸错误: {maze['size']}"
        assert 'tiles' in maze, "缺少 tiles 字段"
        
        print(f"✓ World: {maze['world']}")
        print(f"✓ Size: {maze['size']}")
        print(f"✓ Tiles: {len(maze['tiles'])}")
        
        # 提取所有场景名称
        locations = set()
        for tile in maze['tiles']:
            if 'address' in tile and len(tile['address']) > 0:
                locations.add(tile['address'][0])
        
        print(f"✓ 场景数量: {len(locations)}")
        print(f"✓ 场景列表:")
        for loc in sorted(locations):
            print(f"    - {loc}")
        
        # 检查是否还有英文场景名称
        english_locations = [loc for loc in locations if any(c.isascii() and c.isalpha() for c in loc)]
        if english_locations:
            print(f"\n⚠ 警告: 发现英文场景名称:")
            for loc in english_locations:
                print(f"    - {loc}")
        else:
            print(f"\n✓ 所有场景名称已中文化")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_agent_configs():
    """测试角色配置文件"""
    print("\n" + "=" * 60)
    print("测试角色配置文件")
    print("=" * 60)
    
    agents_dir = Path('generative_agents/frontend/static/assets/qingshi_town/agents')
    
    if not agents_dir.exists():
        print(f"✗ 角色目录不存在: {agents_dir}")
        return False
    
    agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir()]
    print(f"✓ 找到 {len(agent_dirs)} 个角色目录")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for agent_dir in sorted(agent_dirs):
        agent_name = agent_dir.name
        agent_config_path = agent_dir / 'agent.json'
        
        if not agent_config_path.exists():
            print(f"  ✗ {agent_name}: 缺少 agent.json")
            error_count += 1
            errors.append(f"{agent_name}: 缺少 agent.json")
            continue
        
        try:
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必需字段
            required_fields = ['name', 'coord', 'currently', 'scratch', 'spatial']
            missing_fields = [f for f in required_fields if f not in config]
            
            if missing_fields:
                print(f"  ✗ {agent_name}: 缺少字段 {missing_fields}")
                error_count += 1
                errors.append(f"{agent_name}: 缺少字段 {missing_fields}")
                continue
            
            # 检查名称一致性
            if config['name'] != agent_name:
                print(f"  ⚠ {agent_name}: 名称不一致 (配置中为 {config['name']})")
            
            # 检查 spatial 结构
            if 'address' not in config['spatial'] or 'living_area' not in config['spatial']['address']:
                print(f"  ✗ {agent_name}: spatial.address.living_area 缺失")
                error_count += 1
                errors.append(f"{agent_name}: spatial.address.living_area 缺失")
                continue
            
            # 检查 world 名称
            living_area = config['spatial']['address']['living_area']
            if len(living_area) > 0 and living_area[0] != '青石镇':
                print(f"  ⚠ {agent_name}: world 名称未更新 ({living_area[0]})")
            
            # 检查是否有英文地址
            has_english = False
            for part in living_area:
                if any(c.isascii() and c.isalpha() for c in part):
                    has_english = True
                    break
            
            if has_english:
                print(f"  ⚠ {agent_name}: 地址包含英文 ({living_area})")
            
            print(f"  ✓ {agent_name}: 配置正确")
            success_count += 1
            
        except json.JSONDecodeError as e:
            print(f"  ✗ {agent_name}: JSON 解析错误 - {e}")
            error_count += 1
            errors.append(f"{agent_name}: JSON 解析错误")
        except Exception as e:
            print(f"  ✗ {agent_name}: 未知错误 - {e}")
            error_count += 1
            errors.append(f"{agent_name}: 未知错误 - {e}")
    
    print(f"\n总计: {success_count} 成功, {error_count} 失败")
    
    if errors:
        print("\n错误列表:")
        for error in errors:
            print(f"  - {error}")
    
    return error_count == 0

def test_agent_personality():
    """测试角色的情感和人格配置"""
    print("\n" + "=" * 60)
    print("测试角色情感和人格配置")
    print("=" * 60)
    
    agents_dir = Path('generative_agents/frontend/static/assets/qingshi_town/agents')
    
    personality_stats = {
        'has_personality': 0,
        'has_values': 0,
        'has_cultural_traits': 0,
        'total': 0
    }
    
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        
        agent_config_path = agent_dir / 'agent.json'
        if not agent_config_path.exists():
            continue
        
        try:
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            personality_stats['total'] += 1
            
            # 检查人格特质
            if 'personality' in config:
                personality_stats['has_personality'] += 1
            
            # 检查价值观
            if 'values' in config:
                personality_stats['has_values'] += 1
            
            # 检查文化特质
            if 'cultural_traits' in config:
                personality_stats['has_cultural_traits'] += 1
            
        except Exception as e:
            print(f"  ✗ {agent_dir.name}: 读取失败 - {e}")
    
    print(f"总角色数: {personality_stats['total']}")
    print(f"包含人格特质: {personality_stats['has_personality']} ({personality_stats['has_personality']/personality_stats['total']*100:.1f}%)")
    print(f"包含价值观: {personality_stats['has_values']} ({personality_stats['has_values']/personality_stats['total']*100:.1f}%)")
    print(f"包含文化特质: {personality_stats['has_cultural_traits']} ({personality_stats['has_cultural_traits']/personality_stats['total']*100:.1f}%)")
    
    return True

def test_coordinate_coverage():
    """测试坐标覆盖情况"""
    print("\n" + "=" * 60)
    print("测试角色坐标分布")
    print("=" * 60)
    
    agents_dir = Path('generative_agents/frontend/static/assets/qingshi_town/agents')
    
    coordinates = []
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        
        agent_config_path = agent_dir / 'agent.json'
        if not agent_config_path.exists():
            continue
        
        try:
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'coord' in config:
                coord = config['coord']
                coordinates.append((config['name'], coord))
        except Exception as e:
            pass
    
    print(f"✓ 共 {len(coordinates)} 个角色有坐标")
    
    # 检查坐标范围
    x_coords = [c[1][0] for c in coordinates]
    y_coords = [c[1][1] for c in coordinates]
    
    print(f"✓ X 坐标范围: {min(x_coords)} - {max(x_coords)}")
    print(f"✓ Y 坐标范围: {min(y_coords)} - {max(y_coords)}")
    
    # 检查重复坐标
    coord_map = defaultdict(list)
    for name, coord in coordinates:
        coord_map[tuple(coord)].append(name)
    
    duplicates = {k: v for k, v in coord_map.items() if len(v) > 1}
    if duplicates:
        print(f"\n⚠ 发现 {len(duplicates)} 个重复坐标:")
        for coord, names in duplicates.items():
            print(f"  {coord}: {', '.join(names)}")
    else:
        print(f"\n✓ 所有角色坐标唯一")
    
    return True

def test_sprite_config():
    """测试 sprite.json 配置"""
    print("\n" + "=" * 60)
    print("测试 sprite.json 配置")
    print("=" * 60)
    
    sprite_path = 'generative_agents/frontend/static/assets/qingshi_town/agents/sprite.json'
    
    if not os.path.exists(sprite_path):
        print(f"⚠ sprite.json 不存在: {sprite_path}")
        return True  # 不是必需的
    
    try:
        with open(sprite_path, 'r', encoding='utf-8') as f:
            sprites = json.load(f)
        
        print(f"✓ sprite.json 存在")
        print(f"✓ 包含 {len(sprites)} 个角色精灵配置")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "青石镇配置验证测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # 运行所有测试
    results.append(("maze.json 配置", test_maze_config()))
    results.append(("角色配置文件", test_agent_configs()))
    results.append(("角色情感人格", test_agent_personality()))
    results.append(("角色坐标分布", test_coordinate_coverage()))
    results.append(("sprite.json 配置", test_sprite_config()))
    
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
        print("✓ 所有测试通过！配置完整且兼容。")
    else:
        print("⚠ 部分测试失败，请检查上述错误信息。")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
