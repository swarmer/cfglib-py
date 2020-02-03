# pylint: disable=too-many-ancestors
from __future__ import annotations

import abc
import collections.abc
from itertools import chain
from typing import *


__all__ = [
    'Config',
    'MutableConfig',
    'DictConfig',
    'ProxyConfig',
    'CachingConfig',
    'CompositeConfig',
    'ConfigProjection',
    'BasicConfigProjection',
    'LOWERCASE_PROJECTION',
    'UPPERCASE_PROJECTION',
    'ProjectedConfig',
    'to_cfg',
    'to_cfg_list',
]


def to_cfg(value: Any) -> Config:
    if isinstance(value, Config):
        return value
    elif isinstance(value, Mapping):
        return ProxyConfig(value)
    else:
        raise TypeError(f'Cannot convert to config: {value}')


def to_cfg_list(value: Any) -> List[Config]:
    if not isinstance(value, collections.abc.Collection) or isinstance(value, Mapping):
        value = [value]

    return [to_cfg(item) for item in value]


class Config(collections.abc.Mapping):
    """An abstract configuration interface

    A config is really just a dict with some extra methods.

    In a custom implementation you need to define at least:\n
    - __getitem__(item)\n
    - __iter__()\n
    - __len__()\n
    - reload()\n
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
        pass  # pragma: no cover


class MutableConfig(abc.ABC, collections.abc.MutableMapping, Config):
    """An abstract base class for mutable configs (with __setitem__)"""
    pass


class DictConfig(dict, MutableConfig):
    """A config backed by its own dictionary stored in memory. In other words, a fancy dict."""

    def reload(self):
        """Does nothing."""
        pass

    def replace(self, other: Config):
        """Update self in place to become a shallow copy of *other*"""
        self.clear()
        self.update(other)


class ProxyConfig(MutableConfig):
    """A config that uses a separate mapping as source.

    Unlike DictConfig, this is not by itself a dict, it only references a dict.

    Althouth this class has basically zero logic, it's useful to:
    - Wrap any mapping to conform to the Config interface
    - Be a level of indirection to switch source configs easily by changing .source field.
    """

    def __init__(self, source: Mapping):
        self.source = source
        self._mutable = isinstance(source, collections.abc.MutableMapping)

    def __getitem__(self, key):
        return self.source[key]

    def __setitem__(self, key, value):
        if not self._mutable:
            raise TypeError('ProxyConfig\'s source is not mutable')

        self.source[key] = value

    def __delitem__(self, key):
        if not self._mutable:
            raise TypeError('ProxyConfig\'s source is not mutable')

        del self.source[key]

    def __len__(self):
        return len(self.source)

    def __iter__(self):
        return iter(self.source)

    def reload(self):
        """Reload source if it's a Config, otherwise do nothing."""
        if isinstance(self.source, Config):
            self.source.reload()


class CachingConfig(DictConfig):
    """A config that copies data from a wrapped config once and returns data from this copy,
    until manually reloaded."""

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


class ConfigProjection(abc.ABC):  # pragma: no cover
    """ABC for a projection to be passed to a `ProjectedConfig`.

    The projection should be consistent, that is:\n
    - k2sk(sk2k(sk)) == sk for all sk that are relevant\n
    - sk2k(k2sk(k)) == k for all k that are relevant\n
    - is_relevant(key) <=> is_relevant_sourcekey(k2sk(k))
    """

    @abc.abstractmethod
    def is_relevant_key(self, key: str) -> bool:
        """Should a projected config key be accepted by the ProjectedConfig?"""
        ...

    @abc.abstractmethod
    def is_relevant_sourcekey(self, sourcekey: str) -> bool:
        """Should a source config key be used by the ProjectedConfig?"""
        ...

    @abc.abstractmethod
    def key_to_sourcekey(self, key: str) -> str:
        """Map a ProjectedConfig's key to a source config's key"""
        ...

    @abc.abstractmethod
    def sourcekey_to_key(self, sourcekey: str) -> str:
        """Map source config's key to a a ProjectedConfig's key"""
        ...


