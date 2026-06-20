#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaOffsetCli."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pytest import CaptureFixture, raises

from scinoephile.cli.media.media_offset_cli import MediaOffsetCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers import parametrize


def test_media_offset_cli_reports_offset(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test media offset CLI reports a human-readable offset result.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    reference_infile_path = tmp_path / "reference.mkv"
    target_infile_path = tmp_path / "target.mkv"
    reference_infile_path.touch()
    target_infile_path.touch()
    result = SimpleNamespace(
        offset=1.25,
        confidence="high",
        best=SimpleNamespace(
            offset=1.25,
            matched_count=24,
            score=0.5,
            offset_frames=30,
        ),
        second_best=SimpleNamespace(
            offset=1.0,
            matched_count=24,
            score=4.0,
            offset_frames=24,
        ),
        offset_frames=30,
        windows=(),
        aggregate=None,
    )

    with patch(
        "scinoephile.cli.media.media_offset_cli.get_video_offset",
        return_value=result,
    ):
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            "--max-offset 8 --sample-rate 1 --duration 120 --coarse-step 0.5",
        )

    assert capsys.readouterr().out.splitlines() == [
        "Offset: +1.250000 s",
        "Frames: +30",
        "Direction: target is 1.250000 s later than reference",
        "Confidence: high",
        "Matched samples: 24",
        "Best score: 0.500000",
        "Next-best score: 4.000000",
    ]


def test_media_offset_cli_reports_window_aggregate(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test media offset CLI reports multi-window aggregate results.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    reference_infile_path = tmp_path / "reference.mkv"
    target_infile_path = tmp_path / "target.mkv"
    reference_infile_path.touch()
    target_infile_path.touch()
    window_best = SimpleNamespace(
        offset=-0.8341666666666666,
        matched_count=48,
        score=0.1,
        offset_frames=-20,
    )
    window_next = SimpleNamespace(
        offset=-0.7924583333333333,
        matched_count=48,
        score=0.5,
        offset_frames=-19,
    )
    result = SimpleNamespace(
        offset=-0.8341666666666666,
        confidence="medium",
        best=window_best,
        second_best=window_next,
        offset_frames=-20,
        windows=(
            SimpleNamespace(
                start_time=720.0,
                offset=-0.8341666666666666,
                confidence="high",
                best=window_best,
                second_best=window_next,
                offset_frames=-20,
            ),
            SimpleNamespace(
                start_time=2070.0,
                offset=-0.8341666666666666,
                confidence="medium",
                best=window_best,
                second_best=window_next,
                offset_frames=-20,
            ),
        ),
        aggregate=SimpleNamespace(
            offset=-0.8341666666666666,
            offset_frames=-20,
            mean_frames=-20.0,
            median_frames=-20,
            stdev_frames=0.0,
            min_frames=-20,
            max_frames=-20,
            agreeing_count=2,
            total_count=2,
        ),
    )

    with patch(
        "scinoephile.cli.media.media_offset_cli.get_video_offset",
        return_value=result,
    ):
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            "--duration 120 --sample-windows 2",
        )

    assert capsys.readouterr().out.splitlines() == [
        "Window 1: start=00:12:00 offset=-20 frames (-0.834167 s), "
        "confidence=high, best=0.100000, next=0.500000",
        "Window 2: start=00:34:30 offset=-20 frames (-0.834167 s), "
        "confidence=medium, best=0.100000, next=0.500000",
        "",
        "Aggregate:",
        "  Offset: -20 frames (-0.834167 s)",
        "  Mean: -20.00 frames",
        "  Median: -20 frames",
        "  Stdev: 0.00 frames",
        "  Range: -20 to -20 frames",
        "  Agreement: 2/2 windows",
        "  Confidence: medium",
    ]


def test_media_offset_cli_rejects_start_time_argument(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test media offset CLI no longer accepts a start time argument.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    reference_infile_path = tmp_path / "reference.mkv"
    target_infile_path = tmp_path / "target.mkv"
    reference_infile_path.touch()
    target_infile_path.touch()

    with raises(SystemExit):
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            "--start-time 600",
        )

    assert "unrecognized arguments: --start-time 600" in capsys.readouterr().err


@parametrize(
    "argument",
    [
        "--max-offset",
        "--sample-rate",
        "--duration",
        "--coarse-step",
        "--sample-windows",
    ],
)
def test_media_offset_cli_rejects_zero_positive_arguments(
    argument: str,
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test media offset CLI rejects zero for positive arguments.

    Arguments:
        argument: argument to test
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    reference_infile_path = tmp_path / "reference.mkv"
    target_infile_path = tmp_path / "target.mkv"
    reference_infile_path.touch()
    target_infile_path.touch()

    with raises(SystemExit):
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            f"{argument} 0",
        )

    assert "is less than minimum value" in capsys.readouterr().err
