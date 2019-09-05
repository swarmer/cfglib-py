import cfglib


def test_dict_config():
    data = {'a': 3, 'b': 4}
    dc1 = cfglib.DictConfig(data)
    dcs = dc1.snapshot()
    assert dcs is not dc1
    assert dcs == data


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
        cfglib.DictConfig({'x': 'default'}),
        cfglib.EnvConfig(),
        cfglib.DictConfig({'x': 'override'}),
    ])
    assert composite_config['x'] == 'override'
