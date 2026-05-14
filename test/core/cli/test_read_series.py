#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared subtitle-series CLI input helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.common.exceptions import NotAFileError
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import read_series


@pytest.mark.parametrize(
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

    with patch("scinoephile.core.cli.Series.load", side_effect=exception):
        with pytest.raises(SystemExit) as excinfo:
            with redirect_stderr(stderr):
                read_series(parser, infile_path)

    assert excinfo.value.code == 2
    assert str(exception) in stderr.getvalue()


@pytest.mark.parametrize(
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

    with patch("scinoephile.core.cli.stdin", StringIO("not srt")):
        with patch("scinoephile.core.cli.Series.from_string", side_effect=exception):
            with pytest.raises(SystemExit) as excinfo:
                with redirect_stderr(stderr):
                    read_series(parser, "-", allow_stdin=True)

    assert excinfo.value.code == 2
    assert str(exception) in stderr.getvalue()
