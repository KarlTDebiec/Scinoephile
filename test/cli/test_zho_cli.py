#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoCli."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import ScinoephileCli, ZhoCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoCli,),
        (ScinoephileCli, ZhoCli),
    ],
)
def test_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 中文 CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoCli,),
        (ScinoephileCli, ZhoCli),
    ],
)
def test_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 中文 CLI usage output."""
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("cli", "input_path", "args", "expected_path", "expectation"),
    [
        (
            (ZhoCli,),
            "mnt/output/zho-Hans_fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_fuse_clean.srt",
            nullcontext(),
        ),
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hans_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            nullcontext(),
        ),
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            "--romanize",
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten_romanize.srt",
            nullcontext(),
        ),
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten.srt",
            "--convert",
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt",
            nullcontext(),
        ),
        (
            (ZhoCli,),
            "mnt/output/zho-Hant_fuse_clean_validate.srt",
            "--proofread traditional",
            "mnt/output/zho-Hant_fuse_clean_validate_proofread.srt",
            nullcontext(),
        ),
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten.srt",
            "--convert t2s --proofread traditional",
            "-",
            pytest.raises(SystemExit),
        ),
    ],
)
def test_zho_cli(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
    expectation: AbstractContextManager[object],
):
    """Test 中文 CLI processing with file arguments."""
    full_input_path = test_data_root / input_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        with expectation:
            run_cli_with_args(
                cli[0],
                f"{subcommands} --infile {full_input_path} "
                f"{args} --outfile {output_path}",
            )
        if expected_path == "-":
            return
        full_expected_path = test_data_root / expected_path
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
        (
            "mnt/output/zho-Hans_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        ),
    ],
)
def test_zho_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test 中文 CLI processing via stdin/stdout."""
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    input_text = full_input_path.read_text()

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.zho_cli.stdin", stdin_stream):
        with patch("scinoephile.cli.zho_cli.stdout", stdout_stream):
            run_cli_with_args(ZhoCli, args)

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected
