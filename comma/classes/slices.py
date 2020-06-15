import collections

import comma.exceptions


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaFieldSlice",
    "CommaRowSlice"
]


class CommaFieldSlice(list, collections.UserList):
    """
    Contains a column of a CSV file.
    """

    # parent CSV file
    _parent = None

    # field name
    _field_name = None

    def __init__(self, initlist=None, parent=None, field_name=None, *args, **kwargs):

        self._parent = parent
        self._field_name = field_name
        self._field_index = self._parent.header.index(self._field_name)

        ret = super().__init__(initlist, *args, **kwargs)
        return ret

    def __iter__(self):
        for row in super().__iter__():
            yield row[self._field_index]

    def __getitem__(self, key):
        if type(key) is int:
            ret_val = super().__getitem__(key)
            return ret_val[self._field_index]

        elif type(key) is slice:
            ret_slice = super().__getitem__(key)

            return CommaFieldSlice(
                initlist=ret_slice,
                parent=self._parent,
                field_name=self._field_name)

    def __setitem__(self, key, value):
        if type(key) is int:
            row = super().__getitem__(key)
            row[self._field_index] = value

        elif type(key) is slice:
            ret_slice = super().__getitem__(key)

            if len(ret_slice) != len(value):
                raise comma.exceptions.CommaBatchException(
                    ("trying to update a slice ({}) with a "
                     "range of the wrong size ({})").format(
                        len(ret_slice),
                        len(value),
                    ))

            for i in range(len(ret_slice)):
                ret_slice[i][self._field_index] = value[i]

            return ret_slice


class CommaRowSlice(collections.UserList, list, collections.UserDict):
    """
    Contains a column of a CSV file.
    """

    # parent CSV file
    _parent = None

    # header slice
    _header_slice = None

    def __init__(self, initlist=None, parent=None, header_slice=None, *args, **kwargs):

        self._parent = parent
        self._header_slice = header_slice

        ret = super().__init__(initlist, *args, **kwargs)
        return ret

    def __getitem__(self, key):
        ##print("CommaRowSlice.__getitem__", hex(id(self)), key, type(key))

        if type(key) is int:
            ret_val = super().__getitem__(key)
            return ret_val[self._field_index]

        elif type(key) is slice:
            ret_slice = super().__getitem__(key)

            return CommaFieldSlice(
                initlist=ret_slice,
                parent=self._parent,
                field_name=self._field_name)

    def __setitem__(self, key, value):
        ##print("CommaRowSlice.__setitem__", hex(id(self)), key, type(key), "<==", value, type(value))

        if type(key) is int:
            row = super().__getitem__(key)
            row[self._field_index] = value

        elif type(key) is slice:
            ret_slice = super().__getitem__(key)

            if len(ret_slice) != len(value):
                raise comma.exceptions.CommaBatchException(
                    ("trying to update a slice ({}) with a "
                     "range of the wrong size ({})").format(
                        len(ret_slice),
                        len(value),
                    ))

            for i in range(len(ret_slice)):
                ret_slice[i][self._field_index] = value[i]

            return ret_slice
