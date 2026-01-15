"""
关系管理系统（Relationship Manager）

管理智能体之间的多维度关系，包括：
- 血缘关系（Kinship）
- 社会关系（Social）
- 情感关系（Emotional: affection, trust, intimacy）
- 印象关系（Impression）
- 历史关系（History）
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class Relationship:
    """表示与某个智能体的关系"""
    
    def __init__(self, other_name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化关系
        
        Args:
            other_name: 对方的名字
            config: 关系配置（可选）
        """
        self.other_name = other_name
        
        # 血缘关系（静态）
        self.kinship = "none"  # none, parent-child, sibling, grandparent-grandchild, relative
        
        # 社会关系（相对静态）
        self.social = "stranger"  # stranger, neighbor, colleague, superior, subordinate, teacher-student
        
        # 情感关系（动态）
        self.affection = 50  # 好感度 0-100
        self.trust = 20  # 信任度 0-100
        self.intimacy = 0  # 亲密度 0-100
        
        # 印象（动态）
        self.overall_impression = 50  # 整体印象 -100 到 +100
        self.personality_impression = {}  # 对对方性格的认知
        
        # 历史（累积）
        self.interaction_count = 0
        self.last_interaction = None
        self.shared_experiences = []
        self.conflicts = []
        self.favors = []
        
        # 如果提供了配置，加载配置
        if config:
            self.load_from_config(config)
    
    def load_from_config(self, config: Dict[str, Any]):
        """从配置加载关系"""
        self.kinship = config.get("kinship", "none")
        self.social = config.get("social", "stranger")
        
        emotional = config.get("emotional", {})
        self.affection = emotional.get("affection", 50)
        self.trust = emotional.get("trust", 20)
        self.intimacy = emotional.get("intimacy", 0)
        
        impression = config.get("impression", {})
        self.overall_impression = impression.get("overall", 50)
        self.personality_impression = impression.get("personality", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "other_name": self.other_name,
            "kinship": self.kinship,
            "social": self.social,
            "emotional": {
                "affection": self.affection,
                "trust": self.trust,
                "intimacy": self.intimacy
            },
            "impression": {
                "overall": self.overall_impression,
                "personality": self.personality_impression
            },
            "history": {
                "interaction_count": self.interaction_count,
                "last_interaction": self.last_interaction,
                "shared_experiences": len(self.shared_experiences),
                "conflicts": len(self.conflicts),
                "favors": len(self.favors)
            }
        }
    
    def calculate_perception_bias(self, my_emotion: Dict[str, float]) -> Dict[str, float]:
        """
        计算基于关系的感知偏差
        
        Args:
            my_emotion: 我当前的情绪状态
        
        Returns:
            各种偏差的字典
        """
        biases = {}
        
        # 1. 血缘关系偏差
        kinship_bias_map = {
            "parent-child": 0.0,  # 父母对子女理解更客观
            "sibling": 0.05,  # 兄弟姐妹可能有竞争心理
            "none": 0.0
        }
        biases["kinship"] = kinship_bias_map.get(self.kinship, 0.0)
        
        # 2. 社会关系偏差
        social_bias_map = {
            "superior": 0.1,  # 倾向于正面理解上级
            "subordinate": -0.05,  # 可能不太重视下级的情绪
            "colleague": 0.0,
            "stranger": 0.0
        }
        biases["social"] = social_bias_map.get(self.social, 0.0)
        
        # 3. 情感关系偏差
        biases["affection"] = (self.affection - 50) / 100 * 0.2
        biases["trust"] = (self.trust - 50) / 100 * 0.1
        
        # 4. 印象偏差
        biases["impression"] = self.overall_impression / 100 * 0.15
        
        # 5. 历史偏差
        history_bias = 0.0
        if self.conflicts and self.conflicts[-1].get("recent", False):
            history_bias = -0.2  # 最近有冲突
        elif self.favors and self.favors[-1].get("recent", False):
            history_bias = 0.1  # 最近被帮助
        biases["history"] = history_bias
        
        # 6. 总偏差
        biases["total"] = sum(biases.values())
        
        return biases
    
    def update_after_interaction(
        self,
        interaction_positive: bool,
        interaction_intensity: float = 1.0
    ):
        """
        交互后更新关系
        
        Args:
            interaction_positive: 交互是否积极
            interaction_intensity: 交互强度（0-1）
        """
        self.interaction_count += 1
        
        if interaction_positive:
            # 正面交互
            self.affection += 1 * interaction_intensity * (1 - self.affection/100)
            self.trust += 0.5 * interaction_intensity * (1 - self.trust/100)
            self.intimacy += 0.3 * interaction_intensity * (1 - self.intimacy/100)
            self.overall_impression += 2 * interaction_intensity
        else:
            # 负面交互（影响更大）
            self.affection -= 2 * interaction_intensity
            self.trust -= 3 * interaction_intensity
            self.intimacy -= 1 * interaction_intensity
            self.overall_impression -= 5 * interaction_intensity
        
        # 限制范围
        self.affection = max(0, min(100, self.affection))
        self.trust = max(0, min(100, self.trust))
        self.intimacy = max(0, min(100, self.intimacy))
        self.overall_impression = max(-100, min(100, self.overall_impression))
    
    def decay_over_time(self, days_since_last_interaction: float):
        """
        时间衰减（长时间不联系）
        
        Args:
            days_since_last_interaction: 距离上次交互的天数
        """
        if days_since_last_interaction > 30:
            decay_rate = (days_since_last_interaction - 30) * 0.01
            self.intimacy = max(0, self.intimacy - decay_rate)


