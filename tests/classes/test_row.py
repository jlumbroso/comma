
import copy

import pytest

import comma.classes.row
import comma.exceptions


class TestCommaRow:

    SOME_HEADER = ["col1", "col2"]
    SOME_DATA_ROWS = [["dataA1", "dataB1"], ["dataA2", "dataB2"]]
    SOME_DATA_ROW = SOME_DATA_ROWS[0]
    SOME_OTHER_DATA_ROW = SOME_DATA_ROWS[1]
    SOME_DATA_DICT = dict(zip(SOME_HEADER, SOME_DATA_ROW))
    SOME_OTHER_DATA_DICT = dict(zip(SOME_HEADER, SOME_OTHER_DATA_ROW))
    SOME_STRING = "some string"
    SOME_OTHER_STRING = "blah blah string"
    EMPTY_STRING = ""

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
    def other_comma_row(self, mocker):
        """
        Returns a fixture for a functional `comma.classes.row.CommaRow` object,
        with sample data, mock parent `CommaFile` object and a `header`. This
        contains alternate data to the `comma_row` fixture.
        """
        mock_parent = mocker.Mock(header=self.SOME_HEADER)
        comma_row_obj = comma.classes.row.CommaRow(
            self.SOME_OTHER_DATA_ROW,
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

    def test_sliceddict_no_header(self, comma_row_no_header):
        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            comma_row_no_header.items()

    def test_keys_with_header(self, comma_row):
        for a, b in zip(comma_row.keys(), comma_row.header):
            assert a == b

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

    def test_deepcopy_memoization(self, comma_row, mocker, subtests):
        """
        Checks whether the memoization mechanism to avoid recursive infinite
        calls is properly implemented in `CommaRow.__deepcopy__()`.
        """

        # get the memory address of the object we are about to copy
        obj_id = id(comma_row)

        # create mock object that will be returned by memoization
        mock_obj = mocker.Mock()

        # create mock memoization dictionary
        memodict = {obj_id: mock_obj}

        with subtests.test("memoization hit"):
            # check returned object is memoized object
            assert mock_obj == comma_row.__deepcopy__(memodict=memodict)

        with subtests.test("memoization miss"):
            # check that is not the case with different memoization dictionary
            assert mock_obj != comma_row.__deepcopy__(memodict=dict())

    def test_getitem_slice(self, comma_row_no_header):
        lst0 = comma_row_no_header[:]
        lst1 = comma_row_no_header[1:]
        lst2 = comma_row_no_header[:1]
        lst3 = [lst2[0]] + lst1
        assert lst0 != lst1
        assert lst0 == lst3

    def test_getitem_str(self, comma_row):
        some_field_name = self.SOME_HEADER[0]
        comma_row[some_field_name]

    def test_getitem_str_no_header(self, comma_row):
        some_field_name = self.SOME_HEADER[0]
        comma_row._parent.header = None
        with pytest.raises(comma.exceptions.CommaTypeError):
            comma_row[some_field_name]

    def test_cmp(self, comma_row, other_comma_row):
        assert comma_row != other_comma_row
        assert not comma_row == other_comma_row
        assert comma_row < other_comma_row
        assert comma_row <= other_comma_row
        assert not comma_row > other_comma_row
        assert not comma_row >= other_comma_row
        assert comma_row == comma_row
        assert not comma_row != comma_row
        assert other_comma_row == other_comma_row
        assert not other_comma_row != other_comma_row

    def test_cmp_odd(self, comma_row):
        assert not comma_row == True

    def test_getitem_badkey(self, comma_row):
        with pytest.raises(comma.exceptions.CommaKeyError):
            comma_row[self.SOME_STRING]

    def test_get_badkey_with_default(self, comma_row):
        ret1 = comma_row.get(self.SOME_STRING)
        ret2 = comma_row.get(self.SOME_STRING, default=self.EMPTY_STRING)
        assert ret1 == self.EMPTY_STRING
        assert ret2 == self.EMPTY_STRING

    def test_get_badkey_with_changed_default(self, comma_row):
        ret = comma_row.get(self.SOME_STRING, default=self.SOME_OTHER_STRING)
        assert ret == self.SOME_OTHER_STRING

    def test_get_other_errors(self, comma_row):
        ret = comma_row.get(-1000, default=self.SOME_OTHER_STRING)
        assert ret == self.SOME_OTHER_STRING
