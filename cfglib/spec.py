# pylint: disable=empty-docstring
from __future__ import annotations

import enum
from typing import *

from .config import CompositeConfig, Config, DictConfig, to_cfg_list
from .validation import Validator, ValidationContext, ValidationError

__all__ = [
    'MISSING',

    'MissingSettingAction',
    'ERROR', 'USE_DEFAULT', 'LEAVE',

    'Setting',
    'StringSetting',
    'BoolSetting',
    'IntSetting',
    'FloatSetting',
    'DictSetting',
    'ListSetting',

    'ConfigSpec',
    'SpecValidatedConfig',
]


class Marker:
    def __repr__(self):
        if self is MISSING:
            return 'MISSING'
        else:
            return super().__repr__()  # pragma: no cover


# Markers
MISSING = Marker()
"""A singleton marker object denoting that a setting value is (or should be) absent.
Absence here means not being in the config at all (raising KeyError on access)."""


T = TypeVar('T')  # pylint: disable=invalid-name
ExtOptional = Union[Marker, None, T]


class MissingSettingAction(enum.Enum):
    """Action to do when a setting is missing"""

    ERROR = enum.auto()
    """Raise an error"""

    USE_DEFAULT = enum.auto()
    """Set it to the provided default"""

    LEAVE = enum.auto()
    """Leave as it is (missing or None)"""


ERROR = MissingSettingAction.ERROR
USE_DEFAULT = MissingSettingAction.USE_DEFAULT
LEAVE = MissingSettingAction.LEAVE


