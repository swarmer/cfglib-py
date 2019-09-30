# pylint: disable=too-many-ancestors
import abc
import collections.abc
from itertools import chain
from typing import *


__all__ = [
    'Config',
    'DictConfig',
    'CachingConfig',
    'CompositeConfig',
]


class Config(collections.abc.Mapping):
    """An abstract configuration interface

    A config is really just a dict with some extra methods

    In a custom implementation you need to define at least:
    - __getitem__(item)
    - __iter__()
    - __len__()
    - reload()
    """

    def snapshot(self) -> 'DictConfig':
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


class MutableConfig(abc.ABC, collections.abc.MutableMapping, Config):
    pass


class DictConfig(dict, MutableConfig):
    """A config backed by it own dictionary stored in memory. In other words, a fancy dict."""

    def reload(self):
        """Does nothing."""
        pass

    def replace(self, other: Config):
        """Update self in place to become a shallow copy of *other*"""
        self.clear()
        self.update(other)


class CachingConfig(DictConfig):
    """A config that returns data from a wrapped config, until manually reloaded"""

    def __init__(self, wrapped_config: Config):  # type: ignore
        super().__init__()

        self.wrapped_config = wrapped_config
        self.replace(self.wrapped_config)

    def reload(self):
        """Refresh the underlying config and update the cache."""
        self.wrapped_config.reload()
        self.replace(self.wrapped_config)


class CompositeConfig(Config):
    """A config backed by multiple configs

    Entries are searched in subconfigs in reverse order and the first found
    value is returned. That is, the first subconfig has the lowest priority,
    and the last subconfig takes precedence over all others.
    """

    def __init__(self, subconfigs: Iterable[Config]):  # type: ignore
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

    @property
    def _all_keys(self) -> frozenset:
        all_keys = frozenset(chain.from_iterable(
            iter(subconfig)
            for subconfig in self.subconfigs
        ))
        return all_keys

    def reload(self):
        """Reload subconfigs."""
        for subconfig in self.subconfigs:
            subconfig.reload()
