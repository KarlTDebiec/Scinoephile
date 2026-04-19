#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared subtitle CLI I/O helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stdin, stdout

from scinoephile.common.exception import NotAFileError
from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.subtitles import Series


def parser_error_from_exception(parser: ArgumentParser, exc: Exception):
    """Report an exception as an argparse usage error.

    Arguments:
        parser: parser used for user-facing error output
        exc: exception to format for parser error output
    """
    parser.error(str(exc))


def load_subtitle_series(
    parser: ArgumentParser,
    infile: str | Path,
    *,
    allow_stdin: bool = False,
) -> Series:
    """Load a subtitle series from stdin or a file.

    Arguments:
        parser: parser used for user-facing error output
        infile: input path or "-" when stdin is allowed
        allow_stdin: whether "-" should be treated as stdin
    Returns:
        loaded subtitle series
    """
    if allow_stdin and str(infile) == "-":
        return Series.from_string(stdin.read(), format_="srt")

    infile_path = validate_infile_path(parser, infile)
    return Series.load(infile_path)


def validate_infile_path(parser: ArgumentParser, infile: str | Path) -> Path:
    """Validate a subtitle infile path.

    Arguments:
        parser: parser used for user-facing error output
        infile: input path value
    Returns:
        validated input path
    """
    try:
        return val_input_path(infile)
    except (FileNotFoundError, NotAFileError) as exc:
        parser_error_from_exception(parser, exc)
    raise AssertionError("unreachable")


def validate_outfile_path(
    parser: ArgumentParser, outfile: str | Path, overwrite: bool
) -> Path:
    """Validate an output path and enforce overwrite behavior.

    Arguments:
        parser: parser used for user-facing error output
        outfile: output path value
        overwrite: whether existing files may be overwritten
    Returns:
        validated output path
    """
    try:
        outfile_path = val_output_path(outfile, exist_ok=True)
    except (FileExistsError, NotAFileError) as exc:
        parser_error_from_exception(parser, exc)

    if outfile_path.exists() and not overwrite:
        parser.error(f"{outfile_path} already exists")
    return outfile_path


def write_subtitle_series(
    parser: ArgumentParser, series: Series, outfile: str, overwrite: bool
):
    """Write a subtitle series to stdout or a file.

    Arguments:
        parser: parser used for user-facing error output
        series: subtitle series to write
        outfile: output path or "-"
        overwrite: whether existing files may be overwritten
    """
    if outfile == "-":
        stdout.write(series.to_string(format_="srt"))
        return

    outfile_path = validate_outfile_path(parser, outfile, overwrite)
    series.save(outfile_path)
