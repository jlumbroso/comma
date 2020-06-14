import collections

import comma.exceptions


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaTable"
]


class CommaTable(collections.UserList, list, collections.UserDict):
    """
    Contains a table from a CSV file.
    """

    # parent CommaFile object from which to get settings and headers
    _parent = None

    def __init__(self, initlist=None, parent=None, *args, **kwargs):
        self._parent = parent
        ret = super().__init__(initlist, *args, **kwargs)
        return ret

    @property
    def header(self):
        """
        """
        if self._parent is None:
            raise comma.exceptions.CommaOrphanTableException(
                "table not linked to parent structure")

        if self._parent.header is None:
            raise comma.exceptions.CommaNoHeaderException(
                "CSV file does not appear to have a header and "
                "none was provided; key-based access not possible")

        return self._parent.header

    def __getitem__(self, key):
        # FIXME: figure out how to make slices have headers
        if type(key) is int or type(key) is slice:
            return super().__getitem__(key)

        # field-slice, i.e. csv_table["street"]
        if type(key) is str:
            return CommaFieldSlice(
                initlist=self,
                parent=self._parent,
                field_name=key)

    def __setitem__(self, key, value):
        # FIXME: figure out how to make slices have headers
        if type(key) is int or type(key) is slice:
            return super().__setitem__(key, value)

        # field-slice, i.e. csv_table["street"]
        if type(key) is str:

            # check size:
            if len(value) != len(self):
                raise comma.exceptions.CommaBatchException(
                    "not right size")

            for i in range(len(self)):
                self[i][key] = value[i]

            return self