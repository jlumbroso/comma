
import collections
import typing

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
    Contains a table from a CSV file. This is a subclass of
    `collections.UserList`, and it can be manipulated in many regards
    like a list, including in modifications.

    Let `table` be an instance of this class. You can access the items
    by index:
    ```
    table[0]  # => ["row1col1", "row1col2", "row1col3"]
    ````
    would be the first row.

    If the `CommaTable` has a header, it can be accessed at
    `table.header`, and should be a list of strings. When it is set
    is allow for a column-wise access:
    ```
    table.header = ["column1", "column2", "column3"]
    table["column1"]  # => ["row1col1", "row2col1", "row3col1", "row4col3"]
    table[0] = {
        "column1": "row1col1",
        "column2": "row1col2",
        "column3": "row1col3",
        "column4": "row1col4",
    }
    ```
    It the rows can then be accesses as dictionary. (Note: That the row
    indexing is still available, since the dictionary keys are strings.)

    The rows can be modified in place.
    """

    # parent CommaFile object from which to get settings and headers
    _parent = None

    # header override, when this class is not linked to a file
    _local_header = None

    def __init__(
        self,
        initlist=None,  #: typing.List[comma.classes.row.CommaRow] = None,
        parent=None,  #: comma.classes.file.CommaFile = None,
        *args,
        **kwargs,
    ):
        """
        Creates a row that can be tied to a `CommaFile`, which has
        properties such as the `header` or `dialect`. This is an internal
        constructor used to create a `CommaRow` row when converting
        data into a `CommaFile` object.

        `initlist` is the row to be store; `parent` is a reference to
        the parent `CommaFile` object, which provides the `header`,
        and some other parameters.
        """
        self._parent = parent
        super().__init__(initlist, *args, **kwargs)

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

    def dump(
        self,
        filename: typing.Optional[str] = None,
        fp: typing.Optional[typing.IO] = None,
    ) -> str:
        """
        Outputs a serialization of this `CommaTable` object to a string, either
        as a return value, or written to a local file path `filename`, or a
        stream `fp`.
        """
        return comma.methods.dump(self, filename=filename, fp=fp)

    @property
    def has_header(self):
        """
        Checks whether the `CommaTable` has a header as provided in
        the data source.
        """
        return ((not (self._parent is None) and not (self._parent.header is None)) or
                (not (self._local_header is None)))

    @property
    def header(self):
        """
        If the data source had a header, it will be provided in
        this property. Currently it is not possible to set, but this
        is quickly forcoming.
        """

        if self._parent is not None:
            return self._parent.header

        return self._local_header

        # if self._parent is None:
        #     raise comma.exceptions.CommaOrphanTableException(
        #         "table not linked to parent structure")
        #
        # if self._parent.header is None:
        #     raise comma.exceptions.CommaNoHeaderException(
        #         "CSV file does not appear to have a header and "
        #         "none was provided; key-based access not possible")

    @header.setter
    def header(self, value):

        if self._parent is not None:
            # handing it off to the CommaFile's setter to validate
            # and/or reject value
            self._parent.header = value

        self._local_header = value



    def __getitem__(self, key):
        """

        """
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
        """

        """
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