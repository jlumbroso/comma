import collections
import collections.abc
import typing

import comma.classes.file
import comma.exceptions
import comma.helpers


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaRow"
]


# noinspection PyUnresolvedReferences
class CommaRow(collections.UserList, list, collections.UserDict):
    """
    Contains a single row of a CSV file; the row contains only data
    stored in the row, and a pointer to a parent file structure (which
    stores all the extraneous information, such as dialect and header).
    """

    # parent CSV file
    _parent = None  # type: comma.classes.file.CommaFile

    # (optionally) sequence of slicing operations
    _slice_list = None

    # (optionally) original row reference
    _original = None

    def __init__(
        self,
        initlist=None,
        parent: typing.Optional[object] = None,
        slice_list=None,
        original=None,
        *args,
        **kwargs
    ):
        # initialize internal attributes
        self._parent = typing.cast(comma.classes.file.CommaFile, parent)
        self._slice_list = slice_list if slice_list is not None else list()
        self._original = self if original is None else original

        # call base constructor for lists
        ret = super().__init__(initlist, *args, **kwargs)

    @property
    def header(self):
        """
        """
        if self._parent is None:
            raise comma.exceptions.CommaOrphanRowException(
                "row not linked to parent structure")

        if self._parent.header is None:
            raise comma.exceptions.CommaNoHeaderException(
                "CSV file does not appear to have a header and "
                "none was provided; key-based access not possible")

        return comma.helpers.multislice_sequence(
            sequence=self._parent.header,
            slice_list=self._slice_list)

    def keys(self):
        return collections.abc.KeysView(self.header)

    def values(self):
        return dict(self).values()

    def items(self):
        return dict(self).items()

    def __key_to_column_id(self, key):
        """

        """

        # CASE 1: a regular list index
        if type(key) is int:
            return key

        # CASE 2: a slice
        if type(key) is slice:
            slice_start = key.start
            slice_stop = key.stop

            if slice_start is not None:
                slice_start = self.__key_to_column_id(slice_start)

            if slice_stop is not None:
                slice_stop = self.__key_to_column_id(slice_stop)

            return slice(slice_start, slice_stop, key.step)

        # CASE 3: a dictionary key
        header = self.header

        if not key in header:
            raise comma.exceptions.CommaKeyError(
                "{key} is not in header: {header}".format(
                    key=key,
                    header=header))

        key_index = header.index(key)

        return key_index

    # FIXME: add __iter__
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __setitem__(self, key, value):
        ##print("CommaRow.__setitem__", hex(id(self)), key, type(key), "<==", value, type(value))

        # FIXME: figure out how to make slices have headers
        key_index = self.__key_to_column_id(key)
        if type(key) is str and self._original != self:
            ##print(type(key) is str and self._original != self)
            return self._original.__setitem__(key, value)
        ret = super().__setitem__(key_index, value)
        return ret

    def __getitem__(self, key):
        ##print("CommaRow.__getitem__", hex(id(self)), key, type(key))

        # FIXME: figure out how to make slices have headers
        key_index = self.__key_to_column_id(key)
        ret = super().__getitem__(key_index)

        if type(key) is slice:
            ret._parent = self._parent
            ret._slice_list.append(key)
            ret._original = self._original

        return ret

    def __repr__(self):
        # display as list or row
        try:
            self.keys()
        except comma.exceptions.CommaException:
            return super().__repr__()
        return dict(self).__repr__()
