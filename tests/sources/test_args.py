import pytest

from cfglib.sources.args import ArgsNamespaceConfig


class _Namespace:
    pass


def test_arts_config():
    source = _Namespace()
    source.key1 = 'testval'
    source.KEYUPPER = 1  # pylint: disable=invalid-name

    cfg = ArgsNamespaceConfig(source, uppercase=True)

    with pytest.raises(KeyError):
        _ = cfg['missingkey']

    with pytest.raises(KeyError):
        _ = cfg['KEYUPPER']

    with pytest.raises(KeyError):
        _ = cfg['key1']

    assert cfg['KEY1'] == 'testval'

    assert sorted(cfg) == ['KEY1']
