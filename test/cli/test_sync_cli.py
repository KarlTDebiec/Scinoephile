#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.SyncCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.sync_cli import SyncCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (SyncCli,),
        (ScinoephileCli, SyncCli),
    ],
)
def test_sync_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test sync CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (SyncCli,),
        (ScinoephileCli, SyncCli),
    ],
)
def test_sync_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test sync CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("top_path", "bottom_path", "args", "expected_path"),
    [
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_review_flatten.srt",
            "",
            "mlamd/output/zho-Hans_eng.srt",
        ),
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_review_flatten.srt",
            "--sync-cutoff 0.16",
            "mlamd/output/zho-Hans_eng.srt",
        ),
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_review_flatten.srt",
            "--pause-length 3000",
            "mlamd/output/zho-Hans_eng.srt",
        ),
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_review_flatten.srt",
            "--sync-cutoff 0.16 --pause-length 3000",
            "mlamd/output/zho-Hans_eng.srt",
        ),
    ],
)
def test_sync_cli(
    top_path: str,
    bottom_path: str,
    args: str,
    expected_path: str,
):
    """Test sync CLI processing with file arguments.

    Arguments:
        top_path: path to top subtitle fixture
        bottom_path: path to bottom subtitle fixture
        args: extra command-line arguments
        expected_path: path to expected output subtitle fixture
    """
    full_top_path = test_data_root / top_path
    full_bottom_path = test_data_root / bottom_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            SyncCli,
            f"--top-infile {full_top_path} --bottom-infile {full_bottom_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("top_path", "bottom_path", "expected_path"),
    [
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/zho-Hans_eng.srt",
        ),
    ],
)
def test_sync_cli_pipe(top_path: str, bottom_path: str, expected_path: str):
    """Test sync CLI processing writes stdout when outfile is omitted.

    Arguments:
        top_path: path to top subtitle fixture
        bottom_path: path to bottom subtitle fixture
        expected_path: path to expected output subtitle fixture
    """
    full_top_path = test_data_root / top_path
    full_bottom_path = test_data_root / bottom_path
    full_expected_path = test_data_root / expected_path

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            SyncCli,
            f"--top-infile {full_top_path} --bottom-infile {full_bottom_path}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("arg", "value"),
    [
        ("--sync-cutoff", "-0.1"),
        ("--sync-cutoff", "1.1"),
        ("--sync-cutoff", "abc"),
        ("--pause-length", "0"),
        ("--pause-length", "-1"),
        ("--pause-length", "abc"),
    ],
)
def test_sync_cli_invalid_args(arg: str, value: str):
    """Test sync CLI rejects invalid argument values.

    Arguments:
        arg: argument flag
        value: invalid value to supply
    """
    top_path = (
        test_data_root / "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt"
    )
    bottom_path = (
        test_data_root / "mlamd/output/eng_fuse_clean_validate_review_flatten.srt"
    )

    stdout_stream = StringIO()
    stderr_stream = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout_stream):
            with redirect_stderr(stderr_stream):
                run_cli_with_args(
                    SyncCli,
                    f"--top-infile {top_path} --bottom-infile {bottom_path} "
                    f"{arg} {value}",
                )
    assert excinfo.value.code == 2
