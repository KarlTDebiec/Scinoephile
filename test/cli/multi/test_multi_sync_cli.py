#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi sync CLI."""

from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch, raises

from scinoephile.cli.multi.multi_sync_cli import MultiSyncCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, parametrize


def test_multi_sync_cli_shifts_mobile_to_anchor_and_writes_file(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test multi sync estimates offset, shifts mobile subtitles, and writes output.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    output_path = tmp_path / "synced.srt"
    anchor_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    run_cli_with_args(
        MultiSyncCli,
        f"-v --anchor-infile {anchor_path} --mobile-infile {mobile_path} "
        f"--outfile {output_path}",
    )

    expected = Series.from_string(
        "1\n00:00:01,000 --> 00:00:02,000\nB\n",
        format_="srt",
    )
    assert_series_equal(Series.load(output_path), expected)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Mean offset: +0.250 s" in captured.err


def test_multi_sync_cli_pipe(tmp_path: Path):
    """Test multi sync writes shifted mobile subtitles to stdout by default.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    anchor_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    stdout_stream = StringIO()
    with MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("scinoephile.cli.helpers.io.stdout", stdout_stream)
        run_cli_with_args(
            MultiSyncCli,
            f"--anchor-infile {anchor_path} --mobile-infile {mobile_path}",
        )

    expected = Series.from_string(
        "1\n00:00:01,000 --> 00:00:02,000\nB\n",
        format_="srt",
    )
    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output, expected)


@parametrize(
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
    tmp_path: Path,
):
    """Test multi sync CLI rejects invalid synchronization tuning options.

    Arguments:
        args: extra command-line arguments
        expected_error: expected error message
        tmp_path: temporary directory provided by pytest
    """
    anchor_path = tmp_path / "anchor.srt"
    mobile_path = tmp_path / "mobile.srt"
    anchor_path.write_text("1\n00:00:01,000 --> 00:00:02,000\nA\n", encoding="utf-8")
    mobile_path.write_text("1\n00:00:01,250 --> 00:00:02,250\nB\n", encoding="utf-8")

    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stderr(stderr):
            run_cli_with_args(
                MultiSyncCli,
                f"--anchor-infile {anchor_path} --mobile-infile {mobile_path} {args}",
            )

    assert excinfo.value.code == 2
    assert expected_error in stderr.getvalue()
