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


def _run_sync(
    cli: tuple[type[CommandLineInterface], ...],
    args: str,
    *,
    top_input: str,
    bottom_input: str,
    expected_path: str,
):
    """Run sync CLI with file arguments and compare output."""
    top_input_path = test_data_root / top_input
    bottom_input_path = test_data_root / bottom_input
    full_expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} {top_input_path} {bottom_input_path} "
            f"{args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


def test_sync_basic():
    """Test sync with file arguments."""
    _run_sync(
        (SyncCli,),
        "",
        top_input="mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        bottom_input="mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
        expected_path="mlamd/output/zho-Hans_eng.srt",
    )


def test_sync_as_subcommand():
    """Test sync as subcommand."""
    _run_sync(
        (ScinoephileCli, SyncCli),
        "",
        top_input="mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        bottom_input="mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
        expected_path="mlamd/output/zho-Hans_eng.srt",
    )