# Setting types
class Setting:
    """Specification for one config's setting.

    :param name: Name of the setting.
        Only needs to be specified if passed to a ConfigSpec instead of a SpecValidatedConfig.
    :param default: The default value to be used when source config doesn't provide
        this setting. If the default is needed but was not specified, an error will be raised.
    :param on_missing: Action to do if this setting is entirely absent from source configs.
    :param on_null: Action to do if this setting is None in the source configs.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        default: ExtOptional[Any] = MISSING,
        on_missing: MissingSettingAction = MissingSettingAction.USE_DEFAULT,
        on_null: MissingSettingAction = MissingSettingAction.LEAVE,
        validators: Optional[Iterable[Validator]] = None,
    ):
        self.name = name
        self.default = default
        self.on_missing = on_missing
        self.on_null = on_null
        self.validators = list(validators or [])

    def __set_name__(self, owner, name):
        if self.name is not None and self.name != name:
            raise ValueError(f'Setting name already set to {self.name}')

        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance[self.name]

    def validate_value(self, value: Any) -> Any:
        """Validate a value and return the result (with default possibly replacing null values)"""

        if value is MISSING:
            if self.on_missing is ERROR:
                raise ValidationError(f'Config field {self.name} missing')
            elif self.on_missing is USE_DEFAULT:
                if self.default is MISSING:
                    raise ValidationError(
                        f'Config field {self.name} missing and no default is provided'
                    )

                return self.default
            elif self.on_missing is LEAVE:
                return MISSING
            else:
                raise ValueError(f'Invalid on_missing choice in field {self.name}')
        elif value is None:
            if self.on_null is ERROR:
                raise ValidationError(f'Config field {self.name} must not be None')
            elif self.on_null is USE_DEFAULT:
                if self.default is MISSING:
                    raise ValidationError(
                        f'Config field {self.name} is None and no default is provided'
                    )

                return self.default
            elif self.on_null is LEAVE:
                return None
            else:
                raise ValueError(f'Invalid on_null choice in field {self.name}')

        value = self.validate_value_custom(value)
        value = self.apply_validators(value)
        return value

    def apply_validators(self, value: Any) -> Any:
        ctx = ValidationContext(self.name)
        for validator in self.validators:
            value = validator(ctx, value)

        return value

    def validate_value_custom(self, value: Any) -> Any:
        """Override this method to implement custom setting type-specific validation logic."""
        return value


class StringSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[str] = MISSING,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[str]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, str):
            raise ValidationError(
                f'A value for setting {self.name} must be a string or None'
            )

        return value


class BoolSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[bool] = MISSING,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[bool]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, bool):
            raise ValidationError(f'A value for setting {self.name} must be a bool')

        return value


class IntSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[int] = MISSING,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[int]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, int):
            raise ValidationError(f'A value for setting {self.name} must be an int')

        return value


class FloatSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[float] = MISSING,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[float]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, float):
            raise ValidationError(f'A value for setting {self.name} must be a float')

        return value


class DictSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[Mapping] = MISSING,
        subtype: Union[ConfigSpec, Type[SpecValidatedConfig], None] = None,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

        self.subtype = subtype

    def validate_value_custom(self, value: Any) -> Optional[Mapping]:
        """"""  # Remove the parent's docstring about overriding
        if not isinstance(value, Mapping):
            raise ValidationError(f'A value for setting {self.name} must be a mapping')

        if isinstance(self.subtype, ConfigSpec):
            value = self.subtype.validate_config(DictConfig(value))
        elif isinstance(self.subtype, type) and issubclass(self.subtype, SpecValidatedConfig):
            value = self.subtype([DictConfig(value)])
        elif self.subtype is None:
            pass
        else:
            raise ValueError(f'Invalid type in field {self.name}')

        return value


class ListSetting(Setting):
    def __init__(
        self,
        *,
        default: ExtOptional[List[Any]] = MISSING,
        on_empty: MissingSettingAction = MissingSettingAction.LEAVE,
        subsetting: Optional[Setting] = None,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

        self.on_empty = on_empty
        self.subsetting = subsetting

    # noinspection DuplicatedCode
    def validate_value_custom(self, value: Any) -> ExtOptional[List[Any]]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, list):
            raise ValidationError(
                f'A value for a setting {self.name} must be a list or None'
            )

        if not value:
            if self.on_empty is ERROR:
                raise ValidationError(f'Config field {self.name} is empty')
            elif self.on_empty is USE_DEFAULT:
                if self.default is MISSING:
                    raise ValidationError(
                        f'Config field {self.name} empty and no default is provided'
                    )

                return self.default
            elif self.on_empty is LEAVE:
                return value
            else:
                raise ValueError(f'Invalid on_empty choice in field {self.name}')

        if self.subsetting:
            value = [
                self.subsetting.validate_value(item)
                for item in value
            ]

        return value


# Spec
class ConfigSpec:
    """A set of settings specifying some config."""

    def __init__(
        self,
        settings_iterable: Iterable[Setting],
        allow_extra: bool = False,
    ):
        settings_list = list(settings_iterable)
        self.settings: Dict[str, Setting] = {}
        for setting in settings_list:
            if setting.name is None:
                raise ValueError(f'Setting name not set for {setting}')

            self.settings[setting.name] = setting

        if len(self.settings) != len(settings_list):
            raise ValueError('All settings must have unique names')

        self.allow_extra = allow_extra

    def validate_setting(self, config: Config, setting_name: str):
        """Validate one setting of a config."""

        try:
            setting = self.settings[setting_name]
        except KeyError as exc:
            raise KeyError(f'Unknown setting, not in config spec: {setting_name}') from exc

        try:
            value = config[setting_name]
        except KeyError as exc:
            value = MISSING

        return setting.validate_value(value)

    def validate_config(self, config: Config):
        """Validate all settings of a config."""

        extra_fields = frozenset(config) - frozenset(self.settings)
        if extra_fields and not self.allow_extra:
            raise ValidationError(
                f'Unexpected fields in the config: '
                f'{",".join(extra_fields)}'
            )

        result = {}
        for setting_name in self.settings:
            result[setting_name] = self.validate_setting(config, setting_name)

        return result


class SpecValidatedConfig(CompositeConfig):
    """An all-in-one class that allows to specify settings and validate values;
    takes an iterable of configs as its source of values.

    Also defines __getattr__ so settings can be accessed as properties
    instead of indexing.

    :param subconfigs: A number of source configs, from lowest priority to highest.
    :param validate: Whether to validate the config right after initialization.

    Example:

    .. code-block:: python

        class ExampleToolConfig(cfglib.SpecValidatedConfig):
            message = cfglib.StringSetting(default='Hello!')
            config_file = cfglib.StringSetting(default=None)
    """

    allow_extra = False
    """Whether source configs can include extra keys not from the spec."""

    SPEC: ExtOptional[ConfigSpec] = None
    """ConfigSpec of this config."""

    def __init_subclass__(cls, **kwargs):  # pylint: disable=unused-argument
        super().__init_subclass__(**kwargs)

        if getattr(cls, 'SPEC', None) is not None:
            return

        settings = []
        for name, setting in cls.__dict__.items():
            if not isinstance(setting, Setting):
                continue

            if name != setting.name:
                raise ValueError(
                    f'Mismatch between setting\'s attribute {name}'
                    f' and its name {setting.name}'
                )

            settings.append(setting)

        spec = ConfigSpec(settings, allow_extra=cls.allow_extra)
        cls.SPEC = spec

    def __init__(
        self,
        subconfigs: Union[Mapping, Iterable[Mapping]],
        validate=True,
    ):
        super().__init__(to_cfg_list(subconfigs))

        # Store a second composite config that can be passed to spec validation
        # as a plain ordinary config
        self._composite_config = CompositeConfig([])
        self._composite_config.subconfigs = self.subconfigs

        if validate:
            self.validate()

    def validate(self):
        """Revalidate this config according to the spec."""
        self.SPEC.validate_config(self._composite_config)

    def __getitem__(self, item):
        value = self.SPEC.validate_setting(self._composite_config, item)

        if value is MISSING:
            raise KeyError(f'Key {item} not found')

        return value

    def __iter__(self):
        return (key for key in self.SPEC.settings)

    def __len__(self):
        return len(list(self.__iter__()))

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError as exc:
            raise AttributeError(*exc.args)

    def __repr__(self):
        snapshot = self.snapshot()
        return f'<{self.__class__.__name__} {snapshot}>'
