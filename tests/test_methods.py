
import io
import typing

import pytest

import comma

SOME_CSV_STRING = "name,age,gender\nPerson1,33,M\nPerson2,25,M\n"
SOME_CSV_STRING_HAS_HEADER = True
SOME_CSV_STRING_ROW_COUNT = 2
SOME_CSV_STRING_COL_COUNT = 3


class TestLoad:

    def test_none_source(self):
        casted_none = typing.cast(
            comma.typing.SourceType, None)  # (purposefully) invalid cast
        obj = comma.load(source=casted_none)
        assert obj is None

    @pytest.mark.parametrize("source", [SOME_CSV_STRING,
                                        io.StringIO(SOME_CSV_STRING)])
    def test_load_from_string_or_stringio(self, source):

        obj = comma.load(source)

        # make sure we know what we are getting
        assert (len(obj) == SOME_CSV_STRING_ROW_COUNT)
        assert ((obj.header is not None) == SOME_CSV_STRING_HAS_HEADER)
        assert (len(obj.header) == SOME_CSV_STRING_COL_COUNT)
