#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi sync CLI."""

from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.multi.multi_sync_cli import MultiSyncCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import test_data_root


@pytest.mark.parametrize(
    ("args", "expected_sync_cutoff", "expected_pause_length"),
    [
        ("", 0.16, 3000),
        ("--sync-cutoff 0.25 --pause-length 5000", 0.25, 5000),
    ],
)
def test_multi_sync_cli_passes_tuning_options(
    args: str,
    expected_sync_cutoff: float,
    expected_pause_length: int,
):
    """Test multi sync CLI passes synchronization tuning options.

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

    with (
        patch(
            "scinoephile.cli.multi.multi_sync_cli.read_series",
            side_effect=[top_series, bottom_series],
        ),
        patch("scinoephile.cli.multi.multi_sync_cli.write_series") as write_series,
        patch(
            "scinoephile.cli.multi.multi_sync_cli.get_synced_series",
            return_value=synced_series,
        ) as get_synced_series,
    ):
        run_cli_with_args(
            MultiSyncCli,
            f"--top-infile {top_path} --bottom-infile {bottom_path} {args}",
        )

    get_synced_series.assert_called_once_with(
        top_series,
        bottom_series,
        sync_cutoff=expected_sync_cutoff,
        pause_length=expected_pause_length,
    )
    assert write_series.call_args.args[1:] == (synced_series, "-", False)


@pytest.mark.parametrize(
    ("args", "expected_error"),
    [
        ("--sync-cutoff -0.01", "-0.01 is less than minimum value of 0.0"),
        ("--sync-cutoff 1.01", "1.01 is greater than maximum value of 1.0"),
        ("--pause-length 0", "0 is less than minimum value of 1"),
    ],
)
def test_multi_sync_cli_rejects_invalid_tuning_options(
    args: str,
    expected_error: str,
):
    """Test multi sync CLI rejects invalid synchronization tuning options.

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
                MultiSyncCli,
                f"--top-infile {top_path} --bottom-infile {bottom_path} {args}",
            )

    assert excinfo.value.code == 2
    assert expected_error in stderr.getvalue()
