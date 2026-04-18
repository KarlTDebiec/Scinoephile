#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.TimewarpCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import ScinoephileCli, TimewarpCli
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
    """Test timewarp CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (TimewarpCli,),
        (ScinoephileCli, TimewarpCli),
    ],
)
def test_timewarp_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test timewarp CLI usage output."""
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("cli", "anchor_path", "mobile_path", "args", "expected_path"),
    [
        (
            (TimewarpCli,),
            "kob/output/zho-Hant_fuse_clean_validate_proofread.srt",
            "kob/input/yue-Hant.srt",
            "--one-start-idx 1 --one-end-idx 1421 --two-start-idx 1 --two-end-idx 1461",
            "kob/output/yue-Hant_timewarp.srt",
        ),
        (
            (ScinoephileCli, TimewarpCli),
            "kob/output/zho-Hant_fuse_clean_validate_proofread.srt",
            "kob/input/yue-Hant.srt",
            "--one-start-idx 1 --one-end-idx 1421 --two-start-idx 1 --two-end-idx 1461",
            "kob/output/yue-Hant_timewarp.srt",
        ),
    ],
)
def test_timewarp_cli(
    cli: tuple[type[CommandLineInterface], ...],
    anchor_path: str,
    mobile_path: str,
    args: str,
    expected_path: str,
):
    """Test timewarp CLI processing with file arguments."""
    full_anchor_path = test_data_root / anchor_path
    full_mobile_path = test_data_root / mobile_path
    full_expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} {full_anchor_path} {full_mobile_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected
