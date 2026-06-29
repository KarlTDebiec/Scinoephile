#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi timewarp CLI."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.multi.multi_timewarp_cli import MultiTimewarpCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal


def test_multi_timewarp_cli_passes_arguments_and_writes_file(tmp_path: Path):
    """Test multi timewarp CLI passes parsed arguments to timing logic.

    Arguments:
        tmp_path: temporary path fixture
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    output_path = tmp_path / "timewarped.srt"
    anchor_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:02,000 --> 00:00:03,000\nB\n", encoding="utf-8")
    anchor_series = Series.from_string(anchor_path.read_text(encoding="utf-8"))
    mobile_series = Series.from_string(mobile_path.read_text(encoding="utf-8"))
    timewarped_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nB\n",
        format_="srt",
    )
    timewarp_calls = 0

    def get_timewarped(
        *,
        source_one: Series,
        source_two: Series,
        one_start_idx: int,
        one_end_idx: int,
        two_start_idx: int,
        two_end_idx: int,
    ) -> Series:
        """Validate timewarp inputs."""
        nonlocal timewarp_calls
        timewarp_calls += 1
        assert_series_equal(source_one, anchor_series)
        assert_series_equal(source_two, mobile_series)
        assert one_start_idx == 1
        assert one_end_idx == 2
        assert two_start_idx == 3
        assert two_end_idx == 4
        return timewarped_series

    with (
        patch(
            "scinoephile.cli.multi.multi_timewarp_cli.get_series_timewarped",
            side_effect=get_timewarped,
        ),
    ):
        run_cli_with_args(
            MultiTimewarpCli,
            f"--anchor-infile {anchor_path} --mobile-infile {mobile_path} "
            "--anchor-start-idx 1 --anchor-end-idx 2 "
            "--mobile-start-idx 3 --mobile-end-idx 4 "
            f"--outfile {output_path}",
        )

    assert timewarp_calls == 1
    assert_series_equal(Series.load(output_path), timewarped_series)


def test_multi_timewarp_cli_pipe(tmp_path: Path):
    """Test multi timewarp CLI writes stdout when outfile is omitted.

    Arguments:
        tmp_path: temporary path fixture
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    anchor_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:02,000 --> 00:00:03,000\nB\n", encoding="utf-8")
    timewarped_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nB\n",
        format_="srt",
    )

    stdout_stream = StringIO()
    with (
        patch(
            "scinoephile.cli.multi.multi_timewarp_cli.get_series_timewarped",
            return_value=timewarped_series,
        ),
        patch("scinoephile.cli.helpers.io.stdout", stdout_stream),
    ):
        run_cli_with_args(
            MultiTimewarpCli,
            f"--anchor-infile {anchor_path} --mobile-infile {mobile_path}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output, timewarped_series)


def test_multi_timewarp_cli_rejects_old_one_two_index_flags(tmp_path: Path):
    """Test timewarp rejects old one/two index flags.

    Arguments:
        tmp_path: temporary path fixture
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    anchor_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:02,000 --> 00:00:03,000\nB\n", encoding="utf-8")

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            MultiTimewarpCli,
            f"--anchor-infile {anchor_path} --mobile-infile {mobile_path} "
            "--one-start-idx 1 --two-start-idx 1",
        )
