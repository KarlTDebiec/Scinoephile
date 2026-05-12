#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of video offset detection."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from scinoephile.core import ScinoephileError
from scinoephile.media.video_offset import (
    VideoOffsetResult,
    _get_offsets,
    _sample_video_frames,
    get_video_offset,
)


def test_get_video_offset_prefers_known_shift():
    """Test video offset search prefers a known shifted sequence."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with patch(
        "scinoephile.media.video_offset._sample_video_frames",
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
        "scinoephile.media.video_offset._sample_video_frames",
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


def test_get_video_offset_rejects_insufficient_matches():
    """Test video offset search rejects insufficient support."""
    reference_samples = _get_samples([0.0], [10])
    target_samples = _get_samples([1.0], [10])

    with (
        patch(
            "scinoephile.media.video_offset._sample_video_frames",
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
        "scinoephile.media.video_offset._sample_video_frames",
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


def test_get_offsets_clamps_to_requested_end():
    """Test candidate offsets do not exceed the requested end."""
    offsets = _get_offsets(-1.0, 1.0, 0.7)

    assert offsets == [-1.0, -0.3, 0.4, 1.0]
    assert max(offsets) == 1.0


def test_sample_video_frames_normalizes_brightness():
    """Test sampled video frames normalize brightness during sampling."""
    output = np.array(
        [
            [[0, 1], [2, 3]],
            [[10, 12], [14, 16]],
        ],
        dtype=np.uint8,
    ).tobytes()

    with patch(
        "scinoephile.media.video_offset.ffmpeg.input",
    ) as input_:
        input_.return_value.filter.return_value.filter.return_value.filter.return_value.output.return_value.run.return_value = (  # noqa: E501
            output,
            b"",
        )
        samples = _sample_video_frames(
            Path("video.mkv"),
            sample_rate=1.0,
            start_time=0.0,
            duration=2.0,
            width=2,
            height=2,
        )

    assert samples[0].frame.mean() == pytest.approx(0.0)
    assert samples[0].frame.std() == pytest.approx(1.0)
    assert samples[1].frame.mean() == pytest.approx(0.0)
    assert samples[1].frame.std() == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                max_offset=0.0,
            ),
            "0.0 is less than minimum value",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                sample_rate=0.0,
            ),
            "0.0 is less than minimum value",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                start_time=-1.0,
            ),
            "-1.0 is less than minimum value of 0.0",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                coarse_step=0.0,
            ),
            "0.0 is less than minimum value",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                fine_step=0.0,
            ),
            "0.0 is less than minimum value",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                width=0,
            ),
            "0 is less than minimum value of 1",
        ),
        (
            lambda: get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                height=0,
            ),
            "0 is less than minimum value of 1",
        ),
    ],
)
def test_get_video_offset_rejects_invalid_numeric_parameters(
    call: Callable[[], VideoOffsetResult],
    message: str,
):
    """Test video offset rejects invalid numeric parameters.

    Arguments:
        call: call with invalid arguments
        message: expected error message
    """
    with pytest.raises(ValueError, match=message):
        call()


def test_get_video_offset_propagates_sampling_failures():
    """Test sampling failures are propagated as Scinoephile errors."""
    with patch(
        "scinoephile.media.video_offset._sample_video_frames",
        side_effect=ScinoephileError("Could not sample frames"),
    ):
        with pytest.raises(ScinoephileError, match="Could not sample frames"):
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
            )


def _get_sample(time: float, frame: np.ndarray) -> SimpleNamespace:
    """Return a synthetic frame sample.

    Arguments:
        time: sample time
        frame: frame value
    Returns:
        synthetic frame sample
    """
    frame_std = float(np.std(frame))
    if frame_std > 0:
        frame = (frame - float(np.mean(frame))) / frame_std
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
