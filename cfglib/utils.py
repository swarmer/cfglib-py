import abc

from . import config


class NotInitializedError(Exception):
    def __init__(self):
        super().__init__('initialize() has not been called on InitializableConfig')


class InitializableConfig:
    _config = None

    def __new__(cls) -> config.Config:
        if cls._config is not None:
            return cls._config

        # TODO: initialize under mutex?
        try:
            # hope that build_config doesn't require any arguments
            # and we can just initialize a config on our own
            cls.initialize()
            return cls._config  # type: ignore
        except TypeError:
            # Most likely build_config wants additional arguments
            raise NotInitializedError()

    @classmethod
    def initialize(cls, *args, **kwargs):
        cfg = cls.build_config(*args, **kwargs)
        cls._config = cfg

    @classmethod
    @abc.abstractmethod
    def build_config(cls, *args, **kwargs) -> config.Config:
        raise NotImplementedError()
