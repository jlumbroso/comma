
import pytest

import comma.classes.table
import comma.exceptions


class TestCommaTable:

    SOME_HEADER = ["field1", "field2"]
    SOME_DATA = [["data", "data2"], ["datarow2", "datarow2B"]]

    @pytest.fixture()
    def comma_table(self):
        return comma.classes.table.CommaTable()

    @pytest.fixture()
    def comma_table_data(self):
        return comma.classes.table.CommaTable(self.SOME_DATA)

    @pytest.fixture()
    def comma_table_data_header_none(self, mocker):
        obj = comma.classes.table.CommaTable(self.SOME_DATA)
        obj._parent = mocker.Mock(header=None)
        return obj

    @pytest.fixture()
    def comma_table_data_header(self, mocker):
        obj = comma.classes.table.CommaTable(self.SOME_DATA)
        obj._parent = mocker.Mock(header=self.SOME_HEADER)
        return obj

    def test_header_parent_none(self, comma_table):
        """

        """

        # check premise
        assert comma_table._parent is None
        assert not comma_table.has_header

        with pytest.raises(comma.exceptions.CommaOrphanTableException):
            val = comma_table.header
            assert val is not None

    def test_header_parent_header_none(self, comma_table_data_header_none, mocker):
        """

        """

        # check premise
        assert comma_table_data_header_none._parent is not None
        assert not comma_table_data_header_none.has_header

        with pytest.raises(comma.exceptions.CommaNoHeaderException):
            val = comma_table_data_header_none.header
            assert val is not None

    def test_repr_html(self, comma_table):
        assert comma_table._repr_html_() is not None

    def test_repr_html_with_data(self, comma_table_data):
        assert comma_table_data._repr_html_() is not None

    def test_repr_html_with_data_header(self, comma_table_data_header):
        assert comma_table_data_header._repr_html_() is not None
