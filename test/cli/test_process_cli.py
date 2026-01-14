#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Scinoephile command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from scinoephile.cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "mnt/output/eng_fuse.srt",
            "--clean",
            "mnt/output/eng_fuse_clean.srt",
        ),
        (
            (ScinoephileCli,),
            "mnt/output/eng_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/eng_fuse_clean_validate_proofread_flatten.srt",
        ),
    ],
)
def test_english(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test CLI processing of English subtitles.

    Arguments:
        cli: CLI class to test
        input_path: Path to the input subtitle file
        args: Additional arguments for processing
        expected_path: Path to the expected output subtitle file
    """
    input_path = test_data_root / input_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    stdout = StringIO()
    stderr = StringIO()

    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            with get_temp_file_path(".srt") as output_path:
                run_cli_with_args(
                    cli[0], f"{subcommands} -eif {input_path} {args} -eof {output_path}"
                )
                output = Series.load(output_path)
                expected = Series.load(test_data_root / expected_path)

                assert output == expected


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "mnt/output/zho-Hans_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        ),
        (
            (ScinoephileCli,),
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten.srt",
            "--convert",
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt",
        ),
    ],
)
def test_chinese(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test CLI processing of Chinese subtitles.

    Arguments:
        cli: CLI class to test
        input_path: Path to the input subtitle file
        args: Additional arguments for processing
        expected_path: Path to the expected output subtitle file
    """
    input_path = test_data_root / input_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    stdout = StringIO()
    stderr = StringIO()

    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            with get_temp_file_path(".srt") as output_path:
                run_cli_with_args(
                    cli[0], f"{subcommands} -cif {input_path} {args} -cof {output_path}"
                )
                output = Series.load(output_path)
                expected = Series.load(test_data_root / expected_path)

                assert output == expected


@pytest.mark.parametrize(
    ("cli", "chinese_input_path", "english_input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
            "--clean --flatten",
            "mlamd/output/zho-Hans_eng.srt",
        ),
    ],
)
def test_bilingual(
    cli: tuple[type[CommandLineInterface], ...],
    chinese_input_path: str,
    english_input_path: str,
    args: str,
    expected_path: str,
):
    """Test CLI processing of bilingual subtitles.

    Arguments:
        cli: CLI class to test
        chinese_input_path: Path to the Chinese input subtitle file
        english_input_path: Path to the English input subtitle file
        args: Additional arguments for processing
        expected_path: Path to the expected output subtitle file
    """
    chinese_input_path = test_data_root / chinese_input_path
    english_input_path = test_data_root / english_input_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    stdout = StringIO()
    stderr = StringIO()

    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            with get_temp_file_path(".srt") as output_path:
                run_cli_with_args(
                    cli[0],
                    f"{subcommands} -cif {chinese_input_path} "
                    f"-eif {english_input_path} {args} -bof {output_path}",
                )
                output = Series.load(output_path)
                expected = Series.load(test_data_root / expected_path)

                assert output == expected
