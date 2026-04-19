#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.SyncCli."""

from __future__ import annotations

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
            "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt",
            "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt",
            "",
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
            f"{full_top_path} {full_bottom_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert output == expected


def test_sync_cli_pipe():
    """Test sync CLI processing writes stdout when outfile is omitted."""
    full_top_path = (
        test_data_root
        / "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )
    full_bottom_path = (
        test_data_root / "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt"
    )
    full_expected_path = test_data_root / "mlamd/output/zho-Hans_eng.srt"

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            SyncCli,
            f"{full_top_path} {full_bottom_path}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert output == expected


def test_sync_cli_rejects_overwrite_without_outfile():
    """Test sync CLI rejects overwrite when outfile is omitted."""
    full_top_path = (
        test_data_root
        / "mlamd/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )
    full_bottom_path = (
        test_data_root / "mlamd/output/eng_fuse_clean_validate_proofread_flatten.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            SyncCli,
            f"{full_top_path} {full_bottom_path} --overwrite",
        )
