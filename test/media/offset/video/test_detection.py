#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of video offset detection operations."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypedDict
from unittest.mock import patch

import numpy as np
from pytest import approx, raises

from scinoephile.common.subprocess import run_command
from scinoephile.core import ScinoephileError
from scinoephile.media.offset.video.detection import (
    _get_offsets,
    _sample_video_frames,
    get_video_offset,
)
from test.helpers import parametrize


class _VideoOffsetKwargs(TypedDict, total=False):
    """Keyword arguments for video offset detection."""

    max_offset: float
    sample_rate: float
    coarse_step: float
    sample_windows: int
    width: int
    height: int


def test_get_video_offset_prefers_known_shift():
    """Test video offset search prefers a known shifted sequence."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[_get_probe(), _get_probe()],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=[reference_samples, target_samples],
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            sample_windows=1,
        )

    assert result.offset == 1.0
    assert result.offset_frames == 1
    assert result.best.matched_count == 4


def test_get_video_offset_uses_reference_frame_grid_for_fine_search():
    """Test fine video offset search uses reference frame-grid candidates."""
    frame_duration = float(Fraction(1001, 24000))
    reference_samples = _get_samples(
        [frame * frame_duration for frame in range(100, 160)],
        list(range(60)),
    )
    target_samples = _get_samples(
        [(frame - 20) * frame_duration for frame in range(100, 160)],
        list(range(60)),
    )

    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[
                _get_probe(frame_rate="24000/1001"),
                _get_probe(frame_rate="24000/1001"),
            ],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=[reference_samples, target_samples],
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=24.0,
            duration=3.0,
            coarse_step=0.25,
            sample_windows=1,
        )

    assert result.offset == approx(-20 * frame_duration)
    assert result.offset_frames == -20
    assert result.best.offset_frames == -20


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

    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[_get_probe(), _get_probe()],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=[reference_samples, target_samples],
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            sample_windows=1,
        )

    assert result.offset == 1.0
    assert result.best.score == approx(0.0)


def test_get_video_offset_rejects_insufficient_matches():
    """Test video offset search rejects insufficient support."""
    reference_samples = _get_samples([0.0], [10])
    target_samples = _get_samples([1.0], [10])

    with raises(ScinoephileError, match="Could not find enough"):
        with (
            patch(
                "scinoephile.media.offset.video.detection.ffmpeg.probe",
                side_effect=[_get_probe(), _get_probe()],
            ),
            patch(
                "scinoephile.media.offset.video.detection._sample_video_frames",
                side_effect=[reference_samples, target_samples],
            ),
        ):
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                max_offset=2.0,
                sample_rate=1.0,
                duration=30.0,
                coarse_step=1.0,
                sample_windows=1,
            )


def test_get_video_offset_rejects_missing_reference_frame_rate():
    """Test video offset search requires a usable reference frame rate."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with raises(ScinoephileError, match="reference video frame rate"):
        with (
            patch(
                "scinoephile.media.offset.video.detection.ffmpeg.probe",
                side_effect=[
                    _get_probe(frame_rate="0/0"),
                    _get_probe(frame_rate="24/1"),
                ],
            ),
            patch(
                "scinoephile.media.offset.video.detection._sample_video_frames",
                side_effect=[reference_samples, target_samples],
            ),
        ):
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                sample_rate=1.0,
                duration=30.0,
                sample_windows=1,
            )


def test_get_video_offset_samples_multiple_windows_and_aggregates_frames():
    """Test automatic windows aggregate video offsets in reference frames."""
    frame_duration = 1 / 24
    side_effect = []
    for offset_frames in [-20, -20, -21]:
        reference_samples, target_samples = _get_shifted_sample_pair(
            offset_frames=offset_frames,
            frame_duration=frame_duration,
        )
        side_effect.extend([reference_samples, target_samples])

    sampler = _RecordingVideoSampler(side_effect)
    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[
                _get_probe(duration=100.0, frame_rate="24/1"),
                _get_probe(duration=100.0, frame_rate="24/1"),
            ],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            new=sampler,
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=24.0,
            duration=10.0,
            coarse_step=0.25,
            sample_windows=3,
        )

    assert [call["start_time"] for call in sampler.calls] == [
        9.0,
        9.0,
        45.0,
        45.0,
        81.0,
        81.0,
    ]
    assert [window.offset_frames for window in result.windows] == [-20, -20, -21]
    assert result.aggregate is not None
    assert result.offset_frames == -20
    assert result.aggregate.mean_frames == approx(-20.333333)
    assert result.aggregate.median_frames == -20
    assert result.aggregate.min_frames == -21
    assert result.aggregate.max_frames == -20
    assert result.aggregate.agreeing_count == 2
    assert result.aggregate.total_count == 3


