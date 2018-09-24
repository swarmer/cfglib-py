import pytest

import cfglib


def test_dictconfig():
    d = {'a': 3, 'b': 4}
    dc1 = cfglib.DictConfig(d)
    dcs = dc1.snapshot()
    assert dcs is not dc1
    assert dcs == d


def test_composite_config():
    composite_config = cfglib.CompositeConfig([
        cfglib.DictConfig({'x': 'override'}),
        cfglib.EnvConfig(),
        cfglib.DictConfig({'x': 'default'}),
    ])
    assert composite_config['x'] == 'override'
