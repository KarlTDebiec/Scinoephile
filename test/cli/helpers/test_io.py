#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared CLI input and output helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.helpers.io import read_image_series, read_series, write_series
from scinoephile.common.exceptions import NotAFileError
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import parametrize


@parametrize(
    "exception",
    [
        FileNotFoundError("missing image subtitles"),
        NotADirectoryError("invalid image subtitle path"),
        ScinoephileError("invalid image subtitle series"),
        ValueError("invalid image subtitle value"),
    ],
)
def test_read_image_series_maps_file_errors_to_parser_error(
    exception: Exception, tmp_path: Path
):
    """Test image subtitle read failures are reported as parser errors.

    Arguments:
        exception: exception raised while loading the image subtitle series
        tmp_path: temporary test directory
    """
    parser = ArgumentParser(prog="test")
    infile_path = tmp_path / "input.sup"
    infile_path.write_text("", encoding="utf-8")
    stderr = StringIO()

    with patch("scinoephile.cli.helpers.io.ImageSeries.load", side_effect=exception):
        with raises(SystemExit) as excinfo:
            with redirect_stderr(stderr):
                read_image_series(parser, infile_path)

    assert excinfo.value.code == 2
    assert str(exception) in stderr.getvalue()


@parametrize(
    "exception",
    [
        FileNotFoundError("missing subtitles"),
        NotADirectoryError("invalid subtitle path"),
        NotAFileError("not a subtitle file"),
        ScinoephileError("invalid subtitle series"),
        ValueError("invalid subtitle value"),
    ],
)
def test_read_series_maps_file_errors_to_parser_error(
    exception: Exception, tmp_path: Path
):
    """Test file-read failures are reported as parser errors.

    Arguments:
        exception: exception raised while loading the subtitle series
        tmp_path: temporary test directory
    """
    parser = ArgumentParser(prog="test")
    infile_path = tmp_path / "input.srt"
    infile_path.write_text("", encoding="utf-8")
    stderr = StringIO()

    with patch("scinoephile.cli.helpers.io.Series.load", side_effect=exception):
        with raises(SystemExit) as excinfo:
            with redirect_stderr(stderr):
                read_series(parser, infile_path)

    assert excinfo.value.code == 2
    assert str(exception) in stderr.getvalue()


@parametrize(
    "exception",
    [
        ScinoephileError("invalid stdin subtitle series"),
        ValueError("invalid stdin subtitle value"),
    ],
)
def test_read_series_maps_stdin_errors_to_parser_error(exception: Exception):
    """Test stdin-read failures are reported as parser errors.

    Arguments:
        exception: exception raised while loading the subtitle series
    """
    parser = ArgumentParser(prog="test")
    stderr = StringIO()

    with patch("scinoephile.cli.helpers.io.stdin", StringIO("not srt")):
        with patch(
            "scinoephile.cli.helpers.io.Series.from_string", side_effect=exception
        ):
            with raises(SystemExit) as excinfo:
                with redirect_stderr(stderr):
                    read_series(parser, "-", allow_stdin=True)

    assert excinfo.value.code == 2
    assert str(exception) in stderr.getvalue()


def test_write_series_defaults_to_srt_format(tmp_path: Path):
    """Test subtitle output helper writes SRT by default.

    Arguments:
        tmp_path: temporary test directory
    """
    parser = ArgumentParser(prog="test")
    series = Series(events=[Subtitle(start=1000, end=2000, text="recognized")])
    outfile_path = tmp_path / "recognized.ass"

    write_series(parser, series, outfile_path, overwrite=True)

    output_text = outfile_path.read_text(encoding="utf-8")
    assert output_text.startswith("1\n00:00:01,000 --> 00:00:02,000\n")
    assert "[Script Info]" not in output_text
