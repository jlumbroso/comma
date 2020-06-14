
import typing

import comma.classes.file
import comma.classes.row
import comma.classes.table
import comma.helpers
import comma.typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "load"
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


