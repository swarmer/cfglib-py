import pytest

import cfglib


def _one_field_cfg(setting: cfglib.Setting, data: dict) -> cfglib.SpecValidatedConfig:
    class _Config(cfglib.SpecValidatedConfig):
        allow_extra = False

        SPEC = cfglib.ConfigSpec([setting])

    return _Config([cfglib.DictConfig(data)])


def test_spec_validated_config():
    class TestConfig(cfglib.SpecValidatedConfig):
        allow_extra = False

        string = cfglib.StringSetting(default=None)
        string_list = cfglib.StringListSetting(default=None)
        boolean = cfglib.BoolSetting(default=None)
        integer = cfglib.IntSetting(default=None)
        floating = cfglib.FloatSetting(default=None)

    valid_data = {
        'string': 'abc',
        'string_list': ['s1', 's2'],
        'boolean': True,
        'integer': 8,
        'floating': 0.5,
    }

    cfg = TestConfig([cfglib.DictConfig(valid_data)])

    with pytest.raises(KeyError):
        _ = cfg['STRING']

    with pytest.raises(AttributeError):
        _ = cfg.STRING

    assert cfg.snapshot() == valid_data
    assert len(cfg) == 5
    assert list(cfg) == ['string', 'string_list', 'boolean', 'integer', 'floating']
    assert 'TestConfig' in repr(cfg)

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'string': 1})])

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'string_list': 'str'})])

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'string_list': [1, 'str']})])

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'boolean': 0})])

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'integer': 1.0})])

    with pytest.raises(cfglib.ValidationError):
        _ = TestConfig([cfglib.DictConfig({**valid_data, 'floating': 0})])


def test_on_missing_handlers():
    with pytest.raises(ValueError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_missing='qwerty'),
            {},
        )

    with pytest.raises(cfglib.ValidationError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x'),
            {},
        )

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1),
        {},
    )
    assert cfg.x == 1

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1),
        {'x': 2},
    )
    assert cfg.x == 2

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', on_missing=cfglib.ERROR),
        {'x': 2},
    )
    assert cfg.x == 2

    with pytest.raises(cfglib.ValidationError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_missing=cfglib.ERROR),
            {},
        )

    with pytest.raises(cfglib.ValidationError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_missing=cfglib.USE_DEFAULT),
            {},
        )

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_missing=cfglib.USE_DEFAULT),
        {},
    )
    assert cfg.x == 1

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_missing=cfglib.USE_DEFAULT),
        {'x': 2},
    )
    assert cfg.x == 2

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', on_missing=cfglib.LEAVE),
        {},
    )
    with pytest.raises(KeyError):
        _ = cfg['x']

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_missing=cfglib.LEAVE),
        {},
    )
    with pytest.raises(KeyError):
        _ = cfg['x']

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_missing=cfglib.LEAVE),
        {'x': 2},
    )
    assert cfg.x == 2


def test_on_null_handlers():
    with pytest.raises(ValueError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_null='qwerty'),
            {'x': None},
        )

    cfg = _one_field_cfg(
        cfglib.Setting(name='x'),
        {'x': None},
    )
    assert cfg.x is None

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1),
        {'x': None},
    )
    assert cfg.x is None

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1),
        {'x': 2},
    )
    assert cfg.x == 2

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', on_null=cfglib.ERROR),
        {'x': 2},
    )
    assert cfg.x == 2

    with pytest.raises(cfglib.ValidationError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_null=cfglib.ERROR),
            {'x': None},
        )

    with pytest.raises(cfglib.ValidationError):
        cfg = _one_field_cfg(
            cfglib.Setting(name='x', on_null=cfglib.USE_DEFAULT),
            {'x': None},
        )

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_null=cfglib.USE_DEFAULT),
        {'x': None},
    )
    assert cfg.x == 1

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_null=cfglib.USE_DEFAULT),
        {'x': 2},
    )
    assert cfg.x == 2

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', on_null=cfglib.LEAVE),
        {'x': None},
    )
    assert cfg['x'] is None

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_null=cfglib.LEAVE),
        {'x': None},
    )
    assert cfg['x'] is None

    cfg = _one_field_cfg(
        cfglib.Setting(name='x', default=1, on_null=cfglib.LEAVE),
        {'x': 2},
    )
    assert cfg.x == 2


def test_missing_keys():
    class EmptyConfig(cfglib.SpecValidatedConfig):
        allow_extra = False

        setting = cfglib.StringSetting(on_missing=cfglib.LEAVE)

    empty_cfg = EmptyConfig([cfglib.DictConfig({})])
    with pytest.raises(KeyError):
        _ = empty_cfg['setting']


# pylint: disable=unused-variable
def test_setting_names():
    # Python raises RuntimeError when __set_name__ fails
    with pytest.raises(RuntimeError):
        class NameMismatchedConfig(cfglib.SpecValidatedConfig):
            name1 = cfglib.StringSetting(name='name2')

    with pytest.raises(ValueError):
        class DuplicateSettingConfig(cfglib.SpecValidatedConfig):
            SPEC = cfglib.ConfigSpec([
                cfglib.StringSetting(name='X'),
                cfglib.StringSetting(name='X'),
            ])

    with pytest.raises(ValueError):
        class MissingNameConfig(cfglib.SpecValidatedConfig):
            SPEC = cfglib.ConfigSpec([
                cfglib.StringSetting(),
            ])

    with pytest.raises(ValueError):
        class MaliciousSetting(cfglib.Setting):
            def __set_name__(self, owner, name):
                self.name = 'malicious'

        class DeviouslyMismatchedConfig(cfglib.SpecValidatedConfig):
            setting = MaliciousSetting()

    class MixedSettingConfig(cfglib.SpecValidatedConfig):
        allow_extra = False

        SPEC = cfglib.ConfigSpec([
            cfglib.StringSetting(name='X'),
        ])

        Y = cfglib.StringSetting()

    with pytest.raises(cfglib.ValidationError):
        _ = MixedSettingConfig([cfglib.DictConfig({'Y': 'value'})])

    cfg = MixedSettingConfig([cfglib.DictConfig({'X': 'value'})])
    assert cfg.X == 'value'


def test_raw_setting():
    class UndecidedConfig(cfglib.SpecValidatedConfig):
        anything = cfglib.Setting()

    cfg = UndecidedConfig([cfglib.DictConfig({'anything': 'string'})])
    assert cfg.anything == 'string'

    cfg2 = UndecidedConfig([cfglib.DictConfig({'anything': 4})])
    assert cfg2.anything == 4

    cfg2.anything = {}
    assert cfg2.anything == {}


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
        _ = TestConfig([cfglib.DictConfig({'X': 'x_value', 'Y': 6})])


def test_cfg_with_settings_attributes():
    class TestConfig(cfglib.SpecValidatedConfig):
        X = cfglib.StringSetting()

    cfg = TestConfig([cfglib.DictConfig({'X': 'x_value'})])
    assert cfg.X == 'x_value'
    assert isinstance(TestConfig.X, cfglib.StringSetting)


def test_cfg_with_spec_attributes():
    class TestConfig(cfglib.SpecValidatedConfig):
        SPEC = cfglib.ConfigSpec([
            cfglib.StringSetting(name='X')
        ])

    cfg = TestConfig([cfglib.DictConfig({'X': 'x_value'})])
    assert cfg.X == 'x_value'
    assert isinstance(cfg.SPEC.settings['X'], cfglib.StringSetting)
