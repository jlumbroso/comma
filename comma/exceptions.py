
__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CommaException",
    "CommaOrphanException",
    "CommaOrphanRowException",
    "CommaOrphanTableException",
    "CommaNoHeaderException",
    "CommaInvalidHeaderException",
    "CommaKeyError",
    "CommaBatchException",
]


class CommaException(Exception):
    """
    The base exception for the `comma` package.
    """
    pass


class CommaOrphanException(CommaException):
    """
    An internal reference has been broken.
    """
    pass


class CommaOrphanRowException(CommaOrphanException):
    """
    A row required access to information from its parent CSV file but was
    unable to.
    """
    pass


class CommaOrphanTableException(CommaOrphanException):
    """
    A table required access to information from its parent CSV file but was
    unable to.
    """
    pass


class CommaNoHeaderException(CommaException, KeyError):
    """
    A header was expected (or necessary to an operation) but was not found.
    """
    pass


class CommaInvalidHeaderException(CommaException, TypeError):
    """
    The value for a header is not of the right type: It appears not to be
    a list/iterable of strings (column names).
    """
    pass


class CommaKeyError(CommaException, KeyError):
    """
    The requested key is not part of the header of this file.
    """
    pass

class CommaPrimaryKeyMissing(CommaKeyError):
    """
    A row has been found that does not contain the specified primary key.
    """
    pass

class CommaBatchException(CommaException):
    """
    A batch update was not possible, because invalid.
    """
    pass
