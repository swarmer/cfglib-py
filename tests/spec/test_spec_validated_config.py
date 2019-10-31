import pytest

import cfglib


def test_extra_values_allowed():
    class TestConfig(cfglib.SpecValidatedConfig):
        allow_extra = True

        X = cfglib.StringSetting()

    cfg = TestConfig([cfglib.DictConfig({'X': 'x_value', 'Y': 6})])
    cfg.validate()


def test_extra_values_disallowed():
    class TestConfig(cfglib.SpecValidatedConfig):
        allow_extra = False

        X = cfglib.StringSetting()

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.ProxyConfig({'X': 'x_value', 'Y': 6})])


def test_cfg_with_settings_attributes():
    class TestConfig(cfglib.SpecValidatedConfig):
        X = cfglib.StringSetting()

    cfg = TestConfig([cfglib.ProxyConfig({'X': 'x_value'})])
    assert cfg.X == 'x_value'
    assert isinstance(TestConfig.X, cfglib.StringSetting)


def test_cfg_with_spec_attributes():
    class TestConfig(cfglib.SpecValidatedConfig):
        SPEC = cfglib.ConfigSpec([
            cfglib.StringSetting(name='X')
        ])

    cfg = TestConfig([cfglib.ProxyConfig({'X': 'x_value'})])
    assert cfg.X == 'x_value'
    assert isinstance(cfg.SPEC.settings['X'], cfglib.StringSetting)
