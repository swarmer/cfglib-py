from pytest import raises

import cfglib


def test_dict_config():
    data = {'a': 3, 'b': 4}
    dc1 = cfglib.DictConfig(data)
    dcs = dc1.snapshot()
    assert dcs is not dc1
    assert dcs == data

    data['a'] = 9
    assert dcs != data


def test_proxy_config():
    data = {'a': 3, 'b': 4}
    proxy = cfglib.ProxyConfig(data)
    assert proxy == data
    assert len(proxy) == 2

    data['a'] = 9
    assert proxy == data
    assert proxy['a'] == 9

    del proxy['a']
    with raises(KeyError):
        _ = proxy['a']


def test_proxy_cfg_reload():
    source_cfg = cfglib.DictConfig({
        'a': 4,
        'b': 5,
        'irrelevant_key': 6,
    })
    cached_cfg = cfglib.CachingConfig(source_cfg)
    proxy_cfg = cfglib.ProxyConfig(cfglib.CompositeConfig([cached_cfg]))

    assert proxy_cfg['a'] == 4

    source_cfg['a'] = 11
    assert proxy_cfg['a'] == 4

    proxy_cfg.reload()
    assert proxy_cfg['a'] == 11


def test_proxy_immutable():
    data = {'a': 3, 'b': 4}
    proxy = cfglib.ProxyConfig(cfglib.CompositeConfig([cfglib.DictConfig(data)]))

    with raises(TypeError):
        proxy['a'] = 0

    with raises(TypeError):
        del proxy['a']


def test_caching_config():
    source_cfg = cfglib.DictConfig({'x': 1})
    cached_cfg = cfglib.CachingConfig(source_cfg)
    assert cached_cfg['x'] == 1

    source_cfg['x'] = 2
    assert cached_cfg['x'] == 1

    cached_cfg.reload()
    assert cached_cfg['x'] == 2


def test_composite_config():
    composite_config = cfglib.CompositeConfig([
        cfglib.DictConfig({'x': 'default', 'y': 'lower_prio_value'}),
        cfglib.DictConfig({'x': 'override', 'z': 'high_prio_value'}),
    ])
    assert composite_config['x'] == 'override'
    assert composite_config['y'] == 'lower_prio_value'
    assert composite_config['z'] == 'high_prio_value'

    with raises(KeyError):
        _ = composite_config['unknown']

    assert composite_config.snapshot() == {
        'x': 'override',
        'y': 'lower_prio_value',
        'z': 'high_prio_value',
    }
    assert len(composite_config) == 3

    assert 'CompositeConfig' in repr(composite_config)
