import abc
import collections.abc
from itertools import chain
import os
import typing as ty


class Config(collections.abc.Mapping):
    """An abstract configuration interface

    A config is really just a dict with some extra methods
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

    def __init__(self, wrapped_config: Config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wrapped_config = wrapped_config
        self.replace(self.wrapped_config)

    def reload(self):
        self.wrapped_config.reload()
        self.replace(self.wrapped_config)


class EnvConfig(Config):
    """A config that takes its contents from the environment"""

    def __init__(self, prefix=''):
        self.prefix = prefix

    def __getitem__(self, item):
        return self._filtered_environ[item]

    def __iter__(self):
        return iter(self._filtered_environ)

    def __len__(self):
        return len(self._filtered_environ)

    @property
    def _filtered_environ(self):
        return {
            k: v
            for k, v in os.environ.items()
            if k.startswith(self.prefix)
        }

    def reload(self):
        pass


class CompositeConfig(Config):
    """A config backed by multiple configs"""

    def __init__(self, subconfigs: ty.Iterable[Config]):
        self.subconfigs = list(subconfigs)

    def __getitem__(self, item):
        for subconfig in self.subconfigs:
            try:
                return subconfig[item]
            except KeyError:
                continue

        raise KeyError(f'Key {item} not found in any subconfig')

    def __iter__(self):
        return iter(self._all_keys)

    def __len__(self):
        return len(self._all_keys)

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
