#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import ScinoephileCli, ZhoCli
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
    ("cli", "input_path", "args", "expected_path"),
    [
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hans_fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_fuse_clean.srt",
        ),
        (
            (ZhoCli,),
            "mnt/output/zho-Hans_fuse_clean_validate_proofread.srt",
            "--flatten",
            "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        ),
        (
            (ScinoephileCli, ZhoCli),
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten.srt",
            "--convert",
            "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt",
        ),
    ],
)
def test_zho_file_processing(
    cli: tuple[type[CommandLineInterface], ...],
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test 中文 CLI processing with file arguments."""
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} --infile {full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


def test_zho_proofread_file_processing():
    """Test 中文 proofreading with file arguments."""
    input_path = test_data_root / "mnt/output/zho-Hant_fuse_clean_validate.srt"
    expected_path = (
        test_data_root / "mnt/output/zho-Hant_fuse_clean_validate_proofread.srt"
    )

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoCli,
            f"--proofread traditional --infile {input_path} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected


def test_zho_pipe_processing():
    """Test 中文 CLI processing via stdin/stdout."""
    input_path = test_data_root / "mnt/output/zho-Hans_fuse.srt"
    expected_path = test_data_root / "mnt/output/zho-Hans_fuse_clean.srt"
    input_text = input_path.read_text()

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.zho_cli.stdin", stdin_stream):
        with patch("scinoephile.cli.zho_cli.stdout", stdout_stream):
            run_cli_with_args(ZhoCli, "--clean")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(expected_path)

    assert output == expected


def test_zho_proofread_script_validation():
    """Test proofread script validation against conversion output."""
    input_path = (
        test_data_root / "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )

    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with patch("sys.stdout", stdout):
            with patch("sys.stderr", stderr):
                run_cli_with_args(
                    ScinoephileCli,
                    "zho --infile "
                    f"{input_path} "
                    "--convert t2s "
                    "--proofread traditional "
                    "--outfile -",
                )

    assert excinfo.value.code == 2
    assert "Proofread script must match post-conversion script" in stderr.getvalue()
