import os

import pytest

from cfglib.sources.env import EnvConfig


# I hope no one has this in their environment
TEST_VAR_NAME = '__cfglib_test_var'


def test_env_config():
    cfg = EnvConfig()
    with pytest.raises(KeyError):
        _ = cfg[TEST_VAR_NAME]

    os.environ[TEST_VAR_NAME] = 'testval'
    assert cfg[TEST_VAR_NAME] == 'testval'

    os.environ[TEST_VAR_NAME] = 'testval2'
    assert cfg[TEST_VAR_NAME] == 'testval2'

    del os.environ[TEST_VAR_NAME]
    with pytest.raises(KeyError):
        _ = cfg[TEST_VAR_NAME]


def test_env_config_projection():
    cfg = EnvConfig(prefix='__CFGLIB_', lowercase=True)

    os.environ[TEST_VAR_NAME.upper()] = 'testval'
    assert cfg['test_var'] == 'testval'

    with pytest.raises(KeyError):
        _ = cfg['TEST_VAR']

    with pytest.raises(KeyError):
        _ = cfg[TEST_VAR_NAME.upper()]

    os.environ['__CFGLIB_test_var_lower'] = 'testval_lower'
    assert cfg.snapshot() == {'test_var': 'testval'}

    cfg['test_var_inserted'] = '9'
    assert os.environ['__CFGLIB_TEST_VAR_INSERTED'] == '9'

    with pytest.raises(KeyError):
        cfg['test_var_inserted_UPPERCASE'] = '10'
