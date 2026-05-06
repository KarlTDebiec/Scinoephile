#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoFuseCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho.zho_cli import ZhoCli
from scinoephile.cli.zho.zho_fuse_cli import ZhoFuseCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoFuseCli,),
        (ZhoCli, ZhoFuseCli),
        (ScinoephileCli, ZhoCli, ZhoFuseCli),
    ],
)
def test_zho_fuse_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese fuse CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoFuseCli,),
        (ZhoCli, ZhoFuseCli),
        (ScinoephileCli, ZhoCli, ZhoFuseCli),
    ],
)
def test_zho_fuse_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese fuse CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("lens_path", "paddle_path", "args", "expected_path"),
    [
        (
            "kob/input/zho-Hant_ocr/lens.srt",
            "kob/input/zho-Hant_ocr/paddle.srt",
            "--clean --convert s2t",
            "kob/output/zho-Hant_ocr/fuse.srt",
        ),
        (
            "mlamd/input/zho-Hans_ocr/lens.srt",
            "mlamd/input/zho-Hans_ocr/paddle.srt",
            "--clean --convert t2s",
            "mlamd/output/zho-Hans_ocr/fuse.srt",
        ),
        (
            "mnt/input/zho-Hans_ocr/lens.srt",
            "mnt/input/zho-Hans_ocr/paddle.srt",
            "--clean --convert t2s",
            "mnt/output/zho-Hans_ocr/fuse.srt",
        ),
        (
            "t/input/zho-Hans_ocr/lens.srt",
            "t/input/zho-Hans_ocr/paddle.srt",
            "--clean --convert t2s",
            "t/output/zho-Hans_ocr/fuse.srt",
        ),
    ],
)
def test_zho_fuse_cli(
    lens_path: str,
    paddle_path: str,
    args: str,
    expected_path: str,
):
    """Test standard Chinese OCR fusion CLI processing with file output.

    Arguments:
        lens_path: path to Google Lens subtitle fixture
        paddle_path: path to PaddleOCR subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_lens_path = test_data_root / lens_path
    full_paddle_path = test_data_root / paddle_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoFuseCli,
            f"--lens-infile {full_lens_path} "
            f"--paddle-infile {full_paddle_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("lens_path", "paddle_path", "args", "expected_path"),
    [
        (
            "mnt/input/zho-Hans_ocr/lens.srt",
            "mnt/input/zho-Hans_ocr/paddle.srt",
            "--clean --convert t2s",
            "mnt/output/zho-Hans_ocr/fuse.srt",
        ),
    ],
)
def test_zho_fuse_cli_pipe(
    lens_path: str,
    paddle_path: str,
    args: str,
    expected_path: str,
):
    """Test standard Chinese OCR fusion CLI processing with stdout output.

    Arguments:
        lens_path: path to Google Lens subtitle fixture
        paddle_path: path to PaddleOCR subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_lens_path = test_data_root / lens_path
    full_paddle_path = test_data_root / paddle_path
    full_expected_path = test_data_root / expected_path

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            ZhoFuseCli,
            f"--lens-infile {full_lens_path} --paddle-infile {full_paddle_path} {args}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected


def test_zho_fuse_cli_rejects_bare_convert_flag():
    """Test standard Chinese OCR fusion CLI requires an explicit conversion config."""
    full_lens_path = test_data_root / "mnt/input/zho-Hans_ocr/lens.srt"
    full_paddle_path = test_data_root / "mnt/input/zho-Hans_ocr/paddle.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            ZhoFuseCli,
            f"--lens-infile {full_lens_path} "
            f"--paddle-infile {full_paddle_path} --clean --convert",
        )
