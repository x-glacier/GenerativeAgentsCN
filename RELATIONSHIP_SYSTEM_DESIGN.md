# 智能体人际关系系统设计

**设计理念**: 模拟真实人际交往中的多维度关系和情感感知机制

---

## 一、多维度关系模型

### 1.1 关系的五个维度

#### 1. **血缘关系（Kinship）**
- **定义**: 基于家庭、血缘的关系
- **类型**:
  - 父母-子女（parent-child）
  - 兄弟姐妹（sibling）
  - 祖孙（grandparent-grandchild）
  - 其他亲属（relative）
  - 无血缘（none）

- **特点**:
  - 相对稳定，不易改变
  - 强烈的情感纽带
  - 高度的信任和包容

- **影响**:
  - 血缘关系强 → 情感投射偏差小（更客观理解对方）
  - 血缘关系强 → 记忆保留时间长
  - 血缘关系强 → 情绪共鸣强

---

#### 2. **社会关系（Social）**
- **定义**: 基于社会角色、职业、地位的关系
- **类型**:
  - 上下级（superior-subordinate）
  - 同事（colleague）
  - 师生（teacher-student）
  - 邻居（neighbor）
  - 陌生人（stranger）

- **特点**:
  - 受社会规范约束
  - 有明确的角色期待
  - 可能存在权力不对等

- **影响**:
  - 上级说话 → 下级更重视（记忆强度高）
  - 陌生人说话 → 警惕性高（认知偏差大）
  - 同事关系 → 竞争或合作心态

---

#### 3. **情感关系（Emotional）**
- **定义**: 基于情感连接的关系
- **维度**:
  - **好感度（Affection）**: 0-100，喜欢程度
  - **信任度（Trust）**: 0-100，信任程度
  - **亲密度（Intimacy）**: 0-100，亲密程度

- **类型**:
  - 恋人（romantic partner）: 好感>80, 信任>70, 亲密>80
  - 密友（close friend）: 好感>70, 信任>70, 亲密>60
  - 普通朋友（friend）: 好感>50, 信任>40, 亲密>30
  - 熟人（acquaintance）: 好感>30, 信任>20, 亲密>10
  - 陌生人（stranger）: 好感=50, 信任=20, 亲密=0

- **特点**:
  - 动态变化，受交互影响
  - 三个维度可能不一致（如：喜欢但不信任）

- **影响**:
  - 好感度高 → 正面解读对方的话
  - 信任度高 → 认知偏差小
  - 亲密度高 → 情绪共鸣强

---

#### 4. **印象关系（Impression）**
- **定义**: 基于历史交互形成的主观印象
- **维度**:
  - **整体印象（Overall）**: -100 到 +100
  - **性格印象（Personality）**: 对对方性格的认知
    - 外向 vs 内向
    - 友善 vs 冷漠
    - 可靠 vs 不可靠
  - **能力印象（Competence）**: 对对方能力的认知
  - **情绪印象（Emotional Pattern）**: 对对方情绪模式的认知
    - "她总是很开心"
    - "他容易生气"

- **特点**:
  - 基于有限信息的推断
  - 可能存在偏见（首因效应、近因效应）
  - 会随着交互更新

- **影响**:
  - 印象好 → 倾向于正面解读
  - 印象差 → 倾向于负面解读
  - 印象稳定 → 难以改变看法

---

#### 5. **历史关系（History）**
- **定义**: 基于过去交互的历史记录
- **内容**:
  - **交互次数（Interaction Count）**: 见面/对话次数
  - **最近交互（Last Interaction）**: 最后一次交互时间
  - **共同经历（Shared Experiences）**: 重要的共同事件
  - **冲突历史（Conflicts）**: 过去的矛盾和冲突
  - **帮助历史（Favors）**: 互相帮助的记录

- **特点**:
  - 客观记录，不可篡改
  - 影响当前关系的基础

- **影响**:
  - 交互次数多 → 熟悉度高
  - 有共同经历 → 情感连接强
  - 有冲突历史 → 警惕性高

---

## 二、关系对情感感知的影响

### 2.1 情感感知公式

当智能体 B 收到智能体 A 的消息时：

```
B 感知到的 A 的情绪 = f(
    客观情感分析,
    B 的当前情绪,
    B 对 A 的关系
)
```

### 2.2 详细计算模型

#### 步骤 1: 客观情感分析
```python
objective_emotion = analyze_text_emotion(A_text)
# 输出: {valence: 0.7, arousal: 0.5, dominance: 0.6}
```

