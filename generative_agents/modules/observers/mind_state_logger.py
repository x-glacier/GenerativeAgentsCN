"""
心智状态记录器（Mind State Logger）

记录每个智能体在每个时刻的心智状态，包括：
- 情绪状态（PAD 三维）
- 性格特征
- 当前活动
- 记忆统计
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional


class MindStateLogger:
    """记录智能体的心智状态"""
    
    def __init__(self, db_connection=None):
        """
        初始化心智状态记录器
        
        Args:
            db_connection: 数据库连接（可选）
        """
        self.db = db_connection
        self.memory_buffer = []  # 内存缓冲区，用于批量写入
        self.buffer_size = 100
    
    def log_state(
        self,
        agent_name: str,
        emotion: Dict[str, float],
        personality: Dict[str, float],
        current_activity: str = "",
        location: str = "",
        memory_stats: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        记录智能体的当前心智状态
        
        Args:
            agent_name: 智能体名字
            emotion: 情绪状态 {pleasure, arousal, dominance}
            personality: 性格特征 {openness, conscientiousness, ...}
            current_activity: 当前活动描述
            location: 当前位置
            memory_stats: 记忆统计信息
            timestamp: 时间戳（可选，默认为当前时间）
        
        Returns:
            记录的状态快照
        """
        if timestamp is None:
            timestamp = time.time()
        
        state_snapshot = {
            "agent": agent_name,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            
            # 情绪状态
            "emotion": {
                "pleasure": emotion.get("pleasure", 0.0),
                "arousal": emotion.get("arousal", 0.0),
                "dominance": emotion.get("dominance", 0.5)
            },
            
            # 性格特征（相对稳定）
            "personality": personality,
            
            # 当前状态
            "current_activity": current_activity,
            "location": location,
            
            # 记忆统计
            "memory_stats": memory_stats or {}
        }
        
        # 添加到缓冲区
        self.memory_buffer.append(state_snapshot)
        
        # 如果缓冲区满了，写入数据库
        if len(self.memory_buffer) >= self.buffer_size:
            self._flush_buffer()
        
        return state_snapshot
    
    def _flush_buffer(self):
        """将缓冲区的数据写入数据库"""
        if not self.db or not self.memory_buffer:
            return
        
        try:
            # 批量插入数据库
            for state in self.memory_buffer:
                self.db.insert_mind_state(state)
            self.memory_buffer.clear()
        except Exception as e:
            print(f"Warning: Failed to flush mind state buffer: {e}")
    
    def get_recent_states(self, agent_name: str, limit: int = 10):
        """
        获取某个智能体最近的心智状态
        
        Args:
            agent_name: 智能体名字
            limit: 返回数量
        
        Returns:
            状态列表
        """
        # 先从缓冲区查找
        recent_states = [
            s for s in reversed(self.memory_buffer)
            if s["agent"] == agent_name
        ][:limit]
        
        # 如果不够，再从数据库查找
        if len(recent_states) < limit and self.db:
            db_states = self.db.query_mind_states(
                agent_name=agent_name,
                limit=limit - len(recent_states)
            )
            recent_states.extend(db_states)
        
        return recent_states
    
    def get_emotion_timeline(
        self,
        agent_name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """
        获取某个智能体的情绪时间线
        
        Args:
            agent_name: 智能体名字
            start_time: 开始时间戳
            end_time: 结束时间戳
        
        Returns:
            时间线数据 [(timestamp, emotion), ...]
        """
        if not self.db:
            # 从缓冲区获取
            states = [
                s for s in self.memory_buffer
                if s["agent"] == agent_name
            ]
        else:
            # 从数据库获取
            states = self.db.query_mind_states(
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time
            )
        
        # 提取情绪时间线
        timeline = [
            (s["timestamp"], s["emotion"])
            for s in states
        ]
        
        return sorted(timeline, key=lambda x: x[0])
    
    def analyze_emotion_change(
        self,
        agent_name: str,
        time_window: float = 3600  # 1小时
    ):
        """
        分析智能体的情绪变化
        
        Args:
            agent_name: 智能体名字
            time_window: 时间窗口（秒）
        
        Returns:
            情绪变化分析
        """
        now = time.time()
        timeline = self.get_emotion_timeline(
            agent_name,
            start_time=now - time_window,
            end_time=now
        )
        
        if len(timeline) < 2:
            return {
                "change": 0.0,
                "trend": "stable",
                "volatility": 0.0
            }
        
        # 计算情绪变化
        first_emotion = timeline[0][1]
        last_emotion = timeline[-1][1]
        
        pleasure_change = last_emotion["pleasure"] - first_emotion["pleasure"]
        
        # 计算波动性
        pleasures = [e["pleasure"] for _, e in timeline]
        avg_pleasure = sum(pleasures) / len(pleasures)
        volatility = sum(abs(p - avg_pleasure) for p in pleasures) / len(pleasures)
        
        # 判断趋势
        if pleasure_change > 0.1:
            trend = "improving"
        elif pleasure_change < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "change": pleasure_change,
            "trend": trend,
            "volatility": volatility,
            "timeline_length": len(timeline)
        }
    
    def close(self):
        """关闭记录器，刷新缓冲区"""
        self._flush_buffer()
