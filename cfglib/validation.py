from typing import *


__all__ = [
    'ValidationContext',
    'Validator',
    'ValidationError',

    'value_type',
]


class ValidationContext:
    def __init__(self, field_name: Optional[str]):
        self.field_name = field_name


Validator = Callable[[ValidationContext, Any], Any]


# Exceptions
class ValidationError(Exception):
    """Raised when a setting value is not valid according to the setting parameters"""
    pass


def value_type(type_spec: Union[type, Tuple[type, ...]]):
    def _type_validator(ctx: ValidationContext, value: Any) -> Any:
        if not isinstance(value, type_spec):
            if isinstance(type_spec, type):
                expected = type_spec.__name__
            else:
                expected = f'one of: {", ".join(t.__name__ for t in type_spec)}'

            raise ValidationError(
                f'The type of a value for setting {ctx.field_name or "<?>"}'
                f' must be {expected}'
            )

        return value

    return _type_validator


def one_of(options: Iterable[Any]):
    def _oneof_validator(ctx: ValidationContext, value: Any) -> Any:
        if value not in options:
            expected = f'one of: {", ".join(map(repr, options))}'
            raise ValidationError(
                f'A value for setting {ctx.field_name or "<?>"} must be {expected}'
            )

        return value

    return _oneof_validator
