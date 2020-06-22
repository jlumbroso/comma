
import copy
import csv
import os

import pytest

import comma
import comma.classes.file
import comma.classes.row
import comma.classes.slices
import comma.classes.table


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
)


# NOTE: refactor to make this an abstract test class?
class TestSacramentoRealEstateTransactions:

    FILENAME = "Sacramentorealestatetransactions.csv"
    FILEPATH = os.path.join(DATA_DIR, FILENAME)

    DATA_ROW_COUNT = 985
    DATA_COL_COUNT = 12
    DATA_HEADER = (
        "street,city,zip,state,beds,baths,sq__ft,"
        "type,sale_date,price,latitude,longitude").split(",")
    SOME_RECORD_INDEX = 0
    SOME_COLUMN_INDEX = 0

    SOME_STRING = "some-arbitrary-string"

    @pytest.fixture()
    def table(self):
        """
        Returns (as a pytest fixture) a newly loaded `CommaTable` object from
        this class' test data file.
        """
        return comma.load(self.FILEPATH)

    @pytest.fixture()
    def table_csv(self):
        """
        Returns (as a pytest fixture) a newly loaded list of lists from
        this class' test data file, as opened by `csv.reader()`.
        """
        with open(self.FILEPATH, "r") as file:
            data = list(csv.reader(file))
        return data

    @pytest.fixture()
    def table_csv_dict(self):
        """
        Returns (as a pytest fixture) a newly loaded list of lists from
        this class' test data file, as opened by `csv.DictReader()`.
        """
        with open(self.FILEPATH, "r") as file:
            data = list(csv.DictReader(file))
        return data

    @staticmethod
    def assert_iter_by_value(iter1, iter2):
        """
        Asserts that two iterables are identical.
        """
        for a, b in zip(iter1, iter2):
            assert a == b

    def test_readonly_file_validation(self, table):
        """
        Checks whether the file that is being run by this test module is the
        file that is expected, using some magic numbers hard-coded in this class.
        """
        assert isinstance(table, comma.classes.table.CommaTable)
        assert isinstance(table, list)
        assert len(table) == self.DATA_ROW_COUNT
        assert len(table[0]) == self.DATA_COL_COUNT
        assert table.has_header
        assert table.header == self.DATA_HEADER

    def test_readonly_field_slicing(self, table):
        """
        Checks whether the field slicing feature, wherein you can extract an
        entire column, works.
        """
        assert isinstance(table, comma.classes.table.CommaTable)

        for field_index, field_name in enumerate(self.DATA_HEADER):

            # retrieve the columns both ways
            column_by_index = [row[field_index] for row in table]
            column_by_name = table[field_name]

            # should be a normal list
            assert not isinstance(
                column_by_index, comma.classes.slices.CommaFieldSlice)

            # should be a CommaFieldSlice
            assert column_by_name is not None
            assert isinstance(
                column_by_name, comma.classes.slices.CommaFieldSlice)
            assert isinstance(column_by_name, list)

            # compare sizes and types
            assert len(column_by_index) == self.DATA_ROW_COUNT
            assert len(column_by_name) == self.DATA_ROW_COUNT
            assert type(column_by_index[0]) is str
            assert type(column_by_name[0]) is str

            # compare all values
            self.assert_iter_by_value(column_by_index, column_by_name)

    def test_readonly_compare_with_standard_csv(self, table, table_csv, table_csv_dict):
        """
        Checks to see if the data read by `comma.load()` is comparable to that
        read by the standard library's `csv` module.
        """
        # check first line is header line
        assert table.header == table_csv[0]

        # remove header line
        del table_csv[0]
        assert len(table_csv) > 0
        assert table.header != table_csv[0]

        # compare all the data
        for row_index, (row_comma, row_csv) in enumerate(zip(table, table_csv_dict)):
            for field_index, field_name in enumerate(self.DATA_HEADER):

                # compare by field access, e.g. "street", for row-level record
                assert row_comma[field_name] == row_csv[field_name]

                # compare by field index access, e.g. 0, for row-level record
                assert row_comma[field_index] == row_csv[field_name]

                # compare with direct indexing on list CSV file
                assert row_comma[field_index] == table_csv[row_index][field_index]

    def test_modify_record(self, table):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected.
        """
        assert isinstance(table, comma.classes.table.CommaTable)

        record_index = self.SOME_RECORD_INDEX
        field_index = self.SOME_COLUMN_INDEX

        # assert we are able to access that index
        assert len(table) > record_index
        assert len(table[record_index]) > field_index

        # extract first record and make a copy
        some_record = table[record_index]
        assert isinstance(some_record, comma.classes.row.CommaRow)
        some_record_copy = copy.deepcopy(some_record)

        # verify that the two records match
        # NOTE: depending on how the cast to dictionary is done, this may fail
        assert dict(some_record) == dict(some_record_copy)

        some_record[field_index] = self.SOME_STRING

        # has the original record been modified?
        assert table[record_index][field_index] == self.SOME_STRING
        assert table[record_index][field_index] == some_record[field_index]

        # does it differ from the copy?
        assert dict(some_record) != dict(some_record_copy)
        assert dict(table[record_index]) != dict(some_record_copy)




