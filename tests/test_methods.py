
import copy
import io
import typing

import pytest

import comma.exceptions
import comma.helpers
import comma.methods
import comma.typing


SOME_FILENAME = "somefilename.csv"

SOME_CSV_STRING = "name,age,gender\nPerson1,33,F\nPerson2,25,M\n"
SOME_CSV_STRING_NO_HEADER = "\n".join(SOME_CSV_STRING.split("\n")[1:])
SOME_CSV_STRING_HAS_HEADER = True
SOME_CSV_STRING_ROW_COUNT = 2
SOME_CSV_STRING_COL_COUNT = 3

SOME_HEADER = SOME_CSV_STRING.split("\n")[0]
SOME_OTHER_HEADER = "nom,age,genre"

# manually compute the table by splitting lines and commas

SOME_CSV_DATA = list(map(
    lambda s: s.split(","),
    SOME_CSV_STRING.strip().split("\n")))

SOME_CSV_DATA_NO_HEADER = list(map(
    lambda s: s.split(","),
    SOME_CSV_STRING_NO_HEADER.strip().split("\n")))


class TestLoad:

    def test_none_source(self):
        casted_none = typing.cast(
            comma.typing.SourceType, None)  # (purposefully) invalid cast
        obj = comma.methods.load(source=casted_none)
        assert obj is None

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_load_from_string_or_stringio(self, source):

        obj = comma.methods.load(source)

        # make sure we know what we are getting
        assert (len(obj) == SOME_CSV_STRING_ROW_COUNT)
        assert ((obj.header is not None) == SOME_CSV_STRING_HAS_HEADER)
        assert (len(obj.header) == SOME_CSV_STRING_COL_COUNT)

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_dump_from_string_or_stringio(self, source):

        obj = comma.methods.load(source)
        assert obj.dump() == SOME_CSV_STRING

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_dump_from_string_or_stringio_with_alternate_headers(self, source):
        alternate_header = SOME_OTHER_HEADER.split(",")
        obj = comma.methods.load(source)
        assert (comma.methods.dump(obj, header=alternate_header) ==
                SOME_OTHER_HEADER + "\n" + SOME_CSV_STRING_NO_HEADER)

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_dump_from_string_or_stringio_with_list_cast(self, source):

        obj = comma.methods.load(source)
        assert comma.methods.dump(list(obj)) == SOME_CSV_STRING

    def test_dump_from_invalid_records(self, mocker):
        invalid_records = mocker.Mock()
        invalid_records = typing.cast(comma.methods.TableType, invalid_records)
        with pytest.raises(comma.exceptions.CommaException):
            comma.methods.dumps(invalid_records)

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_dump_from_string_or_stringio_with_list_cast_and_tweak(self, source, mocker):
        obj = comma.methods.load(source)
        parent = obj._parent
        obj_list = list(obj)

        obj_mock = mocker.Mock(
            wraps=obj_list,
            __iter__=mocker.Mock(return_value=iter(obj_list)),
            _parent=parent,
        )

        assert comma.methods.dump(obj_mock) == SOME_CSV_STRING

    def test_dump_from_string_no_header(self, mocker):
        obj = comma.methods.load(SOME_CSV_STRING_NO_HEADER)

        parent = obj._parent
        obj_list = list(obj)

        obj_mock = mocker.Mock(
            wraps=obj_list,
            __iter__=mocker.Mock(return_value=iter(obj_list)),
            _parent=parent,
        )

        assert comma.methods.dump(obj_mock) == SOME_CSV_STRING_NO_HEADER

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_dump_to_file(self, source, mocker):
        obj = comma.methods.load(source)

        stream = io.StringIO()
        open_mock = mocker.patch("comma.methods.open", return_value=stream)

        ret = comma.methods.dump(obj, filename=SOME_FILENAME)

        open_mock.assert_called_once_with(SOME_FILENAME, "w")
        assert stream.closed
        assert ret == SOME_CSV_STRING

    @pytest.mark.parametrize("no_echo", [True, False])
    def test_dump_to_steam(self, no_echo):
        obj = comma.methods.load(SOME_CSV_STRING)

        stream = io.StringIO()
        ret = comma.methods.dump(obj, fp=stream, no_echo=no_echo)

        assert not stream.closed

        stream.seek(0)
        assert stream.read() == SOME_CSV_STRING

        stream.close()
        assert stream.closed

        if no_echo:
            assert ret is None
        else:
            assert ret == SOME_CSV_STRING

    @pytest.mark.parametrize("no_echo", [True, False])
    def test_dump_from_raw_data(self, no_echo):
        obj_manual = copy.deepcopy(SOME_CSV_DATA)
        assert comma.methods.dump(obj_manual, no_echo=no_echo) == SOME_CSV_STRING

        # checking that the manual computation makes sense
        obj_comma = comma.methods.load(SOME_CSV_STRING)
        assert comma.methods.dump(obj_manual) == comma.methods.dump(obj_comma)

    def test_dump_from_raw_data_with_dialect_choice(self):
        target_dialect = comma.helpers.DefaultDialect()

        obj_manual = copy.deepcopy(SOME_CSV_DATA)
        str_manual = comma.methods.dump(obj_manual, dialect=target_dialect)
        assert str_manual == SOME_CSV_STRING

        # checking that the manual computation makes sense
        obj_comma = comma.methods.load(SOME_CSV_STRING)
        str_comma = comma.methods.dump(obj_comma, dialect=target_dialect)
        assert str_manual == str_comma

    def test_dump_with_added_headers(self):

        # set up the objects
        obj_manual = copy.deepcopy(SOME_CSV_DATA_NO_HEADER)
        obj_comma = comma.methods.load(SOME_CSV_STRING)

        # compute the dumps
        str_manual_with_headers = comma.methods.dump(obj_manual, header=SOME_HEADER.split(","))
        str_comma = comma.methods.dump(obj_comma)

        # compare both to reference string and result on reference conversion
        assert str_manual_with_headers == SOME_CSV_STRING
        assert str_manual_with_headers == str_comma

