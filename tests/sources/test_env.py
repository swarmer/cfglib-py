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
