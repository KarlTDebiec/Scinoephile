#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoProcessCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho.zho_cli import ZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoProcessCli,),
        (ZhoCli, ZhoProcessCli),
        (ScinoephileCli, ZhoCli, ZhoProcessCli),
    ],
)
def test_zho_process_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese processing CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoProcessCli,),
        (ZhoCli, ZhoProcessCli),
        (ScinoephileCli, ZhoCli, ZhoProcessCli),
    ],
)
def test_zho_process_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese processing CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/zho-Hans_fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_fuse_clean.srt",
        ),
        (
            "mnt/output/zho-Hans_fuse_clean_validate_review.srt",
            "--flatten",
            "mnt/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
        ),
        (
            "mnt/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "--romanize",
            "mnt/output/zho-Hans_fuse_clean_validate_review_flatten_romanize.srt",
        ),
        (
            "mnt/output/zho-Hant_fuse_clean_validate_review_flatten.srt",
            "--convert t2s",
            "mnt/output/zho-Hant_fuse_clean_validate_review_flatten_simplify.srt",
        ),
        (
            "mnt/output/zho-Hant_fuse_clean_validate.srt",
            "--proofread traditional",
            "mnt/output/zho-Hant_fuse_clean_validate_review.srt",
        ),
    ],
)
def test_zho_process_cli(
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test standard Chinese processing CLI with file arguments.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoProcessCli,
            f"--infile {full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/zho-Hans_fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_fuse_clean.srt",
        ),
    ],
)
def test_zho_process_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test standard Chinese processing CLI via stdin/stdout.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    input_text = full_input_path.read_text()

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdin", stdin_stream):
        with patch("scinoephile.core.cli.stdout", stdout_stream):
            run_cli_with_args(ZhoProcessCli, f"--infile - {args}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected


def test_zho_process_cli_offsets_timing():
    """Test standard Chinese processing CLI can offset subtitle timings."""
    full_input_path = test_data_root / "mnt/output/zho-Hans_fuse.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoProcessCli,
            f"--infile {full_input_path} --offset 1250 --outfile {output_path}",
        )
        output = Series.load(output_path)

    expected = Series.load(full_input_path)
    expected.shift(ms=1250)
    assert output == expected


def test_zho_process_cli_rejects_bare_convert_flag():
    """Test standard Chinese processing CLI requires an explicit conversion config."""
    full_input_path = (
        test_data_root / "mnt/output/zho-Hant_fuse_clean_validate_review_flatten.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(ZhoProcessCli, f"--infile {full_input_path} --convert")
