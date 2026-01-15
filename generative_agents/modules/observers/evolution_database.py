"""
心智演化数据库（Evolution Database）

使用 SQLite 存储所有时间序列数据：
- 心智状态
- 关系状态
- 交互事件
"""

import sqlite3
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path


class EvolutionDatabase:
    """心智演化数据库"""
    
    def __init__(self, db_path: str = "storage/evolution.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
        
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 心智状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mind_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                emotion_pleasure REAL,
                emotion_arousal REAL,
                emotion_dominance REAL,
                personality TEXT,
                current_activity TEXT,
                location TEXT,
                memory_stats TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON mind_states (agent, timestamp)")
        
        # 关系状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_a TEXT NOT NULL,
                agent_b TEXT NOT NULL,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                a_to_b_affection REAL,
                a_to_b_trust REAL,
                a_to_b_intimacy REAL,
                a_to_b_impression REAL,
                b_to_a_affection REAL,
                b_to_a_trust REAL,
                b_to_a_intimacy REAL,
                b_to_a_impression REAL,
                kinship TEXT,
                social TEXT,
                interaction_stats TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_timestamp ON relationships (agent_a, agent_b, timestamp)")
        
        # 交互事件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                type TEXT,
                speaker TEXT,
                listener TEXT,
                content TEXT,
                location TEXT,
                speaker_state TEXT,
                listener_state TEXT,
                relationship_change TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_speaker ON interactions (speaker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listener ON interactions (listener)")
        
        self.conn.commit()
    
    def insert_mind_state(self, state: Dict[str, Any]):
        """插入心智状态记录"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO mind_states (
                agent, timestamp, datetime,
                emotion_pleasure, emotion_arousal, emotion_dominance,
                personality, current_activity, location, memory_stats
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state["agent"],
            state["timestamp"],
            state["datetime"],
            state["emotion"]["pleasure"],
            state["emotion"]["arousal"],
            state["emotion"]["dominance"],
            json.dumps(state["personality"], ensure_ascii=False),
            state["current_activity"],
            state["location"],
            json.dumps(state["memory_stats"], ensure_ascii=False)
        ))
        
        self.conn.commit()
    
    def insert_relationship(self, rel: Dict[str, Any]):
        """插入关系状态记录"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO relationships (
                agent_a, agent_b, timestamp, datetime,
                a_to_b_affection, a_to_b_trust, a_to_b_intimacy, a_to_b_impression,
                b_to_a_affection, b_to_a_trust, b_to_a_intimacy, b_to_a_impression,
                kinship, social, interaction_stats
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rel["agent_a"],
            rel["agent_b"],
            rel["timestamp"],
            rel["datetime"],
            rel["a_to_b"]["affection"],
            rel["a_to_b"]["trust"],
            rel["a_to_b"]["intimacy"],
            rel["a_to_b"]["impression"],
            rel["b_to_a"]["affection"],
            rel["b_to_a"]["trust"],
            rel["b_to_a"]["intimacy"],
            rel["b_to_a"]["impression"],
            rel["kinship"],
            rel["social"],
            json.dumps(rel["interaction_stats"], ensure_ascii=False)
        ))
        
        self.conn.commit()
    
    def insert_interaction(self, interaction: Dict[str, Any]):
        """插入交互事件记录"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (
                timestamp, datetime, type, speaker, listener,
                content, location, speaker_state, listener_state, relationship_change
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction["timestamp"],
            interaction["datetime"],
            interaction["type"],
            interaction["speaker"],
            interaction["listener"],
            interaction["content"],
            interaction["location"],
            json.dumps(interaction["speaker_state"], ensure_ascii=False),
            json.dumps(interaction["listener_state"], ensure_ascii=False),
            json.dumps(interaction["relationship_change"], ensure_ascii=False)
        ))
        
        self.conn.commit()
    
    def query_mind_states(
        self,
        agent_name: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查询心智状态"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM mind_states WHERE 1=1"
        params = []
        
        if agent_name:
            query += " AND agent = ?"
            params.append(agent_name)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "agent": row["agent"],
                "timestamp": row["timestamp"],
                "datetime": row["datetime"],
                "emotion": {
                    "pleasure": row["emotion_pleasure"],
                    "arousal": row["emotion_arousal"],
                    "dominance": row["emotion_dominance"]
                },
                "personality": json.loads(row["personality"]) if row["personality"] else {},
                "current_activity": row["current_activity"],
                "location": row["location"],
                "memory_stats": json.loads(row["memory_stats"]) if row["memory_stats"] else {}
            })
        
        return results
    
    def query_relationships(
        self,
        agent_a: Optional[str] = None,
        agent_b: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查询关系状态"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM relationships WHERE 1=1"
        params = []
        
        if agent_a and agent_b:
            query += " AND ((agent_a = ? AND agent_b = ?) OR (agent_a = ? AND agent_b = ?))"
            params.extend([agent_a, agent_b, agent_b, agent_a])
        elif agent_a:
            query += " AND (agent_a = ? OR agent_b = ?)"
            params.extend([agent_a, agent_a])
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "agent_a": row["agent_a"],
                "agent_b": row["agent_b"],
                "timestamp": row["timestamp"],
                "datetime": row["datetime"],
                "a_to_b": {
                    "affection": row["a_to_b_affection"],
                    "trust": row["a_to_b_trust"],
                    "intimacy": row["a_to_b_intimacy"],
                    "impression": row["a_to_b_impression"]
                },
                "b_to_a": {
                    "affection": row["b_to_a_affection"],
                    "trust": row["b_to_a_trust"],
                    "intimacy": row["b_to_a_intimacy"],
                    "impression": row["b_to_a_impression"]
                },
                "kinship": row["kinship"],
                "social": row["social"],
                "interaction_stats": json.loads(row["interaction_stats"]) if row["interaction_stats"] else {}
            })
        
        return results
    
    def query_interactions(
        self,
        agent: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        interaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查询交互事件"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM interactions WHERE 1=1"
        params = []
        
        if agent:
            query += " AND (speaker = ? OR listener = ?)"
            params.extend([agent, agent])
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        if interaction_type:
            query += " AND type = ?"
            params.append(interaction_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row["timestamp"],
                "datetime": row["datetime"],
                "type": row["type"],
                "speaker": row["speaker"],
                "listener": row["listener"],
                "content": row["content"],
                "location": row["location"],
                "speaker_state": json.loads(row["speaker_state"]) if row["speaker_state"] else {},
                "listener_state": json.loads(row["listener_state"]) if row["listener_state"] else {},
                "relationship_change": json.loads(row["relationship_change"]) if row["relationship_change"] else {}
            })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        cursor = self.conn.cursor()
        
        # 统计各表的记录数
        cursor.execute("SELECT COUNT(*) FROM mind_states")
        mind_states_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        relationships_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM interactions")
        interactions_count = cursor.fetchone()[0]
        
        # 统计智能体数量
        cursor.execute("SELECT COUNT(DISTINCT agent) FROM mind_states")
        agents_count = cursor.fetchone()[0]
        
        # 统计时间范围
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM interactions")
        time_range = cursor.fetchone()
        
        return {
            "mind_states_count": mind_states_count,
            "relationships_count": relationships_count,
            "interactions_count": interactions_count,
            "agents_count": agents_count,
            "time_range": {
                "start": time_range[0],
                "end": time_range[1]
            } if time_range[0] else None
        }
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
