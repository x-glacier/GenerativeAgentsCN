"""
关系状态记录器（Relationship Logger）

记录智能体之间的关系状态，包括：
- 情感关系（好感、信任、亲密）
- 社会关系和血缘关系
- 印象和评价
- 交互历史统计
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class RelationshipLogger:
    """记录智能体之间的关系状态"""
    
    def __init__(self, db_connection=None):
        """
        初始化关系状态记录器
        
        Args:
            db_connection: 数据库连接（可选）
        """
        self.db = db_connection
        self.memory_buffer = []
        self.buffer_size = 50
    
    def log_relationship(
        self,
        agent_a: str,
        agent_b: str,
        a_to_b: Dict[str, Any],
        b_to_a: Optional[Dict[str, Any]] = None,
        kinship: str = "none",
        social: str = "stranger",
        interaction_stats: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        记录两个智能体之间的关系状态
        
        Args:
            agent_a: 智能体 A 的名字
            agent_b: 智能体 B 的名字
            a_to_b: A 对 B 的关系 {affection, trust, intimacy, impression}
            b_to_a: B 对 A 的关系（可选，如果不提供则假设对称）
            kinship: 血缘关系类型
            social: 社会关系类型
            interaction_stats: 交互统计
            timestamp: 时间戳
        
        Returns:
            关系快照
        """
        if timestamp is None:
            timestamp = time.time()
        
        if b_to_a is None:
            b_to_a = a_to_b.copy()
        
        relationship_snapshot = {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            
            # A 对 B 的关系
            "a_to_b": {
                "affection": a_to_b.get("affection", 50),
                "trust": a_to_b.get("trust", 20),
                "intimacy": a_to_b.get("intimacy", 0),
                "impression": a_to_b.get("impression", 50)
            },
            
            # B 对 A 的关系
            "b_to_a": {
                "affection": b_to_a.get("affection", 50),
                "trust": b_to_a.get("trust", 20),
                "intimacy": b_to_a.get("intimacy", 0),
                "impression": b_to_a.get("impression", 50)
            },
            
            # 关系类型
            "kinship": kinship,
            "social": social,
            
            # 交互统计
            "interaction_stats": interaction_stats or {
                "interaction_count": 0,
                "last_interaction": None,
                "recent_conflicts": 0,
                "recent_favors": 0
            }
        }
        
        # 添加到缓冲区
        self.memory_buffer.append(relationship_snapshot)
        
        # 如果缓冲区满了，写入数据库
        if len(self.memory_buffer) >= self.buffer_size:
            self._flush_buffer()
        
        return relationship_snapshot
    
    def _flush_buffer(self):
        """将缓冲区的数据写入数据库"""
        if not self.db or not self.memory_buffer:
            return
        
        try:
            for rel in self.memory_buffer:
                self.db.insert_relationship(rel)
            self.memory_buffer.clear()
        except Exception as e:
            print(f"Warning: Failed to flush relationship buffer: {e}")
    
    def get_relationship_timeline(
        self,
        agent_a: str,
        agent_b: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """
        获取两个智能体的关系演化时间线
        
        Args:
            agent_a: 智能体 A
            agent_b: 智能体 B
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            时间线数据
        """
        if not self.db:
            # 从缓冲区获取
            relationships = [
                r for r in self.memory_buffer
                if (r["agent_a"] == agent_a and r["agent_b"] == agent_b) or
                   (r["agent_a"] == agent_b and r["agent_b"] == agent_a)
            ]
        else:
            # 从数据库获取
            relationships = self.db.query_relationships(
                agent_a=agent_a,
                agent_b=agent_b,
                start_time=start_time,
                end_time=end_time
            )
        
        return sorted(relationships, key=lambda x: x["timestamp"])
    
    def analyze_relationship_evolution(
        self,
        agent_a: str,
        agent_b: str
    ):
        """
        分析两个智能体的关系演化
        
        Args:
            agent_a: 智能体 A
            agent_b: 智能体 B
        
        Returns:
            演化分析结果
        """
        timeline = self.get_relationship_timeline(agent_a, agent_b)
        
        if len(timeline) < 2:
            return {
                "status": "insufficient_data",
                "data_points": len(timeline)
            }
        
        initial = timeline[0]
        current = timeline[-1]
        
        # 计算变化（以 A 对 B 的关系为例）
        affection_change = current["a_to_b"]["affection"] - initial["a_to_b"]["affection"]
        trust_change = current["a_to_b"]["trust"] - initial["a_to_b"]["trust"]
        intimacy_change = current["a_to_b"]["intimacy"] - initial["a_to_b"]["intimacy"]
        
        # 判断趋势
        total_change = affection_change + trust_change + intimacy_change
        if total_change > 10:
            trend = "improving"
        elif total_change < -10:
            trend = "declining"
        else:
            trend = "stable"
        
        # 找出关键事件（变化显著的时刻）
        key_events = []
        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]
            
            change = (
                abs(curr["a_to_b"]["affection"] - prev["a_to_b"]["affection"]) +
                abs(curr["a_to_b"]["trust"] - prev["a_to_b"]["trust"]) +
                abs(curr["a_to_b"]["intimacy"] - prev["a_to_b"]["intimacy"])
            )
            
            if change > 5:  # 显著变化阈值
                key_events.append({
                    "time": curr["datetime"],
                    "change": {
                        "affection": curr["a_to_b"]["affection"] - prev["a_to_b"]["affection"],
                        "trust": curr["a_to_b"]["trust"] - prev["a_to_b"]["trust"],
                        "intimacy": curr["a_to_b"]["intimacy"] - prev["a_to_b"]["intimacy"]
                    }
                })
        
        return {
            "initial_state": initial,
            "current_state": current,
            "change": {
                "affection": affection_change,
                "trust": trust_change,
                "intimacy": intimacy_change
            },
            "trend": trend,
            "key_events": key_events[:5],  # 最多返回 5 个关键事件
            "timeline_length": len(timeline)
        }
    
    def get_relationship_network(self, agents: list, timestamp: Optional[float] = None):
        """
        获取一组智能体的关系网络快照
        
        Args:
            agents: 智能体名字列表
            timestamp: 时间戳（可选，默认为最新）
        
        Returns:
            关系网络数据
        """
        network = {
            "nodes": [],
            "edges": []
        }
        
        # 添加节点
        for agent in agents:
            network["nodes"].append({
                "id": agent,
                "label": agent
            })
        
        # 添加边（关系）
        for i, agent_a in enumerate(agents):
            for agent_b in agents[i+1:]:
                # 获取最新的关系状态
                timeline = self.get_relationship_timeline(agent_a, agent_b)
                if timeline:
                    latest = timeline[-1]
                    
                    # A -> B 的边
                    network["edges"].append({
                        "source": agent_a,
                        "target": agent_b,
                        "affection": latest["a_to_b"]["affection"],
                        "trust": latest["a_to_b"]["trust"],
                        "intimacy": latest["a_to_b"]["intimacy"]
                    })
                    
                    # B -> A 的边（如果不对称）
                    if latest["a_to_b"] != latest["b_to_a"]:
                        network["edges"].append({
                            "source": agent_b,
                            "target": agent_a,
                            "affection": latest["b_to_a"]["affection"],
                            "trust": latest["b_to_a"]["trust"],
                            "intimacy": latest["b_to_a"]["intimacy"]
                        })
        
        return network
    
    def close(self):
        """关闭记录器，刷新缓冲区"""
        self._flush_buffer()
