
import pytest

import comma.classes.row
import comma.exceptions


# noinspection PyProtectedMember
class TestCommaFieldSlice:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA_ROWS = [["data", "data2"], ["datarow2", "datarow2B"]]
    SOME_DATA_ROW = SOME_DATA_ROWS[0]
    SOME_DATA_DICT = dict(zip(SOME_HEADER, SOME_DATA_ROW))
    SOME_NON_HEADER_NAME = "cassava"

    @pytest.fixture()
    def comma_field_slice(self, mocker):
        """
        Returns a fixture for a functional `comma.classes.slices.CommaFieldSlice`
        object, with sample data, mock parent `CommaFile` object, a `header` and
        a selected `field_name`.
        """
        mock_parent = mocker.Mock(header=self.SOME_HEADER)
        comma_field_slice_obj = comma.classes.slices.CommaFieldSlice(
            self.SOME_DATA_ROWS,
            parent=mock_parent,
            field_name=self.SOME_HEADER[0],
        )
        return comma_field_slice_obj

    @pytest.fixture()
    def comma_field_slice_bad_field_name(self, comma_field_slice):
        """
        Returns a fixture for a functional `comma.classes.slices.CommaFieldSlice`
        object, configured with the wrong field name (a field name that is not
        among one of the header field names). To get the appropriate exceptions
        need to call `comma_field_slice._recompute_field_index()`.
        """
        comma_field_slice._field_name = self.SOME_NON_HEADER_NAME
        return comma_field_slice

    @pytest.fixture()
    def comma_field_slice_no_parent(self, comma_field_slice):
        """
        Returns a fixture for a functional `comma.classes.slices.CommaFieldSlice`
        object, without a parent `CommaFile`. To get the appropriate exceptions
        need to call `comma_field_slice._recompute_field_index()`.
        """
        # remove (mock) parent
        comma_field_slice._parent = None
        return comma_field_slice

    @pytest.fixture()
    def comma_field_slice_no_header(self, comma_field_slice):
        """
        Returns a fixture for a functional `comma.classes.slices.CommaFieldSlice`
        object, with a parent `CommaFile`, but no `header. To get the appropriate
        exceptions raised, need to call `comma_field_slice._recompute_field_index()`.
        """
        # remove (mock) parent header
        comma_field_slice._parent.header = None
        return comma_field_slice

    def test_field_index_calculation(self, comma_field_slice):
        """
        Checks whether the `_field_index` value is computed properly in a
        typical use case of the class.
        """
        assert comma_field_slice._parent is not None
        assert comma_field_slice._field_name is not None
        assert comma_field_slice._field_index is not None

        # check correctness of _field_index
        recomputed_field_index = comma_field_slice._parent.header.index(
            comma_field_slice._field_name)
        assert recomputed_field_index == comma_field_slice._field_index

    def test_no_parent_exception(self, comma_field_slice_no_parent):
        """
        Checks to see whether a `comma.exceptions.CommaOrphanRowException`
        exception is raised if the `CommaFieldSlice` object has no parent.
        """
        with pytest.raises(comma.exceptions.CommaOrphanRowException):
            comma_field_slice_no_parent._recompute_field_index()

    def test_no_header_exception(self, comma_field_slice_no_header):
        """
        Checks to see whether a `comma.exceptions.CommaOrphanRowException`
        exception is raised if the `CommaFieldSlice` object has no header.
        """
        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            comma_field_slice_no_header._recompute_field_index()

    def test_key_error(self, comma_field_slice_bad_field_name):
        """
        Checks to see whether a `comma.exceptions.CommaKeyError`
        exception is raised if the `CommaFieldSlice` object is provided
        a field name that does not appear in the header.
        """
        with pytest.raises(comma.exceptions.CommaKeyError):
            comma_field_slice_bad_field_name._recompute_field_index()

    def test_iter_does_not_crash(self, comma_field_slice):
        """
        Checks that calls to `CommaFieldSlice.__iter__()` do not crash,
        and that it is possibility to iterate over a well-defined
        `CommaFieldSlice` object.
        """
        comma_field_slice.__iter__()
        for _ in comma_field_slice:
            continue

    def test_iter_correctness(self, comma_field_slice):
        """
        Checks that iteration provides the correct result, by recomputing
        what the answer should be.
        """
        assert comma_field_slice._parent is not None
        assert comma_field_slice._field_name is not None
        assert comma_field_slice._field_index is not None

        field_index = comma_field_slice._field_index

        for val_from_cfs, row in zip(comma_field_slice, self.SOME_DATA_ROWS):
            assert val_from_cfs == row[field_index]


# noinspection PyProtectedMember
class TestCommaRowSlice:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA_ROWS = [["data", "data2"], ["datarow2", "datarow2B"]]
    SOME_DATA_ROW = SOME_DATA_ROWS[0]
    SOME_DATA_DICT = dict(zip(SOME_HEADER, SOME_DATA_ROW))
    SOME_NON_HEADER_NAME = "cassava"

    @pytest.fixture()
    def comma_row_slice(self, mocker):
        """
        Returns a fixture for a functional `comma.classes.slices.CommaRowSlice`
        object, with sample data, mock parent `CommaFile` object and a `header`.
        """
        mock_parent = mocker.Mock(header=self.SOME_HEADER)
        comma_row_slice_obj = comma.classes.slices.CommaRowSlice(
            self.SOME_DATA_ROW,
            parent=mock_parent,
        )
        return comma_row_slice_obj

    def test(self, comma_row_slice):
        assert comma_row_slice._parent is not None

