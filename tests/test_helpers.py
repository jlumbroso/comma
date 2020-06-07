
import os
import typing

import pytest
try:
    import requests
except ImportError:
    # this is an optional package
    requests = None


import comma.helpers


EXPECTED_CONSTANTS = [
    ("MAX_SAMPLE_CHUNKSIZE", int),
    ("URI_SCHEME_LOCAL", str),
    ("URI_SCHEMES_ACCEPTED", typing.List),
    ("LINE_TERMINATORS", typing.List),
    ("LINE_TERMINATOR_DEFAULT", str),
]


def test_are_expected_constants_defined():
    """
    Make sure
    """
    for name, typ in EXPECTED_CONSTANTS:
        if name not in comma.helpers.__dict__:
            raise Exception(
                "{typ} constant comma.helpers.{name} expected but undefined".format(
                    name=name, typ=typ,
                ))


def test_typecheck_constants():
    for name, typ in EXPECTED_CONSTANTS:
        if not isinstance(comma.helpers.__dict__.get(name), typ):
            raise Exception(
                "constant comma.helpers.{name} expected to be of type {typ}".format(
                    name=name, typ=typ,
                ))


def test_detect_unexpected_constants():
    constant_names = map(lambda record: record[0], EXPECTED_CONSTANTS)
    for name in comma.helpers.__dict__.keys():
        if name == name.upper():
            if name not in constant_names:
                raise Exception(
                    ("constant comma.helpers.{name} found but unexpected; "
                     "should be added to tests?").format(
                        name=name,
                    ))


class TestIsAnyStr:
    """
    Test cases for the comma.helpers.is_anystr() method.
    """

    TRUE_CASES = [u"SOME_STRING", b"SOME_BYTE_STRING"]
    FALSE_CASES = [0, 1, list(), dict()]

    @pytest.mark.parametrize('value', TRUE_CASES)
    def test_true(self, value):
        assert comma.helpers.is_anystr(value)

    @pytest.mark.parametrize('value', FALSE_CASES)
    def test_false(self, value):
        assert not comma.helpers.is_anystr(value)


class TestIsLocal:

    class BogusDecodeClass:
        def decode(self):
            pass

    @pytest.mark.parametrize("value", [".", "././.", "file://.", "file://./././"])
    def test_dot(self, value):
        """
        Tests whether synonyms of the current working directory all
        evaluate to the same path.
        """
        assert comma.helpers.is_local(value) == os.getcwd()

    @pytest.mark.parametrize("value", ["", "...", "somesuch://somesuch"])
    def test_invalid_string(self, value):
        """
        Tests whether obviously invalid paths return `None`.
        """
        assert comma.helpers.is_local(value) is None

    @pytest.mark.parametrize("value", [None, {"somekey": "somevalue"}, BogusDecodeClass()])
    def test_invalid_input(self, value):
        """
        Tests whether obviously invalid input types return `None` (likely after
        failing and catching an internal exception).
        """
        casted_value = typing.cast(typing.AnyStr, value)  # (purposefully) invalid cast
        assert comma.helpers.is_local(casted_value) is None

    @pytest.mark.parametrize("value", ["~"])
    def test_user_expansion(self, value):
        """
        Tests whether obviously invalid input types return `None` (likely after
        failing and catching an internal exception).
        """

        expanded_value = os.path.expanduser(value)

        assert expanded_value != value
        assert os.path.exists(expanded_value)
        assert comma.helpers.is_local(value) == expanded_value


class TestIsUrl:
    """
    Test cases for the comma.helpers.is_url() method.
    """

    class BogusDecodeClass:
        def decode(self):
            pass

    TRUE_CASES = ["http://somedomaine.com"]
    FALSE_CASES = ["", ".", "://someschemelesspath", "file://somelocalpath/", "file:///./"]
    INVALID_CASES = [None, {"somekey": "somevalue"}, BogusDecodeClass()]

    SOME_URL = "http://testurl.com/testfile.csv"

    @pytest.mark.parametrize('value', TRUE_CASES)
    def test_true(self, value):
        assert comma.helpers.is_url(value, no_request=True)

    @pytest.mark.parametrize('value', FALSE_CASES)
    def test_false(self, value):
        assert not comma.helpers.is_url(value, no_request=True)

    @pytest.mark.parametrize("value", INVALID_CASES)
    def test_invalid_input(self, value):
        """
        Tests whether obviously invalid input types return `None` (likely after
        failing and catching an internal exception).
        """
        casted_value = typing.cast(typing.AnyStr, value)  # (purposefully) invalid cast
        assert not comma.helpers.is_url(casted_value, no_request=True)

    def test_requests_success(self, requests_mock):
        # package is optional
        if requests is None:
            assert True
            return

        requests_mock.head(self.SOME_URL, status_code=200)
        assert comma.helpers.is_url(self.SOME_URL)

    def test_requests_failed(self, mocker, requests_mock):
        # package is optional
        if requests is None:
            assert True
            return

        # we can handle a connection error
        requests_mock.head(self.SOME_URL, exc=requests.exceptions.ConnectionError)
        assert not comma.helpers.is_url(self.SOME_URL)

        # we can also handle an invalid scheme error
        requests_mock.head(self.SOME_URL, exc=requests.exceptions.InvalidSchema)
        assert not comma.helpers.is_url(self.SOME_URL)

        # we can handle if somehow the returned response is None
        mocker.patch("requests.head", return_value=None)
        assert not comma.helpers.is_url(self.SOME_URL)


