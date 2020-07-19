import collections
import collections.abc
import copy
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
        slice_list: typing.Optional[typing.List[slice]] = None,
        original: typing.Optional[typing.Any] = None,
        *args,
        **kwargs
    ):
        """
        Internal constructor for a `CommaRow` object, which
        takes an `initlist` list (the actual data row) and
        some additional metadata, including the `parent`
        object `CommaFile` object from which the `CommaRow`
        has been loaded---and which may contain additional
        information such as a header.
        """
        # initialize internal attributes
        self._parent = typing.cast(comma.classes.file.CommaFile, parent)
        self._slice_list = slice_list if slice_list is not None else list()
        self._original = self if original is None else original

        # call base constructor for lists
        super().__init__(initlist)

    def __deepcopy__(
        self,
        memodict: typing.Optional[typing.Dict[int, typing.Any]] = None,
    ):
        """

        """
        id_self = id(self)
        if memodict is not None and id_self in memodict:
            return memodict.get(id_self)
        obj = CommaRow(
            initlist=copy.deepcopy(list(self.__iter__())),
            parent=copy.deepcopy(self._parent),
            slice_list=copy.deepcopy(self._slice_list),
            original=self._original
        )
        memodict[id_self] = obj
        return obj

    def __sliced_data(self, data: typing.Sequence = None, enum: bool = False):
        """
        Returns the data (by default, the self's data) sliced
        according to the (possibly `None` or `[]`) internal list
        of slices.
        """

        # default to the internal data
        if data is None:
            data = self.data

        # if enumerate == True, return indices rather than objects
        if enum:
            data = list(range(len(data)))

        return comma.helpers.multislice_sequence(
            sequence=data,
            slice_list=self._slice_list)

    def __len__(self):
        """
        Returns the number of fields stored in this `CommaRow`.
        """
        return len(self.__sliced_data(enum=True))

    def __sliced_dict(self):
        """
        Returns a dictionary-casted version of the `CommaRow` data.
        """
        try:
            header = self.header
        except comma.exceptions.CommaException as exc:
            raise comma.exceptions.CommaNoHeaderException(
                "this operation assumes existence of header which "
                "is unavailable"
            ) from exc

        return dict(zip(
            header,
            self.__sliced_data(),
        ))

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

        return self.__sliced_data(data=self._parent.header)

    def keys(self):
        return collections.abc.KeysView(self.header)

    def values(self):
        return self.__sliced_dict().values()

    def items(self):
        return self.__sliced_dict().items()

    def __key_to_column_id(self, key):
        """
        Internal method that translates a key into a row index.
        """

        # CASE 1: a regular list index
        if type(key) is int:
            # convert from regular index to index after
            # applying multislice operations
            sliced_range = self.__sliced_data(enum=True)
            return sliced_range[key]

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

        # first check there is a header

        try:
            _ = self.header  # validation exceptions
        except comma.exceptions.CommaException as exc:
            raise comma.exceptions.CommaTypeError(
                "no header; therefore this row is like a list: "
                "list indices must be integers or slices, not str"
            ) from exc

        # use the un-multi-sliced header to recover actual
        # index of original header (since we are accessing
        # original rows in self.data)

        header = self._parent.header

        if key not in header:
            raise comma.exceptions.CommaKeyError(
                "{key} is not in header: {header}".format(
                    key=key,
                    header=header))

        key_index = header.index(key)

        return key_index

    # =================================================================

    # As inelegant as it seems, rewriting these operators is necessary
    # to account for the slicing that may take place beneath the scenes
    # to preserve relation to the original row/headers

    def __eq__(self, other):
        # noinspection PyBroadException
        try:
            return list(self).__eq__(list(other))
        except:
            return False

    def __ne__(self, other):
        # noinspection PyBroadException
        try:
            return list(self).__ne__(list(other))
        except:
            return True

    def __ge__(self, other):
        return list(self).__ge__(list(other))

    def __gt__(self, other):
        return list(self).__gt__(list(other))

    def __le__(self, other):
        return list(self).__le__(list(other))

    def __lt__(self, other):
        return list(self).__lt__(list(other))

    # =================================================================

    def __iter__(self):
        ids = range(len(self))
        for i in ids:
            yield self[i]

    def __setitem__(self, key, value):
        ###print("CommaRow.__setitem__", hex(id(self)), key, type(key), value, type(value))

        key_index = self.__key_to_column_id(key)
        if type(key) is str and self._original != self:
            ##print(type(key) is str and self._original != self)
            return self._original.__setitem__(key, value)
        ret = super().__setitem__(key_index, value)
        return ret

    def __add__(self, other):
        casted_self, casted_other = comma.helpers.dict_or_list_many(self, other)
        # self_repr = self.__repr__()
        # print("CommaRow.__add__", self_repr, other, id(other))
        return casted_self.__add__(casted_other)

    def __radd__(self, other):
        casted_self, casted_other = comma.helpers.dict_or_list_many(self, other)
        # self_repr = self.__repr__()
        # print("CommaRow.__radd__", self_repr, other, id(other))
        return casted_other.__add__(casted_self)

    def __getitem__(self, key):


        # FIXME: figure out how to make slices have headers
        key_index = self.__key_to_column_id(key)
        # print("CommaRow.__getitem__", hex(id(self)), key, type(key), "==>", key_index)
        ret = super().__getitem__(key_index)

        if type(key) is slice:
            if comma.settings.SLICE_DEEP_COPY_DATA:
                ret.data = self.data[:]
            else:
                ret.data = self.data
            ret._parent = self._parent
            ret._slice_list = self._slice_list[:] + [key]
            ret._original = self._original

        return ret

    def get(self, key, default=""):
        try:
            return self.__getitem__(key)
        except comma.exceptions.CommaKeyError:
            return default
        except IndexError:
            return default

    def __repr__(self):
        # display as list or row
        try:
            self.keys()
        except comma.exceptions.CommaException:
            return super().__repr__()

        # display as a dict
        dict_repr = dict([(key, self.get(key)) for key in self.header])
        return dict_repr.__repr__()
