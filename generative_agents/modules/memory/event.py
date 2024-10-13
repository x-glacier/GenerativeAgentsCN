"""generative_agents.memory.event"""


class Event:
    def __init__(
        self,
        subject,
        predicate=None,
        object=None,
        address=None,
        describe=None,
        emoji=None,
    ):
        self.subject = subject
        # self.predicate = predicate or "is"
        # self.object = object or "idle"
        self.predicate = predicate or "此时"
        self.object = object or "空闲"
        self._describe = describe or ""
        self.address = address or []
        self.emoji = emoji or ""

    def __str__(self):
        if self._describe:
            des = "{}".format(self._describe)
        else:
            des = "{} {} {}".format(self.subject, self.predicate, self.object)
        # if self.emoji:
        #     des += "[{}]".format(self.emoji)
        if self.address:
            des += " @ " + ":".join(self.address)
        return des

    def __hash__(self):
        return hash(
            (
                self.subject,
                self.predicate,
                self.object,
                self._describe,
                ":".join(self.address),
            )
        )

    def __eq__(self, other):
        if isinstance(other, Event):
            return hash(self) == hash(other)
        return False

    def update(self, predicate=None, object=None, describe=None):
        # self.predicate = predicate or "is"
        # self.object = object or "idle"
        self.predicate = predicate or "此时"
        self.object = object or "空闲"
        self._describe = describe or self._describe

    def to_id(self):
        return self.subject, self.predicate, self.object, self._describe

    def fit(self, subject=None, predicate=None, object=None):
        if subject and self.subject != subject:
            return False
        if predicate and self.predicate != predicate:
            return False
        if object and self.object != object:
            return False
        return True

    def to_dict(self):
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "describe": self._describe,
            "address": self.address,
            "emoji": self.emoji,
        }

    def get_describe(self, with_subject=True):
        describe = self._describe or "{} {}".format(self.predicate, self.object)
        subject = ""
        if with_subject:
            if self.subject not in describe:
                subject = self.subject + " "
        else:
            if describe.startswith(self.subject + " "):
                describe = describe[len(self.subject) + 1:]
        return "{}{}".format(subject, describe)

    @classmethod
    def from_dict(cls, config):
        return cls(**config)

    @classmethod
    def from_list(cls, event):
        if len(event) == 3:
            return cls(event[0], event[1], event[2])
        return cls(event[0], event[1], event[2], event[3])
