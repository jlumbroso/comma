import collections

import comma.exceptions


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaFile"
]


class CommaFile(object):
    """
    """

    # internal instance variable containing header
    _header = None

    def __init__(self, header=None):
        self._header = header

    @property
    def header(self):
        return self._header
