#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the English CLI."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import EngCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import (
    assert_cli_help,
    assert_cli_usage,
    run_cli_with_args,
)
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (EngCli,),
        (ScinoephileCli, EngCli),
    ],
)
def test_eng_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (EngCli,),
        (ScinoephileCli, EngCli),
    ],
)
def test_eng_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English CLI usage output."""
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (EngCli,),
            "mnt/output/eng_fuse.srt",
            "--clean",
            "mnt/output/eng_fuse_clean.srt",
        ),
        (
            (ScinoephileCli, EngCli),
            "mnt/output/eng_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/eng_fuse_clean_validate_proofread_flatten.srt",
        ),
    ],
)
def test_eng_file_processing(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test English CLI processing with file arguments."""
    input_path = test_data_root / input_path
    expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} --infile {input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected


def test_eng_proofread_file_processing():
    """Test English proofreading with file arguments."""
    input_path = test_data_root / "mnt/output/eng_fuse_clean_validate.srt"
    expected_path = test_data_root / "mnt/output/eng_fuse_clean_validate_proofread.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            EngCli,
            f"--infile {input_path} --proofread --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected


def test_eng_pipe_processing():
    """Test English CLI processing via stdin/stdout."""
    input_path = test_data_root / "mnt/output/eng_fuse.srt"
    expected_path = test_data_root / "mnt/output/eng_fuse_clean.srt"
    input_text = input_path.read_text()

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.eng_cli.stdin", stdin_stream):
        with patch("scinoephile.cli.eng_cli.stdout", stdout_stream):
            run_cli_with_args(EngCli, "--clean")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(expected_path)

    assert output == expected
