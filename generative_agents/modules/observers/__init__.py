"""
上帝视角观察系统（God's Eye View System）

这个模块提供了一个独立的观察和记录系统，用于：
- 记录所有智能体的心智状态演化
- 记录智能体之间的关系演化
- 记录所有交互事件的详细信息
- 提供数据查询和分析接口
"""

from .mind_state_logger import MindStateLogger
from .relationship_logger import RelationshipLogger
from .interaction_logger import InteractionLogger
from .gods_eye_system import GodsEyeSystem

__all__ = [
    'MindStateLogger',
    'RelationshipLogger',
    'InteractionLogger',
    'GodsEyeSystem'
]
