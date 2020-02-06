"""Top-level package for cfglib.

Objects from the `config` and `spec` submodules are reexported to the root, so you can use
e.g. `cfglib.Config`.
"""

__author__ = '''Anton Barkovsky'''
__email__ = 'anton@swarmer.me'
__version__ = '1.0.0'


# pylint: disable=wildcard-import
from .config import *
from .spec import *
