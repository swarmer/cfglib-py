import cfglib


def test_dictconfig():
    data = {'a': 3, 'b': 4}
    dc1 = cfglib.DictConfig(data)
    dcs = dc1.snapshot()
    assert dcs is not dc1
    assert dcs == data


def test_composite_config():
    composite_config = cfglib.CompositeConfig([
        cfglib.DictConfig({'x': 'default'}),
        cfglib.EnvConfig(),
        cfglib.DictConfig({'x': 'override'}),
    ])
    assert composite_config['x'] == 'override'
