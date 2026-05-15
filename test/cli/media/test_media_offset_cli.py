#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaOffsetCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.media.media_offset_cli import MediaOffsetCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.media.video_offset import (
    VideoOffsetCandidate,
    VideoOffsetResult,
)


def test_media_offset_cli_reports_offset(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media offset CLI reports a human-readable offset result.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    reference_infile_path = tmp_path / "reference.mkv"
    target_infile_path = tmp_path / "target.mkv"
    reference_infile_path.touch()
    target_infile_path.touch()
    result = VideoOffsetResult(
        offset=1.25,
        confidence="high",
        best=VideoOffsetCandidate(offset=1.25, matched_count=24, score=0.5),
        second_best=VideoOffsetCandidate(offset=1.0, matched_count=24, score=4.0),
    )

    with patch(
        "scinoephile.cli.media.media_offset_cli.get_video_offset",
        return_value=result,
    ) as get_offset:
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            "--max-offset 8 --sample-rate 1 --start-time 600 --duration 120 "
            "--coarse-step 0.5 --fine-step 0.1",
        )

    get_offset.assert_called_once_with(
        reference_infile_path=reference_infile_path.resolve(),
        target_infile_path=target_infile_path.resolve(),
        max_offset=8.0,
        sample_rate=1.0,
        start_time=600.0,
        duration=120.0,
        coarse_step=0.5,
        fine_step=0.1,
    )
    assert capsys.readouterr().out.splitlines() == [
        "Offset: +1.250 s",
        "Direction: target is 1.250 s later than reference",
        "Confidence: high",
        "Matched samples: 24",
        "Best score: 0.500000",
        "Next-best score: 4.000000",
    ]


@pytest.mark.parametrize(
    "argument",
    [
        "--max-offset",
        "--sample-rate",
        "--duration",
        "--coarse-step",
        "--fine-step",
    ],
)
def test_media_offset_cli_rejects_zero_positive_arguments(
    argument: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
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

    with (
        pytest.raises(SystemExit),
        patch(
            "scinoephile.cli.media.media_offset_cli.get_video_offset",
        ) as get_offset,
    ):
        run_cli_with_args(
            MediaOffsetCli,
            f"--reference-infile {reference_infile_path} "
            f"--target-infile {target_infile_path} "
            f"{argument} 0",
        )

    get_offset.assert_not_called()
    assert "is less than minimum value" in capsys.readouterr().err
