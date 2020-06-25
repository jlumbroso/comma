
import csv
import io
import os
import typing
import urllib
import urllib.parse
import zipfile

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

import comma.extras
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "MAX_SAMPLE_CHUNKSIZE",
    "URI_SCHEME_LOCAL",
    "URI_SCHEMES_ACCEPTED",
    "LINE_TERMINATORS",
    "LINE_TERMINATOR_DEFAULT",

    "DefaultDialect",

    "is_anystr",
    "is_local",
    "is_url",
    "detect_line_terminator",
    "open_stream",
    "open_csv",

    "validate_header",

    "multislice_sequence",
    "multislice_range",
    "multislice_index",

    "zip_html_tag",
]


MAX_SAMPLE_CHUNKSIZE = 10000

URI_SCHEME_LOCAL = "file"

URI_SCHEMES_ACCEPTED = ["http", "https"]

LINE_TERMINATORS = ["\r\n", "\r", "\n"]

LINE_TERMINATOR_DEFAULT = "\n"


class DefaultDialect(csv.Dialect):
    """
    The default dialect for output, when no dialect is provided.
    """

    @classmethod
    def override(cls, **kwargs) -> csv.Dialect:
        """
        Creates a `csv.Dialect` object that only overrides certain
        settings from the default dialect.
        """
        obj = cls()

        for field, value in kwargs.items():
            if field not in obj.__dict__:
                raise AttributeError(
                    "Class `{}` does not have a field `{}` to override".format(
                        cls, field))
            obj.__dict__[field] = value

        return obj

    def __init__(self):
        """
        Creates a `csv.Dialect` with the package's default settings.
        """
        self.delimiter = ","
        self.doublequote = True
        self.escapechar = "\\"
        self.lineterminator = LINE_TERMINATOR_DEFAULT
        self.quotechar = '"'
        self.quoting = csv.QUOTE_MINIMAL
        self.skipinitialspace = True
        self.strict = True


def is_anystr(obj: typing.Union[typing.Any, typing.AnyStr]) -> bool:
    """
    Returns `True` if the `obj` object is of type `typing.AnyStr`.
    """
    return (
            obj is not None and
            (isinstance(obj, str) or
             isinstance(obj, bytes)))


def is_local(location: typing.AnyStr) -> typing.Optional[str]:
    """
    Detects whether a string location is a local file path.
    """
    
    # Eliminate obvious non-paths
    if location is None or location == "":
        return
    
    # Try to parse the location using urlparse (to handle file://)
    parsed_location = None
    
    try:        
        parsed_location = urllib.parse.urlparse(location)
        
        # parsed_location = ParseResult(
        #   scheme=..., netloc=..., path=...,
        #   params=..., query=..., fragment=...)

    except TypeError:
        parsed_location = None
    except AttributeError:
        parsed_location = None

    # May not be a string; regular paths should be parsed without
    # trouble
    if parsed_location is None:
        return
        
    path = None
    
    if parsed_location.scheme in [URI_SCHEME_LOCAL, ""]:
        
        parsed_path = parsed_location.path
        
        if parsed_location.netloc != "":
            parsed_path = parsed_location.netloc + parsed_path
        
        if os.path.exists(parsed_path):
            path = parsed_path
        
        if os.path.exists(os.path.expanduser(parsed_path)):
            path = os.path.expanduser(parsed_path)
    
    if os.path.exists(location):
        path = location
    
    elif os.path.exists(os.path.expanduser(location)):
        path = os.path.expanduser(location)
    
    if path is not None:
        path = os.path.abspath(path)
        return path
    
    return


