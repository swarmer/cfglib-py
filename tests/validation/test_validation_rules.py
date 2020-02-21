import pytest

import cfglib
from cfglib import validation as val


def test_value_type_multiple():
    field = cfglib.Setting(name='a', validators=[val.value_type((str, bytes))])

    field.validate_value('string')
    field.validate_value(b'bytes')

    with pytest.raises(cfglib.ValidationError):
        field.validate_value(42.0)


def test_value_type_one():
    field = cfglib.Setting(name='a', validators=[val.value_type(str)])

    field.validate_value('string')

    with pytest.raises(cfglib.ValidationError):
        field.validate_value(b'bytes')


def test_one_of():
    field = cfglib.Setting(name='a', validators=[val.one_of([1, "hello"])])

    field.validate_value('hello')

    with pytest.raises(cfglib.ValidationError):
        field.validate_value('string')

    field.validate_value(1)

    with pytest.raises(cfglib.ValidationError):
        field.validate_value(2)
