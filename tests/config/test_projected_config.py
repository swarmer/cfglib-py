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


def test_non_bijective():
    projection = cfglib.BasicConfigProjection(
        is_relevant_key=lambda k: not k.startswith('IRRELEVANT'),
        is_relevant_sourcekey=lambda sk: not sk.startswith('irrelevant_'),
        key_to_sourcekey=str.lower,
        sourcekey_to_key=str.upper,
    )

    source_cfg = cfglib.DictConfig({
        'a': 4,
        'B': 5,
        'irrelevant_key': 6,
    })

    projected_cfg = cfglib.ProjectedConfig(source_cfg, projection)
    with raises(KeyError):
        _ = projected_cfg['B']

    with raises(KeyError):
        del projected_cfg['B']

    assert len(projected_cfg) == 1
    assert list(projected_cfg) == ['A']


def test_basic_projection():
    projection = cfglib.BasicConfigProjection(
        is_relevant_key=lambda k: not k.startswith('IRRELEVANT'),
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

    assert len(projected_cfg) == 2

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
        del projected_cfg['irrelevant_key']

    with raises(KeyError):
        del projected_cfg['IRRELEVANT_KEY']

    with raises(KeyError):
        projected_cfg['x'] = 8

    assert 'a' in source_cfg
    del projected_cfg['A']
    with raises(KeyError):
        _ = projected_cfg['A']
    assert 'a' not in source_cfg


def test_identity_projection():
    projection = cfglib.BasicConfigProjection()

    source_cfg = cfglib.DictConfig({
        'a': 4,
        'b': 5,
        'irrelevant_key': 6,
    })
    projected_cfg = cfglib.ProjectedConfig(source_cfg, projection)

    assert len(projected_cfg) == 3

    assert projected_cfg['a'] == 4
    assert projected_cfg['b'] == 5
    projected_cfg['X'] = 8
    assert projected_cfg['X'] == 8
    assert source_cfg['X'] == 8
    assert projected_cfg['irrelevant_key'] == 6

    with raises(KeyError):
        _ = projected_cfg['A']

    with raises(KeyError):
        _ = projected_cfg['B']

    with raises(KeyError):
        _ = projected_cfg['IRRELEVANT_KEY']

    assert source_cfg['irrelevant_key'] == 6
    del projected_cfg['irrelevant_key']
    assert 'irrelevant_key' not in source_cfg

    with raises(KeyError):
        del projected_cfg['IRRELEVANT_KEY']

    projected_cfg['x'] = 8
    assert source_cfg['x'] == 8

    assert 'a' in source_cfg
    del projected_cfg['a']
    with raises(KeyError):
        _ = projected_cfg['a']
    assert 'a' not in source_cfg


def test_projected_immutable():
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
    projected_cfg = cfglib.ProjectedConfig(cfglib.CompositeConfig([source_cfg]), projection)

    with raises(TypeError):
        projected_cfg['x'] = 8

    with raises(TypeError):
        del projected_cfg['a']


def test_projected_cfg_reload():
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
    cached_cfg = cfglib.CachingConfig(source_cfg)
    projected_cfg = cfglib.ProjectedConfig(cfglib.CompositeConfig([cached_cfg]), projection)

    assert projected_cfg['A'] == 4

    source_cfg['a'] = 11
    assert projected_cfg['A'] == 4

    projected_cfg.reload()
    assert projected_cfg['A'] == 11


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
