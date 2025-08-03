简体中文 | [English](./README_en.md)

# 生成式智能体（Generative Agents）深度汉化版

斯坦福AI小镇由斯坦福大学和谷歌于2023年8月开源，由25个智能体组成的虚拟世界，模拟了真实的人类生活。

25个智能体完全由ChatGPT驱动，自主组织派对、参加会议、在情人节筹办各种活动。他们能够展现出与人类相似的生活模式和行为习惯。

Generative Agents的原始代码工程化程度较低，难以持续维护或拓展功能，且时隔两年，中文LLM的能力早已胜任此类任务。因此，我们对原项目进行了重构+深度汉化，旨在为中文用户提供一个利于维护的基础版本，以便后续实验或尝试更多玩法。

[wounderland](https://github.com/Archermmt/wounderland)项目是原[Generative Agents](https://github.com/joonspk-research/generative_agents)项目的重构版本，结构良好且代码质量远优于原版，因此本项目基于wounderland开发。

更新：

- 2025.06.02：增加对Qwen3和DeepSeek-R1等新模型的支持（处理输出结果中的\<think\>标签）。

主要工作：

- 重写全部提示语，将智能体的“母语”切换为中文，以便对接Qwen或GLM-4等中文模型；
- 针对中文特点和Qwen2.5/3系列模型的能力，优化中文提示语及智能体之间的对话起止逻辑；
- 所有提示语模板化，便于后期维护；
- 修正原版的小问题（例如wounderland原版中智能体在入睡后便不再醒来）；
- 增加对本地Ollama API的支持，同时将LlamaIndex embedding也接入Ollama，实现完全本地部署，降低实验成本。*Ollama安装及配置可参考[ollama.md](docs/ollama.md)*；
- 增加“断点恢复”等特性；
- 回放界面基于原Generative Agents前端代码精简，同时将智能体活动的时间线及对话内容保存至Markdown文档。

回放画面：

![snapshot](docs/resources/snapshot.png)

*注：地图及人物名称也同步汉化，是为了避免LLM在遇到中英混杂的上下文时，切换到英文语境。*

## 1. 准备工作

### 1.1 获取代码：

```
git clone https://github.com/x-glacier/GenerativeAgentsCN.git
cd GenerativeAgentsCN
```

### 1.2 配置大语言模型（LLM）

修改配置文件 `generative_agents/data/config.json`:
1. 默认使用[Ollama](https://ollama.com/)加载本地量化模型，并提供OpenAI兼容API。需要先拉取量化模型（参考[ollama.md](docs/ollama.md)），并确保`base_url`和`model`与Ollama中的配置一致。
2. 如果希望调用其他OpenAI兼容API，需要将`provider`改为`openai`，并根据API文档修改`model`、`api_key`和`base_url`。

### 1.3 安装python依赖

建议先使用anaconda3创建并激活虚拟环境：

```
conda create -n generative_agents_cn python=3.12
conda activate generative_agents_cn
```

安装依赖：

```
pip install -r requirements.txt
```

## 2. 运行虚拟小镇

```
cd generative_agents
python start.py --name sim-test --start "20250213-09:30" --step 10 --stride 10
```

参数说明:
- `name` - 每次启动虚拟小镇，需要设定唯一的名称，用于事后回放。
- `start` - 虚拟小镇的起始时间。
- `resume` - 在运行结束或意外中断后，从上次的“断点”处，继续运行虚拟小镇。
- `step` - 在迭代多少步之后停止运行。
- `stride` - 每一步迭代在虚拟小镇中对应的时间（分钟）。假如设定`--stride 10`，虚拟小镇在迭代过程中的时间变化将会是 9:00，9:10，9:20 ...

## 3. 回放

### 3.1 生成回放数据

```
python compress.py --name <simulation-name>
```

运行结束后将在`results/compressed/<simulation-name>`目录下生成回放数据文件`movement.json`。同时还将生成`simulation.md`，以时间线方式呈现每个智能体的状态及对话内容。

### 3.2 启动回放服务

```
python replay.py
```

通过浏览器打开回放页面（地址：`http://127.0.0.1:5000/?name=<simulation-name>`），可以看到虚拟小镇中的居民在各个时间段的活动。

*可通过方向键移动画面*

参数说明  
- `name` - 启动虚拟小镇时设定的名称。
- `step` - 回放的起始步数，0代表从第一帧开始回放，预设值为0。
- `speed` - 回放速度（0-5），0最慢，5最快，预设值为2。
- `zoom` - 画面缩放比例，预设值为0.8。

发布版本中内置了名为`example`的回放数据（由qwen2.5:32b-instruct-q4_K_M生成）。若希望以较快速度从头开始回放，画面缩放比例为0.6，则对应的url是：
http://127.0.0.1:5000/?name=example&step=0&speed=2&zoom=0.6

也可直接打开[simulation.md](generative_agents/results/compressed/example/simulation.md)，查看`example`中所有人物活动和对话信息。

### 3.3 回放截图

*画面中对话内容由qwen2.5:14b-instruct-q4_K_M生成*

小镇全景

![小镇全景](docs/resources/snapshot1.gif)

公园

![公园](docs/resources/snapshot2.gif)

咖啡馆

![咖啡馆](docs/resources/snapshot3.gif)

教室

![教室](docs/resources/snapshot4.gif)

## 4. 修改地图

由于wounderland项目原作者没有提供maze.json的生成代码，所以想要创建新地图，有以下几种方案：

1. 参考原始generative_agents项目中maze.py的逻辑，修改现有代码，以便兼容tiled编辑器导出的json和csv数据文件；
2. 参考现有的maze.json格式，编写代码用于合并tiled编辑器导出的maze_meta_info.json、collision_maze.csv、sector_maze.csv等文件，为新地图生成maze.json。
3. `jiejieje`已为本项目开发了一款地图标注工具，项目地址：https://github.com/jiejieje/tiled_to_maze.json

## 5. 参考资料

### 5.1 论文

[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)

### 5.2 代码

[Generative Agents](https://github.com/joonspk-research/generative_agents)

[wounderland](https://github.com/Archermmt/wounderland)
