import cfglib


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
