"""generative_agents.utils.register"""


class GenerativeAgentsRegistery:
    """The registery for GenerativeAgents"""

    REGISTERY = {}
    MODELS = "models"

    @classmethod
    def register(cls, key, value):
        cls.REGISTERY[key] = value
        return value

    @classmethod
    def unregister(cls, key):
        if key in cls.REGISTERY:
            return cls.REGISTERY.pop(key)
        return None

    @classmethod
    def get(cls, key: str, default):
        return cls.REGISTERY.get(key, default)

    @classmethod
    def contains(cls, key: str):
        return key in cls.REGISTERY

    @classmethod
    def reset(cls):
        cls.REGISTERY = {}


def register_model(model):
    """Register a model."""

    for key in ["model_type", "model_style"]:
        assert hasattr(model, key), "{} should be given to register model".format(key)
    models = GenerativeAgentsRegistery.get(GenerativeAgentsRegistery.MODELS, {})
    models.setdefault(model.model_type(), {})[model.model_style()] = model
    GenerativeAgentsRegistery.register(GenerativeAgentsRegistery.MODELS, models)
    return model


def get_registered_model(model_type, model_style="all"):
    """Get the registered model class."""

    models = GenerativeAgentsRegistery.get(GenerativeAgentsRegistery.MODELS, {})
    if model_style == "all":
        return models.get(model_type, {})
    return models.get(model_type, {}).get(model_style)