class BasicConfigProjection(ConfigProjection):
    """A helper to easily create a ConfigProjection"""

    def __init__(
        self,
        is_relevant_key: Optional[Callable] = None,
        is_relevant_sourcekey: Optional[Callable] = None,
        key_to_sourcekey: Optional[Callable] = None,
        sourcekey_to_key: Optional[Callable] = None
    ):
        if is_relevant_key:
            self._is_relevant_key = is_relevant_key
        else:
            def _default_is_relevant_key(key):
                return self.is_relevant_sourcekey(self.key_to_sourcekey(key))

            self._is_relevant_key = _default_is_relevant_key

        if is_relevant_sourcekey:
            self._is_relevant_sourcekey = is_relevant_sourcekey
        else:
            def _default_is_relevant_sourcekey(_key):
                return True

            self._is_relevant_sourcekey = _default_is_relevant_sourcekey

        if key_to_sourcekey:
            self.key_to_sourcekey = key_to_sourcekey  # type: ignore

        if sourcekey_to_key:
            self.sourcekey_to_key = sourcekey_to_key  # type: ignore

    # pylint: disable=method-hidden
    def is_relevant_key(self, key: str) -> bool:
        """Check that sk2k(k2sk(k)) maps key to itself and, by default,
        compute source key and defer to is_relevant_sourcekey."""
        if self.sourcekey_to_key(self.key_to_sourcekey(key)) != key:
            return False

        return self._is_relevant_key(key)

    # pylint: disable=method-hidden
    def is_relevant_sourcekey(self, sourcekey: str) -> bool:
        """Check that k2sk(sk2k(sk)) maps sourcekey to itself and, by default, return True."""
        if self.key_to_sourcekey(self.sourcekey_to_key(sourcekey)) != sourcekey:
            return False

        return self._is_relevant_sourcekey(sourcekey)

    # pylint: disable=method-hidden
    def key_to_sourcekey(self, key: str) -> str:
        """By default, identity function."""
        return key

    # pylint: disable=method-hidden
    def sourcekey_to_key(self, sourcekey: str) -> str:
        """By default, identity function."""
        return sourcekey


LOWERCASE_PROJECTION = BasicConfigProjection(
    key_to_sourcekey=lambda k: k.upper(),
    sourcekey_to_key=lambda sk: sk.lower(),
)

UPPERCASE_PROJECTION = BasicConfigProjection(
    key_to_sourcekey=lambda k: k.lower(),
    sourcekey_to_key=lambda sk: sk.upper(),
)


class ProjectedConfig(MutableConfig):
    """Config that renames or filters source config's keys."""

    def __init__(self, subconfig: Config, projection: ConfigProjection):
        self.subconfig = subconfig
        self.projection = projection

    def __getitem__(self, key):
        if not self.projection.is_relevant_key(key):
            raise KeyError(f'Key {key} not relevant')

        sourcekey = self.projection.key_to_sourcekey(key)
        return self.subconfig[sourcekey]

    def __setitem__(self, key, value):
        if not isinstance(self.subconfig, MutableConfig):
            raise TypeError('ProjectedConfig\'s subconfig is not mutable')

        if not self.projection.is_relevant_key(key):
            raise KeyError(f'Key {key} not relevant')

        sourcekey = self.projection.key_to_sourcekey(key)
        self.subconfig[sourcekey] = value

    def __delitem__(self, key):
        if not isinstance(self.subconfig, MutableConfig):
            raise TypeError('ProjectedConfig\'s subconfig is not mutable')

        if not self.projection.is_relevant_key(key):
            raise KeyError(f'Key {key} not relevant')

        sourcekey = self.projection.key_to_sourcekey(key)
        del self.subconfig[sourcekey]

    def __len__(self):
        return len(list(self._relevant_sourcekeys))

    def __iter__(self):
        return (
            self.projection.sourcekey_to_key(sourcekey)
            for sourcekey in self._relevant_sourcekeys
        )

    @property
    def _relevant_sourcekeys(self) -> Iterable[str]:
        return (
            sourcekey
            for sourcekey in iter(self.subconfig)
            if self.projection.is_relevant_sourcekey(sourcekey)
        )

    def reload(self):
        """Reload the source config."""
        self.subconfig.reload()