def test_get_video_offset_clamps_duration_to_shared_runtime():
    """Test video offset samples short videos without manual duration override."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])

    sampler = _RecordingVideoSampler([reference_samples, target_samples])
    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[
                _get_probe(duration=20.0),
                _get_probe(duration=20.0),
            ],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            new=sampler,
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            sample_rate=1.0,
            coarse_step=1.0,
        )

    assert result.offset_frames == 0
    assert [call["start_time"] for call in sampler.calls] == [
        0.0,
        0.0,
    ]
    assert [call["duration"] for call in sampler.calls] == [
        20.0,
        20.0,
    ]


def test_get_video_offset_handles_aggregate_without_exact_window_match():
    """Test aggregate output handles median offsets no window reported."""
    frame_duration = 1 / 24
    side_effect = []
    for offset_frames in [0, 1, 3, 4]:
        reference_samples, target_samples = _get_shifted_sample_pair(
            offset_frames=offset_frames,
            frame_duration=frame_duration,
        )
        side_effect.extend([reference_samples, target_samples])

    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[
                _get_probe(duration=100.0, frame_rate="24/1"),
                _get_probe(duration=100.0, frame_rate="24/1"),
            ],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=side_effect,
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=1.0,
            sample_rate=24.0,
            duration=10.0,
            coarse_step=0.25,
            sample_windows=4,
        )

    assert [window.offset_frames for window in result.windows] == [0, 1, 3, 4]
    assert result.aggregate is not None
    assert result.offset_frames == 2
    assert result.aggregate.agreeing_count == 0
    assert result.confidence == "low"
    assert result.best.offset_frames in {1, 3}


def test_get_video_offset_uses_separate_second_best_for_confidence():
    """Test confidence ignores immediately adjacent candidate offsets."""
    reference_samples = _get_samples([0.0, 1.0, 2.0, 3.0], [10, 20, 30, 40])
    target_samples = _get_samples([1.0, 2.0, 3.0, 4.0], [10, 20, 30, 40])

    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[_get_probe(), _get_probe()],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=[reference_samples, target_samples],
        ),
    ):
        result = get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            max_offset=2.0,
            sample_rate=1.0,
            duration=30.0,
            coarse_step=1.0,
            sample_windows=1,
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
        "scinoephile.media.offset.video.detection.ffmpeg.input",
        return_value=_FakeFfmpegInput(output),
    ):
        samples = _sample_video_frames(
            Path("video.mkv"),
            sample_rate=1.0,
            start_time=0.0,
            duration=2.0,
            width=2,
            height=2,
        )

    assert samples[0].frame.mean() == approx(0.0)
    assert samples[0].frame.std() == approx(1.0)
    assert samples[1].frame.mean() == approx(0.0)
    assert samples[1].frame.std() == approx(1.0)


@parametrize(
    ("kwargs", "message"),
    [
        (
            {"max_offset": 0.0},
            "0.0 is less than minimum value",
        ),
        (
            {"sample_rate": 0.0},
            "0.0 is less than minimum value",
        ),
        (
            {"coarse_step": 0.0},
            "0.0 is less than minimum value",
        ),
        (
            {"sample_windows": 0},
            "0 is less than minimum value of 1",
        ),
        (
            {"width": 0},
            "0 is less than minimum value of 1",
        ),
        (
            {"height": 0},
            "0 is less than minimum value of 1",
        ),
    ],
)
def test_get_video_offset_rejects_invalid_numeric_parameters(
    kwargs: _VideoOffsetKwargs,
    message: str,
):
    """Test video offset rejects invalid numeric parameters.

    Arguments:
        kwargs: invalid keyword arguments
        message: expected error message
    """
    with raises(ValueError, match=message):
        get_video_offset(
            reference_infile_path=Path("reference.mkv"),
            target_infile_path=Path("target.mkv"),
            **kwargs,
        )


def test_get_video_offset_propagates_sampling_failures():
    """Test sampling failures are propagated as Scinoephile errors."""
    with (
        patch(
            "scinoephile.media.offset.video.detection.ffmpeg.probe",
            side_effect=[_get_probe(), _get_probe()],
        ),
        patch(
            "scinoephile.media.offset.video.detection._sample_video_frames",
            side_effect=ScinoephileError("Could not sample frames"),
        ),
    ):
        with raises(ScinoephileError, match="Could not sample frames"):
            get_video_offset(
                reference_infile_path=Path("reference.mkv"),
                target_infile_path=Path("target.mkv"),
                duration=30.0,
                sample_windows=1,
            )


def test_video_offset_package_imports_detection_only_when_needed():
    """Test importing video offset result types does not import detection."""
    exitcode, _, _ = run_command(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.media.offset.video;"
                "raise SystemExit("
                "'scinoephile.media.offset.video.detection' in sys.modules)"
            ),
        ],
    )

    assert exitcode == 0


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


class _FakeFfmpegInput:
    """Fake ffmpeg input chain returning fixed raw video bytes."""

    def __init__(self, output: bytes):
        """Initialize.

        Arguments:
            output: raw video output bytes
        """
        self.output_bytes = output

    def filter(self, *args: object, **kwargs: object) -> _FakeFfmpegInput:
        """Return self for chained ffmpeg filters.

        Arguments:
            args: positional filter arguments
            kwargs: keyword filter arguments
        Returns:
            self
        """
        return self

    def output(self, *args: object, **kwargs: object) -> _FakeFfmpegInput:
        """Return self for chained ffmpeg output configuration.

        Arguments:
            args: positional output arguments
            kwargs: keyword output arguments
        Returns:
            self
        """
        return self

    def run(self, **kwargs: object) -> tuple[bytes, bytes]:
        """Return fixed raw video bytes.

        Arguments:
            kwargs: ffmpeg run options
        Returns:
            raw stdout and empty stderr
        """
        return self.output_bytes, b""


def _get_probe(
    *,
    duration: float = 100.0,
    frame_rate: str = "1/1",
) -> dict[str, object]:
    """Return synthetic ffprobe output.

    Arguments:
        duration: video duration in seconds
        frame_rate: probed video frame rate
    Returns:
        synthetic ffprobe output
    """
    return {
        "streams": [
            {
                "codec_type": "video",
                "avg_frame_rate": frame_rate,
                "duration": str(duration),
            }
        ],
        "format": {"duration": str(duration)},
    }


class _RecordingVideoSampler:
    """Recording fake for sampled video frames."""

    def __init__(self, outputs: list[list[SimpleNamespace]]):
        """Initialize.

        Arguments:
            outputs: sampled frame outputs to return in call order
        """
        self.calls: list[dict[str, Any]] = []
        self.outputs = list(outputs)

    def __call__(
        self,
        infile_path: Path,
        *,
        sample_rate: float,
        start_time: float,
        duration: float,
        width: int,
        height: int,
    ) -> list[SimpleNamespace]:
        """Record a sampling call and return the next configured output.

        Arguments:
            infile_path: media input path
            sample_rate: samples per second
            start_time: sample start timestamp
            duration: sample duration
            width: sampled frame width
            height: sampled frame height
        Returns:
            configured sampled frames
        """
        self.calls.append(
            {
                "infile_path": infile_path,
                "sample_rate": sample_rate,
                "start_time": start_time,
                "duration": duration,
                "width": width,
                "height": height,
            }
        )
        return self.outputs.pop(0)


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


def _get_shifted_sample_pair(
    *,
    offset_frames: int,
    frame_duration: float,
) -> tuple[list[SimpleNamespace], list[SimpleNamespace]]:
    """Return synthetic reference and shifted target samples.

    Arguments:
        offset_frames: target frame offset
        frame_duration: reference frame duration in seconds
    Returns:
        reference and target frame samples
    """
    frame_numbers = list(range(100, 160))
    values = list(range(60))
    reference_samples = _get_samples(
        [frame * frame_duration for frame in frame_numbers],
        values,
    )
    target_samples = _get_samples(
        [(frame + offset_frames) * frame_duration for frame in frame_numbers],
        values,
    )
    return reference_samples, target_samples
