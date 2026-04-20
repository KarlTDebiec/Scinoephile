#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.TimewarpCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.timewarp_cli import TimewarpCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (TimewarpCli,),
        (ScinoephileCli, TimewarpCli),
    ],
)
def test_timewarp_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test timewarp CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (TimewarpCli,),
        (ScinoephileCli, TimewarpCli),
    ],
)
def test_timewarp_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test timewarp CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("anchor_path", "mobile_path", "args", "expected_path"),
    [
        (
            "kob/output/zho-Hant_fuse_clean_validate_proofread.srt",
            "kob/input/yue-Hant.srt",
            "--one-start-idx 1 --one-end-idx 1421 --two-start-idx 1 --two-end-idx 1461",
            "kob/output/yue-Hant_timewarp.srt",
        ),
    ],
)
def test_timewarp_cli(
    anchor_path: str,
    mobile_path: str,
    args: str,
    expected_path: str,
):
    """Test timewarp CLI processing with file arguments.

    Arguments:
        anchor_path: path to anchor subtitle fixture
        mobile_path: path to mobile subtitle fixture
        args: command-line arguments for anchor indexes
        expected_path: path to expected output subtitle fixture
    """
    full_anchor_path = test_data_root / anchor_path
    full_mobile_path = test_data_root / mobile_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            TimewarpCli,
            f"--anchor-infile {full_anchor_path} --mobile-infile {full_mobile_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


@pytest.mark.parametrize(
    ("anchor_path", "mobile_path", "args", "expected_path"),
    [
        (
            "kob/output/zho-Hant_fuse_clean_validate_proofread.srt",
            "kob/input/yue-Hant.srt",
            "--one-start-idx 1 --one-end-idx 1421 --two-start-idx 1 --two-end-idx 1461",
            "kob/output/yue-Hant_timewarp.srt",
        ),
    ],
)
def test_timewarp_cli_pipe(
    anchor_path: str, mobile_path: str, args: str, expected_path: str
):
    """Test timewarp CLI writes stdout when outfile is omitted.

    Arguments:
        anchor_path: path to anchor subtitle fixture
        mobile_path: path to mobile subtitle fixture
        args: command-line arguments for anchor indexes
        expected_path: path to expected output subtitle fixture
    """
    full_anchor_path = test_data_root / anchor_path
    full_mobile_path = test_data_root / mobile_path
    full_expected_path = test_data_root / expected_path

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            TimewarpCli,
            f"--anchor-infile {full_anchor_path} --mobile-infile {full_mobile_path} "
            f"{args}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected
