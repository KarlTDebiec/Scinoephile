#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Scinoephile command-line interface."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Type

import pytest

from scinoephile.cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "pdp/input/en.srt",
            "--clean",
            "pdp/output/en_clean.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/en.srt",
            "--clean --merge",
            "pdp/output/en_clean_merge.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/en.srt",
            "--merge",
            "pdp/output/en_merge.srt",
        ),
    ],
)
def test_english(
    cli: tuple[Type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    input_path = get_test_file_path(input_path)
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
                expected = Series.load(get_test_file_path(expected_path))

                assert output == expected


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "pdp/input/cmn-Hant.srt",
            "--merge",
            "pdp/output/cmn-Hant_merge.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/cmn-Hant.srt",
            "--merge --simplify",
            "pdp/output/cmn-Hant_merge_simplify.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/cmn-Hant.srt",
            "--simplify",
            "pdp/output/cmn-Hant_simplify.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/yue-Hant.srt",
            "--merge",
            "pdp/output/yue-Hant_merge.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/yue-Hant.srt",
            "--merge --simplify",
            "pdp/output/yue-Hant_merge_simplify.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/yue-Hant.srt",
            "--simplify",
            "pdp/output/yue-Hant_simplify.srt",
        ),
    ],
)
def test_chinese(
    cli: tuple[Type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    input_path = get_test_file_path(input_path)
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
                expected = Series.load(get_test_file_path(expected_path))

                assert output == expected


@pytest.mark.parametrize(
    ("cli", "chinese_input_path", "english_input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli,),
            "mnt/input/cmn-Hans.srt",
            "mnt/input/en-US.srt",
            "--clean",
            "mnt/output/cmn-Hans_en-US.srt",
        ),
        (
            (ScinoephileCli,),
            "pdp/input/yue-Hant.srt",
            "pdp/input/en.srt",
            "--clean --simplify",
            "pdp/output/yue-Hant_en_clean_simplify.srt",
        ),
    ],
)
def test_bilingual(
    cli: tuple[Type[CommandLineInterface], ...],
    chinese_input_path: str,
    english_input_path: str,
    args: str,
    expected_path: str,
):
    chinese_input_path = get_test_file_path(chinese_input_path)
    english_input_path = get_test_file_path(english_input_path)
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
                expected = Series.load(get_test_file_path(expected_path))

                assert output == expected
