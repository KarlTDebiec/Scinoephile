#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared CLI I/O helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stdin, stdout

from scinoephile.common.exception import NotAFileError
from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.subtitles import Series


def read_series(
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

    try:
        infile_path = val_input_path(infile)
    except (FileNotFoundError, NotAFileError) as exc:
        parser.error(str(exc))
    return Series.load(infile_path)


def write_series(parser: ArgumentParser, series: Series, outfile: str, overwrite: bool):
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

    try:
        outfile_path = val_output_path(outfile, exist_ok=True)
    except (FileExistsError, NotAFileError) as exc:
        parser.error(str(exc))

    if outfile_path.exists() and not overwrite:
        parser.error(f"{outfile_path} already exists")
    series.save(outfile_path)
