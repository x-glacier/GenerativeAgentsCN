[简体中文](./README.md) | English

# Generative Agents Chinesized

## 1. Configure the environment

### 1.1 pull the source code:

```
git clone https://github.com/x-glacier/GenerativeAgentsCN.git
cd GenerativeAgentsCN
```

### 1.2 configure the large language model

Modify the configuration file `generative_agents/data/config.json`:
1. By default, [Ollama](https://ollama.com/) is used to load local quantization models and OpenAI compatible APIs are provided. We need to first pull the quantization model and ensure that `base_url` and `model` are consistent with the actual configuration of Ollama.
2. If you want to call other APIs, fill in the relevant keys in `api_keys` and modify `base_url` and `model` to the correct values.

### 1.3 install python dependencies

Use a virtual environment, e.g. with anaconda3:

```
conda create -n generative_agents_cn python=3.11
conda activate generative_agents_cn
```

Install dependencies:

```
pip install -r requirements.txt
```

## 2. Start a simulation

```
cd generative_agents
python start.py --name sim-test --start "20240213-09:30" --step 10 --stride 10
```

arguments:
- `name` - the name of the simulation
- `start` - the starting time of the simulated ville
- `resume` - resume running the simulation
- `step` - how many steps to simulate
- `stride` - how many minutes to forward after each step, e.g. 9:00->9:10->9:20 if stride=10

## 3. Replay a simulation

### 3.1 generate replay data

```
python compress.py --name <simulation-name>
```

After running, the replay data file `movement.json` will be generated in the `results/compressed/<simulation-name>` folder. At the same time, `simulation.md` will be generated to present the status and conversation of each agent in a timeline.

### 3.2 start the replay server

```
python replay.py
```

Visit the server in browser (url: `http://127.0.0.1:5000/?name=<simulation-name>`),  you'll see agents walking around on time.

arguments:  
- `name` - the name of the simulation
- `step` - the starting step of the simulated ville (greater than 0)
- `speed` - replay speed (0-5)
- `zoom` - zoom ratio (e.g. 0.8)

For example, if the simulation name is `sim-test`, the url can be:
http://127.0.0.1:5000/?name=sim-test&step=0&speed=2&zoom=0.6

## 4. Reference

### 4.1 paper

[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)

### 4.2 gitHub repository

[Generative Agents](https://github.com/joonspk-research/generative_agents)

[wounderland](https://github.com/Archermmt/wounderland)
