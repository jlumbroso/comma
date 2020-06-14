# Comma: A Python CSV Library for Humans

This library tries to make manipulating CSV files a great experience.

# Why?




# Alternatives

Python is fortunate to have a lot of very good libraries to read/write
CSV and tabular files in general.

- [`clevercsv`](https://github.com/alan-turing-institute/CleverCSV): An
  excellent library by @GjjvdBurg, builds on statistical and empirical
  to provide powerful and reliable CSV dialect detection. However, it
  strives to be a drop-in replacement for the original Python `csv`
  module, and as such does not improve on the complex syntax.
  
- [`pandas`](https://github.com/pandas-dev/pandas): An advanced data
  science package for Python, this certainly provides a powerful CSV
  (and more generally, table file) reader and parser. The API of the
  table object is very powerful, but you need to take the time to learn
  how to use it. This library is perhaps not ideal for file manipulations.

- [`pyexcel`](https://github.com/pyexcel/pyexcel): This library provides
  access to Excel and other tabular formats, including CSV, and various
  data sources (stream, database, file, ...). It emphasizes one common
  format-agnostic API, that instead has the user choose the data format
  (list, matrix, dictionary, ...).

- [`tabulator`](https://github.com/frictionlessdata/tabulator-py): This
  library provides a single interface to manipulate extremely large
  tabular data---and useful for files so large that they need to be
  streamed line-by-line; the library supports a broad array of formats
  including reading data directly from Google Spreadsheets. However
  this power means that reading a CSV file requires several operations.

# Acknowledgements


# License

This project is licensed under the LGPLv3 license, with the understanding
that importing a Python modular is similar in spirit to dynamically linking
against it.

- You can use the library `comma` in any project, for any purpose, as long
  as you provide some acknowledgement to this original project for use of
  the library.

- If you make improvements to `comma`, you are required to make those
  changes publicly available.

