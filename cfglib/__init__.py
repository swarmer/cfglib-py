"""Top-level package for cfglib.

Objects from the `config` and `spec` submodules are reexported to the root, so you can use
e.g. `cfglib.Config`.
"""

__author__ = '''Anton Barkovsky'''
__email__ = 'anton@swarmer.me'
__version__ = '0.2.0a1'


# pylint: disable=wildcard-import
from .config import *
from .spec import *
