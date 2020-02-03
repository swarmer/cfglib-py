from collections import abc as collections_abc
from typing import *

from ..config import ConfigProjection, ProjectedConfig, ProxyConfig
from ..spec import MISSING


# pylint: disable=too-many-ancestors
class ArgsNamespaceConfig(ProjectedConfig):
    """A config that takes its contents from the environment."""

    def __init__(
        self,
        args: object,
        uppercase: bool = False,
        relevant_keys: Optional[Iterable[str]] = None,
    ):
        projection = ArgsNamespaceConfigProjection(uppercase, relevant_keys)
        args_data = {k: v for k, v in args.__dict__.items() if v is not MISSING}
        super().__init__(ProxyConfig(args_data), projection)


class _Universe(collections_abc.Container):
    def __contains__(self, item):
        return True


class ArgsNamespaceConfigProjection(ConfigProjection):
    """A commonly used projection for cmdline args variables:
    filter and optionally uppercase keys.
    """

    def __init__(
        self,
        uppercase: bool = False,
        relevant_keys: Optional[Iterable[str]] = None,
    ):
        self.uppercase = uppercase
        self.relevant_keys: Container = (
            frozenset(relevant_keys)
            if relevant_keys is not None
            else _Universe()
        )

    def is_relevant_key(self, key: str) -> bool:
        if self.uppercase and not key.isupper():
            return False

        return self.is_relevant_sourcekey(self.key_to_sourcekey(key))

    def is_relevant_sourcekey(self, sourcekey: str) -> bool:
        if self.uppercase and not sourcekey.islower():
            return False

        return sourcekey in self.relevant_keys

    def key_to_sourcekey(self, key: str) -> str:
        if self.uppercase:
            key = key.lower()

        return key

    def sourcekey_to_key(self, sourcekey: str) -> str:
        if self.uppercase:
            sourcekey = sourcekey.upper()

        return sourcekey
