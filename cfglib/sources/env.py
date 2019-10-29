import os

from ..config import ProxyConfig


# pylint: disable=too-many-ancestors
class EnvConfig(ProxyConfig):
    """A config that takes its contents from the environment.

    Often useful together with `ProjectedConfig`.
    """

    def __init__(self):
        super().__init__(os.environ)
