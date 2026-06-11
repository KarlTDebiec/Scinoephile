#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for reading and writing subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stdin, stdout

from scinoephile.common.exceptions import NotAFileError
from scinoephile.common.validation import (
    val_input_file_or_dir_path,
    val_input_path,
    val_output_path,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries

__all__ = [
    "read_image_series",
    "read_series",
    "write_series",
]


def read_image_series(parser: ArgumentParser, infile: str | Path) -> ImageSeries:
    """Load an image subtitle series from a file or directory.

    Arguments:
        parser: parser used for user-facing error output
        infile: input file or directory path
    Returns:
        loaded image subtitle series
    """
    try:
        infile_path = val_input_file_or_dir_path(infile)
        return ImageSeries.load(infile_path)
    except (
        FileNotFoundError,
        NotADirectoryError,
        ScinoephileError,
        ValueError,
    ) as exc:
        parser.error(str(exc))


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
    try:
        if allow_stdin and str(infile) == "-":
            return Series.from_string(stdin.read(), format_="srt")
        infile_path = val_input_path(infile)
        return Series.load(infile_path)
    except (
        FileNotFoundError,
        NotADirectoryError,
        NotAFileError,
        ScinoephileError,
        ValueError,
    ) as exc:
        parser.error(str(exc))


def write_series(
    parser: ArgumentParser,
    series: Series,
    outfile: str | Path,
    overwrite: bool,
    *,
    format_: str = "srt",
):
    """Write a subtitle series to stdout or a file.

    Arguments:
        parser: parser used for user-facing error output
        series: subtitle series to write
        outfile: output path or "-"
        overwrite: whether existing files may be overwritten
        format_: output file format
    """
    if str(outfile) == "-":
        stdout.write(series.to_string(format_=format_))
        return

    try:
        outfile_path = val_output_path(outfile, exist_ok=True)
    except (FileExistsError, NotAFileError) as exc:
        parser.error(str(exc))

    if outfile_path.exists() and not overwrite:
        parser.error(f"{outfile_path} already exists")
    series.save(outfile_path, format_=format_)
