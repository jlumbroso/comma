
import pytest

import comma.config


class TestConfigHelper:

    SOME_INT_VALUES = ["1", "0", "11111", "3214"]
    SOME_NOT_INT_VALUES = ["", "a", None, "1.0", "1e7", "True"]

    SOME_FLOAT_VALUES = SOME_INT_VALUES + ["1.0", "1.3333", "1e7", "1e-7", "1.0e-7"]
    SOME_NOT_FLOAT_VALUES = ["", "a", None, "True"]

    SOME_STRING = "some string"
    SOME_BOOL_STRING = "true"
    SOME_INT_STRING = "1"
    SOME_FLOAT_STRING = "1.0"

    @pytest.mark.parametrize("not_int_value", SOME_NOT_INT_VALUES)
    def test_is_int_false(self, not_int_value):
        assert not comma.config.ConfigHelper.is_int(not_int_value)
        with pytest.raises(Exception):
            comma.config.ConfigHelper.parse_int(not_int_value)

    @pytest.mark.parametrize("int_value", SOME_INT_VALUES)
    def test_is_int_true(self, int_value):
        assert comma.config.ConfigHelper.is_int(int_value)
        comma.config.ConfigHelper.parse_int(int_value)
        comma.config.ConfigHelper.parse_float(int_value)

    @pytest.mark.parametrize("not_float_value", SOME_NOT_FLOAT_VALUES)
    def test_is_float_false(self, not_float_value):
        assert not comma.config.ConfigHelper.is_float(not_float_value)
        with pytest.raises(Exception):
            comma.config.ConfigHelper.parse_float(not_float_value)

    @pytest.mark.parametrize("float_value", SOME_FLOAT_VALUES)
    def test_is_float_true(self, float_value):
        assert comma.config.ConfigHelper.is_float(float_value)
        comma.config.ConfigHelper.parse_float(float_value)

    @pytest.mark.parametrize("bool_value",
                             comma.config.ConfigHelper.BOOL_STR_FALSE +
                             comma.config.ConfigHelper.BOOL_STR_TRUE)
    def test_is_bool_true(self, bool_value):
        assert comma.config.ConfigHelper.is_likely_bool(bool_value)
        comma.config.ConfigHelper.parse_bool(bool_value)

    @pytest.mark.parametrize("value", comma.config.ConfigHelper.BOOL_STR_TRUE)
    def test_parse_bool_true(self, value):
        assert comma.config.ConfigHelper.parse_bool(value)

    @pytest.mark.parametrize("value", comma.config.ConfigHelper.BOOL_STR_FALSE)
    def test_parse_bool_false(self, value):
        assert not comma.config.ConfigHelper.parse_bool(value)

    @pytest.mark.parametrize("value",
                             comma.config.ConfigHelper.BOOL_STR_TRUE +
                             comma.config.ConfigHelper.BOOL_STR_FALSE +
                             [])
    def test_is_likely_bool_true(self, value):
        assert comma.config.ConfigHelper.is_likely_bool(value)

    @pytest.mark.parametrize("value", [1.0])
    def test_is_likely_bool_false(self, value):
        assert not comma.config.ConfigHelper.is_likely_bool(value)

    def test_parse_bool_others(self):
        assert not comma.config.ConfigHelper.is_likely_bool(None)
        assert not comma.config.ConfigHelper.parse_bool(None)
        assert not comma.config.ConfigHelper.parse_bool(0)
        assert not comma.config.ConfigHelper.parse_bool("")
        assert comma.config.ConfigHelper.parse_bool(1)
        assert comma.config.ConfigHelper.parse_bool(2)
        assert comma.config.ConfigHelper.parse_bool(self.SOME_STRING)

    def test_guess(self):
        assert comma.config.ConfigHelper.guess(self.SOME_INT_STRING) is int
        assert comma.config.ConfigHelper.guess(self.SOME_FLOAT_STRING) is float
        assert comma.config.ConfigHelper.guess(self.SOME_BOOL_STRING) is bool
        assert comma.config.ConfigHelper.guess(self.SOME_STRING) is str

    def test_check(self):
        assert comma.config.ConfigHelper.check(self.SOME_INT_STRING, int)
        assert comma.config.ConfigHelper.check(self.SOME_FLOAT_STRING, float)
        assert comma.config.ConfigHelper.check(self.SOME_BOOL_STRING, bool)
        assert comma.config.ConfigHelper.check(self.SOME_STRING, str)
        assert not comma.config.ConfigHelper.check(self.SOME_FLOAT_STRING, int)
        assert not comma.config.ConfigHelper.check(self.SOME_FLOAT_STRING, object)

    def test_parse(self):
        assert comma.config.ConfigHelper.parse(self.SOME_INT_STRING) == int(self.SOME_INT_STRING)
        assert comma.config.ConfigHelper.parse(self.SOME_FLOAT_STRING) == float(self.SOME_FLOAT_STRING)
        assert (comma.config.ConfigHelper.parse(self.SOME_BOOL_STRING) ==
                comma.config.ConfigHelper.parse_bool(self.SOME_BOOL_STRING))
        assert comma.config.ConfigHelper.parse(self.SOME_STRING) == self.SOME_STRING
        assert comma.config.ConfigHelper.parse(self.SOME_STRING, typ=object) is None


class TestConfig:

    def test_config_constructor(self):
        comma.config.ConfigClass()

    def test_misc(self):
        obj = comma.config.ConfigClass()

        obj.SLICE_DEEP_COPY_DATA = True
        assert obj.SLICE_DEEP_COPY_DATA
        obj.SLICE_DEEP_COPY_DATA = False
        assert not obj.SLICE_DEEP_COPY_DATA

        obj.SLICE_DEEP_COPY_PARENT = True
        assert obj.SLICE_DEEP_COPY_PARENT
        obj.SLICE_DEEP_COPY_PARENT = False
        assert not obj.SLICE_DEEP_COPY_PARENT
