import pytest

import cfglib
from cfglib import validation as val


def test_spec_validated_cfg():
    class TestCfg(cfglib.SpecValidatedConfig):
        a = cfglib.Setting(validators=[val.value_type((str, int))])

    TestCfg({'a': 'string'})
    TestCfg({'a': 42})

    with pytest.raises(cfglib.ValidationError):
        TestCfg({'a': 42.0})


def test_spec():
    spec = cfglib.ConfigSpec([
        cfglib.Setting(name='a', validators=[val.value_type((str, int))]),
    ])

    spec.validate_config(cfglib.DictConfig({'a': 'string'}))
    spec.validate_config(cfglib.DictConfig({'a': 42}))

    with pytest.raises(cfglib.ValidationError):
        spec.validate_config(cfglib.DictConfig({'a': 42.0}))


def test_field():
    field = cfglib.Setting(name='a', validators=[val.value_type((str, int))])

    field.validate_value('string')
    field.validate_value(42)

    with pytest.raises(cfglib.ValidationError):
        field.validate_value(42.0)
