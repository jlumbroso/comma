
import pytest

import comma.classes.file
import comma.exceptions
import comma.helpers


class TestCommaFile:

    SOME_HEADER = ["first", "second", "third"]

    SOME_OTHER_STRING = "umpteenth"

    @pytest.fixture()
    def comma_file(self):
        return comma.classes.file.CommaFile()

    @pytest.fixture()
    def comma_file_with_header(self):
        return comma.classes.file.CommaFile(
            header=self.SOME_HEADER,
            primary_key=self.SOME_HEADER[0],
        )

    def test_delete_header(self, comma_file_with_header):
        assert comma_file_with_header._header is not None
        assert comma_file_with_header.header is not None

        del comma_file_with_header.header

        assert comma_file_with_header._header is None
        assert comma_file_with_header.header is None

    def test_header_non_iterable(self, mocker):
        with pytest.raises(comma.exceptions.CommaInvalidHeaderException):
            comma.classes.file.CommaFile(header=mocker.Mock())

    def test_primary_key_with_no_header(self, comma_file):
        """

        """

        # default header is None
        assert comma_file.header is None

        # default values
        assert comma_file._primary_key is None
        assert comma_file.primary_key is None

        # check if primary key throws an exception when tried to set
        with pytest.raises(comma.exceptions.CommaNoHeaderException) as exc:
            comma_file.primary_key = self.SOME_HEADER[0]

    @pytest.mark.parametrize("unsetting_value", [None, "", False])
    def test_primary_key_with_header(self, comma_file_with_header, unsetting_value):
        """

        """

        # check header is set
        assert comma_file_with_header.header is not None
        assert comma_file_with_header.header == self.SOME_HEADER

        primary_key_val = comma_file_with_header.header[0]

        assert comma_file_with_header._primary_key == primary_key_val
        assert comma_file_with_header.primary_key == primary_key_val

        # should set it to None
        del comma_file_with_header.primary_key

        assert comma_file_with_header._primary_key is None
        assert comma_file_with_header.primary_key is None

        # having removed the element
        assert comma_file_with_header._primary_key is None
        assert comma_file_with_header.primary_key is None

        # check if primary key throws an exception when tried to set
        comma_file_with_header.primary_key = primary_key_val

        assert comma_file_with_header._primary_key == primary_key_val
        assert comma_file_with_header.primary_key == primary_key_val

        # check delete primary key
        comma_file_with_header.primary_key = unsetting_value
        assert comma_file_with_header.primary_key is None

    def test_absent_primary_key_with_header(self, comma_file_with_header):
        """

        """

        # check header is set
        assert comma_file_with_header.header is not None
        assert comma_file_with_header.header == self.SOME_HEADER

        with pytest.raises(comma.exceptions.CommaKeyError) as exc_info:
            comma_file_with_header.primary_key = self.SOME_OTHER_STRING

        # if available header should be in exception string
        header_repr = comma_file_with_header.header.__repr__()
        assert header_repr in str(exc_info.getrepr())

    def test_absent_primary_key_crash(self, comma_file, mocker):
        """

        """

        # a header object that throws exception on __repr__()
        mock_header = mocker.MagicMock(__repr__=mocker.Mock(side_effect=Exception))
        mock_header.__iter__.return_value = self.SOME_HEADER
        comma_file._header = mock_header

        with pytest.raises(comma.exceptions.CommaKeyError) as exc_info:
            comma_file.primary_key = self.SOME_OTHER_STRING

    # def test_header_not_implemented(self, comma_file):
    #     """
    #
    #     """
    #     with pytest.raises(NotImplementedError):
    #         comma_file.header = self.SOME_HEADER

    def test_header_change_iterator(self, comma_file_with_header):
        new_headers_iterator = reversed(comma_file_with_header.header[:])
        new_headers_list = list(reversed(comma_file_with_header.header[:]))

        assert comma_file_with_header.header is not None

        comma_file_with_header.header = new_headers_iterator

        assert comma_file_with_header.header is not None
        assert comma_file_with_header.header == new_headers_list

    def test_header_change_list(self, comma_file_with_header):
        new_headers_list = list(reversed(comma_file_with_header.header[:]))

        assert comma_file_with_header.header is not None

        comma_file_with_header.header = new_headers_list

        assert comma_file_with_header.header is not None
        assert comma_file_with_header.header == new_headers_list

    def test_header_change_invalid_value(self, comma_file_with_header, mocker):
        invalid_mock_header = mocker.Mock()

        assert comma_file_with_header.header is not None
        backup_header = comma_file_with_header.header[:]

        with pytest.raises(comma.exceptions.CommaInvalidHeaderException):
            comma_file_with_header.header = invalid_mock_header

        assert comma_file_with_header.header == backup_header

    def test_header_change_list_with_none(self, comma_file_with_header):

        assert comma_file_with_header.header is not None
        backup_header = comma_file_with_header.header[:]
        original_header_length = len(backup_header)

        invalid_header = [None] * original_header_length

        with pytest.raises(comma.exceptions.CommaInvalidHeaderException):
            comma_file_with_header.header = invalid_header

        assert comma_file_with_header.header == backup_header

    def test_header_change_list_with_non_anystr(self, comma_file_with_header, mocker):

        assert comma_file_with_header.header is not None
        backup_header = comma_file_with_header.header[:]
        original_header_length = len(backup_header)

        non_anystr_obj = mocker.Mock()
        assert not comma.helpers.is_anystr(non_anystr_obj)

        # list of non-AnyStr objects
        invalid_header = [non_anystr_obj] * original_header_length

        with pytest.raises(comma.exceptions.CommaInvalidHeaderException):
            comma_file_with_header.header = invalid_header

        assert comma_file_with_header.header == backup_header

    def test_header_change_shorter_longer(self, comma_file_with_header, mocker):

        assert comma_file_with_header.header is not None
        backup_header = comma_file_with_header.header[:]
        original_header_length = len(backup_header)

        # create bogus headers
        shorter_header = [self.SOME_OTHER_STRING] * (original_header_length-1)
        longer_header = [self.SOME_OTHER_STRING] * (original_header_length+1)

        # patch warnings
        warnings_patch = mocker.patch("warnings.warn")

        comma_file_with_header.header = shorter_header
        assert comma_file_with_header.header == shorter_header

        comma_file_with_header.header = longer_header
        assert comma_file_with_header.header == longer_header

        warnings_patch.assert_called()

    def test_header_change_none(self, comma_file_with_header):
        assert comma_file_with_header.header is not None
        comma_file_with_header.header = None
        assert comma_file_with_header.header is None
