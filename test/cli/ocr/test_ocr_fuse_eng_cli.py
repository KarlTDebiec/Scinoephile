#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR fuse CLI for English subtitles."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_cli_help,
    assert_cli_usage,
    assert_series_equal,
    test_data_root,
)


@pytest.mark.parametrize(
    "cli",
    [
        (OcrFuseCli,),
        (OcrCli, OcrFuseCli),
        (ScinoephileCli, OcrCli, OcrFuseCli),
    ],
)
def test_ocr_fuse_eng_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test OCR fuse CLI help output for English subtitles.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OcrFuseCli,),
        (OcrCli, OcrFuseCli),
        (ScinoephileCli, OcrCli, OcrFuseCli),
    ],
)
def test_ocr_fuse_eng_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test OCR fuse CLI usage output for English subtitles.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("lens_input_path", "tesseract_input_path", "args", "expected_path"),
    [
        (
            "kob/input/eng_ocr/lens.srt",
            "kob/input/eng_ocr/tesseract.srt",
            "--clean",
            "kob/output/eng_ocr/fuse_clean.srt",
        ),
        (
            "mlamd/input/eng_ocr/lens.srt",
            "mlamd/input/eng_ocr/tesseract.srt",
            "--clean",
            "mlamd/output/eng_ocr/fuse_clean.srt",
        ),
        (
            "mnt/input/eng_ocr/lens.srt",
            "mnt/input/eng_ocr/tesseract.srt",
            "--clean",
            "mnt/output/eng_ocr/fuse_clean.srt",
        ),
        (
            "t/input/eng_ocr/lens.srt",
            "t/input/eng_ocr/tesseract.srt",
            "--clean",
            "t/output/eng_ocr/fuse_clean.srt",
        ),
    ],
)
def test_ocr_fuse_eng_cli(
    lens_input_path: str,
    tesseract_input_path: str,
    args: str,
    expected_path: str,
):
    """Test OCR fuse CLI processing for English subtitles with file arguments.

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
            OcrFuseCli,
            f"--language eng --lens-infile {full_lens_input_path} "
            f"--tesseract-infile {full_tesseract_input_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@pytest.mark.parametrize(
    ("lens_input_path", "tesseract_input_path", "args", "expected_path"),
    [
        (
            "kob/input/eng_ocr/lens.srt",
            "kob/input/eng_ocr/tesseract.srt",
            "",
            "kob/output/eng_ocr/fuse.srt",
        ),
    ],
)
def test_ocr_fuse_eng_cli_pipe(
    lens_input_path: str,
    tesseract_input_path: str,
    args: str,
    expected_path: str,
):
    """Test OCR fuse CLI processing for English subtitles via stdout.

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
            OcrFuseCli,
            f"--language eng --lens-infile {full_lens_input_path} "
            f"--tesseract-infile {full_tesseract_input_path} {args}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)
