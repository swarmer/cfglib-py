from pytest import raises

import cfglib
from cfglib.sources.env import EnvConfigProjection


def test_custom_projection():
    class Projection(cfglib.ConfigProjection):
        def is_relevant_key(self, key: str) -> bool:
            return not key.startswith('IRRELEVANT_') and key.isupper()

        def is_relevant_sourcekey(self, sourcekey: str) -> bool:
            return not sourcekey.startswith('irrelevant_') and sourcekey.islower()

        def key_to_sourcekey(self, key: str) -> str:
            return key.lower()

        def sourcekey_to_key(self, sourcekey: str) -> str:
            return sourcekey.upper()

    source_cfg = cfglib.DictConfig({
        'a': 4,
        'b': 5,
        'irrelevant_key': 6,
    })

    projected_cfg = cfglib.ProjectedConfig(source_cfg, Projection())

    assert projected_cfg['A'] == 4
    assert projected_cfg['B'] == 5
    projected_cfg['X'] = 8
    assert projected_cfg['X'] == 8
    assert source_cfg['x'] == 8

    with raises(KeyError):
        _ = projected_cfg['a']

    with raises(KeyError):
        _ = projected_cfg['b']

    with raises(KeyError):
        _ = projected_cfg['irrelevant_key']

    with raises(KeyError):
        _ = projected_cfg['IRRELEVANT_KEY']

    with raises(KeyError):
        projected_cfg['x'] = 8


def test_basic_projection():
    projection = cfglib.BasicConfigProjection(
        is_relevant_sourcekey=lambda sk: not sk.startswith('irrelevant_'),
        key_to_sourcekey=str.lower,
        sourcekey_to_key=str.upper,
    )

    source_cfg = cfglib.DictConfig({
        'a': 4,
        'b': 5,
        'irrelevant_key': 6,
    })

    projected_cfg = cfglib.ProjectedConfig(source_cfg, projection)

    assert projected_cfg['A'] == 4
    assert projected_cfg['B'] == 5
    projected_cfg['X'] = 8
    assert projected_cfg['X'] == 8
    assert source_cfg['x'] == 8

    with raises(KeyError):
        _ = projected_cfg['a']

    with raises(KeyError):
        _ = projected_cfg['b']

    with raises(KeyError):
        _ = projected_cfg['irrelevant_key']

    with raises(KeyError):
        _ = projected_cfg['IRRELEVANT_KEY']

    with raises(KeyError):
        projected_cfg['x'] = 8


def test_env_projection():
    projection = EnvConfigProjection(prefix='prefix_')

    source_cfg = cfglib.DictConfig({
        'prefix_a': 4,
        'b': 5,
    })

    projected_cfg = cfglib.ProjectedConfig(source_cfg, projection)

    assert projected_cfg['a'] == 4
    projected_cfg['x'] = 8
    assert projected_cfg['x'] == 8
    assert source_cfg['prefix_x'] == 8

    with raises(KeyError):
        _ = projected_cfg['prefix_a']

    with raises(KeyError):
        _ = projected_cfg['b']

    with raises(KeyError):
        _ = projected_cfg['prefix_b']
