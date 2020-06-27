
import csv
import io
import typing

import comma.classes.file
import comma.classes.row
import comma.classes.table
import comma.exceptions
import comma.helpers
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "TableType",

    "load",

    "dumps",
    "dump",
]


# Our type hint for a tabular type
# NOTE: Because of the reference to CommaTable, must be here rather
# than in comma.typing because otherwise will cause circular import

TableType = typing.Union[
    # either one of our CommaTables
    comma.classes.table.CommaTable,

    # or a list of our CommaRows
    typing.Iterable[comma.classes.row.CommaRow],

    # or just really anything that resembles a matrix
    # (hoping that the typing.Any can be serialized to
    # a string)
    typing.Iterable[typing.Iterable[typing.Any]]]


def load(
    source: comma.typing.SourceType,
    encoding: str = None,
    delimiters: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Optional[comma.classes.table.CommaTable]:
    """
    Deserializes a table from a CSV/DSV source, and returns a
    Python list/dict-like object, which is an instance of the
    `comma.classes.table.CommaTable` type.

    The source can be: A string containing the data directly; a local
    path to a file containing the data; a URL to the data source. The
    data can be in any encoding (which will be detected using the BOM
    if present, or the `chardet` module otherwise), and it can even be
    compressed by ZIP.

    Although everything is autodetected thanks to `clevercsv` and
    `chardet`, you can optionally use the `encoding` and `delimiters`
    parameters to override (or circumvent) automatic detection.
    """

    # Use the helper method to open the data, parse it and return
    # a CommaInfoType typed dictionary.

    csv_comma_info = comma.helpers.open_csv(
        source=source,
        encoding=encoding,
        delimiters=delimiters,
    )

    if csv_comma_info is None:
        return

    csv_rows_raw = csv_comma_info["rows"]
    csv_header = csv_comma_info["header"]

    # create CommaFile object
    parent_comma_file = comma.classes.file.CommaFile(
        header=csv_header,
        params=csv_comma_info["params"],
    )

    def _make_comma_row(csv_row_data):
        return comma.classes.row.CommaRow(
            csv_row_data,
            parent=parent_comma_file,
        )

    csv_comma_rows = list(map(_make_comma_row, csv_rows_raw))

    csv_comma_table = comma.classes.table.CommaTable(
        csv_comma_rows,
        parent=parent_comma_file
    )

    return csv_comma_table


# noinspection PyProtectedMember
def dumps(
    records: TableType,
    header: comma.typing.OptionalHeaderType = None,
    dialect: typing.Optional[csv.Dialect] = None,
) -> str:
    """
    Serializes a table, as specified by `records`, into CSV format and returns a
    string.

    Optionally allows for a user-specified `header`, either to provide a header when
    the `records` do not have one; or to override existing headers.

    Optionally allows for a user-specified `dialect` (or type `csv.Dialect`), which
    will default to `comma.helpers.DefaultDialect()`.
    """

    # initialization of the variables

    parent = None
    existing_header = None

    # ==============================================================================
    # Try to get linked parent to retrieve metadata

    # shortcuts
    klass_cf = comma.classes.file.CommaFile
    klass_ct = comma.classes.table.CommaTable

    # CASE 1: `records` is a `CommaTable`
    if isinstance(records, klass_ct) and isinstance(records._parent, klass_cf):
        parent = records._parent

    # CASE 2: `records` is something (perhaps a derived class, or a mock class)
    # with a `_parent` attribute, which is a `CommaFile`
    elif hasattr(records, "_parent") and isinstance(records._parent, klass_cf):
        parent = records._parent

    # CASE 3: `records` is some iterable structure
    elif isinstance(records, typing.Iterable):
        records = list(records)
        if (len(records) > 0
                and hasattr(records[0], "_parent")
                and isinstance(records[0]._parent, klass_cf)):
            parent = records[0]._parent

    else:
        # not a `CommaTable`, and not iterable
        raise comma.exceptions.CommaException(
            "the `records` provided to the `dumps()` method do not appear "
            "to be a valid `TableType` object"
        )

    # ==============================================================================

    # fill in missing settings with information from linked parent or defaults

    try:
        existing_header = list(records[0].keys())
    except AttributeError:
        pass
    except TypeError:
        pass
    except IndexError:
        # records may be empty
        pass

    if parent is not None:
        existing_header = parent.header
        if dialect is None:
            dialect = parent._params["dialect"]

    if header is None:
        header = existing_header
    else:
        header = list(header)

    if dialect is None:
        dialect = comma.helpers.DefaultDialect()

    # ==============================================================================

    # in this method we output to a StringIO of which we will recuperate the
    # output string, using the `StringIO.getvalue()` method.

    output_stream = io.StringIO()

    # now actually write to the stream

    has_header = (header is not None or existing_header is not None)

    if has_header:
        writer = csv.DictWriter(
            output_stream,
            fieldnames=header or existing_header,
            dialect=dialect,
        )
        writer.writeheader()
    else:
        writer = csv.writer(
            output_stream,
            dialect=dialect,
        )

    for record in records:

        # header: possibly user-specified header
        # existing_header: header from linked parent

        # CASE 1: If there were no headers besides the user-specified one,
        # convert the list records into dict records.

        if existing_header is None and header is not None:
            new_record = dict()
            for i in range(len(record)):
                new_record[header[i]] = record[i]
            record = new_record

        # CASE 2: If the user-specified headers are different than the ones the
        # linked parent knows about, then we need to rename the fields before
        # writing this row

        elif existing_header != header:
            new_record = dict()
            for field_orig, field_renamed in zip(existing_header, header):
                new_record[field_renamed] = record[field_orig]
            record = new_record

        writer.writerow(record)

    ret = output_stream.getvalue()

    return ret


def dump(
    records: TableType,
    filename: typing.Optional[str] = None,
    fp: typing.Optional[typing.IO] = None,
    header: comma.typing.OptionalHeaderType = None,
    dialect: typing.Optional[csv.Dialect] = None,
    no_echo: bool = False,
) -> typing.Optional[str]:
    """
    Serializes a table, as specified by `records`, into CSV format and outputs
    the result either in a file (if `filename` is provided), writes it to a
    stream (if `fp` is provided) or returns it as a string otherwise.

    Optionally allows for a user-specified `header`, either to provide a header when
    the `records` do not have one; or to override existing headers.

    Optionally allows for a user-specified `dialect` (or type `csv.Dialect`), which
    will default to `comma.helpers.DefaultDialect()`.

    The option `no_echo` prevents the method from returning the serialized table
    when it has been output to a file or a stream.
    """

    # use our `dumps()` method to compute the actual output string

    csv_str = dumps(
        records=records,
        header=header,
        dialect=dialect,
    )

    # figure out how to output the result

    output_stream = fp
    close_at_end = False
    if output_stream is None:
        close_at_end = True
        if filename is None:
            output_stream = None  # io.StringIO()
        else:
            output_stream = open(filename, "w")

    # if we've got a stream to write to, write to it

    if output_stream is not None:

        output_stream.write(csv_str)

        if close_at_end:
            output_stream.close()

        if no_echo:
            return

    # unless `no_echo` is `True` and we are writing to a stream,
    # return the value as a string

    return csv_str

