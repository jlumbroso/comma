
import comma.extras
import comma.helpers  # for comma.helpers.MAX_SAMPLE_CHUNKSIZE

import pytest


# noinspection PyProtectedMember
class TestDetectCsvType:

    SOME_EMPTY_STRING = ""

    SOME_STRING = "0,1,2\n"

    # fields expected in the dictionary returned by this method
    EXPECTED_FIELDS = [
        "dialect", "simple_dialect", "has_header", "line_terminator"]

    def test_fields_available_in_default(self):
        """
        Checks that the internal method, which uses the default Python
        `csv` package returns the expected kind of dictionary, with all
        expected fields.
        """

        result = comma.extras._default_detect_csv_type(sample=self.SOME_STRING)
        for fieldname in self.EXPECTED_FIELDS:
            assert fieldname in result

    def test_fields_available(self):
        """
        Checks that the publicly available `detect_csv_type()` method returns
        the expected kind of dictionary, with all expected fields.
        """

        result = comma.extras.detect_csv_type(sample=self.SOME_STRING)
        for fieldname in self.EXPECTED_FIELDS:
            assert fieldname in result

    def test_clevercsv(self):
        """
        Checks either that the `clevercsv` module is unavailable, or if it
        is available, it has been used to compute the CSV dialect heuristic
        (by checking that its specific dialect format, provided by the
        "simple_dialect" key in the returned dictionary, is defined).
        """

        try:
            import clevercsv
        except ImportError or ModuleNotFoundError:
            assert True
            return

        result = comma.extras.detect_csv_type(sample=self.SOME_STRING)

        # make sure "simple_dialect" is not None
        assert result.get("simple_dialect") is not None

    def test_empty(self):
        result = comma.extras.detect_csv_type(sample=self.SOME_EMPTY_STRING)
        assert result is not None
        assert "has_header" in result and not result["has_header"]

    def test_empty_default(self):
        result = comma.extras._default_detect_csv_type(sample=self.SOME_EMPTY_STRING)
        assert result is not None
        assert "has_header" in result and not result["has_header"]


