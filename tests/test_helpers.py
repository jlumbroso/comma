
import io
import itertools
import os
import typing

import pytest
try:
    import requests
except ImportError:
    # this is an optional package
    requests = None

import comma.helpers
import comma.typing


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

    SOME_URL = "https://somesite.io/file.csv"

    SOME_DATA = "col1,col2,col3\n,'row1',1,2\n'row2',5,6\n"

    SOME_UTF8_ENCODED_STRING = (
        b"\xe5\xb7\x9d\xe6\x9c\x88\xe6\x9c\xa8\xe5\xbf\x83\xe7"
        b"\x81\xab\xe5\xb7\xa6\xe5\x8c\x97\xe4\xbb\x8a\xe5\x90"
        b"\x8d\xe7\xbe\x8e\xe8\xa6\x8b\xe5\xa4\x96\xe6\x88\x90"
        b"\xe7\xa9\xba\xe6\x98\x8e\xe9\x9d\x99\xe6\xb5\xb7\xe9"
        b"\x9b\xb2\xe6\x96\xb0\xe8\xaa\x9e\xe9\x81\x93\xe8\x81"
        b"\x9e\xe5\xbc\xb7\xe9\xa3\x9b")  # also the Kanji string

    SOME_UTF8_DECODED_STRING = SOME_UTF8_ENCODED_STRING.decode("utf-8")

    @staticmethod
    def check_stream(
            stream: typing.IO,
            check_seekable: typing.Optional[bool] = None,
            check_position: typing.Optional[int] = None,
            reset_position: typing.Optional[bool] = False,
            check_content: typing.Optional[typing.AnyStr] = None,
            check_closeable: typing.Optional[bool] = True
    ) -> typing.NoReturn:
        # check input is not None
        assert stream is not None, "provided `stream` is None"

        # check input is a stream
        assert hasattr(stream, "seekable"), \
            "provided `stream` does not appear file-like"

        # check_seekable
        if check_seekable is not None:
            assert stream.seekable() == check_seekable, \
                "value of stream.seekable() is not as expected"

        # check_position
        if check_position is not None:
            if hasattr(stream, "tell"):
                assert stream.tell() == check_position, "position not as expected"
            elif hasattr(stream, "seek"):
                # stream.seek(0, 1) is an alternate to stream.tell()
                assert stream.seek(0, 1) == check_position, "position not as expected"

        # reset_position
        if reset_position is not None and reset_position:
            # the stream.seek(0) will fail if these don't pass
            assert hasattr(stream, "seekable")
            assert stream.seekable()

            # reset the stream's position
            stream.seek(0)

        # check_content
        if check_content is not None and check_content:
            content = stream.read()
            assert content == check_content, "stream content is not as expected"

        # check_closeable
        if check_closeable is not None and check_closeable:
            assert hasattr(stream, "closed") and not stream.closed
            assert hasattr(stream, "close")
            stream.close()
            assert stream.closed, "cannot close stream"

    def test_none_source(self):
        casted_none = typing.cast(
            comma.typing.SourceType, None)  # (purposefully) invalid cast
        assert comma.helpers.open_stream(source=casted_none) is None

    def test_string_data_input(self):
        result = comma.helpers.open_stream(source=self.SOME_DATA)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_DATA)

    def test_string_data_input_windows_newline(self):
        some_windows_data = self.SOME_DATA.replace("\n", "\r\n")
        result = comma.helpers.open_stream(source=some_windows_data)

        # the resulting stream should be normalized, despite the windows newline
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_DATA)

    def test_file_open(self, mocker):
        mocker.patch("comma.helpers.is_local", return_value="file.csv")
        mocker.patch("comma.helpers.open", return_value=io.BytesIO(b"aaa\0"))
        result = comma.helpers.open_stream(source="file.csv")
        comma.helpers.open.assert_called_with("file.csv", mode="rb")
        TestOpenStream.check_stream(stream=result, reset_position=True, check_content="aaa\0")

    def test_byte_data_input(self):
        result = comma.helpers.open_stream(source=self.SOME_UTF8_ENCODED_STRING)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_unseekable_string_stream(self, mocker):
        # setup the mock source
        source = mocker.Mock(
            seekable=mocker.Mock(return_value=False),
            read=mocker.Mock(return_value=self.SOME_DATA))
        # check source
        result = comma.helpers.open_stream(source=source)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_DATA)

    def test_unseekable_byte_stream(self, mocker):
        # setup the mock source
        source = mocker.Mock(
            seekable=mocker.Mock(return_value=False),
            read=mocker.Mock(return_value=self.SOME_UTF8_ENCODED_STRING))
        # check source
        result = comma.helpers.open_stream(source=source)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_is_bad_url(self, mocker, requests_mock):
        mocker.patch("comma.helpers.is_url", return_value=True)
        requests_mock.get(
            url=self.SOME_URL,
            status_code=404)
        result = comma.helpers.open_stream(source=self.SOME_URL, no_request=False)
        assert result is None

    def test_is_url_text(self, mocker, requests_mock):
        mocker.patch("comma.helpers.is_url", return_value=True)
        requests_mock.get(
            url=self.SOME_URL,
            content=self.SOME_DATA.encode("ascii"),
            headers={"Content-Type": "text/html; charset=ascii"})
        result = comma.helpers.open_stream(source=self.SOME_URL, no_request=False)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_DATA)

        # redo with explicit encoding
        result = comma.helpers.open_stream(source=self.SOME_URL,
                                           encoding="ascii",
                                           no_request=False)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_DATA)

    def test_is_url_bytes(self, mocker, requests_mock):
        mocker.patch("comma.helpers.is_url", return_value=True)
        requests_mock.get(
            url=self.SOME_URL,
            content=self.SOME_UTF8_ENCODED_STRING)
        result = comma.helpers.open_stream(source=self.SOME_URL, no_request=False)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_none_string(self, mocker):
        mocker.patch("comma.helpers.is_local", return_value=None)
        mocker.patch("comma.helpers.is_url", return_value=False)
        result = comma.helpers.open_stream(source=self.SOME_URL, no_request=True)
        assert result is None

    def test_bad_input(self):
        casted_bad_input = typing.cast(comma.typing.SourceType, list())
        result = comma.helpers.open_stream(source=casted_bad_input, no_request=True)
        assert result is None

    def test_nonseekable_broken_source(self, mocker):
        mock_source = mocker.Mock(
            seekable=mocker.Mock(return_value=False),
            read=mocker.Mock(return_value=[False]),
        )
        with pytest.raises(ValueError):
            comma.helpers.open_stream(source=mock_source, no_request=True)

    def aux_test_zipfile(self, mocker, csv_file_count, txt_file_count):
        # build list of filenames
        filenames = list(itertools.chain(
            map("file{}.csv".format, range(csv_file_count)),
            map("file{}.txt".format, range(txt_file_count))
        ))
        mocker.patch("zipfile.is_zipfile", return_value=True)
        mocker.patch("zipfile.ZipFile", return_value=mocker.Mock(
            namelist=mocker.Mock(return_value=filenames),
            read=mocker.Mock(return_value=self.SOME_UTF8_ENCODED_STRING)))
        result = comma.helpers.open_stream(source=io.StringIO(), no_request=False)
        return result

    def test_zipfile_one(self, mocker):
        result = self.aux_test_zipfile(mocker=mocker, csv_file_count=1, txt_file_count=0)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_zipfile_one_no_csv(self, mocker):
        result = self.aux_test_zipfile(mocker=mocker, csv_file_count=0, txt_file_count=1)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_zipfile_two(self, mocker):
        result = self.aux_test_zipfile(mocker=mocker, csv_file_count=1, txt_file_count=1)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_zipfile_more(self, mocker):
        result = self.aux_test_zipfile(mocker=mocker, csv_file_count=1, txt_file_count=10)
        TestOpenStream.check_stream(stream=result, check_content=self.SOME_UTF8_DECODED_STRING)

    def test_zipfile_conflict(self, mocker):
        with pytest.raises(ValueError):
            self.aux_test_zipfile(mocker=mocker, csv_file_count=2, txt_file_count=1)

    def test_zipfile_no_files(self, mocker):
        with pytest.raises(ValueError):
            self.aux_test_zipfile(mocker=mocker, csv_file_count=0, txt_file_count=0)


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


