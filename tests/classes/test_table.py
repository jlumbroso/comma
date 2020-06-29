
import copy

import pytest

import comma.classes.table
import comma.exceptions


# noinspection PyProtectedMember
class TestCommaTable:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA = [["data", "data2"], ["datarow2", "datarow2B"]]
    SOME_FILENAME = "filename.ext"
    SOME_EMPTY_STRING = ""
    SOME_STRING = "some string"

    SOME_CSV_STRING = (
            "header1,header2,header3\n"
            "rowAcol1,rowAcol2,rowAcol3\n"
            "rowBcol1,rowBcol2,rowBcol3\n")

    SOME_CSV_STRING_MISSING_FIELDSS = (
        "header1,header2,header3\n"
        "rowAcol1,rowAcol2,rowAcol3\n"
        "BADrowBcol1,BADrowBcol3\n"
        "rowCcol1,rowCcol2,rowCcol3\n"
        "BADrowDcol1\n")

    @pytest.fixture()
    def comma_table(self):
        return comma.classes.table.CommaTable()

    @pytest.fixture()
    def comma_table_data(self):
        return comma.classes.table.CommaTable(self.SOME_DATA)

    @pytest.fixture()
    def comma_table_data_header_none(self, mocker):
        obj = comma.classes.table.CommaTable(self.SOME_DATA)
        obj._parent = mocker.Mock(header=None, primary_key=None)
        return obj

    @pytest.fixture()
    def comma_table_data_header(self, mocker):
        obj = comma.classes.table.CommaTable(self.SOME_DATA)
        obj._parent = mocker.Mock(header=self.SOME_HEADER, primary_key=None)
        return obj

    @pytest.fixture()
    def real_comma_table(self):
        obj = comma.load(self.SOME_CSV_STRING)
        return obj

    @pytest.fixture()
    def real_comma_table_missing_fields(self):
        obj = comma.load(self.SOME_CSV_STRING_MISSING_FIELDSS)
        return obj

    @pytest.fixture()
    def real_csv_data(self):
        reconstituted_csv_matrix = list(map(
            lambda s: s.split(","),
            self.SOME_CSV_STRING.strip().split("\n")))
        return reconstituted_csv_matrix

    @pytest.fixture()
    def real_csv_data_missing_fieldss(self):
        reconstituted_csv_matrix = list(map(
            lambda s: s.split(","),
            self.SOME_CSV_STRING_MISSING_FIELDSS.strip().split("\n")))
        return reconstituted_csv_matrix

    def test_comma_table_local_header_internal(self, comma_table):
        """
        Checks whether `CommaTable().header` properly detects a header that is
        locally set (as opposed to provide from a `CommaFile`)..
        """
        assert comma_table._parent is None
        assert comma_table._local_header is None
        assert comma_table.header is None

        # set local header (but internally)
        comma_table._local_header = copy.deepcopy(self.SOME_HEADER)

        assert comma_table._local_header is not None
        assert comma_table._local_header == self.SOME_HEADER
        assert comma_table.header == self.SOME_HEADER

    def test_comma_table_local_header_external(self, comma_table):
        """
        Checks whether `CommaTable().header` properly detects a header
        provided by the parent `CommaFile` object.
        """
        assert comma_table._parent is None
        assert comma_table._local_header is None
        assert comma_table.header is None

        # set local header (but externally)
        comma_table.header = copy.deepcopy(self.SOME_HEADER)

        assert comma_table._local_header is not None
        assert comma_table._local_header == self.SOME_HEADER
        assert comma_table.header == self.SOME_HEADER

        # unset
        comma_table.header = None
        assert comma_table._local_header is None
        assert comma_table.header is None

        # unset with other way
        del comma_table.header

    def test_comma_table_parent_header_delete(self, comma_table_data_header):
        """
        Checks whether the `CommaTable().header` attribute can be modified
        when it is sourced from the parent `CommaFile`.
        """
        assert comma_table_data_header._parent is not None
        assert comma_table_data_header._parent.header is not None

        comma_table_data_header.header = None

        assert comma_table_data_header._parent is not None
        assert comma_table_data_header._parent.header is None
        assert comma_table_data_header.header is None

        comma_table_data_header.header = copy.deepcopy(self.SOME_HEADER)

        assert comma_table_data_header._parent is not None
        assert comma_table_data_header._parent.header is not None
        assert comma_table_data_header.header is not None
        assert comma_table_data_header.header == self.SOME_HEADER

    def test_comma_table_local_header_size_change(self, comma_table, mocker):
        """
        Checks whether a warning is emitted when the size of the `header`
        is changed (this means that the expected number of fields will
        have changed without the data having changed).
        """
        mock_warn = mocker.patch("warnings.warn")

        comma_table.header = copy.deepcopy(self.SOME_HEADER)
        mock_warn.assert_not_called()

        comma_table.header = copy.deepcopy(self.SOME_HEADER) * 2
        mock_warn.assert_called_once()

    def test_comma_dump(self, comma_table, mocker):
        """
        Checks that the `CommaTable().dump()` method makes a call to the
        (separately tested/validated) `comma.methods.dump()`, and that it
        propagates the right parameters.
        """

        # check that an empty table is serialized to the empty string
        assert comma_table.dump() == self.SOME_EMPTY_STRING

        mock_dump = mocker.patch("comma.methods.dump")
        mock_filename = self.SOME_FILENAME
        mock_io = mocker.MagicMock()

        comma_table.dump(filename=mock_filename, fp=mock_io)

        # just checking the arguments are passed on exactly as is
        mock_dump.assert_called_once_with(
            comma_table, filename=mock_filename, fp=mock_io)

    def test_primary_key_no_parent(self, comma_table):
        """
        Checks that the right exceptions are raised if the user tries
        to manipulate the `primary_key` without having first defined
        a `header`.
        """

        assert comma_table._parent is None
        assert comma_table._local_primary_key is None
        assert comma_table.primary_key is None

        # should do nothing
        comma_table._update_primary_key_dict()

        # initially the empty comma_table has no header
        # so trying to set a primary key should complain about
        # missing header
        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            comma_table.primary_key = self.SOME_STRING

        # now lets add the header
        comma_table.header = self.SOME_HEADER

        # and check again to see if we now complain about
        # the specified primary key NOT being a header
        with pytest.raises(comma.exceptions.CommaKeyError):
            comma_table.primary_key = self.SOME_STRING

        comma_table.primary_key = self.SOME_HEADER[0]

    def test_primary_key_with_parent(self, comma_table_data_header):
        """
        Checks
        """
        assert comma_table_data_header._parent is not None
        assert comma_table_data_header._parent.header is not None
        assert comma_table_data_header._parent.primary_key is None
        assert comma_table_data_header._local_primary_key is None
        assert comma_table_data_header.primary_key is None
        assert comma_table_data_header.header == self.SOME_HEADER

        pk = self.SOME_HEADER[0]
        comma_table_data_header.primary_key = pk

        # the change is made directly to the parent
        assert comma_table_data_header._parent.primary_key == pk
        assert comma_table_data_header._local_primary_key is None
        assert comma_table_data_header.primary_key == pk

    def test_real_comma_table(self, real_comma_table, real_csv_data):
        """
        Validates that the `real_comma_table` pytest fixture contains the
        expected data.
        """
        reconstituted_header_fields = real_csv_data[0]

        assert real_comma_table.header is not None
        assert real_comma_table.header == reconstituted_header_fields
        assert real_comma_table._local_header is None
        assert real_comma_table.primary_key is None
        assert real_comma_table._parent.primary_key is None
        assert real_comma_table._local_primary_key is None

        # no caching of primary keys, since none is set
        assert real_comma_table._primary_key_dict is None

    def test_real_primary_key_table(self, real_comma_table):
        """
        Checks that the setter for the `primary_key` property is
        properly able to change the underlying data.
        """
        assert real_comma_table._primary_key_dict is None

        real_comma_table.primary_key = real_comma_table.header[0]

        assert real_comma_table._local_primary_key is None
        assert real_comma_table.primary_key is not None
        assert real_comma_table._primary_key_dict is None

        real_comma_table._update_primary_key_dict()

        assert real_comma_table._primary_key_dict is not None

    def test_real_primary_key_table_missing_fields(self, real_comma_table_missing_fields, mocker):
        """
        Checks whether `CommaTable()._update_primary_key_dict()`, a protected
        member
        """
        mock_warn = mocker.patch("warnings.warn")

        assert real_comma_table_missing_fields._primary_key_dict is None

        real_comma_table_missing_fields.primary_key = (
            real_comma_table_missing_fields.header[-1])

        real_comma_table_missing_fields._update_primary_key_dict()

        assert real_comma_table_missing_fields._primary_key_dict is not None

        assert mock_warn.call_count == 2

    def test_real_pk_access(self, real_comma_table, real_csv_data):
        """

        """
        example_csv_header = real_csv_data[0]

        for header_index in range(len(example_csv_header)):
            real_comma_table.primary_key = example_csv_header[header_index]

            for row in real_csv_data[1:]:
                key = row[header_index]
                assert real_comma_table[key] is not None
                assert real_comma_table[key] == row

    def test_real_pk_access_comma_key_error(self, real_comma_table):
        """

        """
        with pytest.raises(comma.exceptions.CommaKeyError):
            real_comma_table[self.SOME_STRING]

        real_comma_table.primary_key = real_comma_table.header[0]

        with pytest.raises(comma.exceptions.CommaKeyError):
            real_comma_table[self.SOME_STRING]



    # def test_header_parent_none(self, comma_table):
    #     """
    #
    #     """
    #
    #     # check premise
    #     assert comma_table._parent is None
    #     assert not comma_table.has_header
    #
    #     with pytest.raises(comma.exceptions.CommaOrphanTableException):
    #         val = comma_table.header
    #         assert val is not None
    #
    # def test_header_parent_header_none(self, comma_table_data_header_none, mocker):
    #     """
    #
    #     """
    #
    #     # check premise
    #     assert comma_table_data_header_none._parent is not None
    #     assert not comma_table_data_header_none.has_header
    #
    #     with pytest.raises(comma.exceptions.CommaNoHeaderException):
    #         val = comma_table_data_header_none.header
    #         assert val is not None

    def test_repr_html(self, comma_table):
        assert comma_table._repr_html_() is not None

    def test_repr_html_with_data(self, comma_table_data):
        assert comma_table_data._repr_html_() is not None

    def test_repr_html_with_data_header(self, comma_table_data_header):
        assert comma_table_data_header._repr_html_() is not None
