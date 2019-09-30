import os

from ..config import ProxyConfig


# pylint: disable=too-many-ancestors
class EnvConfig(ProxyConfig):
    """A config that takes its contents from the environment"""

    def __init__(self):
        super().__init__(os.environ)