def is_url(location: str, no_request: bool = False) -> bool:
    """
    Detects whether a string location is a URL; may make a test HEAD request
    if the location is likely to be an actual URL (this behavior can be
    deactivated by setting `no_request` to `True`).
    """
    
    # Eliminate obvious non-URL
    if location is None or location == "":
        return False
    
    # Try to parse the URL using urlparse
    parsed_location = None
    
    try:        
        parsed_location = urllib.parse.urlparse(location)
        
        # parsed_location = ParseResult(
        #   scheme=..., netloc=..., path=...,
        #   params=..., query=..., fragment=...)

    except AttributeError:
        # May not be a string
        parsed_location = None
    
    except Exception as exc:
        # Unexpected error
        parsed_location = None
    
    if parsed_location is None:
        return False
    
    # Check parsed location
    if parsed_location.scheme == "" or parsed_location.netloc == "":
        return False
    
    # This is an actual file
    if parsed_location.scheme == URI_SCHEME_LOCAL:
        return False
    
    # If we cannot make an actual HEAD request, then this is 
    if no_request or requests is None:
        return parsed_location.scheme in URI_SCHEMES_ACCEPTED
    
    response = None
    
    # Try to make a HEAD request on the location to see if it is successful
    try:
        response = requests.head(location, allow_redirects=True, timeout=10)
    
    except requests.exceptions.InvalidSchema:
        # Not a supported scheme
        return False
    
    except requests.exceptions.ConnectionError:
        # Not able to connect
        return False
    
    if response is None:
        return False
    
    return response.ok


def detect_line_terminator(
        sample: typing.Optional[typing.AnyStr],
        default: typing.Optional[typing.AnyStr] = None
) -> str:
    """
    Detects the most likely line terminator (from `\r`, `\n`, `\r\n`), given
    a sample string, by counting the occurrences of each pattern and finding
    the longest and most frequent.
    """

    # update default
    if default is None:
        default = LINE_TERMINATOR_DEFAULT

    if sample is None or not hasattr(sample, "count"):
        return default

    # check to see if can obtain valid counts for all line terminators
    for lt in LINE_TERMINATORS:
        try:
            val = sample.count(lt)
            if type(val) is not int:
                return default
        except TypeError:
            return default

    # the sorting of options is made taking into account both
    # the number of occurrences of a pattern, and the length of
    # the pattern (this is so when "\r\n" occurs, it also boosts
    # the count of "\r" and "\n", so we must also look at the
    # LONGEST pattern with the best number of occurrences)

    ranked_options = sorted(
        zip(
            map(sample.count, LINE_TERMINATORS),  # counts
            map(len, LINE_TERMINATORS),           # length
            LINE_TERMINATORS),                    # line terminators
        reverse=True)

    best_option = ranked_options[0]

    # if the best option has been counted 0 times, means no line terminators
    # were found
    if best_option[0] == 0:
        return default

    # otherwise return the value of the best option
    return best_option[2]


