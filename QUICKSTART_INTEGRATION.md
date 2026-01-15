# MemOS-Mind 整合快速入门

本文档提供 MemOS-Mind 与 GenerativeAgentsCN 整合的快速入门指南。

---

## 一、前置准备

### 1.1 确认环境

```bash
# 确认 Python 版本
python3.11 --version  # 应为 3.11.x

# 确认 GenerativeAgentsCN 已克隆
cd /home/ubuntu/GenerativeAgentsCN
ls generative_agents/  # 应看到 start.py
```

### 1.2 克隆 memos-mind

```bash
cd /home/ubuntu
gh repo clone sxhfut/memos-mind
```

### 1.3 安装依赖

```bash
cd /home/ubuntu/memos-mind
sudo pip3 install -r requirements.txt
```

---

## 二、配置智能体性格

### 2.1 编辑智能体配置文件

以"阿伊莎"为例：

```bash
cd /home/ubuntu/GenerativeAgentsCN
vim generative_agents/frontend/static/assets/village/agents/阿伊莎/agent.json
```

### 2.2 添加性格字段

在 JSON 文件的根级别添加以下字段：

```json
{
  "name": "阿伊莎",
  "age": 25,
  "innate": "...",
  "learned": "...",
  
  "personality": {
    "openness": 0.8,
    "conscientiousness": 0.6,
    "extraversion": 0.7,
    "agreeableness": 0.9,
    "neuroticism": 0.3
  },
  
  "values": {
    "benevolence": 0.9,
    "universalism": 0.8,
    "self-direction": 0.7,
    "achievement": 0.5,
    "power": 0.3
  }
}
```

**字段说明**：

| 字段 | 含义 | 取值范围 |
|------|------|----------|
| `openness` | 开放性（好奇心、创造力） | 0.0 - 1.0 |
| `conscientiousness` | 尽责性（自律、有条理） | 0.0 - 1.0 |
| `extraversion` | 外向性（社交、活力） | 0.0 - 1.0 |
| `agreeableness` | 宜人性（友善、合作） | 0.0 - 1.0 |
| `neuroticism` | 神经质（情绪不稳定） | 0.0 - 1.0 |

**价值观字段**（Schwartz 价值观）：

| 字段 | 含义 |
|------|------|
| `benevolence` | 仁慈（关心他人福祉） |
| `universalism` | 普世主义（公平、正义） |
| `self-direction` | 自我导向（独立、自由） |
| `achievement` | 成就（成功、能力） |
| `power` | 权力（地位、控制） |

### 2.3 为所有智能体配置性格

重复上述步骤，为每个智能体添加性格配置。

**建议**：

- 根据智能体的背景故事设计性格。
- 保持多样性，避免所有智能体性格相同。

---

## 三、运行系统

### 3.1 启动服务

```bash
cd /home/ubuntu/GenerativeAgentsCN/generative_agents
python3.11 start.py
```

### 3.2 观察日志

在日志中应看到类似输出：

```
[INFO] 阿伊莎 initialized mind adapter
[INFO] 阿伊莎 emotion state: Pleasure=0.50, Arousal=0.50, Dominance=0.50
```

### 3.3 访问前端

打开浏览器，访问：

```
http://localhost:8000
```

---

## 四、验证整合效果

### 4.1 查看情绪状态

在前端界面中，点击某个智能体，查看其状态面板。应看到新增的 `emotion` 字段：

```json
{
  "name": "阿伊莎",
  "emotion": {
    "pleasure": 0.65,
    "arousal": 0.72,
    "dominance": 0.58
  }
}
```

### 4.2 观察对话变化

让两个智能体对话，观察情绪对语气的影响：

**高兴时**：
```
阿伊莎: "哈哈，今天天气真好！我们去公园散步吧！"
```

**沮丧时**：
```
阿伊莎: "唉...我最近有点累，不太想说话。"
```

### 4.3 查看记忆强度

在数据库中查看记忆强度：

```bash
sqlite3 /home/ubuntu/GenerativeAgentsCN/generative_agents/storage/mind_db/阿伊莎.db
```

```sql
SELECT content, strength, emotional_valence FROM memories ORDER BY strength DESC LIMIT 10;
```

---

## 五、常见问题

### 5.1 导入错误：`ModuleNotFoundError: No module named 'memos_mind'`

**原因**：memos-mind 未正确安装或路径不对。

**解决方案**：

```bash
# 确认 memos-mind 路径
ls /home/ubuntu/memos-mind/src/memos_mind/

# 重新安装
cd /home/ubuntu/memos-mind
sudo pip3 install -e .
```

### 5.2 性格配置缺失

**原因**：`agent.json` 中未添加 `personality` 和 `values` 字段。

**解决方案**：

- 检查 JSON 文件格式是否正确。
- 使用默认值：系统会自动使用 0.5 作为所有性格维度的默认值。

### 5.3 情绪状态不更新

**原因**：事件处理逻辑未正确触发。

**解决方案**：

- 检查日志，确认 `process_event` 被调用。
- 确认 `mind_cube.emotion_engine.decay()` 在每个 tick 被调用。

### 5.4 数据库锁定错误

**原因**：多个进程同时访问同一个 SQLite 数据库。

**解决方案**：

- 确保每个智能体使用独立的数据库文件（已在代码中实现）。
- 检查是否有其他进程在访问数据库。

---

## 六、高级配置

### 6.1 调整情绪衰减速度

编辑 `mind_adapter.py`：

```python
# 在 process_event 后添加
self.mind_cube.emotion_engine.decay(rate=0.05)  # 默认为 0.1
```

### 6.2 自定义情绪-记忆映射

编辑 `memos-mind` 的配置文件：

```python
# 在 MindMemoryCubeV2 初始化时
self.mind_cube = MindMemoryCubeV2(
    ai_profile=self.mind_profile,
    user_profile=None,
    storage=self.storage,
    emotion_memory_boost=1.5  # 情绪对记忆的增强系数（默认 1.3）
)
```

### 6.3 启用遗忘机制

在 `Agent.reflect` 方法中添加：

```python
def reflect(self):
    # ... 原有逻辑 ...
    
    # 每次反思时运行遗忘循环
    self.mind.run_forgetting_cycle()
```

---

## 七、调试技巧

### 7.1 打印情绪状态

在 `agent.py` 的 `think` 方法中添加：

```python
emotion = self.mind.get_emotion_state()
self.logger.info(f"{self.name} emotion: {emotion}")
```

### 7.2 查看记忆数据库

```bash
sqlite3 /path/to/agent.db
.tables
SELECT * FROM memories LIMIT 10;
```

### 7.3 启用详细日志

编辑 `start.py`：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 八、下一步

恭喜！您已成功整合 MemOS-Mind 到 GenerativeAgentsCN。接下来可以：

1. **实验不同性格组合**：观察性格对行为的影响。
2. **分析情绪演化**：记录智能体的情绪变化曲线。
3. **实现情绪传染**：让智能体之间的情绪互相影响。
4. **可视化情绪**：在前端界面中用颜色表示情绪状态。

---

**祝您探索愉快！**
