"""
交互事件记录器（Interaction Logger）

记录智能体之间的每次交互，包括：
- 对话内容
- 说话者的真实情绪状态
- 听话者感知到的情绪和反应
- 交互对关系的影响
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional


class InteractionLogger:
    """记录智能体之间的交互事件"""
    
    def __init__(self, db_connection=None):
        """
        初始化交互事件记录器
        
        Args:
            db_connection: 数据库连接（可选）
        """
        self.db = db_connection
        self.memory_buffer = []
        self.buffer_size = 100
    
    def log_interaction(
        self,
        interaction_type: str,
        speaker: str,
        listener: str,
        content: str,
        speaker_state: Dict[str, Any],
        listener_state: Dict[str, Any],
        relationship_change: Optional[Dict[str, float]] = None,
        location: str = "",
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        记录一次交互事件
        
        Args:
            interaction_type: 交互类型（dialogue, action, event等）
            speaker: 说话者/行动者
            listener: 听话者/接收者
            content: 交互内容
            speaker_state: 说话者的状态
            listener_state: 听话者的状态和反应
            relationship_change: 关系变化
            location: 交互发生的位置
            timestamp: 时间戳
        
        Returns:
            交互记录
        """
        if timestamp is None:
            timestamp = time.time()
        
        interaction_record = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "type": interaction_type,
            "location": location,
            
            # 参与者
            "speaker": speaker,
            "listener": listener,
            
            # 内容
            "content": content,
            
            # 说话者的真实状态
            "speaker_state": {
                "real_emotion": speaker_state.get("real_emotion", {}),
                "intention": speaker_state.get("intention", ""),
                "activity": speaker_state.get("activity", "")
            },
            
            # 听话者的感知和反应
            "listener_state": {
                "perceived_emotion": listener_state.get("perceived_emotion", {}),
                "perception_error": listener_state.get("perception_error", 0.0),
                "my_emotion_before": listener_state.get("my_emotion_before", {}),
                "my_emotion_after": listener_state.get("my_emotion_after", {}),
                "response": listener_state.get("response", ""),
                "perception_bias": listener_state.get("perception_bias", {})
            },
            
            # 关系变化
            "relationship_change": relationship_change or {}
        }
        
        # 添加到缓冲区
        self.memory_buffer.append(interaction_record)
        
        # 如果缓冲区满了，写入数据库
        if len(self.memory_buffer) >= self.buffer_size:
            self._flush_buffer()
        
        return interaction_record
    
    def _flush_buffer(self):
        """将缓冲区的数据写入数据库"""
        if not self.db or not self.memory_buffer:
            return
        
        try:
            for interaction in self.memory_buffer:
                self.db.insert_interaction(interaction)
            self.memory_buffer.clear()
        except Exception as e:
            print(f"Warning: Failed to flush interaction buffer: {e}")
    
    def get_interactions(
        self,
        agent: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        interaction_type: Optional[str] = None,
        limit: int = 100
    ):
        """
        查询交互记录
        
        Args:
            agent: 智能体名字（查询涉及该智能体的交互）
            start_time: 开始时间
            end_time: 结束时间
            interaction_type: 交互类型
            limit: 返回数量限制
        
        Returns:
            交互记录列表
        """
        # 从缓冲区筛选
        interactions = list(self.memory_buffer)
        
        if agent:
            interactions = [
                i for i in interactions
                if i["speaker"] == agent or i["listener"] == agent
            ]
        
        if interaction_type:
            interactions = [
                i for i in interactions
                if i["type"] == interaction_type
            ]
        
        if start_time:
            interactions = [
                i for i in interactions
                if i["timestamp"] >= start_time
            ]
        
        if end_time:
            interactions = [
                i for i in interactions
                if i["timestamp"] <= end_time
            ]
        
        # 如果数据库存在且需要更多数据
        if self.db and len(interactions) < limit:
            db_interactions = self.db.query_interactions(
                agent=agent,
                start_time=start_time,
                end_time=end_time,
                interaction_type=interaction_type,
                limit=limit - len(interactions)
            )
            interactions.extend(db_interactions)
        
        # 按时间排序并限制数量
        interactions.sort(key=lambda x: x["timestamp"], reverse=True)
        return interactions[:limit]
    
    def analyze_perception_accuracy(
        self,
        agent: str,
        time_window: Optional[float] = None
    ):
        """
        分析某个智能体的情绪感知准确度
        
        Args:
            agent: 智能体名字
            time_window: 时间窗口（秒）
        
        Returns:
            感知准确度分析
        """
        start_time = None
        if time_window:
            start_time = time.time() - time_window
        
        # 获取该智能体作为听话者的交互
        interactions = self.get_interactions(
            agent=agent,
            start_time=start_time
        )
        
        listener_interactions = [
            i for i in interactions
            if i["listener"] == agent
        ]
        
        if not listener_interactions:
            return {
                "status": "no_data",
                "interaction_count": 0
            }
        
        # 计算平均感知误差
        errors = [
            i["listener_state"]["perception_error"]
            for i in listener_interactions
            if "perception_error" in i["listener_state"]
        ]
        
        avg_error = sum(errors) / len(errors) if errors else 0.0
        
        # 按说话者分组统计
        by_speaker = {}
        for i in listener_interactions:
            speaker = i["speaker"]
            if speaker not in by_speaker:
                by_speaker[speaker] = []
            if "perception_error" in i["listener_state"]:
                by_speaker[speaker].append(i["listener_state"]["perception_error"])
        
        speaker_accuracy = {
            speaker: {
                "avg_error": sum(errors) / len(errors),
                "interaction_count": len(errors)
            }
            for speaker, errors in by_speaker.items()
        }
        
        return {
            "agent": agent,
            "total_interactions": len(listener_interactions),
            "avg_perception_error": avg_error,
            "accuracy_by_speaker": speaker_accuracy
        }
    
    def analyze_emotion_contagion(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """
        分析情感传染效应
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            情感传染分析
        """
        interactions = self.get_interactions(
            start_time=start_time,
            end_time=end_time
        )
        
        contagion_effects = []
        
        for i in interactions:
            listener_state = i["listener_state"]
            if "my_emotion_before" in listener_state and "my_emotion_after" in listener_state:
                before = listener_state["my_emotion_before"].get("pleasure", 0)
                after = listener_state["my_emotion_after"].get("pleasure", 0)
                speaker_emotion = i["speaker_state"]["real_emotion"].get("pleasure", 0)
                
                # 情感传染效应 = 听话者情绪变化与说话者情绪的相关性
                emotion_change = after - before
                
                contagion_effects.append({
                    "speaker": i["speaker"],
                    "listener": i["listener"],
                    "speaker_emotion": speaker_emotion,
                    "listener_change": emotion_change,
                    "contagion_strength": emotion_change if speaker_emotion > 0 else -emotion_change
                })
        
        if not contagion_effects:
            return {
                "status": "no_data"
            }
        
        # 计算平均传染强度
        avg_contagion = sum(c["contagion_strength"] for c in contagion_effects) / len(contagion_effects)
        
        return {
            "total_interactions": len(interactions),
            "avg_contagion_strength": avg_contagion,
            "examples": contagion_effects[:10]  # 返回前10个例子
        }
    
    def close(self):
        """关闭记录器，刷新缓冲区"""
        self._flush_buffer()