def open_stream(
    source: comma.typing.SourceType,
    encoding: str = None,
    no_request: bool = False,
) -> typing.Optional[typing.TextIO]:
    """
    Returns a seekable stream for text data that is properly decoded
    and ready to be read: The `source` can be actual data, a local file
    path, or a URL; it is possible to provide a stream that is compressed
    using ZIP. (This method will store all the data in memory.)
    """
    
    if source is None:
        return

    # local variable to keep track of the (most accurate for the user)
    # caption of the source
    internal_name = None
    
    # is this a STRING?
    if type(source) is str:
        source = typing.cast(typing.AnyStr, source)
        
        # multiline?
        if "\n" in source or "\r" in source:
            newline = comma.helpers.detect_line_terminator(
                sample=source,
                default="\n")

            # change to a standard newline
            source = source.replace(newline, "\n")

            return io.StringIO(initial_value=source, newline="\n")
        
        internal_name = source
        
        # is this a FILE?
        local_path = is_local(location=source)
        if local_path is not None:
            source = open(local_path, mode="rb")
        
        # is this a URL?
        elif not no_request and is_url(location=source):
            
            response = requests.get(url=source, allow_redirects=True)
            
            if not response.ok:
                return None
            
            if encoding is None:
                encoding = response.encoding
            
            if encoding is not None:
                source = io.StringIO(response.text)
            else:
                source = io.BytesIO(response.content)
        
        else:
            return None

    # is this BYTES?
    if type(source) is bytes:
        source = typing.cast(bytes, source)
        source = io.BytesIO(source)

    # is this a STREAM?
    if hasattr(source, "seekable"):
        
        # is it not seekable? if so, make it seekable
        if not source.seekable():
            
            # if not, read in all the data
            data = source.read()
            
            if type(data) is str:
                source = io.StringIO(data)
            
            elif type(data) is bytes:
                source = io.BytesIO(data)

            else:
                raise ValueError(
                    "provided source is neither StringIO nor BytesIO")
        
        # is it compressed? if so, unzip it
        if zipfile.is_zipfile(source):
            zipsource = zipfile.ZipFile(source, mode="r")
            
            names = zipsource.namelist()
            
            count_total = 0
            count_csv = 0
            
            csv_filename = None
            
            for name in names:
                count_total += 1
                if os.path.splitext(name)[1].lower() == ".csv":
                    count_csv += 1
                    csv_filename = name
            
            if count_total == 1:
                # if only one file, we don't care if it is a CSV (we assume)
                data = zipsource.read(name=names[0])
                source = io.BytesIO(data)
            
            elif count_total > 1 and count_csv == 1:
                # if exactly one CSV, we know what to do
                data = zipsource.read(name=csv_filename)
                source = io.BytesIO(data)
            
            elif count_total == 0:
                raise ValueError(
                    "it seems the provided source is ZIP compressed; but "
                    "there are unknown issues unzipping it (or the archive "
                    "is empty)")
                
            else:
                # other situations are unclear
                raise ValueError(
                    "provided ZIP source is ambiguous, "
                    "contains multiple files: {}".format(names))
    
    # if at this point, has not been converted to stream, error
    if not hasattr(source, "seekable"):
        return None
    
    # look at a sample and analyze
    source.seek(0)
    sample = source.read(MAX_SAMPLE_CHUNKSIZE)
    source.seek(0)   # fixed this bug with tests! :-)
    
    # detect encoding if bytestring
    if type(sample) is bytes:
        if encoding is None:
            encoding = comma.extras.detect_encoding(sample)
        source = io.TextIOWrapper(source, encoding=encoding)
    
    # try to add useful metadata
    if internal_name is not None:
        try:
            source.buffer.name = internal_name
        except AttributeError:
            pass
    
    return source


def open_csv(
    source: comma.typing.SourceType,
    encoding: str = None,
    delimiters: typing.Optional[typing.Iterable[str]] = None,
    no_request: bool = False,
) -> comma.typing.CommaInfoType:
    """
    Returns a `CommaInfoType` typed dictionary containing the data and
    metadata related to a CSV file. The `source` can be actual data,
    a local file path, or a URL; it is possible to provide a stream
    that is compressed using ZIP.

    The `source` is opened using the `comma.helpers.open_stream()`
    helper method. The metadata data is detected using internal
    helpers and either the `csv` or `clevercsv` dialect sniffers.
    """

    stream = comma.helpers.open_stream(
        source=source,
        encoding=encoding,
        no_request=no_request,
    )
    if stream is None:
        return

    # close at end if a stream was opened by this method (but not if
    # a stream was provided to this method)
    try:
        close_at_end = (
                not hasattr(source, "seekable") or
                source.buffer.name != stream.buffer.name)
    except AttributeError:
        close_at_end = True

    # streams returned by open_stream should be seekable
    # FIXME: handle non-seekable streams
    assert(hasattr(stream, "seekable"))

    # get a sample and analyze
    stream.seek(0)
    csv_sample = stream.read(comma.helpers.MAX_SAMPLE_CHUNKSIZE)
    stream.seek(0)

    csv_params = comma.extras.detect_csv_type(
        sample=csv_sample,
        delimiters=delimiters)

    reader = csv.reader(stream, dialect=csv_params["dialect"])
    csv_rows = [row for row in reader]

    # close if necessary
    if close_at_end:
        stream.close()

    data = {
        "rows": csv_rows,
        "params": csv_params,
        "sample": csv_sample,
        "header": None,
    }

    # isolate the headers if they exist
    if data["params"].get("has_header", False):

        if len(csv_rows) == 0:
            data["params"]["has_header"] = False
            data["column_count"] = 0

        else:
            data["header"] = csv_rows[0]
            data["rows"] = csv_rows[1:]
            data["column_count"] = len(data["header"])

    if len(csv_rows) > 0 and "column_count" not in data:
        data["column_count"] = max(map(len, csv_rows))

    # store the source location if it was a string
    if comma.helpers.is_anystr(source):
        data["source"] = source

    return data