#### 步骤 2: 情感投射
```python
# B 的当前情绪影响感知
if B_current_emotion.valence > 0.5:  # B 很开心
    projection_bias = +0.1  # 倾向于认为 A 也开心
else:  # B 很沮丧
    projection_bias = -0.1  # 倾向于认为 A 也不开心

# 但如果 B 的神经质高，投射更强
projection_bias *= B_personality.neuroticism
```

#### 步骤 3: 关系偏差

##### 3.1 血缘关系偏差
```python
if kinship == "parent-child":
    kinship_bias = 0.0  # 父母对子女理解更客观
elif kinship == "sibling":
    kinship_bias = 0.05  # 兄弟姐妹可能有竞争心理
else:
    kinship_bias = 0.0
```

##### 3.2 社会关系偏差
```python
if social == "superior":  # A 是 B 的上级
    social_bias = 0.1  # B 倾向于正面理解上级
elif social == "subordinate":  # A 是 B 的下级
    social_bias = -0.05  # B 可能不太重视下级的情绪
else:
    social_bias = 0.0
```

##### 3.3 情感关系偏差
```python
affection_bias = (affection - 50) / 100 * 0.2
# 好感度 80 → bias = +0.06
# 好感度 20 → bias = -0.06

trust_bias = (trust - 50) / 100 * 0.1
# 信任度高 → 偏差小（更客观）
# 信任度低 → 偏差大（更主观）
```

##### 3.4 印象偏差
```python
impression_bias = overall_impression / 100 * 0.15
# 印象好 → 正面解读
# 印象差 → 负面解读
```

##### 3.5 历史偏差
```python
if has_recent_conflict:
    history_bias = -0.2  # 最近有冲突，倾向于负面理解
elif has_recent_favor:
    history_bias = +0.1  # 最近被帮助，倾向于正面理解
else:
    history_bias = 0.0
```

#### 步骤 4: 综合计算
```python
perceived_emotion = {
    'valence': clip(
        objective_emotion.valence 
        + projection_bias 
        + kinship_bias 
        + social_bias 
        + affection_bias 
        + impression_bias 
        + history_bias,
        -1.0, 1.0
    ),
    'arousal': objective_emotion.arousal,
    'dominance': objective_emotion.dominance
}

perception_error = abs(perceived_emotion.valence - A_real_emotion.valence)
```

---

## 三、关系的动态演化

### 3.1 关系如何变化

#### 情感关系的更新
```python
# 每次交互后更新
if interaction_positive:
    affection += 1 * (1 - affection/100)  # 越高越难增长
    trust += 0.5 * (1 - trust/100)
    intimacy += 0.3 * (1 - intimacy/100)
else:
    affection -= 2  # 负面交互影响更大
    trust -= 3
    intimacy -= 1

# 时间衰减（长时间不联系）
days_since_last_interaction = ...
if days_since_last_interaction > 30:
    intimacy -= days_since_last_interaction * 0.01
```

#### 印象的更新
```python
# 首因效应：第一次交互影响大
if interaction_count == 1:
    weight = 0.8
# 近因效应：最近的交互影响大
elif is_recent:
    weight = 0.5
else:
    weight = 0.2

overall_impression = (
    overall_impression * (1 - weight) 
    + new_impression * weight
)
```

---

## 四、记忆中的关系信息

### 4.1 记忆条目的扩展

当 B 记录与 A 的交互时，应该包含：

```python
{
    "content": "A 邀请我去散步",
    "timestamp": "2026-01-15 14:30",
    
    # A 的真实情绪（系统记录，B 不知道）
    "speaker_real_emotion": {
        "valence": 0.8,
        "arousal": 0.6,
        "dominance": 0.7
    },
    
    # B 感知到的 A 的情绪
    "speaker_perceived_emotion": {
        "valence": 0.6,
        "arousal": 0.6,
        "dominance": 0.7
    },
    
    # B 的当前情绪
    "my_emotion": {
        "valence": -0.3,
        "arousal": 0.2,
        "dominance": 0.4
    },
    
    # 感知偏差分析
    "perception_analysis": {
        "objective_emotion": 0.7,
        "projection_bias": -0.2,
        "relationship_bias": 0.1,
        "perception_error": 0.2
    },
    
    # 当时的关系状态
    "relationship_snapshot": {
        "affection": 65,
        "trust": 70,
        "intimacy": 50,
        "overall_impression": 60
    },
    
    # 这次交互对关系的影响
    "relationship_change": {
        "affection": +2,
        "trust": +1,
        "intimacy": +1
    }
}
```

---

## 五、实现架构

### 5.1 新增模块

