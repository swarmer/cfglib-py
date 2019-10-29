import os

from ..config import ConfigProjection, ProjectedConfig, ProxyConfig


# pylint: disable=too-many-ancestors
class EnvConfig(ProjectedConfig):
    """A config that takes its contents from the environment."""

    def __init__(self, prefix: str = '', lowercase: bool = False):
        projection = EnvConfigProjection(prefix, lowercase)

        super().__init__(ProxyConfig(os.environ), projection)


class EnvConfigProjection(ConfigProjection):
    """A commonly used projection for env variables: remove prefix and optionally lowercase keys."""

    def __init__(self, prefix: str, lowercase: bool = False):
        self.prefix = prefix
        self.lowercase = lowercase

    def is_relevant_key(self, key: str) -> bool:
        if self.lowercase and not key.islower():
            return False

        return True

    def is_relevant_sourcekey(self, sourcekey: str) -> bool:
        if self.lowercase and not sourcekey.isupper():
            return False

        return sourcekey.startswith(self.prefix)

    def key_to_sourcekey(self, key: str) -> str:
        if self.lowercase:
            key = key.upper()

        return self.prefix + key

    def sourcekey_to_key(self, sourcekey: str) -> str:
        assert sourcekey.startswith(self.prefix)
        key = sourcekey[len(self.prefix):]

        if self.lowercase:
            key = key.lower()

        return key
