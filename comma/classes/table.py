import collections

import comma.abstract
import comma.classes.slices
import comma.exceptions
import comma.helpers
import comma.methods

__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaTable"
]


class CommaTable(collections.UserList, list, collections.UserDict, comma.abstract.CloneableCollection):
    """
    Contains a table from a CSV file.
    """

    # parent CommaFile object from which to get settings and headers
    _parent = None

    def __init__(self, initlist=None, parent=None, *args, **kwargs):
        self._parent = parent
        ret = super().__init__(initlist, *args, **kwargs)
        return ret

    def to_html(self):
        """
        Returns an HTML string representation of the table data.
        """

        # NOTE: should we use tabulator or prettytable instead of reinventing?

        # contain all the rows
        table_rows = []

        if self.has_header:
            table_rows = [comma.helpers.zip_html_tag(data=self.header, in_pattern="<th>{}</th>")]

        for row in self.data:
            table_rows += [comma.helpers.zip_html_tag(data=row, indent=4)]

        table_html = "<table style='text-align: left;'>{}</table>".format("\n\n".join(table_rows))

        return table_html

    def _repr_html_(self):
        """
        Returns an HTML string representation of the table data, this is a magic
        helper method for IPython/Jupyter notebooks.
        """
        return self.to_html()

    def dump(self, filename=None, fp=None):
        return comma.methods.dump(self, filename=filename, fp=fp)

    @property
    def has_header(self):
        """

        """
        return not (self._parent is None) and not (self._parent.header is None)

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
        ##print("CommaTable.__getitem__", hex(id(self)), key, type(key))

        # if getting a specific row: Return underlying CommaRow
        if type(key) is int:
            return super().__getitem__(key)

        # if getting a range of rows: Create a new CommaTable to
        # serve the subset of rows; since the rows will be the
        # same references, any changes will propagate to the whole
        # file (unlike when creating a slice, which usually creates
        # a copy)

        if type(key) is slice:
            return self.clone(newdata=self.data[key])

        # field-slice, i.e. csv_table["street"]
        if type(key) is str:
            return comma.classes.slices.CommaFieldSlice(
                initlist=self,
                parent=self._parent,
                field_name=key)

    def __setitem__(self, key, value):
        ##print("CommaTable.__setitem__", hex(id(self)), key, type(key), "<==", value, type(value))

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