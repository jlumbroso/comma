
import copy
import csv
import os
import typing

import extradict
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


CommaTableTestingExtrasType = typing.TypedDict(
    "CommaTableTestingExtrasType", {
        # the fixture table
        "table": comma.classes.table.CommaTable,

        # coordinates to a record that is guaranteed to exist
        "record_index": int,
        "field_index": int,
        "field_name": str,
        "original_value": typing.Any,

        # references to the record and a copy
        "some_record": comma.classes.row.CommaRow,
        "some_record_copy": comma.classes.row.CommaRow,
    })


# NOTE: refactor to make this an abstract test class?
# noinspection DuplicatedCode
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

    @pytest.fixture()
    def table(self) -> comma.classes.table.CommaTable:
        """
        Returns (as a pytest fixture) a newly loaded `CommaTable` object from
        this class' test data file.
        """
        return comma.load(self.FILEPATH)

    @pytest.fixture()
    def table_info(
            self,
            table: comma.classes.table.CommaTable
    ) -> CommaTableTestingExtrasType:
        """
        Returns a subclass with a few different setup interdependent fixtures.
        """
        assert isinstance(table, comma.classes.table.CommaTable)
        assert table.has_header
        assert table.header is not None

        record_index = self.SOME_RECORD_INDEX
        field_index = self.SOME_COLUMN_INDEX
        assert len(table.header) > field_index
        field_name = table.header[field_index]

        # assert we are able to access that index
        assert len(table) > record_index
        assert len(table[record_index]) > field_index

        # extract first record and make a copy
        some_record = table[record_index]
        assert isinstance(some_record, comma.classes.row.CommaRow)
        some_record_copy = copy.deepcopy(some_record)
        assert isinstance(some_record_copy, comma.classes.row.CommaRow)

        # verify that the two records match
        # NOTE: depending on how the cast to dictionary is done, this may fail
        assert dict(some_record) == dict(some_record_copy)

        return typing.cast(CommaTableTestingExtrasType, {
            # the fixture table
            "table": table,

            # coordinates to a record that is guaranteed to exist
            "record_index": record_index,
            "field_index": field_index,
            "field_name": field_name,
            "original_value": some_record[field_index],

            # references to the record and a copy
            "some_record": some_record,
            "some_record_copy": some_record_copy,
        })

    # noinspection PyUnresolvedReferences
    @staticmethod
    def assert_record_has_changed(
            table_info: CommaTableTestingExtrasType,
            modified_string: typing.Optional[str] = None,
    ):
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, original_value
            from info import some_record, some_record_copy

            # integrity: is the isolated record consistent with main record?
            assert table[record_index][field_index] == some_record[field_index]

            # correctness: has the isolated record been modified?
            if modified_string is not None:
                assert table[record_index][field_index] == modified_string

            # does it differ from the copy?
            assert dict(some_record) != dict(some_record_copy)
            assert dict(table[record_index]) != dict(some_record_copy)

            # check if copy still has original value
            if original_value is not None:
                assert some_record_copy[field_index] == original_value

    # noinspection PyUnresolvedReferences
    @staticmethod
    def assert_record_unmodified(
            table_info: CommaTableTestingExtrasType,
    ):
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, original_value
            from info import some_record, some_record_copy

            # integrity: is the isolated record consistent with main record?
            assert table[record_index][field_index] == some_record[field_index]

            # check whether all accesses to this record produce the same value
            if string is not None:
                assert table[record_index][field_index] == original_value
                assert record[field_index] == string
                assert some_record_copy[field_index] == original_value

            # is the same as the copy? (the above may succeed and below fail,
            # but not the opposite; i.e. below is strictly stronger than above,
            # but test is intended to be granular)
            assert dict(some_record) == dict(some_record_copy)
            assert dict(table[record_index]) == dict(some_record)
            assert dict(table[record_index]) == dict(some_record_copy)

    @staticmethod
    def assert_iter_by_value(iter1, iter2):
        """
        Asserts that two iterables are identical.
        """
        for a, b in zip(iter1, iter2):
            assert a == b

    def test_readonly_file_validation(self, table: comma.classes.table.CommaTable):
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

    def test_readonly_field_slicing(self, table: comma.classes.table.CommaTable):
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

    def test_readonly_compare_with_standard_csv(
            self,
            table: comma.classes.table.CommaTable,
            table_csv,
            table_csv_dict
    ):
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

    # noinspection PyUnresolvedReferences
    def test_modify_record_by_index(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by index (list access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index
            from info import some_record, some_record_copy

            some_record[field_index] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # noinspection PyUnresolvedReferences
    def test_modify_record_by_name(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by key (dict access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, field_name
            from info import some_record, some_record_copy

            some_record[field_name] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # noinspection PyUnresolvedReferences
    def test_modify_record_field_slicing(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by key (dict access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, field_name
            from info import some_record, some_record_copy

            # TEST: CAN EDITING BY FIELD SLICING PROPAGATE MODIFICATIONS
            table[field_name][record_index] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # noinspection PyUnresolvedReferences
    def test_modify_record_with_slice(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by key (dict access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, field_name
            from info import some_record, some_record_copy

            assert record_index < 10
            table[0:10][record_index][field_name] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # noinspection PyUnresolvedReferences
    def test_modify_record_slice_and_field_slice(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by key (dict access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, field_name
            from info import some_record, some_record_copy

            assert record_index < 10
            table[0:10][field_name][record_index] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # noinspection PyUnresolvedReferences
    def test_modify_record_field_slice_and_slice(self, table_info: CommaTableTestingExtrasType):
        """
        Checks to see if modifications to a `CommaTable` object are correctly
        propagated where expected, when fields are edited by key (dict access).
        """
        with extradict.MapGetter(table_info) as info:
            from info import table, record_index, field_index, field_name
            from info import some_record, some_record_copy

            assert record_index < 10
            table[field_name][0:10][record_index] = self.SOME_STRING

            # has the original record been modified?
            self.assert_record_has_changed(
                table_info=table_info,
                modified_string=self.SOME_STRING,
            )

    # # noinspection PyUnresolvedReferences
    # def test_modify_record_field_slice_and_slice(self, table_info: CommaTableTestingExtrasType):
    #     """
    #     Checks to see if modifications to a `CommaTable` object are correctly
    #     propagated where expected, when fields are edited by key (dict access).
    #     """
    #     with extradict.MapGetter(table_info) as info:
    #         from info import table, record_index, field_index, field_name, original_value
    #         from info import some_record, some_record_copy
    #
    #         assert record_index < 10
    #         table[field_name][record_index][field_index:field_index+1] = self.SOME_STRING
    #
    #         # has the original record been modified?
    #         self.assert_record_unchanged(
    #             table_info=table_info,
    #             string=original_value,
    #         )



