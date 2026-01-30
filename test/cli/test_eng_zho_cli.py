#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the English/中文 CLI."""

from __future__ import annotations

import pytest

from scinoephile.cli import EngZhoCli, ScinoephileCli
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
        (EngZhoCli,),
        (ScinoephileCli, EngZhoCli),
    ],
)
def test_eng_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English/中文 CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (EngZhoCli,),
        (ScinoephileCli, EngZhoCli),
    ],
)
def test_eng_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English/中文 CLI usage output."""
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("cli", "subcommands"),
    [
        ((EngZhoCli,), "sync"),
        ((ScinoephileCli, EngZhoCli), "eng_zho sync"),
    ],
)
def test_eng_zho_sync_dispatch(
    cli: tuple[type[CommandLineInterface], ...],
    subcommands: str,
):
    """Test EngZho CLI dispatch to sync command."""
    zho_input = (
        test_data_root
        / "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )
    eng_input = (
        test_data_root / "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt"
    )
    expected_path = test_data_root / "mlamd/output/zho-Hans_eng.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            cli[0],
            f"{subcommands} --zho-infile {zho_input} "
            f"--eng-infile {eng_input} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(expected_path)

    assert output == expected
