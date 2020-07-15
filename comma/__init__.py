
"""
Library to make CSV reading/writing fun and enjoyable!
"""

__version__ = "0.1.5"
__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split('.'))

from comma.methods import load
from comma.methods import dump, dumps
from comma.config import settings as settings


import warnings
warnings.warn(
    "Thank you for trying comma. This package is currently in "
    "development (alpha release). If you find any issues, please "
    "report. A final version will be released by mid-July."
)