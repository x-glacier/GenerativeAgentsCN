"""generative_agents.utils.timer"""

import datetime

from .namespace import GenerativeAgentsMap, GenerativeAgentsKey


def to_date(date_str, date_format="%Y%m%d-%H:%M:%S"):
    if date_format == "%H:%M" and date_str.startswith("24:"):
        date_str = date_str.replace("24:", "0:")
    return datetime.datetime.strptime(date_str, date_format)


def daily_duration(date, mode="minute"):
    duration = date.hour % 24
    if mode == "hour":
        return duration
    duration = duration * 60 + date.minute
    if mode == "minute":
        return duration
    return datetime.timedelta(minutes=duration)


class Timer:
    def __init__(self, start=None):
        self._mode = "on_time"
        if start:
            d_format = "%Y%m%d-%H:%M" if "-" in start else "%H:%M"
            self._offset = to_date(start, d_format)
        else:
            self._offset = datetime.datetime.now()

    def forward(self, offset):
        self._offset += datetime.timedelta(minutes=offset)

    def get_date(self, date_format=""):
        date = self._offset
        if date_format:
            return date.strftime(date_format)
        return date

    def get_delta(self, start, end=None, mode="minute"):
        end = end or self.get_date()
        seconds = (end - start).total_seconds()
        if mode == "second":
            return seconds
        if mode == "minute":
            return round(seconds / 60)
        if mode == "hour":
            return round(seconds / 3600)
        return end - start

    def daily_format(self):
        return self.get_date("%A %B %d")

    def get_weekday(self, t):
        weekday_dict = {
            0: "星期一",
            1: "星期二",
            2: "星期三",
            3: "星期四",
            4: "星期五",
            5: "星期六",
            6: "星期日"
        }
        weekday = weekday_dict[t.weekday()]
        return weekday

    def daily_format_cn(self):
        weekday = self.get_weekday(self.get_date())
        date = self.get_date("%Y年%m月%d日")
        return f"{date}（{weekday}）"

    def time_format_cn(self, t):
        weekday = self.get_weekday(t)
        date = t.strftime("%Y年%m月%d日")
        time = t.strftime("%H:%M")
        return f"{date}（{weekday}）{time}"

    def daily_duration(self, mode="minute"):
        return daily_duration(self.get_date(), mode)

    def daily_time(self, duration):
        base = self.get_date().replace(hour=0, minute=0, second=0, microsecond=0)
        return base + datetime.timedelta(minutes=duration)

    @property
    def mode(self):
        return self._mode


def set_timer(start=None):
    GenerativeAgentsMap.set(GenerativeAgentsKey.TIMER, Timer(start=start))
    return GenerativeAgentsMap.get(GenerativeAgentsKey.TIMER)


def get_timer():
    if not GenerativeAgentsMap.get(GenerativeAgentsKey.TIMER):
        set_timer()
    return GenerativeAgentsMap.get(GenerativeAgentsKey.TIMER)
