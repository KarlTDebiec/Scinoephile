#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi stack CLI."""

from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from pytest import raises

from scinoephile.cli.multi.multi_stack_cli import MultiStackCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, parametrize


def test_multi_stack_cli_stacks_without_sync_by_default(tmp_path: Path):
    """Test multi stack combines top and bottom subtitles without pre-syncing.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    top_path = tmp_path / "top.srt"
    bottom_path = tmp_path / "bottom.srt"
    output_path = tmp_path / "stacked.srt"
    top_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    bottom_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    run_cli_with_args(
        MultiStackCli,
        f"--top-infile {top_path} --bottom-infile {bottom_path} "
        f"--outfile {output_path}",
    )

    expected = Series.from_string(
        "1\n00:00:01,000 --> 00:00:02,250\nA\\NB\n",
        format_="srt",
    )
    assert_series_equal(Series.load(output_path), expected)


def test_multi_stack_cli_can_sync_bottom_to_top_anchor(tmp_path: Path):
    """Test multi stack can shift bottom subtitles to top before stacking.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    top_path = tmp_path / "top.srt"
    bottom_path = tmp_path / "bottom.srt"
    output_path = tmp_path / "stacked.srt"
    top_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    bottom_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    run_cli_with_args(
        MultiStackCli,
        f"--top-infile {top_path} --bottom-infile {bottom_path} "
        f"--sync anchor-top --outfile {output_path}",
    )

    expected = Series.from_string(
        "1\n00:00:01,000 --> 00:00:02,000\nA\\NB\n",
        format_="srt",
    )
    assert_series_equal(Series.load(output_path), expected)


@parametrize(
    ("args", "expected_error"),
    [
        ("--sync-cutoff -0.01", "-0.01 is less than minimum value of 0.0"),
        ("--sync-cutoff 1.01", "1.01 is greater than maximum value of 1.0"),
        ("--pause-length 0", "0 is less than minimum value of 1"),
        (
            "--sync inside",
            "'inside' is not one of the supported values: "
            "anchor-top, anchor-bottom, off",
        ),
    ],
)
def test_multi_stack_cli_rejects_invalid_tuning_options(
    args: str,
    expected_error: str,
    tmp_path: Path,
):
    """Test multi stack CLI rejects invalid synchronization tuning options.

    Arguments:
        args: extra command-line arguments
        expected_error: expected error message
        tmp_path: temporary directory provided by pytest
    """
    top_path = tmp_path / "top.srt"
    bottom_path = tmp_path / "bottom.srt"
    top_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    bottom_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stderr(stderr):
            run_cli_with_args(
                MultiStackCli,
                f"--top-infile {top_path} --bottom-infile {bottom_path} {args}",
            )

    assert excinfo.value.code == 2
    assert expected_error in stderr.getvalue()