class TestOpenCSV:

    NO_DATA_STRING = ""
    NO_DATA_LIST = list()

    SOME_FILENAME = "some_filename.csv"

    SOME_DATA_NO_HEADER = ("Person1,45,blue\n"
                           "Person2,82,green\n"
                           "Person3,17,brown\n"
                           "Person4,27,brown\n")

    SOME_DATA_WITH_HEADER = ("name,age,eye_color\n" + SOME_DATA_NO_HEADER)

    def test_none_source(self):
        """
        Checks whether the `comma.helpers.open_csv()` gracefully handles the
        case where the provided `source` is a `None` object.
        """
        # (purposefully) invalid cast
        casted_none = typing.cast(comma.typing.SourceType, None)
        assert comma.helpers.open_csv(source=casted_none) is None

    def test_none_stream(self, mocker):
        """
        Checks whether the `comma.helpers.open_csv()` gracefully handles the
        case where `comma.helpers.open_stream()` returns a `None` object. 
        """
        mocker.patch("comma.helpers.open_stream", return_value=None)
        assert comma.helpers.open_csv(source=self.SOME_FILENAME) is None

    def test_some_data_no_header(self):
        ret = comma.helpers.open_csv(source=self.SOME_DATA_NO_HEADER)
        assert ret is not None
        assert "params" in ret and "has_header" in ret.get("params")
        assert not ret["params"]["has_header"]

    def test_some_data_with_header(self):
        ret = comma.helpers.open_csv(source=self.SOME_DATA_WITH_HEADER)
        assert ret is not None
        assert "params" in ret and "has_header" in ret.get("params")
        assert ret["params"]["has_header"]

    def test_misdetected_no_headers(self, mocker):
        """
        Checks whether the `comma.helpers.open_csv()` is able to detect when
        headers are missing.
        """
        no_data_stream = io.StringIO(self.NO_DATA_STRING)

        mocker.patch("comma.helpers.open_stream", return_value=no_data_stream)
        mocker.patch("csv.reader", return_value=self.NO_DATA_LIST)
        mocker.patch("comma.extras.detect_csv_type", return_value={
            "dialect": None,  # ignored
            "simple_dialect": None,  # ignored
            "has_header": True,  # <-- important because trying to trick method
            "line_terminator": "\n",  # not important
        })

        ret = comma.helpers.open_csv(source=self.SOME_FILENAME)

        assert ret is not None
        assert "params" in ret and "has_header" in ret.get("params")
        assert not ret["params"]["has_header"]

    def test_close_at_end(self, mocker):
        """
        Checks whether internally created streams are closed.
        """
        byte_stream = io.BytesIO(self.SOME_DATA_WITH_HEADER.encode("utf-8"))
        try:
            byte_stream.buffer.name = "some binary stream"
        except AttributeError:
            pass

        string_stream = io.StringIO(self.SOME_DATA_WITH_HEADER)
        try:
            string_stream.buffer.name = "some string stream"
        except AttributeError:
            pass
        mocker.patch("comma.helpers.open_stream", return_value=string_stream)

        comma.helpers.open_csv(source=byte_stream)

        # original stream should not be closed
        assert not byte_stream.closed

        # internally produced stream ("created" by `comma.helpers.open_stream()`)
        # should be closed
        assert string_stream.closed


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


class TestZipHtmlTag:

    SOME_ITERABLE = [1]
    SOME_INVALID_INDENT = "badindent"

    def test_produces_string(self):
        assert type(comma.helpers.zip_html_tag(data=self.SOME_ITERABLE)) is str

    def test_bad_indentg(self):
        assert type(comma.helpers.zip_html_tag(
            data=self.SOME_ITERABLE,
            indent=self.SOME_INVALID_INDENT
        )) is str
