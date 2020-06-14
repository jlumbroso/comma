
import typing

import comma.exceptions
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaFile"
]


class CommaFile(object):
    """
    """

    # Internal instance variable containing header
    _header = None

    # Internal instance variable with params
    _params = None

    # "Primary key" through which to access the records
    _primary_key = None

    def __init__(
            self,
            header=None,
            params: comma.typing.CommaInfoParams = None,
            primary_key: typing.Optional[str] = None
    ):
        self._header = header
        self._params = params
        self._primary_key = primary_key

    @property
    def header(self):
        """

        """
        return self._header

    @header.setter
    def header(self, value):
        raise NotImplementedError("not yet implemented")

    @property
    def primary_key(self):
        """

        """
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value):

        # shortcuts to un-setting the primary key
        if value is None or value == "" or value == False:
            del self.primary_key
            return

        # from this point on, consider we are setting the primary key

        # first check whether there are headers
        if self.header is None:
            raise comma.exceptions.CommaNoHeaderException(
                "cannot set the primary key of a `CommaFile` "
                "that does not have a header"
            )

        # next check if proposed header belongs to headers
        if value not in self.header:
            # Try to get a string representation of headers for diagnostic
            # purposes for user; yes, the exception is too broad because
            # we don't really care why the headers couldn't be converted
            # to string

            # Thanks @pylover!
            # See: https://gist.github.com/pylover/7870c235867cf22817ac5b096defb768

            # noinspection PyBroadException
            try:
                header_string = self.header.__repr__()
            except Exception:  # pylint: disable=too-general-exception
                header_string = ""

            raise comma.exceptions.CommaKeyError(
                "the requested primary key (" +
                value +
                ") is not one of the headers: " +
                header_string
            )

        # seems we have validated the primary key and so setting it
        self._primary_key = value

    @primary_key.deleter
    def primary_key(self):
        self._primary_key = None