# noinspection PyProtectedMember
class TestIsBinaryString:

    class BogusClass:
        pass

    SOME_BINARY_STRING_1 = (
        b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x9dftD\x8d5\xdbe\r"
        b"\x13|\x00\x10\x1a=\x02\n\x00\x1c\x00itcont.txtUT\t\x00"
        b"\x03\xe9\x1c+S\xe8\x1c+Sux\x0b\x00\x01\x04e\x00\x00\x00"
        b"\x04d\x00\x00\x00\xbc\\\xdb\x92\xa3\xb8\xb2}?_\xa1\xa7"
        b"\xd9/\xdd\xb1\x11w\x1ee\x90\x8d\xca\x80\xd8\x02\xca\xe3"
        b"\xfe\x16}\xfc")  # from a ZIP file

    SOME_BINARY_STRING_2 = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00H\x00"
        b"H\x00\x00\xff\xe1\x00\xb2Exif\x00\x00MM\x00*\x00\x00\x00"
        b"\x08\x00\x06\x01\x12\x00\x03\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x01\x1a\x00\x05\x00\x00\x00\x01\x00\x00\x00V\x01\x1b"
        b"\x00\x05\x00\x00\x00\x01\x00\x00\x00^\x01(\x00\x03\x00\x00"
        b"\x00\x01\x00\x02\x00\x00\x01;\x00\x02\x00\x00\x00\x19\x00"
        b"\x00\x00f")  # from a JPG file

    SOME_NON_BINARY_STRING = (
        b"\xe5\xb7\x9d\xe6\x9c\x88\xe6\x9c\xa8\xe5\xbf\x83\xe7"
        b"\x81\xab\xe5\xb7\xa6\xe5\x8c\x97\xe4\xbb\x8a\xe5\x90"
        b"\x8d\xe7\xbe\x8e\xe8\xa6\x8b\xe5\xa4\x96\xe6\x88\x90"
        b"\xe7\xa9\xba\xe6\x98\x8e\xe9\x9d\x99\xe6\xb5\xb7\xe9"
        b"\x9b\xb2\xe6\x96\xb0\xe8\xaa\x9e\xe9\x81\x93\xe8\x81"
        b"\x9e\xe5\xbc\xb7\xe9\xa3\x9b")  # also the Kanji string

    TRUE_CASES = [SOME_BINARY_STRING_1, SOME_BINARY_STRING_2]
    FALSE_CASES = [SOME_NON_BINARY_STRING]
    EDGE_CASES = [None, "", b"", BogusClass()]

    @pytest.mark.parametrize("bytestring", TRUE_CASES)
    def test_helper_internal_true(self, bytestring):
        assert comma.extras._is_binary_string_internal(bytestring)  # pylint: disable=protected-access

    @pytest.mark.parametrize("bytestring", FALSE_CASES)
    def test_helper_internal_false(self, bytestring):
        assert not comma.extras._is_binary_string_internal(bytestring)  # pylint: disable=protected-access

    @pytest.mark.parametrize("bytestring", TRUE_CASES)
    def test_helper_true(self, bytestring):
        assert comma.extras._is_binary_string(bytestring)  # pylint: disable=protected-access

    @pytest.mark.parametrize("bytestring", FALSE_CASES)
    def test_helper_false(self, bytestring):
        assert not comma.extras._is_binary_string(bytestring)  # pylint: disable=protected-access

    @pytest.mark.parametrize("value", EDGE_CASES)
    def test_edge_cases(self, value):
        assert not comma.extras.is_binary_string(value)

    def test_truncate(self, mocker):
        # construct a value larger than accepted
        max_size = comma.helpers.MAX_SAMPLE_CHUNKSIZE
        long_value = "\0" * (max_size + 10)

        mocker.patch("comma.extras._is_binary_string", return_value=True)

        # we expected return_value=True (even/especially since it shouldn't
        # and wouldn't if the method had not been patched)
        assert comma.extras.is_binary_string(long_value, truncate=True)

        # noinspection PyUnresolvedReferences
        comma.extras._is_binary_string.assert_called_once_with(
            long_value[:max_size])