def validate_header(value: typing.Any) -> typing.List[str]:
    """
    Checks that a value is an iterable of string-like values. And converts
    to a list of strings. This is to verify user-specified header values.
    """
    # verify the value is a list (or can be converted to one if,
    # say, an iterator)

    import comma.exceptions

    if value is None:
        raise comma.exceptions.CommaInvalidHeaderException(
            "the header that is being validated is `None`; this is not a "
            "valid header, though perhaps a signal to unset a variable"
        )

    try:
        header_as_list = list(value)
    except TypeError as e:
        raise comma.exceptions.CommaInvalidHeaderException(
            "type error arose as validating specified header") from e

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

    header_as_list = list(map(str, header_as_list))

    return header_as_list

def multislice_sequence(
    sequence: typing.Sequence[typing.Any],
    slice_list: typing.List[slice] = None,
) -> typing.Sequence[typing.Any]:
    """
    Returns the sub-sequence obtained from sequentially slicing the
    sequence `sequence` according to the series of slices in `slice_list`.
    """
    new_sequence = sequence

    if slice_list is not None:
        for sl in slice_list:
            new_sequence = new_sequence.__getitem__(sl)

    return new_sequence


def multislice_range(size: int, slice_list: typing.List[slice] = None) -> range:
    """
    Returns the range of indexes that are preserved by a succession of
    slicing operations on the range [0, size). This makes it easier to
    recover the original index.
    """
    # noinspection PyArgumentList
    return typing.cast(
        typ=range,
        val=comma.helpers.multislice_sequence(range(size), slice_list=slice_list))


def multislice_index(index: int, size: int, slice_list: typing.List[slice] = None) -> int:
    """
    Returns the original index in the original sequence from the index
    in the sequence after applying multiple slicing operations. This
    makes it easier to recover the original index.
    """
    return multislice_range(size=size, slice_list=slice_list)[index]


def zip_html_tag(
    data: typing.Iterable,
    in_pattern: str = "<td style='text-align: left;'>{}</td>",
    out_pattern: str = "<tr>{}</tr>",
    indent: int = 0
) -> str:
    """
    Returns the HTML code of a template applied to a Python list; to
    be used to build the rows of tables, or bullet lists in
    `_repr_html_()` outputs.
    """
    if type(indent) is not int:
        indent = 0

    linebreak = "\n" + (indent * " ")

    inner_html = linebreak.join(map(in_pattern.format, data))
    outer_html = out_pattern.format(inner_html)

    return outer_html


# NOTE: Have not decided whether to use this or not yet
#
# def comment_stripper(stream: typing.TextIO, comment_line_chars: str = '#;'):
#     for line in stream.readlines():
#
#         stripped_line = line.strip()
#         if not stripped_line:
#             # empty lines
#             continue
#
#         # look at first character
#         if stripped_line[:1] in comment_line_chars:
#             # lines that are commented out
#             continue
#
#         # yield line
#         yield line
