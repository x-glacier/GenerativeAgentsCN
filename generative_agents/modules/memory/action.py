"""generative_agents.memory.action"""

import datetime

from modules import utils
from .event import Event


class Action:
    def __init__(
        self,
        event,
        obj_event=None,
        start=None,
        duration=0,
    ):
        self.event = event
        self.obj_event = obj_event
        self.start = start or utils.get_timer().get_date()
        self.duration = duration
        self.end = self.start + datetime.timedelta(minutes=self.duration)

    def abstract(self):
        status = "{} [{}~{}]".format(
            "已完成" if self.finished() else "进行中",
            self.start.strftime("%Y%m%d-%H:%M"),
            self.end.strftime("%Y%m%d-%H:%M"),
        )
        info = {"status": status, "event": str(self.event)}
        if self.obj_event:
            info["object"] = str(self.obj_event)
        return info

    def __str__(self):
        return utils.dump_dict(self.abstract())

    @property
    def agent_event(self):
        """返回代理事件"""
        return self.event
    
    @property
    def object_event(self):
        """返回对象事件"""
        return self.obj_event
    
    def is_awake(self):
        """检查代理是否清醒（未睡觉）"""
        if self.event and hasattr(self.event, 'action'):
            return '睡觉' not in str(self.event.action)
        return True
    
    def finished(self):
        if not self.duration:
            return True
        if not self.event.address:
            return True
        return utils.get_timer().get_date() > self.end

    def to_dict(self):
        return {
            "event": self.event.to_dict(),
            "obj_event": self.obj_event.to_dict() if self.obj_event else None,
            "start": self.start.strftime("%Y%m%d-%H:%M:%S"),
            "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, config):
        config["event"] = Event.from_dict(config["event"])
        if config.get("obj_event"):
            config["obj_event"] = Event.from_dict(config["obj_event"])
        config["start"] = utils.to_date(config["start"])
        return cls(**config)
