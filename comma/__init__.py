
"""
Library to make CSV reading/writing fun and enjoyable!
"""

from comma.config import settings as settings
from comma.methods import dump, dumps
from comma.methods import load
__version__ = "0.5.4"
__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

version_info = tuple(int(v) if v.isdigit()
                     else v for v in __version__.split('.'))
