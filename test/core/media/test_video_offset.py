#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of video offset detection."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import VideoOffsetCandidate, VideoOffsetResult
from scinoephile.core.media.video_offset import (
    get_video_offset,
)


def test_get_video_offset_prefers_known_shift():
    """Test video offset search prefers a known shifted sequence."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with patch(
        "scinoephile.core.media.video_offset._sample_video_frames",
        side_effect=[reference_samples, target_samples],
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            fine_step=0.5,
        )

    assert result.offset == 1.0
    assert result.best.matched_count == 4


def test_get_video_offset_tolerates_brightness_shift():
    """Test video offset search normalizes brightness differences."""
    reference_samples = [
        _get_sample(
            time=0.0,
            frame=np.array([[0, 1], [2, 3]], dtype=np.float32),
        ),
        _get_sample(
            time=1.0,
            frame=np.array([[4, 5], [6, 7]], dtype=np.float32),
        ),
    ]
    target_samples = [
        _get_sample(
            time=1.0,
            frame=np.array([[10, 12], [14, 16]], dtype=np.float32),
        ),
        _get_sample(
            time=2.0,
            frame=np.array([[18, 20], [22, 24]], dtype=np.float32),
        ),
    ]

    with patch(
        "scinoephile.core.media.video_offset._sample_video_frames",
        side_effect=[reference_samples, target_samples],
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            fine_step=0.5,
        )

    assert result.offset == 1.0
    assert result.best.score == pytest.approx(0.0)


def test_get_video_offset_uses_ten_second_default():
    """Test video offset search defaults to a ten-second maximum offset."""
    reference_samples = _get_samples([0.0, 1.0, 2.0], [1, 2, 3])
    target_samples = _get_samples([9.0, 10.0, 11.0], [1, 2, 3])

    with patch(
        "scinoephile.core.media.video_offset._sample_video_frames",
        side_effect=[reference_samples, target_samples],
    ) as sample_video_frames:
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            fine_step=0.5,
        )

    assert sample_video_frames.call_args_list[0].kwargs["duration"] == 30.0
    assert result.offset == 9.0
    assert result.best.offset == 9.0


def test_get_video_offset_reports_none_for_insufficient_matches():
    """Test video offset search rejects insufficient support."""
    reference_samples = _get_samples([0.0], [10])
    target_samples = _get_samples([1.0], [10])

    with (
        patch(
            "scinoephile.core.media.video_offset._sample_video_frames",
            side_effect=[reference_samples, target_samples],
        ),
        pytest.raises(ScinoephileError, match="Could not find enough"),
    ):
        get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            fine_step=0.5,
        )


def test_get_video_offset_uses_separate_second_best_for_confidence():
    """Test confidence ignores immediately adjacent candidate offsets."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with patch(
        "scinoephile.core.media.video_offset._sample_video_frames",
        side_effect=[reference_samples, target_samples],
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            fine_step=0.5,
        )

    assert result.offset == 1.0
    assert result.second_best is not None
    assert abs(result.second_best.offset - result.offset) >= 1.0


@pytest.mark.parametrize(
    ("parameter_name", "message"),
    [
        ("max_offset", "max_offset must be positive"),
        ("sample_rate", "sample_rate must be positive"),
        ("coarse_step", "coarse_step must be positive"),
        ("fine_step", "fine_step must be positive"),
        ("width", "width must be positive"),
        ("height", "height must be positive"),
    ],
)
def test_get_video_offset_rejects_invalid_numeric_parameters(
    parameter_name: str,
    message: str,
):
    """Test video offset rejects invalid numeric parameters.

    Arguments:
        parameter_name: invalid parameter name
        message: expected error message
    """
    with pytest.raises(ValueError, match=message):
        if parameter_name == "max_offset":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                max_offset=0.0,
            )
        elif parameter_name == "sample_rate":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                sample_rate=0.0,
            )
        elif parameter_name == "coarse_step":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                coarse_step=0.0,
            )
        elif parameter_name == "fine_step":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                fine_step=0.0,
            )
        elif parameter_name == "width":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                width=0,
            )
        elif parameter_name == "height":
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                height=0,
            )


def test_get_video_offset_wraps_sampling_failures():
    """Test sampling failures are reported as Scinoephile errors."""
    with patch(
        "scinoephile.core.media.video_offset._sample_video_frames",
        side_effect=ScinoephileError("Could not sample frames"),
    ):
        with pytest.raises(ScinoephileError, match="Could not sample frames"):
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
            )


def test_result_types_are_public_dataclasses():
    """Test result dataclasses expose expected fields."""
    best = VideoOffsetCandidate(offset=1.0, matched_count=3, score=0.5)
    second_best = VideoOffsetCandidate(offset=0.0, matched_count=3, score=5.0)
    result = VideoOffsetResult(
        offset=1.0,
        confidence="high",
        best=best,
        second_best=second_best,
    )

    assert result.best == best
    assert result.second_best == second_best


def _get_sample(time: float, frame: np.ndarray) -> SimpleNamespace:
    """Return a synthetic frame sample.

    Arguments:
        time: sample time
        frame: frame value
    Returns:
        synthetic frame sample
    """
    return SimpleNamespace(time=time, frame=frame)


def _get_samples(times: list[float], values: list[int]) -> list[SimpleNamespace]:
    """Return synthetic frame samples.

    Arguments:
        times: sample times
        values: frame values
    Returns:
        synthetic frame samples
    """
    return [
        _get_sample(
            time=time,
            frame=np.full((2, 2), value, dtype=np.float32),
        )
        for time, value in zip(times, values, strict=True)
    ]