#### RelationshipManager
```python
class RelationshipManager:
    """管理智能体之间的关系"""
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.relationships = {}  # {other_name: Relationship}
    
    def get_relationship(self, other_name):
        """获取与某人的关系"""
        if other_name not in self.relationships:
            self.relationships[other_name] = Relationship(other_name)
        return self.relationships[other_name]
    
    def update_relationship(self, other_name, interaction_result):
        """根据交互结果更新关系"""
        rel = self.get_relationship(other_name)
        rel.update(interaction_result)
```

#### Relationship
```python
class Relationship:
    """表示与某人的关系"""
    
    def __init__(self, other_name):
        self.other_name = other_name
        
        # 血缘关系（静态）
        self.kinship = "none"
        
        # 社会关系（相对静态）
        self.social = "stranger"
        
        # 情感关系（动态）
        self.affection = 50
        self.trust = 20
        self.intimacy = 0
        
        # 印象（动态）
        self.overall_impression = 50
        self.personality_impression = {}
        
        # 历史（累积）
        self.interaction_count = 0
        self.last_interaction = None
        self.shared_experiences = []
        self.conflicts = []
        self.favors = []
    
    def calculate_perception_bias(self, my_emotion):
        """计算基于关系的感知偏差"""
        # 实现上面的公式
        ...
```

#### EmotionPerception
```python
class EmotionPerception:
    """情感感知模块"""
    
    def perceive_emotion(
        self,
        text,
        my_emotion,
        relationship
    ):
        """
        感知对方的情绪
        
        Returns:
            {
                'perceived_emotion': {...},
                'objective_emotion': {...},
                'perception_bias': {...},
                'perception_error': float
            }
        """
        # 1. 客观分析
        objective = self._analyze_text(text)
        
        # 2. 情感投射
        projection = self._calculate_projection(my_emotion, objective)
        
        # 3. 关系偏差
        relation_bias = relationship.calculate_perception_bias(my_emotion)
        
        # 4. 综合
        perceived = self._combine(objective, projection, relation_bias)
        
        return {
            'perceived_emotion': perceived,
            'objective_emotion': objective,
            'projection_bias': projection,
            'relationship_bias': relation_bias,
            'perception_error': abs(perceived['valence'] - objective['valence'])
        }
```

---

## 六、研究价值

### 6.1 可以研究的问题

1. **情感传染**
   - 一个开心的智能体会让周围的智能体也开心吗？
   - 传染速度与关系强度的关系？

2. **群体极化**
   - 密友圈内的情绪会相互强化吗？
   - 负面情绪的传播速度更快吗？

3. **关系演化**
   - 什么样的交互模式导致关系恶化？
   - 长期不联系的朋友关系如何变化？

4. **认知偏差**
   - 首因效应有多强？
   - 印象一旦形成，需要多少次正面交互才能改变？

5. **社会网络**
   - 关系网络的结构如何影响信息传播？
   - 中心节点（社交达人）的情绪影响力更大吗？

---

## 七、实现优先级

### Phase 1: 核心功能（必须）
- [x] 情感关系（好感、信任、亲密）
- [x] 基本印象
- [x] 情感感知（客观分析 + 简单偏差）

### Phase 2: 增强功能（重要）
- [ ] 血缘关系和社会关系
- [ ] 完整的感知偏差模型
- [ ] 关系动态演化

### Phase 3: 高级功能（可选）
- [ ] 历史关系的详细记录
- [ ] 性格印象的细粒度建模
- [ ] 关系网络分析

---

## 八、数据结构设计

### 8.1 Agent 配置扩展

```json
{
  "name": "阿伊莎",
  "personality": {...},
  "relationships": {
    "张伟": {
      "kinship": "none",
      "social": "colleague",
      "emotional": {
        "affection": 65,
        "trust": 70,
        "intimacy": 50
      },
      "impression": {
        "overall": 60,
        "personality": {
          "extraversion": 0.7,
          "agreeableness": 0.8
        }
      }
    },
    "李娜": {
      "kinship": "sibling",
      "social": "none",
      "emotional": {
        "affection": 90,
        "trust": 95,
        "intimacy": 85
      },
      "impression": {
        "overall": 85,
        "personality": {
          "conscientiousness": 0.9
        }
      }
    }
  }
}
```

---

## 九、总结

这个人际关系系统将使智能体的交互更加真实和复杂：

1. **多维度关系**：不再是简单的"朋友"或"陌生人"，而是包含血缘、社会、情感、印象、历史五个维度

2. **情感感知**：不再是直接传递情绪，而是通过文字分析 + 情感投射 + 关系偏差来感知

3. **动态演化**：关系会随着交互而变化，有正反馈也有负反馈

4. **记忆丰富**：每次交互都记录详细的情感和关系信息，可以用于后续分析

5. **研究价值**：可以研究情感传染、群体极化、认知偏差等社会心理学问题

这是一个非常有深度的系统，值得投入时间来实现！
