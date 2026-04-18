#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.SyncCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import ScinoephileCli, SyncCli
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
    """Test sync CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (SyncCli,),
        (ScinoephileCli, SyncCli),
    ],
)
def test_sync_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test sync CLI usage output."""
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("cli", "top_path", "bottom_path", "args", "expected_path"),
    [
        (
            (SyncCli,),
            "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
            "",
            "mlamd/output/zho-Hans_eng.srt",
        ),
        (
            (ScinoephileCli, SyncCli),
            "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
            "",
            "mlamd/output/zho-Hans_eng.srt",
        ),
    ],
)
def test_sync_cli(
    cli: tuple[type[CommandLineInterface], ...],
    top_path: str,
    bottom_path: str,
    args: str,
    expected_path: str,
):
    """Test sync CLI processing with file arguments."""
    full_top_path = test_data_root / top_path
    full_bottom_path = test_data_root / bottom_path
    full_expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} {full_top_path} {full_bottom_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected
