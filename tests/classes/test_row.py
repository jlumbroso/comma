
import pytest

import comma.classes.row
import comma.exceptions


class TestCommaRow:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA_ROWS = [["data", "data2"], ["datarow2", "datarow2B"]]
    SOME_DATA_ROW = SOME_DATA_ROWS[0]
    SOME_DATA_DICT = dict(zip(SOME_HEADER, SOME_DATA_ROW))

    @pytest.fixture()
    def comma_row(self, mocker):
        """
        Returns a fixture for a functional `comma.classes.row.CommaRow` object,
        with sample data, mock parent `CommaFile` object and a `header`.
        """
        mock_parent = mocker.Mock(header=self.SOME_HEADER)
        comma_row_obj = comma.classes.row.CommaRow(
            self.SOME_DATA_ROW,
            parent=mock_parent
        )
        return comma_row_obj

    @pytest.fixture()
    def comma_row_no_parent(self, comma_row):
        """
        Returns a fixture for a functional `comma.classes.row.CommaRow` object,
        without a parent `CommaFile`.
        """
        # remove (mock) parent
        comma_row._parent = None
        return comma_row

    @pytest.fixture()
    def comma_row_no_header(self, comma_row):
        """
        Returns a fixture for a functional `comma.classes.row.CommaRow` object,
        with a parent `CommaFile`, but no `header`.
        """
        # remove (mock) parent header
        comma_row._parent.header = None
        return comma_row


    def test_header_fails_no_parent(self, comma_row_no_parent):
        """
        Checks access to attribute `CommaRow().header` raises an exception if
        there is no parent `CommaFile` object linked to the `CommaRow` object.
        """
        assert comma_row_no_parent._parent is None
        with pytest.raises(comma.exceptions.CommaOrphanRowException):
            assert comma_row_no_parent.header

    def test_header_fails_parent_no_header(self, mocker, comma_row_no_header):
        """
        Checks access to attribute `CommaRow().header` raises an exception if
        the parent `CommaFile` object does not have a header.
        """
        assert comma_row_no_header._parent is not None
        assert comma_row_no_header._parent.header is None
        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            assert comma_row_no_header.header

    def test_header_parent_with_header(self, comma_row):
        """
        Checks access to attribute `CommaRow().header` works when both the `parent`
        attribute is defined, and the referred to `CommaFile` object has a `header`.
        """
        assert comma_row._parent is not None
        assert comma_row._parent.header is not None
        assert comma_row._slice_list is None or comma_row._slice_list == []
        assert comma_row.header == self.SOME_HEADER

    def test_keys_with_header(self, comma_row):
        assert comma_row.keys() == comma_row.header

    def test_keys_no_header(self, comma_row_no_parent):
        with pytest.raises(comma.exceptions.CommaException):
            comma_row_no_parent.keys()

    def test_values_with_header(self, comma_row):
        assert list(comma_row.values()) == self.SOME_DATA_ROW

    def test_items_with_header(self, comma_row):
        assert comma_row.items() == self.SOME_DATA_DICT.items()

    def test_repr_with_header(self, comma_row):
        assert comma_row.__repr__() != ""

    def test_repr_without_header(self, comma_row_no_header):
        assert comma_row_no_header.__repr__() != ""

