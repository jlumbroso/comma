
# MapGetter from extradict by Joao S. O. Bueno <gwidion@gmail.com>
#
# Originally from: https://github.com/jsbueno/extradict
#
# Snapshot of the submodule "MapGetter" included here with attribution and
# no modification, in compliance with LGPLv3 license. (Why reinvent the
# wheel when someone's written very nice code?! :-)


import sys
import threading

from collections import defaultdict
_sentinel = object()


class _PseudoModule(object):
    def __init__(self, mapping, default=_sentinel):
        try:
            self.__dict__ = mapping
        except TypeError:
            self._obj = mapping
        else:
            self._obj = _sentinel
        self._default = default

    def getlines(self, file):
        return ""

    def __getattr__(self, attr):
        if self._obj is not _sentinel:
            try:
                return getattr(self._obj, attr)
            except AttributeError:
                if _default is _sentinel:
                    raise AttributeError("Object '{}' has no attribute '{}' ".format(type(self._obj), attr ))
        if self._default is _sentinel:
            # Try to extract a value from mapping, which could be a
            # defaultdict or some similar mapping:
            try:
                value = self.__dict__[attr]
            except KeyError:
                raise AttributeError("Mapping '{}' has no '{}' key".format(type(self.mapping), attr ))
            return value
        if not callable(self._default):
            return self._default
        try:
            value = self._default(attr)
        except TypeError:
            # try default dict style argumentless default factory:
            value = self._default()
        return value


class MapGetter(object):
    """
    A context manager to allow one to "import" variables from a mapping or
    factory function. This helps preserve DRY principle:
    # Example:
    >>> a = dict(b=1, c=2)
    >>> with MapGetter(a) as blah:
    ...    from blah import b, c
    >>> print((b, c))
    (1, 2)
    It is intesresting to note that it will work for ordinary attributes
    from Python objects, and, as well, for constant names inside a Python
    enum.Enum class. That may be the major use case of this:
    In[1]: import enum
    In [2]: from extradict import MapGetter
    In 43]: class Colors(enum.Enum):
        ...:     RED = 1, 0, 0
        ...:     GREEN = 0, 1, 0
        ...:     BLUE = 0, 0, 1
        ...:
    In [4]: with MapGetter(Colors):
        ...:     from Colors import RED, GREEN, BLUE
        ...:
    In [5]: RED, GREEN, BLUE
    Out[5]: (<Colors.RED: (1, 0, 0)>, <Colors.GREEN: (0, 1, 0)>, <Colors.BLUE: (0, 0, 1)>)
    """
    def __init__(self, mapping=None, default=_sentinel):
        if mapping is None and default is _sentinel:
            raise TypeError("MapGetter must be called with at least one of mapping or default (value/factory function)")
        self.builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        self.mapping = mapping if mapping is not None else {}
        self.default = default

    def __enter__(self):
        self.original_import = self.builtins["__import__"]
        self.builtins["__import__"] = self._map_getter
        self._thread = threading.current_thread()
        return self.mapping

    def _map_getter(self, name, globals_, locals_, from_list, level=-1):
        # "from_list" gets the names wanted in the "import ... from ... " statement,
        # however, they are not actually expected to be returned.
        # the fact the remainer of the import machinery does not use them
        # makes it worth to keep this implementation using a __import__ monkey patch -
        # no other func gets "from_list" and all the machinery expects the actual
        # module to be created on sys.modules - which we don't want.

        # FIXME: Make this asyncio safe as well.
        # (May wait for Python 3.7 with PEP-555 implemented)
        if threading.current_thread() != self._thread or sys._getframe().f_back.f_locals.get(name, None) is not self.mapping:
            return self.original_import(name, globals_, locals_, from_list, level)
        return _PseudoModule(self.mapping, self.default)

    def __exit__(self, type, value, traceback):
        self.builtins["__import__"] = self.original_import
        return False
