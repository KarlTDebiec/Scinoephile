#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoFuseCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import ScinoephileCli, ZhoCli, ZhoFuseCli, zho_fuse_cli
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
    """Test 中文 fuse CLI help output.

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
    """Test 中文 fuse CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("lens_path", "paddle_path", "args", "expected_path"),
    [
        (
            "mnt/input/zho-Hans_lens.srt",
            "mnt/input/zho-Hans_paddle.srt",
            "--clean --convert",
            "mnt/output/zho-Hans_fuse.srt",
        ),
        (
            "kob/input/zho-Hant_lens.srt",
            "kob/input/zho-Hant_paddle.srt",
            "--clean --convert s2t",
            "kob/output/zho-Hant_fuse.srt",
        ),
    ],
)
def test_zho_fuse_cli_file_output(
    lens_path: str,
    paddle_path: str,
    args: str,
    expected_path: str,
):
    """Test 中文 OCR fusion CLI processing with file output.

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
            f"{full_lens_path} {full_paddle_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


def test_zho_fuse_cli_stdout_output():
    """Test 中文 OCR fusion CLI processing with stdout output."""
    lens_path = test_data_root / "mnt/input/zho-Hans_lens.srt"
    paddle_path = test_data_root / "mnt/input/zho-Hans_paddle.srt"
    expected_path = test_data_root / "mnt/output/zho-Hans_fuse.srt"

    stdout_stream = StringIO()
    with patch("scinoephile.cli.zho_fuse_cli.stdout", stdout_stream):
        run_cli_with_args(
            ZhoFuseCli,
            f"{lens_path} {paddle_path} --clean --convert",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(expected_path)

    assert output == expected


def test_zho_fuse_cli_clean_is_opt_in():
    """Test 中文 OCR fusion CLI only cleans when --clean is provided."""
    lens_path = test_data_root / "mnt/input/zho-Hans_lens.srt"
    paddle_path = test_data_root / "mnt/input/zho-Hans_paddle.srt"

    with get_temp_file_path(".srt") as output_path:
        with patch.object(
            zho_fuse_cli,
            "get_zho_cleaned",
            wraps=zho_fuse_cli.get_zho_cleaned,
        ) as get_zho_cleaned_mock:
            run_cli_with_args(
                ZhoFuseCli,
                f"{lens_path} {paddle_path} --convert --outfile {output_path}",
            )
            get_zho_cleaned_mock.assert_not_called()

    with get_temp_file_path(".srt") as output_path:
        with patch.object(
            zho_fuse_cli,
            "get_zho_cleaned",
            wraps=zho_fuse_cli.get_zho_cleaned,
        ) as get_zho_cleaned_mock:
            run_cli_with_args(
                ZhoFuseCli,
                f"{lens_path} {paddle_path} --clean --convert --outfile {output_path}",
            )
            get_zho_cleaned_mock.assert_called()
            assert get_zho_cleaned_mock.call_count == 2
