
import io
import typing

import pytest

import comma.methods
import comma.typing


SOME_CSV_STRING = "name,age,gender\nPerson1,33,F\nPerson2,25,M\n"
SOME_CSV_STRING_NO_HEADER = "\n".join(SOME_CSV_STRING.split("\n")[1:])
SOME_CSV_STRING_HAS_HEADER = True
SOME_CSV_STRING_ROW_COUNT = 2
SOME_CSV_STRING_COL_COUNT = 3

SOME_FILENAME = "somefilename.csv"


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
    def test_dump_from_string_or_stringio_with_list_cast(self, source):

        obj = comma.methods.load(source)
        assert comma.methods.dump(list(obj)) == SOME_CSV_STRING

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