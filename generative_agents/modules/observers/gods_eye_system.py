"""
上帝视角系统（God's Eye System）

整合所有观察和记录组件，提供统一的接口
"""

from typing import Dict, Any, Optional, List
from .mind_state_logger import MindStateLogger
from .relationship_logger import RelationshipLogger
from .interaction_logger import InteractionLogger
from .evolution_database import EvolutionDatabase


class GodsEyeSystem:
    """上帝视角观察系统"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "storage/evolution.db", enable_db: bool = True):
        """
        初始化上帝视角系统
        
        Args:
            db_path: 数据库文件路径
            enable_db: 是否启用数据库存储
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # 初始化数据库
        self.db = EvolutionDatabase(db_path) if enable_db else None
        
        # 初始化记录器
        self.mind_logger = MindStateLogger(self.db)
        self.relationship_logger = RelationshipLogger(self.db)
        self.interaction_logger = InteractionLogger(self.db)
        
        print(f"✓ 上帝视角系统已启动")
        if enable_db:
            print(f"  数据库: {db_path}")
    
    # ========== 记录接口 ==========
    
    def log_mind_state(
        self,
        agent_name: str,
        emotion: Dict[str, float],
        personality: Dict[str, float],
        current_activity: str = "",
        location: str = "",
        memory_stats: Optional[Dict[str, Any]] = None
    ):
        """记录智能体的心智状态"""
        return self.mind_logger.log_state(
            agent_name=agent_name,
            emotion=emotion,
            personality=personality,
            current_activity=current_activity,
            location=location,
            memory_stats=memory_stats
        )
    
    def log_relationship(
        self,
        agent_a: str,
        agent_b: str,
        a_to_b: Dict[str, Any],
        b_to_a: Optional[Dict[str, Any]] = None,
        kinship: str = "none",
        social: str = "stranger",
        interaction_stats: Optional[Dict[str, Any]] = None
    ):
        """记录两个智能体之间的关系"""
        return self.relationship_logger.log_relationship(
            agent_a=agent_a,
            agent_b=agent_b,
            a_to_b=a_to_b,
            b_to_a=b_to_a,
            kinship=kinship,
            social=social,
            interaction_stats=interaction_stats
        )
    
    def log_interaction(
        self,
        interaction_type: str,
        speaker: str,
        listener: str,
        content: str,
        speaker_state: Dict[str, Any],
        listener_state: Dict[str, Any],
        relationship_change: Optional[Dict[str, float]] = None,
        location: str = ""
    ):
        """记录一次交互事件"""
        return self.interaction_logger.log_interaction(
            interaction_type=interaction_type,
            speaker=speaker,
            listener=listener,
            content=content,
            speaker_state=speaker_state,
            listener_state=listener_state,
            relationship_change=relationship_change,
            location=location
        )
    
    # ========== 查询接口 ==========
    
    def get_agent_emotion_timeline(
        self,
        agent_name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """获取智能体的情绪时间线"""
        return self.mind_logger.get_emotion_timeline(
            agent_name=agent_name,
            start_time=start_time,
            end_time=end_time
        )
    
    def get_relationship_timeline(
        self,
        agent_a: str,
        agent_b: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """获取两个智能体的关系演化时间线"""
        return self.relationship_logger.get_relationship_timeline(
            agent_a=agent_a,
            agent_b=agent_b,
            start_time=start_time,
            end_time=end_time
        )
    
    def get_recent_interactions(
        self,
        agent: Optional[str] = None,
        limit: int = 10
    ):
        """获取最近的交互事件"""
        return self.interaction_logger.get_interactions(
            agent=agent,
            limit=limit
        )
    
    def get_relationship_network(self, agents: List[str]):
        """获取关系网络快照"""
        return self.relationship_logger.get_relationship_network(agents)
    
    # ========== 分析接口 ==========
    
    def analyze_emotion_change(
        self,
        agent_name: str,
        time_window: float = 3600
    ):
        """分析智能体的情绪变化"""
        return self.mind_logger.analyze_emotion_change(
            agent_name=agent_name,
            time_window=time_window
        )
    
    def analyze_relationship_evolution(
        self,
        agent_a: str,
        agent_b: str
    ):
        """分析两个智能体的关系演化"""
        return self.relationship_logger.analyze_relationship_evolution(
            agent_a=agent_a,
            agent_b=agent_b
        )
    
    def analyze_perception_accuracy(
        self,
        agent: str,
        time_window: Optional[float] = None
    ):
        """分析智能体的情绪感知准确度"""
        return self.interaction_logger.analyze_perception_accuracy(
            agent=agent,
            time_window=time_window
        )
    
    def analyze_emotion_contagion(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """分析情感传染效应"""
        return self.interaction_logger.analyze_emotion_contagion(
            start_time=start_time,
            end_time=end_time
        )
    
    # ========== 统计接口 ==========
    
    def get_statistics(self):
        """获取系统统计信息"""
        if self.db:
            db_stats = self.db.get_statistics()
        else:
            db_stats = {}
        
        return {
            "database": db_stats,
            "buffers": {
                "mind_states": len(self.mind_logger.memory_buffer),
                "relationships": len(self.relationship_logger.memory_buffer),
                "interactions": len(self.interaction_logger.memory_buffer)
            }
        }
    
    def export_data(
        self,
        output_file: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """
        导出数据到文件
        
        Args:
            output_file: 输出文件路径
            start_time: 开始时间
            end_time: 结束时间
        """
        import json
        
        data = {
            "mind_states": [],
            "relationships": [],
            "interactions": []
        }
        
        if self.db:
            data["mind_states"] = self.db.query_mind_states(
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
            data["relationships"] = self.db.query_relationships(
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
            data["interactions"] = self.db.query_interactions(
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已导出到: {output_file}")
    
    def close(self):
        """关闭系统，刷新所有缓冲区"""
        self.mind_logger.close()
        self.relationship_logger.close()
        self.interaction_logger.close()
        
        if self.db:
            self.db.close()
        
        print("✓ 上帝视角系统已关闭")


# 全局单例实例
_gods_eye = None


def get_gods_eye_system(db_path: str = "storage/evolution.db", enable_db: bool = True) -> GodsEyeSystem:
    """获取上帝视角系统的全局单例"""
    global _gods_eye
    if _gods_eye is None:
        _gods_eye = GodsEyeSystem(db_path=db_path, enable_db=enable_db)
    return _gods_eye
