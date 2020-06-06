import codecs
import collections
import csv
import io
import os
import pathlib
import urllib, urllib.parse
import zipfile

import comma.helpers


__author__ = ("Jérémie Lumbroso <lumbroso@cs.princeton.edu>")

__all__ = [
    "detect_csv_type",
    "detect_encoding",
    "is_binary_string",
]


# Better CSV dialect detection, thanks to clevercsv

detect_csv_type = None

try:
    import clevercsv
    
    def detect_csv_type(sample, delimiters=None):
        sniffer = clevercsv.Sniffer()
        truncated_sample = sample[:comma.helpers.MAX_SAMPLE_CHUNKSIZE]
        simple_dialect = sniffer.detect(sample=truncated_sample, delimiters=delimiters)
        line_terminator = comma.helpers.detect_line_terminator(truncated_sample)

        dialect = simple_dialect.to_csv_dialect()
        dialect.lineterminator = line_terminator

        return {
            "dialect": dialect,
            "simple_dialect": simple_dialect,
            "has_header": sniffer.has_header(sample=truncated_sample),
            "line_terminator": line_terminator,
        }

except ImportError:
    clevercsv = None
    
    # define a helper based on the standard CSV package
    def detect_csv_type(sample, delimiters=None):
        sniffer = csv.Sniffer()
        truncated_sample = sample[:comma.helpers.MAX_SAMPLE_CHUNKSIZE]

        line_terminator = comma.helpers.detect_line_terminator(truncated_sample)

        dialect = sniffer.sniff(sample=truncated_sample, delimiters=delimiters)
        dialect.lineterminator = line_terminator

        return {
            "dialect": dialect,
            "simple_dialect": None,
            "has_header": sniffer.has_header(sample=truncated_sample),
            "line_terminator": line_terminator,
        }


# Better detection of binary data (i.e., zipped files), thanks to binaryornot

_is_binary_string = None

try:
    # See https://github.com/audreyr/binaryornot/
    import binaryornot
    import binaryornot.helpers
    
    # Alias to helper method
    _is_binary_string = binaryornot.helpers.is_binary_string

except ImportError:
    binaryornot = None
    
    # Define our own helper method
    # Based on file(1), see https://stackoverflow.com/a/7392391/408734
    TEXT_CHARS = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})

    def _is_binary_string(bytestring):
        return bool(bytestring.translate(None, TEXT_CHARS))


def is_binary_string(bytestring, truncate=True):
    """
    Detect, using heuristics, whether a string of bytes is text or binary data.
    If available, this will use the `binaryornot` lightweight package.
    """
    
    if bytestring is None:
        return False
    
    bytestring_length = -1
    try:
        bytestring_length = len(bytestring)
        
    except TypeError:
        return False
    
    if truncate and bytestring_length > comma.helpers.MAX_SAMPLE_CHUNKSIZE:
        return _is_binary_string(bytestring[:comma.helpers.MAX_SAMPLE_CHUNKSIZE])
    
    return _is_binary_string(bytestring)


# Better encoding detection

def _detect_encoding_by_bom(sample, default=None):
    # See https://stackoverflow.com/a/24370596/408734
    sample = sample[0:4]
    for enc, boms in \
            ('utf-8-sig', (codecs.BOM_UTF8,)),\
            ('utf-16', (codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE)),\
            ('utf-32', (codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE)):
        if any(sample.startswith(bom) for bom in boms): return enc
    
    return default


detect_encoding = _detect_encoding_by_bom

try:
    import chardet
    
    def detect_encoding(sample, default="utf-8"):
        # First try a fool-proof deterministic method
        encoding = _detect_encoding_by_bom(sample)
        if encoding is not None:
            return encoding
        
        # If that doesn't work, try a heuristic
        result = chardet.detect(sample)
        if result is not None and result.get("encoding") is not None:
            return result.get("encoding")
        
        return default
    
except ImportError:
    pass


