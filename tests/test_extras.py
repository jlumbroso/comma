
import comma.extras

import pytest


class TestIsBinaryString:
    pass


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

