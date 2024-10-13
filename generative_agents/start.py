import os
import copy
import json
import argparse
import datetime

from dotenv import load_dotenv, find_dotenv

from modules.game import create_game, get_game
from modules import utils

personas = [
    "阿伊莎", "克劳斯", "玛丽亚", "沃尔夫冈",  # 学生
    "梅", "约翰", "埃迪",  # 家庭：教授、药店主人、学生
    "简", "汤姆",  # 家庭：家庭主妇、市场主人
    "卡门", "塔玛拉",  # 室友：供应店主人、儿童读物作家
    "亚瑟", "伊莎贝拉",  # 酒吧老板、咖啡馆老板
    "山姆", "詹妮弗",  # 家庭：退役军官、水彩画家
    "弗朗西斯科", "海莉", "拉吉夫", "拉托亚",  # 共居空间：喜剧演员、作家、画家、摄影师
    "阿比盖尔", "卡洛斯", "乔治", "瑞恩", "山本百合子", "亚当",  # 动画师、诗人、数学家、软件工程师、税务律师、哲学家
]


class SimulateServer:
    def __init__(self, name, static_root, checkpoints_folder, config, start_step=0, verbose="info", log_file=""):
        self.name = name
        self.static_root = static_root
        self.checkpoints_folder = checkpoints_folder

        # 历史存档数据（用于断点恢复）
        self.config = config

        os.makedirs(checkpoints_folder, exist_ok=True)

        # 载入历史对话数据（用于断点恢复）
        self.conversation_log = f"{checkpoints_folder}/conversation.json"
        if os.path.exists(self.conversation_log):
            with open(self.conversation_log, "r", encoding="utf-8") as f:
                conversation = json.load(f)
        else:
            conversation = {}

        if len(log_file) > 0:
            self.logger = utils.create_file_logger(f"{checkpoints_folder}/{log_file}", verbose)
        else:
            self.logger = utils.create_io_logger(verbose)

        # 创建游戏
        game = create_game(name, static_root, config, conversation, logger=self.logger)
        game.reset_game(keys=config["api_keys"])

        self.game = get_game()
        self.tile_size = self.game.maze.tile_size
        self.agent_status = {}
        if "agent_base" in config:
            agent_base = config["agent_base"]
        else:
            agent_base = {}
        for agent_name, agent in config["agents"].items():
            agent_config = copy.deepcopy(agent_base)
            agent_config.update(self.load_static(agent["config_path"]))
            self.agent_status[agent_name] = {
                "coord": agent_config["coord"],
                "path": [],
            }
        self.think_interval = max(
            a.think_config["interval"] for a in self.game.agents.values()
        )
        self.start_step = start_step

    def simulate(self, step, stride=0):
        timer = utils.get_timer()
        for i in range(self.start_step, self.start_step + step):
            title = "Simulate Step[{}/{}, time: {}]".format(i+1, self.start_step + step, timer.get_date())
            self.logger.info("\n" + utils.split_line(title, "="))
            for name, status in self.agent_status.items():
                plan = self.game.agent_think(name, status)["plan"]
                agent = self.game.get_agent(name)
                if name not in self.config["agents"]:
                    self.config["agents"][name] = {}
                self.config["agents"][name].update(agent.to_dict())
                if plan.get("path"):
                    status["coord"], status["path"] = plan["path"][-1], []
                self.config["agents"][name].update(
                    # {"coord": status["coord"], "path": plan["path"]}
                    {"coord": status["coord"]}
                )

            sim_time = timer.get_date("%Y%m%d-%H:%M")
            self.config.update(
                {
                    "time": sim_time,
                    "step": i + 1,
                }
            )
            # 保存Agent活动数据
            with open(f"{self.checkpoints_folder}/simulate-{sim_time.replace(':', '')}.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.config, indent=2, ensure_ascii=False))
            # 保存对话数据
            with open(f"{self.checkpoints_folder}/conversation.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.game.conversation, indent=2, ensure_ascii=False))

            if stride > 0:
                timer.forward(stride)

    def load_static(self, path):
        return utils.load_dict(os.path.join(self.static_root, path))


# 从存档数据总载入配置，用于断点恢复
def get_config_from_log(checkpoints_folder):
    files = sorted(os.listdir(checkpoints_folder))

    json_files = list()
    for file_name in files:
        if file_name.endswith(".json") and file_name != "conversation.json":
            json_files.append(os.path.join(checkpoints_folder, file_name))

    if len(json_files) < 1:
        return None

    with open(json_files[-1], "r", encoding="utf-8") as f:
        config = json.load(f)

    assets_root = os.path.join("assets", "village")

    start_time = datetime.datetime.strptime(config["time"], "%Y%m%d-%H:%M")
    start_time += datetime.timedelta(minutes=config["stride"])
    config["time"] = {"start": start_time.strftime("%Y%m%d-%H:%M")}
    agents = config["agents"]
    for a in agents:
        config["agents"][a]["config_path"] = os.path.join(assets_root, "agents", a.replace(" ", "_"), "agent.json")

    return config


# 为新游戏创建配置
def get_config(start_time="20240213-09:30", stride=15, agents=None):
    with open("data/config.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        agent_config = json_data["agent"]

    assets_root = os.path.join("assets", "village")
    config = {
        "stride": stride,
        "time": {"start": start_time},
        "maze": {"path": os.path.join(assets_root, "maze.json")},
        "agent_base": agent_config,
        "agents": {},
        "api_keys": json_data["api_keys"],
    }
    for a in agents:
        config["agents"][a] = {
            "config_path": os.path.join(
                assets_root, "agents", a.replace(" ", "_"), "agent.json"
            ),
        }
    return config


load_dotenv(find_dotenv())

parser = argparse.ArgumentParser(description="console for village")
parser.add_argument("--name", type=str, default="", help="The simulation name")
parser.add_argument("--start", type=str, default="20240213-09:30", help="The starting time of the simulated ville")
parser.add_argument("--resume", action="store_true", help="Resume running the simulation")
parser.add_argument("--step", type=int, default=10, help="The simulate step")
parser.add_argument("--stride", type=int, default=10, help="The step stride in minute")
parser.add_argument("--verbose", type=str, default="debug", help="The verbose level")
parser.add_argument("--log", type=str, default="", help="Name of the log file")
args = parser.parse_args()


if __name__ == "__main__":
    checkpoints_path = "results/checkpoints"

    name = args.name
    if len(name) < 1:
        name = input("Please enter a simulation name (e.g. sim-test): ")

    resume = args.resume
    if resume:
        while not os.path.exists(f"{checkpoints_path}/{name}"):
            name = input(f"'{name}' doesn't exists, please re-enter the simulation name: ")
    else:
        while os.path.exists(f"{checkpoints_path}/{name}"):
            name = input(f"The name '{name}' already exists, please enter a new name: ")

    checkpoints_folder = f"{checkpoints_path}/{name}"

    start_time = args.start
    if resume:
        sim_config = get_config_from_log(checkpoints_folder)
        if sim_config is None:
            print("No checkpoint file found to resume running.")
            exit(0)
        start_step = sim_config["step"]
    else:
        sim_config = get_config(start_time, args.stride, personas)
        start_step = 0

    static_root = "frontend/static"

    server = SimulateServer(name, static_root, checkpoints_folder, sim_config, start_step, args.verbose, args.log)
    server.simulate(args.step, args.stride)
