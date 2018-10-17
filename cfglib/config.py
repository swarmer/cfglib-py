# pylint: disable=too-many-ancestors
import abc
import collections.abc
from itertools import chain
import os
import typing as ty


class Config(collections.abc.Mapping):
    """An abstract configuration interface

    A config is really just a dict with some extra methods

    In a custom implementation you need to define at least:
    - __getitem__(item)
    - __iter__()
    - __len__()
    - reload()
    """

    def snapshot(self) -> 'Config':
        """Return a copied snapshot of this config, backed by memory
        """
        return DictConfig(self)

    @abc.abstractmethod
    def reload(self):
        """Reload all config items from its backing store. The contents may change arbitrarily.

        Not all configs can meaningfully reload. In this case this method will do nothing.
        Some configs always pull fresh data. In that case this method also does nothing.
        """
        pass


class DictConfig(dict, Config):
    """A config backed by it own dictionary stored in memory. In other words, a fancy dict."""

    def reload(self):
        pass

    def replace(self, other: Config):
        """Update self in place to become a shallow copy of *other*"""
        self.clear()
        self.update(other)


class CachingConfig(DictConfig):
    """A config that returns data from a wrapped config, until manually reloaded"""

    def __init__(self, wrapped_config: Config, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)

        self.wrapped_config = wrapped_config
        self.replace(self.wrapped_config)

    def reload(self):
        self.wrapped_config.reload()
        self.replace(self.wrapped_config)


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
        pass


class CompositeConfig(Config):
    """A config backed by multiple configs

    Entries are searched in subconfigs in reverse order and the first found
    value is returned. That is, the first subconfig has the lowest priority,
    and the last subconfig takes precedence over all others.
    """

    def __init__(self, subconfigs: ty.Iterable[Config]):  # type: ignore
        self.subconfigs = list(subconfigs)

    def __getitem__(self, item):
        for subconfig in self.subconfigs[::-1]:
            try:
                return subconfig[item]
            except KeyError:
                continue

        raise KeyError(f'Key {item} not found in any subconfig')

    def __iter__(self):
        return iter(self._all_keys)

    def __len__(self):
        return len(self._all_keys)

    def __repr__(self):
        snapshot = self.snapshot()
        return f'<CompositeConfig {snapshot}>'

    def __str__(self):
        return self.__repr__()

    @property
    def _all_keys(self) -> frozenset:
        all_keys = frozenset(chain.from_iterable(
            iter(subconfig)
            for subconfig in self.subconfigs
        ))
        return all_keys

    def reload(self):
        for subconfig in self.subconfigs:
            subconfig.reload()
