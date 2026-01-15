#!/usr/bin/env python3
"""分析青石镇模拟结果"""

import json
import sqlite3
from pathlib import Path
from collections import defaultdict, Counter
import sys

def analyze_simulation(checkpoint_dir):
    """分析模拟结果"""
    checkpoint_path = Path(checkpoint_dir)
    
    if not checkpoint_path.exists():
        print(f"错误：目录不存在 {checkpoint_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"青石镇模拟结果分析")
    print(f"{'='*60}\n")
    
    # 1. 分析模拟步骤
    simulate_files = sorted(checkpoint_path.glob("simulate-*.json"))
    print(f"📊 模拟步骤数: {len(simulate_files)}")
    
    if simulate_files:
        # 读取第一步和最后一步
        with open(simulate_files[0], 'r', encoding='utf-8') as f:
            first_step = json.load(f)
        with open(simulate_files[-1], 'r', encoding='utf-8') as f:
            last_step = json.load(f)
        
        print(f"   起始时间: {first_step.get('time', 'N/A')}")
        print(f"   结束时间: {last_step.get('time', 'N/A')}")
        print(f"   参与角色: {len(first_step.get('agents', {}))}")
    
    # 2. 分析对话记录
    conversation_file = checkpoint_path / "conversation.json"
    if conversation_file.exists():
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        print(f"\n💬 对话统计:")
        print(f"   对话组数: {len(conversations)}")
        
        # 统计每个角色的对话次数
        agent_chat_count = Counter()
        total_utterances = 0
        for conv_key, conv_data in conversations.items():
            for utterance in conv_data:
                agent_chat_count[utterance[0]] += 1
                total_utterances += 1
        
        print(f"   总对话轮次: {total_utterances}")
        print(f"\n   最活跃的对话者:")
        for agent, count in agent_chat_count.most_common(5):
            print(f"      {agent}: {count} 次")
    
    # 3. 分析上帝之眼数据库
    gods_eye_db = checkpoint_path / "storage" / "evolution.db"
    if gods_eye_db.exists():
        conn = sqlite3.connect(str(gods_eye_db))
        cursor = conn.cursor()
        
        print(f"\n🔍 上帝之眼数据:")
        
        # 统计心智状态记录
        cursor.execute("SELECT COUNT(*) FROM mind_states")
        mind_count = cursor.fetchone()[0]
        print(f"   心智状态记录: {mind_count}")
        
        # 统计互动记录
        cursor.execute("SELECT COUNT(*) FROM interactions")
        interaction_count = cursor.fetchone()[0]
        print(f"   互动记录: {interaction_count}")
        
        # 统计关系变化
        cursor.execute("SELECT COUNT(*) FROM relationship_changes")
        rel_change_count = cursor.fetchone()[0]
        print(f"   关系变化记录: {rel_change_count}")
        
        # 分析情绪变化
        cursor.execute("""
            SELECT agent_name, 
                   AVG(pleasure) as avg_pleasure,
                   AVG(arousal) as avg_arousal,
                   AVG(dominance) as avg_dominance
            FROM mind_states
            GROUP BY agent_name
            ORDER BY avg_pleasure DESC
            LIMIT 5
        """)
        
        print(f"\n   情绪最积极的角色:")
        for row in cursor.fetchall():
            agent, pleasure, arousal, dominance = row
            print(f"      {agent}: 愉悦度={pleasure:.2f}, 唤醒度={arousal:.2f}, 支配度={dominance:.2f}")
        
        # 分析最频繁的互动
        cursor.execute("""
            SELECT agent1_name, agent2_name, COUNT(*) as count
            FROM interactions
            GROUP BY agent1_name, agent2_name
            ORDER BY count DESC
            LIMIT 5
        """)
        
        print(f"\n   最频繁的互动:")
        for row in cursor.fetchall():
            agent1, agent2, count = row
            print(f"      {agent1} ↔ {agent2}: {count} 次")
        
        conn.close()
    
    # 4. 分析个体记忆数据库
    mind_db_dir = checkpoint_path / "storage" / "mind_db"
    if mind_db_dir.exists():
        db_files = list(mind_db_dir.glob("*.db"))
        print(f"\n🧠 个体记忆数据库:")
        print(f"   角色数量: {len(db_files)}")
        
        # 统计每个角色的记忆数量
        memory_counts = {}
        for db_file in db_files:
            agent_name = db_file.stem
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            memory_counts[agent_name] = count
            conn.close()
        
        # 显示记忆最多的角色
        sorted_memories = sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)
        print(f"\n   记忆最丰富的角色:")
        for agent, count in sorted_memories[:5]:
            print(f"      {agent}: {count} 条记忆")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        checkpoint_dir = sys.argv[1]
    else:
        checkpoint_dir = "generative_agents/results/checkpoints/qingshi-full-50"
    
    analyze_simulation(checkpoint_dir)
