
import copy

import pytest

import comma
import comma.classes.row
import comma.exceptions


# noinspection PyProtectedMember
class TestCommaFieldSlice:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA_ROWS = [["data", "data2"], ["datarow2", "datarow2B"]]
    SOME_DATA_ROW = SOME_DATA_ROWS[0]
    SOME_COL_SLICE = [SOME_DATA_ROWS[0][0], SOME_DATA_ROWS[1][0]]
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
            copy.deepcopy(self.SOME_DATA_ROWS),
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

    def test_typeerror_get(self, comma_field_slice):
        with pytest.raises(comma.exceptions.CommaTypeError):
            comma_field_slice[self.SOME_NON_HEADER_NAME]

    def test_typeerror_set(self, comma_field_slice):
        with pytest.raises(comma.exceptions.CommaTypeError):
            comma_field_slice[self.SOME_NON_HEADER_NAME] = self.SOME_NON_HEADER_NAME

    # @pytest.mark.parametrize("deep", [True, False])
    # def test_set(self, mocker, deep, comma_field_slice):
    #     mocker.patch("comma.settings", SLICE_DEEP_COPY_DATA=deep)
    #     assert comma.settings.SLICE_DEEP_COPY_DATA == deep
    #
    #     data_orig = copy.deepcopy(self.SOME_DATA_ROWS)
    #     data_copy = copy.deepcopy(data_orig)
    #     comma_field_slice.data = data_copy
    #
    #     comma_field_slice[:1] = [self.SOME_NON_HEADER_NAME]
    #
    #     if not deep:
    #         assert data_copy[0][0] == self.SOME_NON_HEADER_NAME
    #     else:
    #         assert not data_copy[0][0] == self.SOME_NON_HEADER_NAME
    @pytest.mark.parametrize("deep", [True, False])
    def test_set_slicevalue(self, mocker, deep):
        # NOTE: This somehow did not work (i.e., does not seem to propagate
        # everywhere it is needed)
        # mocker.patch("comma.settings",
        #              SLICE_DEEP_COPY_DATA=deep,
        #              SLICE_DEEP_COPY_PARENT=False)
        # assert comma.settings.SLICE_DEEP_COPY_DATA == deep

        # backup global setting
        backup_sdcd = comma.settings.SLICE_DEEP_COPY_DATA
        comma.settings.SLICE_DEEP_COPY_DATA = deep
        assert comma.settings.SLICE_DEEP_COPY_DATA == deep

        cf = comma.load(
            "col1,col2,col3,col4,col5\n"
            "row1col1,row1col2,row1col3,row1col4,row1col5\n"
            "row2col1,row2col2,row2col3,row2col4,row2col5\n")

        actual_slice = ["row1col1", "row2col1"]
        modified_slice = ["ROW1COL1", "ROW2COL1"]

        # query check
        assert list(cf["col1"]) == actual_slice

        # modification check
        cf["col1"][0] = modified_slice[0]

        # verification
        if deep:
            # change should not have propagated because of deep copy
            assert cf["col1"][0] == actual_slice[0]
        else:
            assert cf["col1"][0] == modified_slice[0]

        # restore original global setting
        comma.settings.SLICE_DEEP_COPY_DATA = backup_sdcd

    @pytest.mark.parametrize("deep", [True, False])
    def test_set_sliceslice(self, mocker, deep):
        # NOTE: This somehow did not work (i.e., does not seem to propagate
        # everywhere it is needed)
        # mocker.patch("comma.settings",
        #              SLICE_DEEP_COPY_DATA=deep,
        #              SLICE_DEEP_COPY_PARENT=False)
        # assert comma.settings.SLICE_DEEP_COPY_DATA == deep

        # backup global setting
        backup_sdcd = comma.settings.SLICE_DEEP_COPY_DATA
        comma.settings.SLICE_DEEP_COPY_DATA = deep
        assert comma.settings.SLICE_DEEP_COPY_DATA == deep

        cf = comma.load(
            "col1,col2,col3,col4,col5\n"
            "row1col1,row1col2,row1col3,row1col4,row1col5\n"
            "row2col1,row2col2,row2col3,row2col4,row2col5\n")

        actual_slice = ["row1col1", "row2col1"]
        modified_slice = ["ROW1COL1", "ROW2COL1"]

        # query check
        assert list(cf["col1"]) == actual_slice

        # modification check
        cf["col1"][:] = modified_slice

        # verification
        if deep:
            # change should not have propagated because of deep copy
            assert cf["col1"][0] == actual_slice[0]
        else:
            assert cf["col1"][0] == modified_slice[0]

        # restore original global setting
        comma.settings.SLICE_DEEP_COPY_DATA = backup_sdcd

    def test_set_slice_badlen(self, comma_field_slice):
        with pytest.raises(comma.exceptions.CommaBatchException):
            comma_field_slice[:] = []

    def test_get_slice_deepcopy(self, comma_field_slice):
        # backup global setting
        backup_sdcd = comma.settings.SLICE_DEEP_COPY_DATA
        comma.settings.SLICE_DEEP_COPY_DATA = True
        slice = comma_field_slice[:]
        assert list(slice) == self.SOME_COL_SLICE
        # restore original global setting
        comma.settings.SLICE_DEEP_COPY_DATA = backup_sdcd

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
