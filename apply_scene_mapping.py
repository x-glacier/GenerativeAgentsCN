#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
应用场景映射到 maze.json
将原始西方场景名称替换为中国化场景名称
"""

import json
import os
from pathlib import Path

def load_scene_mapping():
    """加载场景映射配置"""
    with open('scene_mapping.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_mapping_to_maze(maze_path, mapping):
    """应用映射到 maze.json"""
    print(f"正在处理 {maze_path}...")
    
    with open(maze_path, 'r', encoding='utf-8') as f:
        maze = json.load(f)
    
    # 更新 world 名称
    old_world = maze['world']
    new_world = mapping['world_name']['chinese']
    maze['world'] = new_world
    print(f"✓ 更新 world: {old_world} -> {new_world}")
    
    # 创建映射字典（原始名称 -> 中文名称）
    location_map = {}
    for chinese_name, loc_data in mapping['locations'].items():
        original_name = loc_data.get('original')
        if original_name:
            location_map[original_name] = chinese_name
    
    # 同时支持已经翻译过的中文名称到新中文名称的映射
    # 例如："霍布斯咖啡馆" -> "青石茶馆"
    current_to_new_map = {
        "霍布斯咖啡馆": "青石茶馆",
        "玫瑰酒吧": "桂花小酒馆",
        "柳树市场和药店": "柳树市集",
        "哈维奥克供应店": "张记五金店",
        "约翰逊公园": "青石公园",
        "奥克山学院": "青石中学",
        "奥克山学院宿舍": "青石中学宿舍",
        "艺术家共居空间": "文艺工作室",
        "摩尔家族的房子": "李家大院",
        "林氏家族的房子": "林家小院",
        "莫雷诺家族的房子": "陈家老宅",
        "塔玛拉和卡门的家": "王家小楼",
        "山本百合子的房子": "赵家别墅",
        "亚当的家": "刘家小院",
        "乔治的公寓": "张伟公寓",
        "亚瑟的公寓": "周杰公寓",
        "伊莎贝拉的公寓": "吴晓雨公寓",
        "卡洛斯的公寓": "马强公寓",
        "瑞恩的公寓": "孙浩公寓"
    }
    
    # 统计替换次数
    replacement_count = {}
    
    # 遍历所有 tiles 并更新地址
    for tile in maze['tiles']:
        if 'address' in tile and isinstance(tile['address'], list):
            old_address = tile['address'].copy()
            new_address = []
            
            for addr_part in tile['address']:
                # 尝试从当前中文名称映射到新中文名称
                if addr_part in current_to_new_map:
                    new_part = current_to_new_map[addr_part]
                    new_address.append(new_part)
                    
                    # 统计
                    if addr_part not in replacement_count:
                        replacement_count[addr_part] = 0
                    replacement_count[addr_part] += 1
                else:
                    # 保持不变
                    new_address.append(addr_part)
            
            tile['address'] = new_address
    
    # 显示替换统计
    print("\n场景名称替换统计:")
    for old_name, count in sorted(replacement_count.items()):
        new_name = current_to_new_map.get(old_name, old_name)
        print(f"  {old_name} -> {new_name}: {count} 次")
    
    # 保存更新后的 maze.json
    with open(maze_path, 'w', encoding='utf-8') as f:
        json.dump(maze, f, ensure_ascii=False, indent=4)
    
    print(f"\n✓ 已保存更新后的 {maze_path}")
    return maze

def update_agent_configs(agents_dir, mapping):
    """更新角色配置文件中的地址引用"""
    print(f"\n正在更新角色配置文件...")
    
    # 创建映射字典
    current_to_new_map = {
        "霍布斯咖啡馆": "青石茶馆",
        "玫瑰酒吧": "桂花小酒馆",
        "柳树市场和药店": "柳树市集",
        "哈维奥克供应店": "张记五金店",
        "约翰逊公园": "青石公园",
        "奥克山学院": "青石中学",
        "奥克山学院宿舍": "青石中学宿舍",
        "艺术家共居空间": "文艺工作室",
        "摩尔家族的房子": "李家大院",
        "林氏家族的房子": "林家小院",
        "莫雷诺家族的房子": "陈家老宅",
        "塔玛拉和卡门的家": "王家小楼",
        "山本百合子的房子": "赵家别墅",
        "亚当的家": "刘家小院",
        "乔治的公寓": "张伟公寓",
        "亚瑟的公寓": "周杰公寓",
        "伊莎贝拉的公寓": "吴晓雨公寓",
        "卡洛斯的公寓": "马强公寓",
        "瑞恩的公寓": "孙浩公寓",
        "the Ville": "青石镇"
    }
    
    updated_count = 0
    
    # 遍历所有角色目录
    for agent_dir in Path(agents_dir).iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_config_path = agent_dir / 'agent.json'
        if not agent_config_path.exists():
            continue
        
        # 读取配置
        with open(agent_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        modified = False
        
        # 更新 spatial.address.living_area
        if 'spatial' in config and 'address' in config['spatial']:
            if 'living_area' in config['spatial']['address']:
                living_area = config['spatial']['address']['living_area']
                new_living_area = []
                for part in living_area:
                    if part in current_to_new_map:
                        new_living_area.append(current_to_new_map[part])
                        modified = True
                    else:
                        new_living_area.append(part)
                config['spatial']['address']['living_area'] = new_living_area
        
        # 更新 spatial.tree
        if 'spatial' in config and 'tree' in config['spatial']:
            new_tree = {}
            for world_name, world_data in config['spatial']['tree'].items():
                # 更新 world 名称
                new_world_name = current_to_new_map.get(world_name, world_name)
                if new_world_name != world_name:
                    modified = True
                
                # 更新建筑名称
                new_world_data = {}
                for building_name, building_data in world_data.items():
                    new_building_name = current_to_new_map.get(building_name, building_name)
                    if new_building_name != building_name:
                        modified = True
                    new_world_data[new_building_name] = building_data
                
                new_tree[new_world_name] = new_world_data
            
            config['spatial']['tree'] = new_tree
        
        # 更新 currently 描述中的场景名称
        if 'currently' in config:
            currently = config['currently']
            for old_name, new_name in current_to_new_map.items():
                if old_name in currently:
                    config['currently'] = currently.replace(old_name, new_name)
                    modified = True
        
        # 如果有修改，保存文件
        if modified:
            with open(agent_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            updated_count += 1
            print(f"  ✓ 更新 {agent_dir.name}")
    
    print(f"\n✓ 共更新 {updated_count} 个角色配置文件")

def main():
    """主函数"""
    print("=" * 60)
    print("应用场景映射到青石镇")
    print("=" * 60)
    
    # 加载映射配置
    mapping = load_scene_mapping()
    print(f"\n加载场景映射配置: {len(mapping['locations'])} 个场景")
    
    # 应用到 maze.json
    maze_path = 'generative_agents/frontend/static/assets/qingshi_town/maze.json'
    apply_mapping_to_maze(maze_path, mapping)
    
    # 更新角色配置文件
    agents_dir = 'generative_agents/frontend/static/assets/qingshi_town/agents'
    update_agent_configs(agents_dir, mapping)
    
    print("\n" + "=" * 60)
    print("✓ 场景映射应用完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
