#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
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
from scinoephile.core import Series
from scinoephile.testing import test_data_root


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "pdp/input/eng.srt",
            "--clean",
            "pdp/output/eng_clean.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/eng.srt",
            "--flatten",
            "pdp/output/eng_flatten.srt",
        ),
    ],
)
def test_english(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
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
            "pdp/input/zho-Hant.srt",
            "--flatten",
            "pdp/output/zho-Hant_flatten.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/zho-Hant.srt",
            "--simplify",
            "pdp/output/zho-Hant_simplify.srt",
        ),
    ],
)
def test_chinese(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
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
            "pdp/input/yue-Hant.srt",
            "pdp/input/eng.srt",
            "--clean --simplify",
            "pdp/output/yue-Hans_eng.srt",
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
                    f"{subcommands} -cif {chinese_input_path} -eif {english_input_path} {args} -bof {output_path}",
                )
                output = Series.load(output_path)
                expected = Series.load(test_data_root / expected_path)

                assert output == expected