class TestOpenStream:
    pass


class TestDetectLineTerminator:
    """

    """

    DEFAULT = comma.helpers.LINE_TERMINATOR_DEFAULT
    OTHER_DEFAULT = "somestring"
    UNIX_NEWLINE = "\n"
    WINDOWS_NEWLINE = "\r\n"
    WINDOWS_NEWLINE_TEST = WINDOWS_NEWLINE*100

    class BogusCountClass1:
        def count(self):
            return

    class BogusCountClass2:
        def count(self, *args, **kwargs):
            return

    class BogusCountClass3:
        def count(self, value, *args, **kwargs):
            return 0

    @pytest.mark.parametrize("value", [None, ""])
    def test_default_cases(self, value):
        assert comma.helpers.detect_line_terminator(
            sample=value, default=None) == self.DEFAULT

    @pytest.mark.parametrize("value", [None, ""])
    def test_default_cases_with_alternate_default(self, value):
        assert comma.helpers.detect_line_terminator(
            sample=value, default=self.OTHER_DEFAULT) == self.OTHER_DEFAULT

    @pytest.mark.parametrize("value", [BogusCountClass1(),
                                       BogusCountClass2(),
                                       BogusCountClass3()])
    def test_default_cases_with_bogus_classes(self, value):
        assert comma.helpers.detect_line_terminator(
            sample=value, default=None) == self.DEFAULT

    def test_windows_newline(self):
        assert comma.helpers.detect_line_terminator(
            sample=self.WINDOWS_NEWLINE_TEST,
            default=self.OTHER_DEFAULT) == self.WINDOWS_NEWLINE

    def test_unix_newline(self):
        # with one more UNIX new line, the count should be in that favor
        assert comma.helpers.detect_line_terminator(
            sample=self.WINDOWS_NEWLINE_TEST + self.UNIX_NEWLINE,
            default=self.OTHER_DEFAULT) == self.UNIX_NEWLINE


class TestMultisliceSequence:
    """
    Tests for the `comma.helpers.multislice_sequence()` helper method, which
    applies a sequence of slice operations to an initial list. This test module
    checks the edge-cases, and then checks whether one repeated slicing
    operation provides the same result as doing the operation manually.
    """

    SOME_LIST = list(range(10))
    ALL_BUT_LAST_SLICE = slice(0, -1, None)

    def test_none_slice_list(self):
        """
        Checks whether the `comma.helpers.multislice_sequence()` method is a no-op
        for the input `sequence` if the `slice_list` is `None`.
        """
        assert comma.helpers.multislice_sequence(
            sequence=self.SOME_LIST, slice_list=None) == self.SOME_LIST

    def test_empty_slice_list(self):
        """
        Checks whether the `comma.helpers.multislice_sequence()` method is a no-op
        for the input `sequence` if the `slice_list` is `[]` (the empty list).
        """
        assert comma.helpers.multislice_sequence(
            sequence=self.SOME_LIST, slice_list=list()) == self.SOME_LIST

    def test_slice_list(self):
        """
        Checks whether the `comma.helpers.multislice_sequence()` method is a no-op
        for the input `sequence` if the `slice_list` is `[]` (the empty list).
        """
        slice_list = []
        current = self.SOME_LIST[:]

        while len(current) > 1:
            # check
            assert comma.helpers.multislice_sequence(
                sequence=self.SOME_LIST, slice_list=slice_list) == current

            # append another slice (which will remove an extra element from the
            # tail of the list)
            slice_list.append(self.ALL_BUT_LAST_SLICE)

            # remove last element of comparison list
            current = current[self.ALL_BUT_LAST_SLICE]

