# 青石镇：一个深度中国化的生成式智能体模拟世界

简体中文 | [English](./README_en.md)

**青石镇** 是一个基于斯坦福大学和谷歌开源的 [Generative Agents](https://arxiv.org/abs/2304.03442) 项目的深度中国化版本。我们对原项目进行了全面的重构和文化本地化，将一个西方的虚拟小镇转变为一个充满中国文化气息的模拟世界。在这里，25 位由大型语言模型（LLM）驱动的 AI 智能体拥有了全新的中国化身份、情感、记忆和人际关系，在一个名为“青石镇”的虚拟环境中生活、工作和互动。

这个项目不仅是对 Generative Agents 的简单汉化，更是一次深入的文化移植和技术增强。我们引入了 **memos-mind** 情感记忆系统，赋予了每个智能体更丰富的内心世界和更真实的行为模式。

![青石镇全景](docs/resources/qingshi_town_overview.png)
*（上图为青石镇的概念图，展示了茶馆、公园、市集等核心场景）*

## 核心特性

- **深度文化本地化**：所有场景、角色、对话和行为模式都经过了精心的中国化设计，用“青石茶馆”取代了咖啡馆，用“柳树市集”取代了药店，让智能体的互动更符合中国文化语境。
- **memos-mind 情感记忆系统**：集成了先进的情感与记忆模块，包括：
  - **PAD 情感空间**：使用三维情感模型（Pleasure-Arousal-Dominance）来动态追踪每个智能体的情感状态。
  - **情感记忆**：将事件与情感关联，形成长期记忆，影响未来的决策和行为。
  - **上帝之眼**：通过 SQLite 数据库记录所有智能体的心理状态、互动和关系演化，为研究提供丰富的数据支持。
- **动态关系演化**：智能体之间的关系不再是静态的，而是会根据互动和共同经历动态演化，形成亲情、友情、爱情等复杂的社交网络。
- **中国文化维度**：在智能体的行为模型中融入了“面子”、“人情”、“集体主义”等中国特有的文化维度，使其行为更具真实感。
- **完整的技术栈**：项目代码基于 [wounderland](https://github.com/Archermmt/wounderland) 进行了重构，并修复了多个 bug，支持使用本地 LLM（如 Ollama + Qwen）进行部署，大大降低了实验成本。

## 青石镇的世界

青石镇是一个典型的中国小镇，拥有茶馆、小酒馆、市集、公园、学校等丰富的场景。25 位智能体在这里生活，他们有各自的职业、家庭和社交圈。

### 主要场景

| 原始场景 | 青石镇场景 | 描述 |
| :--- | :--- | :--- |
| Hobbs Cafe | 青石茶馆 | 居民们喝茶、聊天、交换信息的主要场所。 |
| The Rose and Crown Pub | 桂花小酒馆 | 提供传统酒水和社交氛围的晚间娱乐场所。 |
| Oak Hill College | 青石中学 | 镇上的中学，是年轻智能体学习和成长的地方。 |
| Johnson Park | 青石公园 | 居民们晨练、下棋、跳广场舞的公共空间。 |
| Willow Market and Pharmacy | 柳树市集 | 售卖新鲜食材、中药材和日常用品的传统集市。 |

### 角色示例

每个角色都拥有详细的背景故事、人格特质（Big Five）、价值观（Schwartz）和中国文化特质。

| 姓名 | 职业 | 简介 |
| :--- | :--- | :--- |
| 李建国 | 青石茶馆老板 | 一位沉稳、见多识广的退伍军人，喜欢在茶馆里观察社会百态。 |
| 王浩 | 桂花小酒馆调酒师 | 一个充满激情和创造力的年轻人，梦想着调制出代表青石镇的鸡尾酒。 |
| 张伟 | 青石中学历史老师 | 对历史充满热情，致力于将枯燥的知识变得生动有趣。 |
| 苏晴 | 花店老板 | 一个热爱生活、对美有独特见解的年轻女性。 |
| 马强 | 快递员 | 对小镇的每一条街道都了如指掌，是连接整个小镇信息和物流的纽带。 |

## 技术实现

我们对原项目进行了大量的技术改进和 bug 修复，主要包括：

- **代码重构**：全面审查和重构了核心代码，提高了可读性和可维护性。
- **Bug 修复**：解决了包括 `Event.describe`、`prompt_poignancy`、`utils.get_uuid`、`Concept.from_event` 和 `Associate.add_concept` 在内的多个关键 bug。
- **本地化部署**：增加了对 Ollama 的支持，可以完全使用本地 LLM 和嵌入模型，无需依赖昂贵的 API。
- **前端可视化**：保留并优化了前端回放功能，可以直观地观察智能体的活动轨迹和互动过程。

## 如何开始

### 1. 准备工作

**获取代码**
```bash
git clone https://github.com/sxhfut/GenerativeAgentsCN-Mind.git
cd GenerativeAgentsCN-Mind
```

**安装依赖**
```bash
pip install -r requirements.txt
```

**配置 LLM**

修改 `generative_agents/data/config.json` 文件，配置您希望使用的语言模型。默认配置为使用 OpenAI API，您也可以修改为使用本地 Ollama。

### 2. 运行模拟

我们提供了一个专为青石镇优化的启动脚本 `start_qingshi.py`。

```bash
cd generative_agents
python3.11 start_qingshi.py --name qingshi-test --step 10
```

- `name`：为本次模拟设定一个唯一的名称。
- `step`：模拟运行的步数。

### 3. 查看结果与回放

**压缩数据**
```bash
python3.11 compress.py --name qingshi-test
```

**启动回放服务器**
```bash
python3.11 replay.py
```

然后打开浏览器访问 `http://127.0.0.1:5000/?name=qingshi-test` 即可看到青石镇的可视化回放。

## 贡献与致谢

本项目基于 [wounderland](https://github.com/Archermmt/wounderland) 和原始的 [Generative Agents](https://github.com/joonspk-research/generative_agents) 项目开发。感谢原作者的开创性工作。

我们也欢迎社区的贡献，如果您有任何建议或发现了 bug，请随时提交 issue 或 pull request。