# noinspection PyProtectedMember
class TestDetectEncoding:

    SOME_MADE_UP_ENCODING = "native-9"

    SOME_UTF8_STRING_KANJI = (
        b"\xe5\xb7\x9d\xe6\x9c\x88\xe6\x9c\xa8\xe5\xbf\x83\xe7"
        b"\x81\xab\xe5\xb7\xa6\xe5\x8c\x97\xe4\xbb\x8a\xe5\x90"
        b"\x8d\xe7\xbe\x8e\xe8\xa6\x8b\xe5\xa4\x96\xe6\x88\x90"
        b"\xe7\xa9\xba\xe6\x98\x8e\xe9\x9d\x99\xe6\xb5\xb7\xe9"
        b"\x9b\xb2\xe6\x96\xb0\xe8\xaa\x9e\xe9\x81\x93\xe8\x81"
        b"\x9e\xe5\xbc\xb7\xe9\xa3\x9b").decode("utf-8")  # utf-8 encoded

    SOME_UTF8_STRING_FRENCH_NAME = b"J\xc3\xa9r\xc3\xa9mie Lumbroso".decode("utf-8")

    SOME_UTF8_STRINGS = [SOME_UTF8_STRING_KANJI,
                         SOME_UTF8_STRING_FRENCH_NAME]

    ENCODINGS_GUESSABLE_BY_BOM = [
        "utf-8-sig",

        "utf-16",
        "utf-16-le",
        "utf-16-be",

        "utf-32",
        "utf-32-le",
        "utf-32-be",
    ]

    ENCODINGS_GUESSABLE_BY_CHARDET = [
        "latin-1",
        "iso-8859-9",
    ]

    @pytest.mark.parametrize("original_string", SOME_UTF8_STRINGS)
    @pytest.mark.parametrize("encoding", ENCODINGS_GUESSABLE_BY_BOM)
    def test_detect_by_bom(self, original_string, encoding):
        """
        Checks that the (deterministic) encoding detection method
        for Unicode compatible encodings (UTF-8, UTF-16, UTF-32, etc.)
        works on a test string encoded in each of those encodings.
        """

        # checking that this works
        encoded_string = original_string.encode(encoding)
        decoded_string = encoded_string.decode(encoding)

        # check the result is what it should be
        assert original_string == decoded_string

        # now checking we would detect this encoding properly with BOM
        guessed_encoding = (
            comma.extras._detect_encoding_by_bom(encoded_string))  # pylint: disable=protected-access
        assert (guessed_encoding == encoding or guessed_encoding is None)

        # now check that this is the same output produced by detect_encoding
        if guessed_encoding is not None:
            assert (guessed_encoding == comma.extras.detect_encoding(
                sample=encoded_string,
                default=None))

    def test_detect_by_bom_failing(self):
        """
        Checks whether
        """
        # this is a made up BOM which happens to have 3 nulls (like the BOM for
        # UTF-32); it was chosen to pass all tests of the BOM detection except
        # the last one
        bogus_bom = (
            comma.extras._null +
            '\x13'.encode('ascii') +
            comma.extras._null +
            comma.extras._null
        )
        result = comma.extras._detect_encoding_by_bom(
            bogus_bom,
            default=self.SOME_MADE_UP_ENCODING)

        # all BOM detection should have failed, and we should have gotten the
        # (made up) default encoding
        assert result == self.SOME_MADE_UP_ENCODING

    @pytest.mark.parametrize("original_string", [SOME_UTF8_STRING_FRENCH_NAME])
    @pytest.mark.parametrize("encoding", ENCODINGS_GUESSABLE_BY_CHARDET)
    def test_detect_by_chardet(self, original_string, encoding):
        """
        Checks that the heuristic provided by chardet is used when the BOM
        detection fails, and checks that strings (at least among the test
        pool of strings) are correctly decoded with the chosen encoding.
        """

        # first check if chardet is available, if not, tests succeeds by default
        try:
            import chardet
        except ImportError or ModuleNotFoundError:
            assert True
            return

        # checking that this works
        encoded_string = original_string.encode(encoding)
        decoded_string = encoded_string.decode(encoding)

        # check the result is what it should be
        assert original_string == decoded_string

        # now checking we would NOT detect this encoding properly with BOM
        guessed_encoding_by_bom = (
            comma.extras._detect_encoding_by_bom(
                sample=encoded_string,
                default=None))  # pylint: disable=protected-access
        assert guessed_encoding_by_bom is None

        # look at chardet's answer
        chardet_result = chardet.detect(encoded_string)
        assert chardet_result is not None
        chardet_encoding = chardet_result.get("encoding")
        assert chardet_encoding is not None

        chardet_decoded_string = encoded_string.decode(chardet_encoding)

        # succeed either if we guess the right encoding, or the encoding that
        # was guessed results in the right decoding of the encoded string
        # (e.g., latin-1 and ISO-8859-9 can be equivalent for some inputs)
        assert (
            (chardet_encoding == encoding) or
            (chardet_decoded_string == decoded_string))

        # now check that this is the same output produced by detect_encoding
        assert (chardet_encoding == comma.extras.detect_encoding(
            sample=encoded_string,
            default=None))

    def test_detect_by_default(self, mocker):
        """
        Checks that the `comma.extras.detect_encoding()` method returns
        the user-specified `default` (by default, `None`) if none of the
        heuristics provided a guess.
        """

        # check that _detect_encoding_by_bom is defined, and patch it
        assert "_detect_encoding_by_bom" in comma.extras.__dict__
        mocker.patch("comma.extras._detect_encoding_by_bom", return_value=None)

        # only patch the chardet module if it is available
        try:
            import chardet
            mocker.patch("chardet.detect", return_value=None)
        except ImportError or ModuleNotFoundError:
            pass

        # having had all the heuristics fail, check if the returned
        # default value is what we expect it will be
        assert comma.extras.detect_encoding(
            sample=self.SOME_UTF8_STRING_KANJI,
            default=self.SOME_MADE_UP_ENCODING) == self.SOME_MADE_UP_ENCODING

