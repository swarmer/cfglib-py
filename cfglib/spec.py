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
class MISSING:
    """A singleton marker object denoting that a setting value is (or should be) absent.
    Absence here means not being in the config at all (raising KeyError on access).

    Use the class itself, creating instances is useless.
    """

    def __new__(cls, *args, **kwargs):
        raise ValueError('Singleton marker classes shouldn\'t be instantiated')


class MissingSettingAction(enum.Enum):
    # If a setting is missing:
    ERROR = enum.auto()  # Raise an error
    USE_DEFAULT = enum.auto()  # Set it to the provided default
    LEAVE = enum.auto()  # Leave as it is (missing or None)


ERROR = MissingSettingAction.ERROR
USE_DEFAULT = MissingSettingAction.USE_DEFAULT
LEAVE = MissingSettingAction.LEAVE


# Exceptions
class ValidationError(Exception):
    pass


# Setting types
class Setting:
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

    def validate_value(self, value: Any) -> Any:
        if value is MISSING:
            if self.on_missing is ERROR:
                raise ValidationError(f'Config field {self.name} missing')
            elif self.on_missing is USE_DEFAULT:
                if self.default is MISSING:
                    raise ValidationError(
                        f'Config field {self.name} missing and no default is provided'
                    )

                value = self.default
            elif self.on_missing is LEAVE:
                value = MISSING
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

                value = self.default
            elif self.on_null is LEAVE:
                value = None
            else:
                raise ValueError(f'Invalid on_null choice in field {self.name}')

        return self.validate_value_custom(value)

    def validate_value_custom(self, value: Any) -> Any:
        return value


class StringSetting(Setting):
    def __init__(
        self,
        default: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(default=default, **kwargs)

    def validate_value_custom(self, value: Any) -> Optional[str]:
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
        if not isinstance(value, float):
            raise ValidationError(f'A value for setting {self.name} must be a float')

        return value


# Spec
class ConfigSpec:
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
        extra_fields = frozenset(config) - frozenset(self.settings)
        if extra_fields and not allow_extra:
            raise ValidationError(f'Unexpected fields in the config: {extra_fields}')

        for setting_name in self.settings:
            self.validate_setting(config, setting_name)


class SpecValidatedConfig(CompositeConfig):  # pylint: disable=too-many-ancestors
    allow_extra = False
    SPEC = None

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
        self.SPEC.validate_config(self, self.allow_extra)

    def __getitem__(self, item):
        return self.SPEC.validate_setting(self._composite_config, item)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __repr__(self):
        snapshot = self.snapshot()
        return f'<{self.__class__.__name__} {snapshot}>'
