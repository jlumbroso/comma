
import typing
import warnings

import comma.exceptions
import comma.helpers
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaFile"
]


class CommaFile(object):
    """
    Store the metadata associated with a CSV/DSV file. This includes the
    `header` (a list of column names) if it exists; the `primary_key` (that is,
    whether one of the columns should function as an index for rows); and
    the internal parameters, such as dialect and encoding, that are detetcted
    when the table data was loaded.
    """

    # Internal instance variable containing header
    _header = None

    # Internal instance variable with params
    _params = None

    # "Primary key" through which to access the records
    _primary_key = None

    def __init__(
        self,
        header: comma.typing.OptionalHeaderType = None,
        params: typing.Optional[comma.typing.CommaInfoParamsType] = None,
        primary_key: typing.Optional[str] = None
    ):
        if header is not None:
            self._header = list(header)
        self._params = params
        self._primary_key = primary_key

    @property
    def header(self) -> comma.typing.OptionalHeaderType:
        """
        The header of the associated `CommaFile`, if such a header has been
        defined and `None` otherwise.
        """
        return self._header

    @header.setter
    def header(self, value: comma.typing.OptionalHeaderType):
        """
        Changes the header associated with this `CommaFile`; this operation
        only affects the metadata, but does not modify any of the underlying
        rows.
        """

        # equivalent to a delete

        if value is None:
            self._header = None
            return

        # verify the value is a list (or can be converted to one if,
        # say, an iterator)

        try:
            header_as_list = list(value)
        except TypeError as e:
            raise comma.exceptions.CommaInvalidHeaderException(
                "type error arose as changing header") from e

        # check individual fields

        for subval in header_as_list:
            if subval is None:
                raise comma.exceptions.CommaInvalidHeaderException(
                    ("attempting to set a header with invalid `None` field name"
                     "\nfull header: {header}").format(header=header_as_list))

            if not comma.helpers.is_anystr(subval):
                raise comma.exceptions.CommaInvalidHeaderException(
                    ("attempting to set a header with invalid field name `{field}`"
                     "\nfull header: {header}").format(
                        field=subval,
                        header=header_as_list))

        # if we are replacing an existing header, check length

        if self._header is not None:
            old_length = len(self._header)
            new_length = len(header_as_list)

            if old_length != new_length:
                warnings.warn(
                    "changing length of header; was {old}, now is {new}".format(
                        old=old_length,
                        new=new_length))

        self._header = header_as_list

    @header.deleter
    def header(self):
        """
        Deletes the header associated with this `CommaFile`; this operation
        only affects the metadata, but does not modify any of the underlying
        rows.
        """
        self._header = None

    @property
    def primary_key(self) -> str:
        """

        """
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str):

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

