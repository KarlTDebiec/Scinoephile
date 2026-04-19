#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.EngFuseCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.eng.eng_cli import EngCli
from scinoephile.cli.eng.eng_fuse_cli import EngFuseCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
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


@pytest.mark.parametrize(
    ("lens_input_path", "tesseract_input_path", "args", "expected_path"),
    [
        (
            "kob/input/eng_lens.srt",
            "kob/input/eng_tesseract.srt",
            "",
            "kob/output/eng_fuse.srt",
        ),
        (
            "kob/input/eng_lens.srt",
            "kob/input/eng_tesseract.srt",
            "--clean",
            "kob/output/eng_fuse_clean.srt",
        ),
        (
            "mlamd/input/eng_lens.srt",
            "mlamd/input/eng_tesseract.srt",
            "",
            "mlamd/output/eng_fuse.srt",
        ),
        (
            "mlamd/input/eng_lens.srt",
            "mlamd/input/eng_tesseract.srt",
            "--clean",
            "mlamd/output/eng_fuse_clean.srt",
        ),
        (
            "mnt/input/eng_lens.srt",
            "mnt/input/eng_tesseract.srt",
            "",
            "mnt/output/eng_fuse.srt",
        ),
        (
            "mnt/input/eng_lens.srt",
            "mnt/input/eng_tesseract.srt",
            "--clean",
            "mnt/output/eng_fuse_clean.srt",
        ),
        (
            "t/input/eng_lens.srt",
            "t/input/eng_tesseract.srt",
            "",
            "t/output/eng_fuse.srt",
        ),
        (
            "t/input/eng_lens.srt",
            "t/input/eng_tesseract.srt",
            "--clean",
            "t/output/eng_fuse_clean.srt",
        ),
    ],
)
def test_eng_fuse_cli(
    lens_input_path: str,
    tesseract_input_path: str,
    args: str,
    expected_path: str,
):
    """Test English fuse CLI processing with file arguments.

    Arguments:
        lens_input_path: path to Google Lens subtitle fixture
        tesseract_input_path: path to Tesseract subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_lens_input_path = test_data_root / lens_input_path
    full_tesseract_input_path = test_data_root / tesseract_input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            EngFuseCli,
            f"{full_lens_input_path} {full_tesseract_input_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("lens_input_path", "tesseract_input_path", "args", "expected_path"),
    [
        (
            "kob/input/eng_lens.srt",
            "kob/input/eng_tesseract.srt",
            "",
            "kob/output/eng_fuse.srt",
        ),
    ],
)
def test_eng_fuse_cli_pipe(
    lens_input_path: str,
    tesseract_input_path: str,
    args: str,
    expected_path: str,
):
    """Test English fuse CLI processing via stdout.

    Arguments:
        lens_input_path: path to Google Lens subtitle fixture
        tesseract_input_path: path to Tesseract subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_lens_input_path = test_data_root / lens_input_path
    full_tesseract_input_path = test_data_root / tesseract_input_path
    full_expected_path = test_data_root / expected_path

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            EngFuseCli,
            f"{full_lens_input_path} {full_tesseract_input_path} {args}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected
