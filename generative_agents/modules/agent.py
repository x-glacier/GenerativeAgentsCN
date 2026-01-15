"""generative_agents.agent"""

import os
import math
import random
import datetime

from modules import memory, prompt, utils
from modules.model.llm_model import create_llm_model
from modules.memory.associate import Concept
from generative_agents.modules.mind_adapter import AgentMindAdapter
from generative_agents.modules.observers.gods_eye_system import get_gods_eye_system
from generative_agents.modules.relationship_manager import RelationshipManager


class Agent:
    def __init__(self, config, maze, conversation, logger):
        self.name = config["name"]
        self.maze = maze
        self.conversation = conversation
        self._llm = None
        self.logger = logger

        # 初始化心智适配器（简化版）
        db_dir = os.path.join(config["storage_root"], "mind_db")
        os.makedirs(db_dir, exist_ok=True)
        db_file = os.path.join(db_dir, f"{self.name}.db")
        self.mind = AgentMindAdapter(self.name, config, db_path=db_file)
        
        # 初始化上帝视角系统（全局单例）
        gods_eye_db = os.path.join(config["storage_root"], "evolution.db")
        self.gods_eye = get_gods_eye_system(db_path=gods_eye_db, enable_db=True)
        
        # 初始化关系管理器
        rel_config_path = os.path.join(config["storage_root"], f"{self.name}_relationships.json")
        self.relationships = RelationshipManager(self.name, rel_config_path if os.path.exists(rel_config_path) else None)

        # agent config
        self.percept_config = config["percept"]
        self.think_config = config["think"]
        self.chat_iter = config["chat_iter"]

        # memory
        self.spatial = memory.Spatial(**config["spatial"])
        self.schedule = memory.Schedule(**config["schedule"])
        self.associate = memory.Associate(
            os.path.join(config["storage_root"], "associate"), **config["associate"]
        )
        self.concepts, self.chats = [], config.get("chats", [])

        # prompt
        self.scratch = prompt.Scratch(self.name, config["currently"], config["scratch"])

        # status
        status = {"poignancy": 0}
        self.status = utils.update_dict(status, config.get("status", {}))
        self.plan = config.get("plan", {})

        # record
        self.last_record = utils.get_timer().daily_duration()

        # action and events
        if "action" in config:
            self.action = memory.Action.from_dict(config["action"])
            tiles = self.maze.get_address_tiles(self.get_event().address)
            config["coord"] = random.choice(list(tiles))
        else:
            tile = self.maze.tile_at(config["coord"])
            address = tile.get_address("game_object", as_list=True)
            self.action = memory.Action(
                memory.Event(self.name, address=address),
                memory.Event(address[-1], address=address),
            )

        # update maze
        self.coord, self.path = None, None
        self.move(config["coord"], config.get("path"))
        if self.coord is None:
            self.coord = config["coord"]

    def abstract(self):
        des = {
            "name": self.name,
            "currently": self.scratch.currently,
            "tile": self.maze.tile_at(self.coord).abstract(),
            "status": self.status,
            "concepts": {c.node_id: c.abstract() for c in self.concepts},
            "chats": self.chats,
            "action": self.action.abstract(),
            "associate": self.associate.abstract(),
            "emotion": self.mind.get_emotion_state() # 新增：暴露情绪状态
        }
        if self.schedule.scheduled():
            des["schedule"] = self.schedule.abstract()
        if self.llm_available():
            des["llm"] = self._llm.get_summary()
        return des

    def __str__(self):
        return utils.dump_dict(self.abstract())

    def reset(self):
        if not self._llm:
            self._llm = create_llm_model(self.think_config["llm"])

    def completion(self, func_hint, *args, **kwargs):
        assert hasattr(
            self.scratch, "prompt_" + func_hint
        ), "Can not find func prompt_{} from scratch".format(func_hint)
        func = getattr(self.scratch, "prompt_" + func_hint)
        res = func(*args, **kwargs)._asdict()
        title, msg = "{}.{}".format(self.name, func_hint), {}
        if self.llm_available():
            self.logger.info("{} -> {}".format(self.name, func_hint))
            output = self._llm.completion(**res)
            msg = {"<PROMPT>": "\n" + res["prompt"] + "\n"}
            msg.update({"response": output})
        self.logger.debug(utils.block_msg(title, msg))
        return output

    def think(self, status, agents):
        move_events = self.move(status["coord"], status.get("path"))
        # 更新情绪：处理移动产生的事件
        for event in move_events.keys():
            self.mind.process_event(event)
        # 更新情绪：自然衰减
        self.mind.update_emotion_decay(delta_time=1.0)
        events = move_events
        
        plan, _ = self.make_schedule()

        if (plan["describe"] == "sleeping" or "睡" in plan["describe"]) and self.is_awake():
            self.logger.info("{} is going to sleep...".format(self.name))
            address = self.spatial.find_address("睡觉", as_list=True)
            tiles = self.maze.get_address_tiles(address)
            coord = random.choice(list(tiles))
            events = self.move(coord)
            self.action = memory.Action(
                memory.Event(self.name, "正在", "睡觉", address=address, emoji="😴"),
                memory.Event(
                    address[-1],
                    "被占用",
                    self.name,
                    address=address,
                    emoji="🛌",
                ),
                duration=plan["duration"],
                start=utils.get_timer().daily_time(plan["start"]),
            )
        if self.is_awake():
            observed_concepts = self.percept()
            # 更新情绪：处理感知到的事件 (concept.event)
            for concept in observed_concepts:
                self.mind.process_event(concept.event)

            self.make_plan(agents)
            self.reflect()
        else:
            if self.action.finished():
                self.action = self._determine_action()

        emojis = {}
        if self.action:
            emojis[self.name] = {"emoji": self.get_event().emoji, "coord": self.coord}
        for eve, coord in events.items():
            if eve.subject in agents:
                continue
            emojis[":".join(eve.address)] = {"emoji": eve.emoji, "coord": coord}
        self.plan = {
            "name": self.name,
            "path": self.find_path(agents),
            "emojis": emojis,
        }
        
        # 记录心智状态到上帝视角系统
        emotion = self.mind.get_emotion_state()
        personality = self.mind.get_personality()
        self.gods_eye.log_mind_state(
            agent_name=self.name,
            emotion=emotion,
            personality=personality,
            current_activity=self.scratch.currently,
            location=str(self.coord)
        )
        
        return self.plan

    def move(self, coord, path=None):
        events = {}

        def _update_tile(coord):
            tile = self.maze.tile_at(coord)
            if not self.action:
                return {}
            if not tile.update_events(self.get_event()):
                tile.add_event(self.get_event())
            obj_event = self.get_event(False)
            if obj_event:
                self.maze.update_obj(coord, obj_event)
            return {e: coord for e in tile.get_events()}

        if self.coord and self.coord != coord:
            tile = self.get_tile()
            tile.remove_events(subject=self.name)
            if tile.has_address("game_object"):
                addr = tile.get_address("game_object")
                self.maze.update_obj(
                    self.coord, memory.Event(addr[-1], address=addr)
                )
            events.update({e: self.coord for e in tile.get_events()})
        if not path:
            events.update(_update_tile(coord))
        self.coord = coord
        self.path = path or []

        return events

    def make_schedule(self):
        if not self.schedule.scheduled():
            self.logger.info("{} is making schedule...".format(self.name))
            # update currently
            if self.associate.index.nodes_num > 0:
                self.associate.cleanup_index()
                focus = [
                    f"{self.name} 在 {utils.get_timer().daily_format_cn()} 的计划。",
                    f"在 {self.name} 的生活中，重要的近期事件。",
                ]
                retrieved = self.associate.retrieve_focus(focus)
                self.logger.info(
                    "{} retrieved {} concepts".format(self.name, len(retrieved))
                )
                if retrieved:
                    plan = self.completion("retrieve_plan", retrieved)
                    thought = self.completion("retrieve_thought", retrieved)
                    self.scratch.currently = self.completion(
                        "retrieve_currently", plan, thought
                    )
            # make init schedule
            self.schedule.create = utils.get_timer().get_date()
            wake_up = self.completion("wake_up")
            init_schedule = self.completion("schedule_init", wake_up)
            # make daily schedule
            hours = [f"{i}:00" for i in range(24)]
            seed = [(h, "睡觉") for h in hours[:wake_up]]
            seed += [(h, "") for h in hours[wake_up:]]
            schedule = {}
            for _ in range(self.schedule.max_try):
                schedule = {h: s for h, s in seed[:wake_up]}
                schedule.update(
                    self.completion("schedule_daily", wake_up, init_schedule)
                )
                if len(set(schedule.values())) >= self.schedule.diversity:
                    break

            def _to_duration(date_str):
                return utils.daily_duration(utils.to_date(date_str, "%H:%M"))

            schedule = {_to_duration(k): v for k, v in schedule.items()}
            starts = list(sorted(schedule.keys()))
            for idx, start in enumerate(starts):
                end = starts[idx + 1] if idx + 1 < len(starts) else 24 * 60
                self.schedule.add_plan(schedule[start], end - start)
            schedule_time = utils.get_timer().time_format_cn(self.schedule.create)
            thought = "这是 {} 在 {} 的计划：{}".format(
                self.name, schedule_time, "；".join(init_schedule)
            )
            event = memory.Event(
                self.name,
                "计划",
                schedule_time,
                describe=thought,
                address=self.get_tile().get_address(),
            )
            self._add_concept(
                "thought",
                event,
                expire=self.schedule.create + datetime.timedelta(days=30),
            )
        # decompose current plan
        plan, _ = self.schedule.current_plan()
        if self.schedule.decompose(plan):
            decompose_schedule = self.completion(
                "schedule_decompose", plan, self.schedule
            )
            decompose, start = [], plan["start"]
            for describe, duration in decompose_schedule:
                decompose.append(
                    {
                        "idx": len(decompose),
                        "describe": describe,
                        "start": start,
                        "duration": duration,
                    }
                )
                start += duration
            plan["decompose"] = decompose
        return self.schedule.current_plan()

    def revise_schedule(self, event, start, duration):
        self.action = memory.Action(event, start=start, duration=duration)
        plan, _ = self.schedule.current_plan()
        if len(plan["decompose"]) > 0:
            plan["decompose"] = self.completion(
                "schedule_revise", self.action, self.schedule
            )

    def percept(self):
        scope = self.maze.get_scope(self.coord, self.percept_config)
        # add spatial memory
        for tile in scope:
            if tile.has_address("game_object"):
                self.spatial.add_leaf(tile.address)
        events, arena = {}, self.get_tile().get_address("arena")
        # gather events in scope
        for tile in scope:
            if not tile.events or tile.get_address("arena") != arena:
                continue
            dist = math.dist(tile.coord, self.coord)
            for event in tile.get_events():
                if dist < events.get(event, float("inf")):
                    events[event] = dist
        events = list(sorted(events.keys(), key=lambda k: events[k]))
        # get concepts
        self.concepts, valid_num = [], 0
        for idx, event in enumerate(events[: self.percept_config["att_bandwidth"]]):
            recent_nodes = (
                self.associate.retrieve_events() + self.associate.retrieve_chats()
            )
            recent_nodes = set(n.describe for n in recent_nodes)
            if event.get_describe() not in recent_nodes:
                if event.object == "idle" or event.object == "空闲":
                    node = Concept.from_event(
                        "idle_" + str(idx), "event", event, poignancy=1
                    )
                else:
                    valid_num += 1
                    node_type = "chat" if event.fit(self.name, "对话") else "event"
                    node = self._add_concept(node_type, event)
                    self.status["poignancy"] += node.poignancy
                self.concepts.append(node)
        self.concepts = [c for c in self.concepts if c.event.subject != self.name]
        self.logger.info(
            "{} percept {}/{} concepts".format(self.name, valid_num, len(self.concepts))
        )
        return self.concepts

    def make_plan(self, agents):
        if self._reaction(agents):
            return
        if self.path:
            return
        if self.action.finished():
            self.action = self._determine_action()

    def make_event(self, subject, describe, address, emotion=None):
        e_describe = describe.replace("(", "").replace(")", "").replace("<", "").replace(">", "")
        if e_describe.startswith(subject + "此时"):
            e_describe = e_describe[len(subject + "此时"):]
        if e_describe.startswith(subject):
            e_describe = e_describe[len(subject):]
        event = memory.Event(
            subject, "此时", e_describe, describe=describe, address=address,
            emotion=emotion  # 支持传入情绪信息
        )
        return event

    def reflect(self):
        def _add_thought(thought, evidence=None):
            event = self.make_event(self.name, thought, self.get_tile().get_address())
            return self._add_concept("thought", event, filling=evidence)

        if self.status["poignancy"] < self.think_config["poignancy_max"]:
            return
        nodes = self.associate.retrieve_events() + self.associate.retrieve_thoughts()
        if not nodes:
            return
        self.logger.info(
            "{} reflect(P{}/{}) with {} concepts...".format(
                self.name,
                self.status["poignancy"],
                self.think_config["poignancy_max"],
                len(nodes),
            )
        )
        nodes = sorted(nodes, key=lambda n: n.access, reverse=True)[
            : self.associate.max_importance
        ]
        # summary thought
        focus = self.completion("reflect_focus", nodes, 3)
        retrieved = self.associate.retrieve_focus(focus, reduce_all=False)
        for r_nodes in retrieved.values():
            thoughts = self.completion("reflect_insights", r_nodes, 5)
            for thought, evidence in thoughts:
                _add_thought(thought, evidence)
        # summary chats
        if self.chats:
            recorded, evidence = set(), []
            for name, _ in self.chats:
                if name == self.name or name in recorded:
                    continue
                res = self.associate.retrieve_chats(name)
                if res and len(res) > 0:
                    node = res[-1]
                    evidence.append(node.node_id)
            thought = self.completion("reflect_chat_planing", self.chats)
            _add_thought(f"对于 {self.name} 的计划：{thought}", evidence)
            thought = self.completion("reflect_chat_memory", self.chats)
            _add_thought(f"{self.name} {thought}", evidence)
        self.status["poignancy"] = 0
        self.chats = []

    def find_path(self, agents):
        address = self.get_event().address
        if self.path:
            return self.path
        if address == self.get_tile().get_address():
            return []
        if address[0] == "<waiting>":
            return []
        if address[0] == "<persona>":
            target_tiles = self.maze.get_around(agents[address[1]].coord)
        else:
            target_tiles = self.maze.get_address_tiles(address)
        if tuple(self.coord) in target_tiles:
            return []

        def _ignore_target(t_coord):
            if list(t_coord) == list(self.coord):
                return True
            events = self.maze.tile_at(t_coord).get_events()
            if any(e.subject in agents for e in events):
                return True
            return False

        target_tiles = [t for t in target_tiles if not _ignore_target(t)]
        if not target_tiles:
            return []
        paths = self.maze.find_path(self.coord, target_tiles)
        if not paths:
            return []
        return list(paths[0])

    def get_tile(self):
        return self.maze.tile_at(self.coord)

    def get_event(self, is_agent=True):
        return self.action.agent_event if is_agent else self.action.object_event

    def is_awake(self):
        return self.action.is_awake()

    def add_chat(self, name, text, speaker_emotion=None):
        # 创建事件时附带说话者的情绪
        event = self.make_event(name, text, self.get_tile().get_address(), emotion=speaker_emotion)
        # 关键修复：让心智模块处理收到的消息，产生情感反应
        # 上下文中包含对方的情绪状态
        context = f"收到 {name} 的消息"
        if speaker_emotion:
            context += f"，{name} 的情绪状态：Pleasure={speaker_emotion.get('pleasure', 0):.2f}, Arousal={speaker_emotion.get('arousal', 0):.2f}"
        # 获取自己处理前后的情绪状态
        my_emotion_before = self.mind.get_emotion_state()
        self.mind.process_event(event, context=context)
        my_emotion_after = self.mind.get_emotion_state()
        
        self._add_concept("chat", event)
        self.chats.append((name, text))
        
        # 记录交互到上帝视角系统
        self.gods_eye.log_interaction(
            interaction_type="dialogue",
            speaker=name,
            listener=self.name,
            content=text,
            speaker_state={
                "real_emotion": speaker_emotion or {},
                "activity": ""
            },
            listener_state={
                "perceived_emotion": speaker_emotion or {},
                "my_emotion_before": my_emotion_before,
                "my_emotion_after": my_emotion_after
            },
            location=str(self.coord)
        )
        
        # 更新关系
        emotion_change = my_emotion_after.get('pleasure', 0) - my_emotion_before.get('pleasure', 0)
        interaction_positive = emotion_change > 0
        rel_changes = self.relationships.update_relationship(
            other_name=name,
            interaction_positive=interaction_positive,
            interaction_intensity=abs(emotion_change) if emotion_change != 0 else 0.5
        )
        
        # 记录关系变化
        rel = self.relationships.get_relationship(name)
        self.gods_eye.log_relationship(
            agent_a=self.name,
            agent_b=name,
            a_to_b={
                "affection": rel.affection,
                "trust": rel.trust,
                "intimacy": rel.intimacy,
                "impression": rel.overall_impression
            },
            kinship=rel.kinship,
            social=rel.social
        )

    def _add_concept(self, node_type, event, poignancy=None, filling=None, expire=None):
        if poignancy is None:
            poignancy = self.completion("poignancy", event.describe)
        node = Concept.from_event(
            utils.get_uuid(event.get_describe()),
            node_type,
            event,
            poignancy=poignancy,
            filling=filling,
            expire=expire,
        )
        self.associate.add_concept(node)
        return node

    def _determine_action(self):
        plan, idx = self.schedule.current_plan()
        if idx < 0:
            return None
        if plan["describe"] == "sleeping" or "睡" in plan["describe"]:
            return None
        describe = plan["decompose"][idx]["describe"]
        duration = plan["decompose"][idx]["duration"]
        start = plan["decompose"][idx]["start"]
        address = self.spatial.find_address(describe, as_list=True)
        event = self.make_event(self.name, describe, address)
        return memory.Action(event, start=start, duration=duration)

    def _reaction(self, agents):
        if len(self.concepts) == 0:
            return False
        other = self.concepts[0].event.subject
        if other not in agents:
            return False
        if self._skip_react(agents[other]):
            return False
        react = self.completion("react", agents[other], self.concepts)
        if not react[0]:
            return False
        self.logger.info("{} react to {} -> {}".format(self.name, other, react[1]))
        if react[1] == "chat" or react[1] == "对话":
            self._chat_with(agents[other], self.concepts)
        else:
            address = self.spatial.find_address(react[1], as_list=True)
            event = self.make_event(self.name, react[1], address)
            self.revise_schedule(event, self.action.start, self.action.duration)
        return True

    def _skip_react(self, other):
        if not self.is_awake() or not other.is_awake():
            return True
        if self.get_event().fit(other.name, "对话") or other.get_event().fit(
            self.name, "对话"
        ):
            return True

        def _skip(event):
            if not event:
                return False
            if event.object == "idle" or event.object == "空闲":
                return True
            if event.fit(self.name, "对话") or event.fit(other.name, "对话"):
                return True
            return False

        if _skip(self.get_event()) or _skip(other.get_event()):
            return True
        return False

    def _chat_with(self, other, focus):
        # 获取自身当前情绪
        my_emotion = self.mind.get_emotion_state()

        chats, relations = self.conversation.get_chats(self, other)
        if relations:
            self.logger.info("{} is chatting with {}...".format(self.name, other.name))
            for i in range(self.chat_iter):
                # 在提示词中加入自身情绪上下文
                text = self.completion(
                    "generate_chat", self, other, relations[0], chats,
                    my_emotion=my_emotion
                )
                if "<END OF CHAT>" in text:
                    break
                # 创建事件时附带自己的情绪状态
                event = self.make_event(
                    self.name, text, self.get_tile().get_address(),
                    emotion=my_emotion  # 附带情绪信息
                )
                # 让心智模块也处理这次对话事件
                self.mind.process_event(event)
                self._add_concept("chat", event)
                self.chats.append((self.name, text))
                chats.append((self.name, text))
                # 关键：将自己的情绪传递给对方
                other.add_chat(self.name, text, speaker_emotion=my_emotion)
        return

    def get_path(self):
        if not self.path:
            return []
        path, self.path = [self.path[0]], self.path[1:]
        return path
