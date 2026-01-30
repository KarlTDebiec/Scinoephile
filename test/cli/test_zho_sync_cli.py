#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the English/中文 sync CLI."""

from __future__ import annotations

import pytest

from scinoephile.cli import EngZhoCli, EngZhoSyncCli, ScinoephileCli
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
        (EngZhoSyncCli,),
        (EngZhoCli, EngZhoSyncCli),
    ],
)
def test_eng_zho_sync_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English/中文 sync CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (EngZhoSyncCli,),
        (EngZhoCli, EngZhoSyncCli),
    ],
)
def test_eng_zho_sync_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English/中文 sync CLI usage output."""
    assert_cli_usage(cli)


def _run_sync(
    cli: tuple[type[CommandLineInterface], ...],
    args: str,
    *,
    zho_input: str,
    eng_input: str,
    expected_path: str,
):
    """Run sync CLI with file arguments and compare output."""
    zho_input_path = test_data_root / zho_input
    eng_input_path = test_data_root / eng_input
    expected_path = test_data_root / expected_path
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} --zho-infile {zho_input_path} "
            f"--eng-infile {eng_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected


def test_eng_zho_sync_clean():
    """Test English/中文 sync with cleaning enabled."""
    _run_sync(
        (EngZhoSyncCli,),
        "--clean",
        zho_input="mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_input="mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
        expected_path="mlamd/output/zho-Hans_eng.srt",
    )


def test_eng_zho_sync_convert_as_subcommand():
    """Test English/中文 sync conversion as subcommand."""
    _run_sync(
        (ScinoephileCli, EngZhoCli, EngZhoSyncCli),
        "--convert",
        zho_input="mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_input="mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
        expected_path="mlamd/output/zho-Hans_eng.srt",
    )
