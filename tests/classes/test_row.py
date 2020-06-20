
import pytest

import comma.classes.row
import comma.exceptions


class TestCommaRow:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA = [["data", "data2"], ["datarow2", "datarow2B"]]

    @pytest.fixture()
    def comma_row_no_parent(self):
        return comma.classes.row.CommaRow()

    @pytest.fixture()
    def comma_row_no_parent_data(self):
        return comma.classes.row.CommaRow(self.SOME_DATA)

    def test_comma_row_header_no_parent(self, comma_row_no_parent):
        """
        Checks access to attribute `CommaRow().header` raises an exception if
        there is no parent `CommaFile` object linked to the `CommaRow` object.
        """
        # no parent
        assert comma_row_no_parent._parent is None
        with pytest.raises(comma.exceptions.CommaOrphanRowException):
            assert comma_row_no_parent.header

    def test_comma_row_header_parent_no_header(self, mocker, comma_row_no_parent):
        """
        Checks access to attribute `CommaRow().header` raises an exception if
        the parent `CommaFile` object does not have a header.
        """
        # bogus parent
        comma_row_no_parent._parent = mocker.Mock(header=None)
        assert comma_row_no_parent._parent.header is None
        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            assert comma_row_no_parent.header
