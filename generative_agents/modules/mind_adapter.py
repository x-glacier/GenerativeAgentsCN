# generative_agents/modules/mind_adapter.py

"""
适配器模块（简化版）：将 MemOS-Mind 的 AI 心智层集成到 GenerativeAgentsCN

作者: Manus AI
日期: 2026-01-15
"""

import sys
import os

# 动态添加 memos-mind 的路径，确保可以导入
# 假设 memos-mind 项目与 GenerativeAgentsCN 在同一目录下 /home/ubuntu/
sys.path.insert(0, "/home/ubuntu/memos-mind/src")

try:
    from memos_mind import MindMemoryCubeV2, MindProfile
    from memos_mind.storage.sqlite_storage import SQLiteStorage
except ImportError as e:
    print(f"Error importing memos_mind: {e}")
    print("Please ensure the memos-mind repository is cloned to /home/ubuntu/memos-mind")
    raise

class AgentMindAdapter:
    """
    适配器（简化版）：将 MemOS-Mind 的 AI 心智层作为智能体的“灵魂”。

    职责：
    1. 将 Agent 的配置（性格、价值观）转换为 MemOS-Mind 的 MindProfile。
    2. 管理智能体自身的情绪状态和情感化记忆。
    3. 将 GenerativeAgentsCN 的 Event 转换为 MemOS-Mind 的输入进行处理。
    4. 提供接口获取当前情绪状态，以影响行为决策。
    """

    def __init__(self, agent_name, agent_config, db_path):
        """
        初始化适配器。

        Args:
            agent_name (str): 智能体的名字。
            agent_config (dict): 来自 agent.json 的配置。
            db_path (str): 该智能体用于持久化心智记忆的 SQLite 数据库文件路径。
        """
        # 1. 从 agent.json 配置创建 MindProfile
        self.mind_profile = self._create_mind_profile_from_config(agent_config)

        # 2. 初始化 SQLite 存储后端
        self.storage = SQLiteStorage(db_path=db_path)

        # 3. 初始化 MindMemoryCubeV2
        # 根据您的指示，我们只关心智能体自身的心智，所以 user_profile 设置为 None。
        self.mind_cube = MindMemoryCubeV2(
            ai_profile=self.mind_profile,
            user_profile=None,  # 关键简化：不追踪其他智能体
            storage=self.storage
        )

    def _create_mind_profile_from_config(self, config):
        """从 agent.json 配置提取性格、价值观等信息。"""
        personality_config = config.get("personality", {})
        values_config = config.get("values", {})

        # 映射到大五人格和 Schwartz 价值观
        mind_profile = MindProfile(
            personality={
                "openness": personality_config.get("openness", 0.5),
                "conscientiousness": personality_config.get("conscientiousness", 0.5),
                "extraversion": personality_config.get("extraversion", 0.5),
                "agreeableness": personality_config.get("agreeableness", 0.5),
                "neuroticism": personality_config.get("neuroticism", 0.5),
            },
            values=values_config,
        )
        return mind_profile

    def process_event(self, event, context=None):
        """
        处理一个事件，更新自身的情绪和记忆。

        Args:
            event: GenerativeAgentsCN 的 Event 对象 (subject, predicate, object)。
            context (dict): 可选的上下文信息（如当前位置、时间）。

        Returns:
            memos_mind 的处理结果，或在事件无效时返回 None。
        """
        # 将 Event 转换为自然语言描述
        event_text = f"{event.subject} {event.predicate} {event.object}".strip()
        if not event_text:
            return None

        # 调用 MemOS-Mind 处理。process_user_input 这个名字虽然带 user，
        # 但在这里我们用它来处理任何外部输入，以更新智能体自身的心智状态。
        result = self.mind_cube.process_user_input(
            content=event_text,
            context=context
        )

        return result

    def get_emotion_state(self):
        """获取当前情绪状态（VAD 格式的字典）。"""
        emotion_obj = self.mind_cube.get_emotional_state()
        if emotion_obj:
            return emotion_obj.to_dict()
        return None

    def retrieve_emotional_memories(self, query, top_k=5):
        """检索与查询相关的情感化记忆。"""
        return self.mind_cube.retrieve_memories(query=query, top_k=top_k)

    def run_forgetting_cycle(self):
        """运行遗忘循环，清理低强度记忆。"""
        return self.mind_cube.run_forgetting_cycle()
