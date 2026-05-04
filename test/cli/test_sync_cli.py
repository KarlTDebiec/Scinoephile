#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.SyncCli."""

from __future__ import annotations

from contextlib import redirect_stderr
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
            "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_ocr/fuse_clean_validate_review_flatten.srt",
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
            "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt",
            "mlamd/output/eng_ocr/fuse_clean_validate_review_flatten.srt",
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
    ("args", "expected_sync_cutoff", "expected_pause_length"),
    [
        ("", 0.16, 3000),
        ("--sync-cutoff 0.25 --pause-length 5000", 0.25, 5000),
    ],
)
def test_sync_cli_passes_tuning_options(
    args: str,
    expected_sync_cutoff: float,
    expected_pause_length: int,
):
    """Test sync CLI passes synchronization tuning options.

    Arguments:
        args: extra command-line arguments
        expected_sync_cutoff: expected sync cutoff passed to synchronization
        expected_pause_length: expected pause length passed to synchronization
    """
    top_path = (
        test_data_root
        / "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    bottom_path = (
        test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate_review_flatten.srt"
    )
    top_series = Series()
    bottom_series = Series()
    synced_series = Series()

    with patch(
        "scinoephile.cli.sync_cli.read_series",
        side_effect=[top_series, bottom_series],
    ):
        with patch("scinoephile.cli.sync_cli.write_series"):
            with patch(
                "scinoephile.cli.sync_cli.get_synced_series",
                return_value=synced_series,
            ) as get_synced_series:
                run_cli_with_args(
                    SyncCli,
                    f"--top-infile {top_path} --bottom-infile {bottom_path} {args}",
                )

    get_synced_series.assert_called_once_with(
        top_series,
        bottom_series,
        sync_cutoff=expected_sync_cutoff,
        pause_length=expected_pause_length,
    )


@pytest.mark.parametrize(
    ("args", "expected_error"),
    [
        ("--sync-cutoff -0.01", "-0.01 is less than minimum value of 0.0"),
        ("--sync-cutoff 1.01", "1.01 is greater than maximum value of 1.0"),
        ("--pause-length 0", "0 is less than minimum value of 1"),
    ],
)
def test_sync_cli_rejects_invalid_tuning_options(
    args: str,
    expected_error: str,
):
    """Test sync CLI rejects invalid synchronization tuning options.

    Arguments:
        args: extra command-line arguments
        expected_error: expected error message
    """
    top_path = (
        test_data_root
        / "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    bottom_path = (
        test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate_review_flatten.srt"
    )

    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stderr(stderr):
            run_cli_with_args(
                SyncCli,
                f"--top-infile {top_path} --bottom-infile {bottom_path} {args}",
            )

    assert excinfo.value.code == 2
    assert expected_error in stderr.getvalue()
