
import comma.extras

import pytest


class TestIsBinaryString:
    pass

class TestDetectEncoding:

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

    @pytest.mark.parametrize("original_string", SOME_UTF8_STRINGS)
    @pytest.mark.parametrize("encoding", ENCODINGS_GUESSABLE_BY_BOM)
    def test_detect_by_bom(self, original_string, encoding):

        # checking that this works
        encoded_string = original_string.encode(encoding)
        decoded_string = encoded_string.decode(encoding)

        # check the result is what it should be
        assert original_string == decoded_string

        # now checking we would detect this encoding properly with BOM
        guessed_encoding = (
            comma.extras._detect_encoding_by_bom(encoded_string))  # pylint: disable=protected-access
        assert (guessed_encoding == encoding or guessed_encoding is None)


