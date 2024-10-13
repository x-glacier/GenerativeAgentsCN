"""generative_agents.memory.schedule"""

from modules import utils


class Schedule:
    def __init__(self, create=None, daily_schedule=None, diversity=5, max_try=5):
        if create:
            self.create = utils.to_date(create)
        else:
            self.create = None
        self.daily_schedule = daily_schedule or []
        self.diversity = diversity
        self.max_try = max_try

    def abstract(self):
        def _to_stamp(plan):
            start, end = self.plan_stamps(plan, time_format="%H:%M")
            return "{}~{}".format(start, end)

        des = {}
        for plan in self.daily_schedule:
            stamp = _to_stamp(plan)
            if plan.get("decompose"):
                s_info = {_to_stamp(p): p["describe"] for p in plan["decompose"]}
                des[stamp + ": " + plan["describe"]] = s_info
            else:
                des[stamp] = plan["describe"]
        return des

    def __str__(self):
        return utils.dump_dict(self.abstract())

    def add_plan(self, describe, duration, decompose=None):
        if self.daily_schedule:
            last_plan = self.daily_schedule[-1]
            start = last_plan["start"] + last_plan["duration"]
        else:
            start = 0
        self.daily_schedule.append(
            {
                "idx": len(self.daily_schedule),
                "describe": describe,
                "start": start,
                "duration": duration,
                "decompose": decompose or {},
            }
        )
        return self.daily_schedule[-1]

    def current_plan(self):
        total_minute = utils.get_timer().daily_duration()
        for plan in self.daily_schedule:
            if self.plan_stamps(plan)[1] <= total_minute:
                continue
            for de_plan in plan.get("decompose", []):
                if self.plan_stamps(de_plan)[1] <= total_minute:
                    continue
                return plan, de_plan
            return plan, plan
        last_plan = self.daily_schedule[-1]
        return last_plan, last_plan

    def plan_stamps(self, plan, time_format=None):
        def _to_date(minutes):
            return utils.get_timer().daily_time(minutes).strftime(time_format)

        start, end = plan["start"], plan["start"] + plan["duration"]
        if time_format:
            start, end = _to_date(start), _to_date(end)
        return start, end

    def decompose(self, plan):
        d_plan = plan.get("decompose", {})
        if len(d_plan) > 0:
            return False
        describe = plan["describe"]
        if "sleep" not in describe and "bed" not in describe:
            return True
        if "睡" not in describe and "床" not in describe:
            return True
        if "sleeping" in describe or "asleep" in describe or "in bed" in describe:
            return False
        if "睡" in describe or "床" in describe:
            return False
        if "sleep" in describe or "bed" in describe:
            return plan["duration"] <= 60
        if "睡" in describe or "床" in describe:
            return plan["duration"] <= 60
        return True

    def scheduled(self):
        if not self.daily_schedule:
            return False
        return utils.get_timer().daily_format() == self.create.strftime("%A %B %d")

    def to_dict(self):
        return {
            "create": (
                self.create.strftime("%Y%m%d-%H:%M:%S") if self.create else None
            ),
            "daily_schedule": self.daily_schedule,
        }
