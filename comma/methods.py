
import csv
import io
import typing

import comma.classes.file
import comma.classes.row
import comma.classes.table
import comma.helpers
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "load",
    "dump",
]


def load(
    source: comma.typing.SourceType,
    encoding: str = None,
    delimiters: typing.Optional[typing.Iterable[str]] = None,
):
    """

    """

    # Use the helper method to open the data, parse it and return
    # a CommaInfo typed dictionary.

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
def dump(
    records: typing.Union[comma.classes.table.CommaTable, typing.Iterable[typing.Iterable[typing.Any]]],
    filename: typing.Optional[str] = None,
    fp: typing.Optional[typing.IO] = None,
    header: typing.Optional[typing.Iterable[typing.Any]] = None,
) -> str:
    """

    """

    output = fp
    close_at_end = False
    if output is None:
        close_at_end = True
        if filename is None:
            output = io.StringIO()
        else:
            output = open(filename, "w")

    parent = None
    has_header = header is not None
    dialect = comma.helpers.DefaultDialect()

    klass_cf = comma.classes.file.CommaFile
    if isinstance(records, comma.classes.table.CommaTable):
        parent = records._parent
        has_header = records.has_header

    elif hasattr(records, "_parent") and isinstance(records._parent, klass_cf):
        parent = records._parent

    elif len(records) > 0 and hasattr(records[0], "_parent") and isinstance(records[0]._parent, klass_cf):
        parent = records[0]._parent

    if parent is not None:
        # only overwrite if not user specified
        if header is None:
            header = parent.header
        has_header = header is not None
        dialect = parent._params["dialect"]

    if has_header:
        writer = csv.DictWriter(
            output,
            fieldnames=header,
            dialect=dialect,
        )
        writer.writeheader()
    else:
        writer = csv.writer(
            output,
            dialect=dialect,
        )

    for record in records:
        writer.writerow(record)

    ret = output.getvalue()
    if close_at_end:
        output.close()

    return ret

