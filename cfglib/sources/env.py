import os

from ..config import Config


class EnvConfig(Config):
    """A config that takes its contents from the environment"""

    def __init__(self, prefix='', keymap=None):
        self.prefix = prefix
        self.keymap = keymap or (lambda x: x.lower())

    def __getitem__(self, item):
        return self._filtered_environ[item]

    def __iter__(self):
        return iter(self._filtered_environ)

    def __len__(self):
        return len(self._filtered_environ)

    def __repr__(self):
        filtered_env = self._filtered_environ
        return f'<EnvConfig {filtered_env}>'

    def __str__(self):
        return self.__repr__()

    @property
    def _filtered_environ(self):
        prefix_len = len(self.prefix)
        return {
            self.keymap(k[prefix_len:]): v
            for k, v in os.environ.items()
            if k.startswith(self.prefix)
        }

    def reload(self):
        """Does nothing."""
        pass
