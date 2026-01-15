import random
import datetime
import re
from string import Template
from pydantic import BaseModel
from collections import namedtuple
from typing import List, Tuple
from modules import utils
from modules.memory import Event


Result = namedtuple("Result", ["prompt", "callback", "failsafe", "return_type"])

class Scratch:
    def __init__(self, name, currently, config):
        self.name = name
        self.currently = currently
        self.config = config
        self.template_path = "data/prompts"

    def build_prompt(self, template, data):
        with open(f"{self.template_path}/{template}.txt", "r", encoding="utf-8") as file:
            file_content = file.read()

        template = Template(file_content)
        filled_content = template.substitute(data)

        return filled_content

    def _base_desc(self):
        return self.build_prompt(
            "base_desc",
            {
                "name": self.name,
                "age": self.config["age"],
                "innate": self.config["innate"],
                "learned": self.config["learned"],
                "lifestyle": self.config["lifestyle"],
                "daily_plan": self.config["daily_plan"],
                "date": utils.get_timer().daily_format_cn(),
                "currently": self.currently,
            }
        )

    def prompt_poignancy_event(self, event):
        prompt = self.build_prompt(
            "poignancy_event",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "event": event.get_describe(),
            }
        )

        class PoignancyEventResponse(BaseModel):
            res: int

        return Result(prompt, None, random.choice(list(range(10))) + 1, PoignancyEventResponse)

    def prompt_poignancy_chat(self, event):
        prompt = self.build_prompt(
            "poignancy_chat",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "event": event.get_describe(),
            }
        )

        class PoignancyChatResponse(BaseModel):
            res: int

        return Result(prompt, None, random.choice(list(range(10))) + 1, PoignancyChatResponse)

    def prompt_wake_up(self):
        prompt = self.build_prompt(
            "wake_up",
            {
                "base_desc": self._base_desc(),
                "lifestyle": self.config["lifestyle"],
                "agent": self.name,
            }
        )

        class wakeupResponse(BaseModel):
            res: int

        def _callback(response):
            value = response
            if value > 11:
                value = 11
            return value

        return Result(prompt, _callback, 8, wakeupResponse)

    def prompt_schedule_init(self, wake_up):
        prompt = self.build_prompt(
            "schedule_init",
            {
                "base_desc": self._base_desc(),
                "lifestyle": self.config["lifestyle"],
                "agent": self.name,
                "wake_up": wake_up,
            }
        )

        class schedule_initResponse(BaseModel):
            res: list[str]

        failsafe = [
            "早上6点起床并完成早餐的例行工作",
            "早上7点吃早餐",
            "早上8点看书",
            "中午12点吃午饭",
            "下午1点小睡一会儿",
            "晚上7点放松一下，看电视",
            "晚上11点睡觉",
        ]
        return Result(prompt, None, failsafe, schedule_initResponse)

    def prompt_schedule_daily(self, wake_up, daily_schedule):
        hourly_schedule = ""
        for i in range(wake_up):
            hourly_schedule += f"[{i}:00] 睡觉\n"
        for i in range(wake_up, 24):
            hourly_schedule += f"[{i}:00] <活动>\n"

        prompt = self.build_prompt(
            "schedule_daily",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "daily_schedule": "；".join(daily_schedule),
                "hourly_schedule": hourly_schedule,
            }
        )

        class schedule_dailyResponse(BaseModel):
            res: dict[str, str]

        failsafe = {
            "6:00": "起床并完成早晨的例行工作",
            "7:00": "吃早餐",
            "8:00": "读书",
            "9:00": "读书",
            "10:00": "读书",
            "11:00": "读书",
            "12:00": "吃午饭",
            "13:00": "小睡一会儿",
            "14:00": "小睡一会儿",
            "15:00": "小睡一会儿",
            "16:00": "继续工作",
            "17:00": "继续工作",
            "18:00": "回家",
            "19:00": "放松，看电视",
            "20:00": "放松，看电视",
            "21:00": "睡前看书",
            "22:00": "准备睡觉",
            "23:00": "睡觉",
        }

        def _callback(response):
            assert len(response) >= 5, "less than 5 schedules"
            return response

        return Result(prompt, _callback, failsafe, schedule_dailyResponse)

    def prompt_schedule_decompose(self, plan, schedule):
        def _plan_des(plan):
            start, end = schedule.plan_stamps(plan, time_format="%H:%M")
            return f'{start} 至 {end}，{self.name} 计划 {plan["describe"]}'

        indices = range(
            max(plan["idx"] - 1, 0), min(plan["idx"] + 2, len(schedule.daily_schedule))
        )

        start, end = schedule.plan_stamps(plan, time_format="%H:%M")
        increment = max(int(plan["duration"] / 100) * 5, 5)

        prompt = self.build_prompt(
            "schedule_decompose",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "plan": "；".join([_plan_des(schedule.daily_schedule[i]) for i in indices]),
                "increment": increment,
                "start": start,
                "end": end,
            }
        )

        class schedule_decomposeResponse(BaseModel):  
            res: List[Tuple[str, int]]

        def _callback(response):
            left = plan["duration"] - sum([s[1] for s in response])
            if left > 0:
                response.append((plan["describe"], left))
            return response

        failsafe = [(plan["describe"], 10) for _ in range(int(plan["duration"] / 10))]
        return Result(prompt, _callback, failsafe, schedule_decomposeResponse)

    def prompt_schedule_revise(self, action, schedule):
        plan, _ = schedule.current_plan()
        start, end = schedule.plan_stamps(plan, time_format="%H:%M")
        act_start_minutes = utils.daily_duration(action.start)
        original_plan, new_plan = [], []

        def _plan_des(start, end, describe):
            if not isinstance(start, str):
                start = start.strftime("%H:%M")
            if not isinstance(end, str):
                end = end.strftime("%H:%M")
            return "[{} 至 {}] {}".format(start, end, describe)

        for de_plan in plan["decompose"]:
            de_start, de_end = schedule.plan_stamps(de_plan, time_format="%H:%M")
            original_plan.append(_plan_des(de_start, de_end, de_plan["describe"]))
            if de_plan["start"] + de_plan["duration"] <= act_start_minutes:
                new_plan.append(_plan_des(de_start, de_end, de_plan["describe"]))
            elif de_plan["start"] <= act_start_minutes:
                new_plan.extend(
                    [
                        _plan_des(de_start, action.start, de_plan["describe"]),
                        _plan_des(
                            action.start, action.end, action.event.get_describe(False)
                        ),
                    ]
                )

        original_plan, new_plan = "\n".join(original_plan), "\n".join(new_plan)

        prompt = self.build_prompt(
            "schedule_revise",
            {
                "agent": self.name,
                "start": start,
                "end": end,
                "original_plan": original_plan,
                "duration": action.duration,
                "event": action.event.get_describe(),
                "new_plan": new_plan,
            }
        )

        class schedule_reviseResponse(BaseModel):
            res: List[Tuple[str, str, str]]

        def _callback(response):  
            # response已经是List[Tuple[str, str, str]]类型  
            # 格式: [(开始时间, 结束时间, 描述), ...]  
            decompose = []  
            for start, end, describe in response:  
                m_start = utils.daily_duration(utils.to_date(start, "%H:%M"))  
                m_end = utils.daily_duration(utils.to_date(end, "%H:%M"))  
                decompose.append(  
                    {  
                        "idx": len(decompose),  
                        "describe": describe,  
                        "start": m_start,  
                        "duration": m_end - m_start,  
                    }  
                )  
            return decompose

        return Result(prompt, _callback, plan["decompose"], schedule_reviseResponse)

    def prompt_determine_sector(self, describes, spatial, address, tile):
        live_address = spatial.find_address("living_area", as_list=True)[:-1]
        curr_address = tile.get_address("sector", as_list=True)

        prompt = self.build_prompt(
            "determine_sector",
            {
                "agent": self.name,
                "live_sector": live_address[-1],
                "live_arenas": ", ".join(i for i in spatial.get_leaves(live_address)),
                "current_sector": curr_address[-1],
                "current_arenas": ", ".join(i for i in spatial.get_leaves(curr_address)),
                "daily_plan": self.config["daily_plan"],
                "areas": ", ".join(i for i in spatial.get_leaves(address)),
                "complete_plan": describes[0],
                "decomposed_plan": describes[1],
            }
        )

        sectors = spatial.get_leaves(address)
        arenas = {}
        for sec in sectors:
            arenas.update(
                {a: sec for a in spatial.get_leaves(address + [sec]) if a not in arenas}
            )
        failsafe = random.choice(sectors)

        class determine_sectorResponse(BaseModel):
            res: str

        def _callback(response):  
            # response已经是str类型  
            # 验证sector是否在有效列表中，或进行映射  
            if response in sectors:  
                return response  
            if response in arenas:  
                return arenas[response]  
            for s in sectors:  
                if response.startswith(s):  
                    return s  
            return failsafe
        return Result(prompt, _callback, failsafe, determine_sectorResponse)

    def prompt_determine_arena(self, describes, spatial, address):
        prompt = self.build_prompt(
            "determine_arena",
            {
                "agent": self.name,
                "target_sector": address[-1],
                "target_arenas": ", ".join(i for i in spatial.get_leaves(address)),
                "daily_plan": self.config["daily_plan"],
                "complete_plan": describes[0],
                "decomposed_plan": describes[1],
            }
        )

        arenas = spatial.get_leaves(address)
        failsafe = random.choice(arenas)

        class determine_arenaResponse(BaseModel):  
            res: str

        def _callback(response):
            return response if response in arenas else failsafe

        return Result(prompt, _callback, failsafe, determine_arenaResponse)

    def prompt_determine_object(self, describes, spatial, address):
        objects = spatial.get_leaves(address)

        prompt = self.build_prompt(
            "determine_object",
            {
                "activity": describes[1],
                "objects": ", ".join(objects),
            }
        )

        failsafe = random.choice(objects)

        class determine_objectResponse(BaseModel):
            res: str
        def _callback(response):
            # pattern = ["The most relevant object from the Objects is: <(.+?)>", "<(.+?)>"]
            return response if response in objects else failsafe

        return Result(prompt, _callback, failsafe, determine_objectResponse)

    def prompt_describe_event(self, subject, describe, address, emoji=None):
        prompt = self.build_prompt(
            "describe_event",
            {
                "action": describe,
            }
        )

        e_describe = describe.replace("(", "").replace(")", "").replace("<", "").replace(">", "")
        if e_describe.startswith(subject + "此时"):
            e_describe = e_describe.replace(subject + "此时", "")
        failsafe = Event(
            subject, "此时", e_describe, describe=describe, address=address, emoji=emoji
        )
        class describe_eventResponse(BaseModel):
            res: List[Tuple[str, str, str]]

        def _callback(response):  
            # response已经是List[Tuple[str, str, str]]类型  
            # 格式: [(主语, 谓语, 宾语), ...]  
            for subject, predicate, obj in response:  
                # 验证三元组不为空  
                if subject and predicate and obj:  
                    return Event(subject, predicate, obj, describe=describe, address=address, emoji=emoji)  
            return None
        return Result(prompt, _callback, failsafe, describe_eventResponse)

    def prompt_describe_object(self, obj, describe):
        prompt = self.build_prompt(
            "describe_object",
            {
                "object": obj,
                "agent": self.name,
                "action": describe,
            }
        )

        class describe_objectResponse(BaseModel):
            res: str

        failsafe = "空闲"
        return Result(prompt, None, failsafe, describe_objectResponse)

    def prompt_decide_chat(self, agent, other, focus, chats):
        def _status_des(a):
            event = a.get_event()
            if a.path:
                return f"{a.name} 正去往 {event.get_describe(False)}"
            return event.get_describe()

        context = "。".join(
            [c.describe for c in focus["events"]]
        )
        context += "\n" + "。".join([c.describe for c in focus["thoughts"]]) 
        date_str = utils.get_timer().get_date("%Y-%m-%d %H:%M:%S")
        chat_history = ""
        if chats:
            chat_history = f" {agent.name} 和 {other.name} 上次在 {chats[0].create} 聊过关于 {chats[0].describe} 的话题"
        a_des, o_des = _status_des(agent), _status_des(other)

        prompt = self.build_prompt(
            "decide_chat",
            {
                "context": context,
                "date": date_str,
                "chat_history": chat_history,
                "agent_status": a_des,
                "another_status": o_des,
                "agent": agent.name,
                "another": other.name,
            }
        )

        class decide_chatResponse(BaseModel):
            res: bool

        failsafe = False
        return Result(prompt, None, failsafe, decide_chatResponse)

    def prompt_decide_chat_terminate(self, agent, other, chats):
        prompt = self.build_prompt(
            "decide_chat_terminate",
            {
                "agent": agent.name,
                "other": other.name,
                "chats": self._format_chats(chats),
            }
        )

        class decide_chat_terminateResponse(BaseModel):
            res: bool

        failsafe = True
        return Result(prompt, None, failsafe, decide_chat_terminateResponse)

    def prompt_generate_chat(self, agent, other, relation, chats, my_emotion=None):
        info = {
            "base_desc": self._base_desc(),
            "agent": agent.name,
            "other": other.name,
            "relation": relation,
            "my_emotion": ""
        }
        if my_emotion:
            info["my_emotion"] = f"""You are currently feeling: Pleasure={my_emotion['pleasure']:.2f}, Arousal={my_emotion['arousal']:.2f}, Dominance={my_emotion['dominance']:.2f}. This should subtly influence your tone and response."""

        info["chats"] = self._format_chats(chats)

        prompt = self.build_prompt("generate_chat", info)

        class generate_chatResponse(BaseModel):
            res: str

        failsafe = "..."
        return Result(prompt, None, failsafe, generate_chatResponse)

    def _format_chats(self, chats):
        output = []
        for name, text in chats:
            output.append(f"{name}: {text}")
        return "\n".join(output)

    def prompt_retrieve_plan(self, retrieved):
        prompt = self.build_prompt(
            "retrieve_plan",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "retrieved": "\n".join(retrieved.values()),
            }
        )

        class retrieve_planResponse(BaseModel):
            res: str

        failsafe = "睡一整天"
        return Result(prompt, None, failsafe, retrieve_planResponse)

    def prompt_retrieve_thought(self, retrieved):
        prompt = self.build_prompt(
            "retrieve_thought",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "retrieved": "\n".join(retrieved.values()),
            }
        )

        class retrieve_thoughtResponse(BaseModel):
            res: str

        failsafe = "我需要休息"
        return Result(prompt, None, failsafe, retrieve_thoughtResponse)

    def prompt_retrieve_currently(self, plan, thought):
        prompt = self.build_prompt(
            "retrieve_currently",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "plan": plan,
                "thought": thought,
            }
        )

        class retrieve_currentlyResponse(BaseModel):
            res: str

        failsafe = "我需要休息"
        return Result(prompt, None, failsafe, retrieve_currentlyResponse)

    def prompt_reflect_focus(self, nodes, num):
        prompt = self.build_prompt(
            "reflect_focus",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "retrieved": "\n".join([n.describe for n in nodes]),
                "num": num,
            }
        )

        class reflect_focusResponse(BaseModel):
            res: list[str]

        failsafe = ["我最近在忙什么？"]
        return Result(prompt, None, failsafe, reflect_focusResponse)

    def prompt_reflect_insights(self, nodes, num):
        prompt = self.build_prompt(
            "reflect_insights",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "retrieved": "\n".join([n.describe for n in nodes]),
                "num": num,
            }
        )

        class reflect_insightsResponse(BaseModel):
            res: List[Tuple[str, list[int]]]

        failsafe = [("我需要休息", [0])]

        def _callback(response):
            insights = []
            for thought, evidence_indices in response:
                evidence = [nodes[i].node_id for i in evidence_indices if i < len(nodes)]
                insights.append((thought, evidence))
            return insights

        return Result(prompt, _callback, failsafe, reflect_insightsResponse)

    def prompt_reflect_chat_planing(self, chats):
        prompt = self.build_prompt(
            "reflect_chat_planing",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "chats": self._format_chats(chats),
            }
        )

        class reflect_chat_planingResponse(BaseModel):
            res: str

        failsafe = "我需要休息"
        return Result(prompt, None, failsafe, reflect_chat_planingResponse)

    def prompt_reflect_chat_memory(self, chats):
        prompt = self.build_prompt(
            "reflect_chat_memory",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "chats": self._format_chats(chats),
            }
        )

        class reflect_chat_memoryResponse(BaseModel):
            res: str

        failsafe = "我需要休息"
        return Result(prompt, None, failsafe, reflect_chat_memoryResponse)

    def prompt_react(self, other, concepts):
        prompt = self.build_prompt(
            "react",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "other": other.name,
                "event": concepts[0].describe,
            }
        )

        class reactResponse(BaseModel):
            res: Tuple[bool, str]

        failsafe = (False, "")
        return Result(prompt, None, failsafe, reactResponse)

__all__ = ['Scratch', 'Result']