class RelationshipManager:
    """管理智能体的所有关系"""
    
    def __init__(self, agent_name: str, config_path: Optional[str] = None):
        """
        初始化关系管理器
        
        Args:
            agent_name: 智能体名字
            config_path: 配置文件路径（可选）
        """
        self.agent_name = agent_name
        self.relationships: Dict[str, Relationship] = {}
        
        # 如果提供了配置文件，加载配置
        if config_path and Path(config_path).exists():
            self.load_from_config(config_path)
    
    def load_from_config(self, config_path: str):
        """从配置文件加载关系"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        relationships_config = config.get("relationships", {})
        for other_name, rel_config in relationships_config.items():
            self.relationships[other_name] = Relationship(other_name, rel_config)
    
    def get_relationship(self, other_name: str) -> Relationship:
        """
        获取与某人的关系
        
        Args:
            other_name: 对方的名字
        
        Returns:
            关系对象
        """
        if other_name not in self.relationships:
            # 如果没有记录，创建一个新的陌生人关系
            self.relationships[other_name] = Relationship(other_name)
        return self.relationships[other_name]
    
    def update_relationship(
        self,
        other_name: str,
        interaction_positive: bool,
        interaction_intensity: float = 1.0
    ) -> Dict[str, float]:
        """
        根据交互结果更新关系
        
        Args:
            other_name: 对方的名字
            interaction_positive: 交互是否积极
            interaction_intensity: 交互强度
        
        Returns:
            关系变化量
        """
        rel = self.get_relationship(other_name)
        
        # 记录更新前的状态
        before = {
            "affection": rel.affection,
            "trust": rel.trust,
            "intimacy": rel.intimacy
        }
        
        # 更新关系
        rel.update_after_interaction(interaction_positive, interaction_intensity)
        
        # 计算变化量
        changes = {
            "affection": rel.affection - before["affection"],
            "trust": rel.trust - before["trust"],
            "intimacy": rel.intimacy - before["intimacy"]
        }
        
        return changes
    
    def get_all_relationships(self) -> Dict[str, Dict[str, Any]]:
        """获取所有关系的字典表示"""
        return {
            name: rel.to_dict()
            for name, rel in self.relationships.items()
        }
    
    def save_to_file(self, filepath: str):
        """保存关系到文件"""
        data = {
            "agent": self.agent_name,
            "relationships": self.get_all_relationships()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
