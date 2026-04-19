#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.EngFuseCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import EngCli, EngFuseCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (EngFuseCli,),
        (EngCli, EngFuseCli),
        (ScinoephileCli, EngCli, EngFuseCli),
    ],
)
def test_eng_fuse_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English fuse CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (EngFuseCli,),
        (EngCli, EngFuseCli),
        (ScinoephileCli, EngCli, EngFuseCli),
    ],
)
def test_eng_fuse_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English fuse CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_eng_fuse_cli_file_output():
    """Test English fuse CLI processing with file output."""
    lens_path = test_data_root / "mnt/input/eng_lens.srt"
    tesseract_path = test_data_root / "mnt/input/eng_tesseract.srt"
    expected_path = test_data_root / "mnt/output/eng_fuse.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            EngFuseCli,
            f"{lens_path} {tesseract_path} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected


def test_eng_fuse_cli_stdout_output():
    """Test English fuse CLI processing with stdout output."""
    lens_path = test_data_root / "mnt/input/eng_lens.srt"
    tesseract_path = test_data_root / "mnt/input/eng_tesseract.srt"
    expected_path = test_data_root / "mnt/output/eng_fuse.srt"

    stdout_stream = StringIO()
    with patch("scinoephile.cli.eng_fuse_cli.stdout", stdout_stream):
        run_cli_with_args(EngFuseCli, f"{lens_path} {tesseract_path}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(expected_path)

    assert output == expected


def test_eng_fuse_cli_clean():
    """Test English fuse CLI cleaning behavior."""
    lens_path = test_data_root / "mnt/input/eng_lens.srt"
    tesseract_path = test_data_root / "mnt/input/eng_tesseract.srt"

    with patch(
        "scinoephile.cli.eng_fuse_cli.get_eng_cleaned",
        side_effect=lambda series, remove_empty=False: series,
    ) as mocked_get_eng_cleaned:
        run_cli_with_args(EngFuseCli, f"{lens_path} {tesseract_path} --clean")

    assert mocked_get_eng_cleaned.call_count == 2
    for call in mocked_get_eng_cleaned.call_args_list:
        assert call.kwargs == {"remove_empty": False}
