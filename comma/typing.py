
import csv
import typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "SourceType",

    "DialectType",
    "SimpleDialectType",

    "CommaInfo",
    "CommaInfoParams"
]


# Our type hint for a data source:
#  - a location (URL or file path), or string data
#  - a stream (text or binary)
#  - a string of bytes

SourceType = typing.Union[typing.AnyStr, typing.IO, bytes]


# The original CSV Dialect type from Python library

DialectType = csv.Dialect


# The simplified CSV dialect description from the excellent
# https://github.com/alan-turing-institute/CleverCSV/blob/master/clevercsv/dialect.py

SimpleDialectType = typing.Any
try:
    import clevercsv
    import clevercsv.dialect
    SimpleDialectType = clevercsv.dialect.SimpleDialect
except ImportError:  # pragma: no cover
    clevercsv = None


# Type definitions for helper dictionaries

CommaInfoParams = typing.TypedDict(
    "CommaInfoParams", {
        #
        "dialect":         DialectType,

        #
        "simple_dialect":  SimpleDialectType,

        "has_header":      bool,

        "line_terminator": str,
    })

CommaInfo = typing.TypedDict(
    "CommaInfo", {
        # the parsed CSV rows
        "rows":   typing.List[typing.List[str]],

        # a raw sample of the original file
        "sample": str,

        # an identifier for the source (if not raw buffer)
        "source_name": str,

        # CSV parameters
        "header": typing.Optional[typing.List[str]],
        "params": CommaInfoParams,
    })
