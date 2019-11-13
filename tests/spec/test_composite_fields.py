import pytest

import cfglib


def _one_field_cfg(setting: cfglib.Setting, data: dict) -> cfglib.SpecValidatedConfig:
    class _Config(cfglib.SpecValidatedConfig):  # type: ignore
        allow_extra = False

        SPEC = cfglib.ConfigSpec([setting])

    return _Config([cfglib.DictConfig(data)])


def test_dict_settings():
    cfg = _one_field_cfg(
        cfglib.DictSetting(name='x'),
        {'x': {}}
    )
    assert cfg.x == {}

    cfg = _one_field_cfg(
        cfglib.DictSetting(name='x'),
        {'x': {5: 6}}
    )
    assert cfg.x == {5: 6}

    with pytest.raises(cfglib.ValidationError):
        _ = _one_field_cfg(
            cfglib.DictSetting(name='x'),
            {'x': []}
        )


def test_list_settings():
    cfg = _one_field_cfg(
        cfglib.ListSetting(name='x'),
        {'x': []}
    )
    assert cfg.x == []

    cfg = _one_field_cfg(
        cfglib.ListSetting(name='x'),
        {'x': [1]}
    )
    assert cfg.x == [1]

    with pytest.raises(cfglib.ValidationError):
        _ = _one_field_cfg(
            cfglib.ListSetting(name='x'),
            {'x': {}}
        )


def test_list_on_empty():
    cfg = _one_field_cfg(
        cfglib.ListSetting(name='x'),
        {'x': []}
    )
    assert cfg.x == []

    with pytest.raises(cfglib.ValidationError):
        _ = _one_field_cfg(
            cfglib.ListSetting(name='x', on_empty=cfglib.ERROR),
            {'x': []}
        )

    with pytest.raises(cfglib.ValidationError):
        _ = _one_field_cfg(
            cfglib.ListSetting(name='x', on_empty=cfglib.USE_DEFAULT),
            {'x': []}
        )

    cfg = _one_field_cfg(
        cfglib.ListSetting(name='x', default=[5], on_empty=cfglib.USE_DEFAULT),
        {'x': []}
    )
    assert cfg.x == [5]

    cfg = _one_field_cfg(
        cfglib.ListSetting(name='x', on_empty=cfglib.LEAVE),
        {'x': []}
    )
    assert cfg.x == []
