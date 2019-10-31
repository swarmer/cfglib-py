# pylint: disable=empty-docstring
import enum
from typing import *

from .config import CompositeConfig, Config


__all__ = [
    'MISSING',

    'MissingSettingAction',
    'ERROR', 'USE_DEFAULT', 'LEAVE',

    'ValidationError',

    'Setting',
    'StringSetting',
    'StringListSetting',
    'BoolSetting',
    'IntSetting',
    'FloatSetting',

    'ConfigSpec',
    'SpecValidatedConfig',
]


# Markers
MISSING = object()
"""A singleton marker object denoting that a setting value is (or should be) absent.
Absence here means not being in the config at all (raising KeyError on access)."""


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


# Exceptions
class ValidationError(Exception):
    """Raised when a setting value is not valid according to the setting parameters"""
    pass


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
        name: str = '<unset>',
        default: Optional[Any] = MISSING,
        on_missing: MissingSettingAction = MissingSettingAction.USE_DEFAULT,
        on_null: MissingSettingAction = MissingSettingAction.LEAVE,
    ):
        self.name = name
        self.default = default
        self.on_missing = on_missing
        self.on_null = on_null

    def __set_name__(self, owner, name):
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

        return self.validate_value_custom(value)

    def validate_value_custom(self, value: Any) -> Any:
        """Override this method to implement custom setting type-specific validation logic."""
        return value


class StringSetting(Setting):
    def __init__(
        self,
        default: Optional[str] = None,
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


class StringListSetting(Setting):
    def __init__(
        self,
        default: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[List[str]]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, list):
            raise ValidationError(
                f'A value for a setting {self.name} must be a list or None'
            )

        if any(not isinstance(item, str) for item in value):
            raise ValidationError(
                f'All items in a setting {self.name} must strings'
            )

        return value


class BoolSetting(Setting):
    def __init__(
        self,
        default: Optional[bool] = None,
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
        default: Optional[int] = None,
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
        default: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[float]:
        """"""  # Remove the parents docstring about overriding
        if not isinstance(value, float):
            raise ValidationError(f'A value for setting {self.name} must be a float')

        return value


# Spec
class ConfigSpec:
    """A set of settings specifying some config."""

    def __init__(
        self,
        settings_iterable: Iterable[Setting],
    ):
        settings_list = list(settings_iterable)
        self.settings = {
            setting.name: setting
            for setting in settings_list
        }
        if len(self.settings) != len(settings_list):
            raise ValueError('All settings must have unique names')

    def validate_setting(self, config: Config, setting_name: str):
        """Validate one setting of a config."""

        try:
            setting = self.settings[setting_name]
        except KeyError as exc:
            raise ValueError(f'Unknown setting, not in config spec: {setting_name}') from exc

        try:
            value = config[setting_name]
        except KeyError as exc:
            value = MISSING

        return setting.validate_value(value)

    def validate_config(self, config: Config, allow_extra: bool = False):
        """Validate all settings of a config."""

        extra_fields = frozenset(config) - frozenset(self.settings)
        if extra_fields and not allow_extra:
            raise ValidationError(f'Unexpected fields in the config: {extra_fields}')

        result = {}
        for setting_name in self.settings:
            result[setting_name] = self.validate_setting(config, setting_name)

        return result


class SpecValidatedConfig(CompositeConfig):
    """An all-in-one class that allows to specify settings and validate values;
    takes an iterable of configs as its source of values.

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

    SPEC = None
    """ConfigSpec of this config."""

    def __init_subclass__(cls, **kwargs):  # pylint: disable=unused-argument
        if getattr(cls, 'SPEC', None) is not None:
            return

        settings = [
            attr
            for attr in cls.__dict__.values()
            if isinstance(attr, Setting)
        ]
        spec = ConfigSpec(settings)
        cls.SPEC = spec

    def __init__(self, subconfigs: Iterable[Config], validate=True):
        super().__init__(subconfigs)

        # Store a second composite config that can be passed to spec validation
        # as a plain ordinary config
        self._composite_config = CompositeConfig([])
        self._composite_config.subconfigs = self.subconfigs

        if validate:
            self.validate()

    def validate(self):
        """Revalidate this config according to the spec."""
        self.SPEC.validate_config(self._composite_config, self.allow_extra)

    def __getitem__(self, item):
        value = self.SPEC.validate_setting(self._composite_config, item)

        if value is MISSING:
            raise KeyError(f'Key {item} not found')

        return value

    def __iter__(self):
        return (key for key in self.SPEC.settings if self.SPEC.validate_setting(self, key))

    def __len__(self):
        return len(list(self.__iter__()))

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __repr__(self):
        snapshot = self.snapshot()
        return f'<{self.__class__.__name__} {snapshot}>'
