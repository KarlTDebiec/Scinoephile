#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video offset detection from sampled frame comparisons."""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

import ffmpeg
import numpy as np

from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "VideoOffsetCandidate",
    "VideoOffsetResult",
    "get_video_offset",
]

logger = getLogger(__name__)


@dataclass(frozen=True)
class _VideoFrameSample:
    """Sampled video frame at a timestamp."""

    time: float
    """Timestamp of the sampled frame in seconds."""

    frame: np.ndarray
    """Normalized grayscale frame data."""


@dataclass(frozen=True)
class VideoOffsetCandidate:
    """Score for one candidate video offset."""

    offset: float
    """Target timestamp minus reference timestamp in seconds."""

    matched_count: int
    """Number of reference samples matched against target samples."""

    score: float
    """Aggregate frame difference score; lower values are better."""


@dataclass(frozen=True)
class VideoOffsetResult:
    """Best visual offset estimate between two videos."""

    offset: float
    """Estimated target timestamp minus reference timestamp in seconds."""

    confidence: str
    """Confidence label for the estimate."""

    best: VideoOffsetCandidate
    """Best-scoring candidate offset."""

    second_best: VideoOffsetCandidate | None
    """Second-best candidate offset, if available."""


def get_video_offset(
    *,
    reference_infile_path: Path,
    target_infile_path: Path,
    max_offset: float = 10.0,
    sample_rate: float = 2.0,
    start_time: float = 0.0,
    duration: float = 300.0,
    coarse_step: float = 0.25,
    fine_step: float = 0.04,
    width: int = 160,
    height: int = 90,
) -> VideoOffsetResult:
    """Estimate the constant visual offset between two video files.

    Arguments:
        reference_infile_path: reference media input path
        target_infile_path: target media input path
        max_offset: maximum absolute offset to search, in seconds
        sample_rate: frame sample rate in samples per second
        start_time: media timestamp at which sampling starts, in seconds
        duration: sampled window duration in seconds
        coarse_step: coarse search step in seconds
        fine_step: fine search step in seconds
        width: sampled frame width in pixels
        height: sampled frame height in pixels
    Returns:
        estimated visual offset result
    Raises:
        ValueError: if numeric parameters are invalid
        ScinoephileError: if frames cannot be sampled or scored
    """
    _validate_positive("max_offset", max_offset)
    _validate_positive("sample_rate", sample_rate)
    _validate_nonnegative("start_time", start_time)
    _validate_positive("duration", duration)
    _validate_positive("coarse_step", coarse_step)
    _validate_positive("fine_step", fine_step)
    _validate_positive("width", width)
    _validate_positive("height", height)

    reference_samples = _sample_video_frames(
        reference_infile_path,
        sample_rate=sample_rate,
        start_time=start_time,
        duration=duration,
        width=width,
        height=height,
    )
    target_samples = _sample_video_frames(
        target_infile_path,
        sample_rate=sample_rate,
        start_time=start_time,
        duration=duration,
        width=width,
        height=height,
    )

    min_matches = max(2, int(sample_rate * 2))
    coarse_offsets = _get_offsets(-max_offset, max_offset, coarse_step)
    coarse_candidates = _score_offsets(
        reference_samples,
        target_samples,
        offsets=coarse_offsets,
        sample_rate=sample_rate,
        min_matches=min_matches,
    )
    if not coarse_candidates:
        raise ScinoephileError("Could not find enough matching video samples")

    best_coarse = coarse_candidates[0]
    fine_start = max(-max_offset, best_coarse.offset - coarse_step)
    fine_end = min(max_offset, best_coarse.offset + coarse_step)
    fine_offsets = _get_offsets(fine_start, fine_end, fine_step)
    candidates = _score_offsets(
        reference_samples,
        target_samples,
        offsets=fine_offsets,
        sample_rate=sample_rate,
        min_matches=min_matches,
    )
    if not candidates:
        candidates = coarse_candidates

    best = candidates[0]
    second_best = _get_second_best(
        candidates, best, minimum_offset_distance=coarse_step
    )

    confidence = _classify_confidence(
        best=best,
        second_best=second_best,
        min_matches=min_matches,
    )
    return VideoOffsetResult(
        offset=best.offset,
        confidence=confidence,
        best=best,
        second_best=second_best,
    )


def _classify_confidence(
    *,
    best: VideoOffsetCandidate,
    second_best: VideoOffsetCandidate | None,
    min_matches: int,
) -> str:
    """Classify offset confidence from match count and score separation.

    Arguments:
        best: best offset candidate
        second_best: next-best offset candidate, if available
        min_matches: minimum required match count
    Returns:
        confidence label
    """
    confidence = "low"
    if best.matched_count < min_matches:
        confidence = "none"
    elif second_best is None:
        confidence = "low"
    elif best.score <= 0:
        if second_best.score > 0:
            confidence = "high"
    else:
        ratio = second_best.score / best.score
        if ratio >= 4.0:
            confidence = "high"
        elif ratio >= 2.0:
            confidence = "medium"
    return confidence


def _get_offsets(start: float, end: float, step: float) -> list[float]:
    """Return inclusive candidate offsets.

    Arguments:
        start: first offset
        end: last offset
        step: offset interval
    Returns:
        candidate offsets
    """
    count = int(round((end - start) / step))
    offsets = []
    for index in range(count + 1):
        offset = start + index * step
        offsets.append(round(offset, 6))
    if offsets[-1] < end:
        offsets.append(round(end, 6))
    return offsets


def _get_second_best(
    candidates: list[VideoOffsetCandidate],
    best: VideoOffsetCandidate,
    minimum_offset_distance: float,
) -> VideoOffsetCandidate | None:
    """Return the best candidate outside a minimum distance of the winner.

    Arguments:
        candidates: sorted candidates
        best: best candidate
        minimum_offset_distance: minimum offset distance from the winner
    Returns:
        second-best candidate
    """
    for candidate in candidates:
        if abs(candidate.offset - best.offset) >= minimum_offset_distance:
            return candidate
    return None


def _sample_video_frames(
    infile_path: Path,
    *,
    sample_rate: float,
    start_time: float,
    duration: float,
    width: int,
    height: int,
) -> list[_VideoFrameSample]:
    """Sample grayscale frames from a video file.

    Arguments:
        infile_path: media input path
        sample_rate: samples per second
        start_time: media timestamp at which sampling starts, in seconds
        duration: sampled window duration in seconds
        width: output frame width
        height: output frame height
    Returns:
        sampled video frames
    Raises:
        ScinoephileError: if ffmpeg fails or no frames are sampled
    """
    frame_size = width * height
    input_kwargs = {}
    if start_time > 0:
        input_kwargs["ss"] = start_time
    if duration > 0:
        input_kwargs["t"] = duration
    try:
        output, _ = (
            ffmpeg.input(str(infile_path), **input_kwargs)
            .filter("fps", fps=sample_rate)
            .filter("scale", width, height)
            .filter("format", "gray")
            .output("pipe:", format="rawvideo", pix_fmt="gray")
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as exc:
        raise ScinoephileError(
            f"Could not sample video frames from {infile_path}"
        ) from exc

    if len(output) < frame_size:
        raise ScinoephileError(f"No video frames sampled from {infile_path}")
    if len(output) % frame_size != 0:
        logger.warning(
            f"Truncating partial sampled video frame from {infile_path}: "
            f"{len(output) % frame_size} trailing bytes"
        )

    frame_count = len(output) // frame_size
    array = np.frombuffer(output[: frame_count * frame_size], dtype=np.uint8)
    array = array.reshape((frame_count, height, width)).astype(np.float32)

    return [
        _VideoFrameSample(time=index / sample_rate, frame=array[index])
        for index in range(frame_count)
    ]


def _score_offset(
    reference_samples: list[_VideoFrameSample],
    target_samples: list[_VideoFrameSample],
    *,
    offset: float,
    sample_rate: float,
    min_matches: int,
) -> VideoOffsetCandidate | None:
    """Score one candidate offset.

    Arguments:
        reference_samples: reference video samples
        target_samples: target video samples
        offset: target timestamp minus reference timestamp
        sample_rate: samples per second
        min_matches: minimum required match count
    Returns:
        scored offset if enough samples matched
    """
    tolerance = 0.49 / sample_rate
    target_times = [sample.time for sample in target_samples]
    scores = []

    for reference_sample in reference_samples:
        target_time = reference_sample.time + offset
        target_sample = _get_nearest_sample(
            target_samples, target_times, target_time, tolerance
        )
        if target_sample is None:
            continue

        score = _get_frame_difference(reference_sample.frame, target_sample.frame)
        scores.append(score)

    if len(scores) < min_matches:
        return None

    aggregate_score = float(np.median(np.array(scores, dtype=np.float32)))
    return VideoOffsetCandidate(
        offset=offset,
        matched_count=len(scores),
        score=aggregate_score,
    )


def _score_offsets(
    reference_samples: list[_VideoFrameSample],
    target_samples: list[_VideoFrameSample],
    *,
    offsets: list[float],
    sample_rate: float,
    min_matches: int,
) -> list[VideoOffsetCandidate]:
    """Score candidate offsets.

    Arguments:
        reference_samples: reference video samples
        target_samples: target video samples
        offsets: candidate offsets
        sample_rate: samples per second
        min_matches: minimum required match count
    Returns:
        sorted candidate scores
    """
    candidates = []
    for offset in offsets:
        scored = _score_offset(
            reference_samples,
            target_samples,
            offset=offset,
            sample_rate=sample_rate,
            min_matches=min_matches,
        )
        if scored is not None:
            candidates.append(scored)
    return sorted(candidates, key=lambda candidate: candidate.score)


def _get_frame_difference(
    reference_frame: np.ndarray, target_frame: np.ndarray
) -> float:
    """Return normalized difference between two grayscale frames.

    Arguments:
        reference_frame: reference grayscale frame
        target_frame: target grayscale frame
    Returns:
        frame difference score
    """
    reference_std = float(np.std(reference_frame))
    target_std = float(np.std(target_frame))
    if reference_std > 0 and target_std > 0:
        reference_frame = (
            reference_frame - float(np.mean(reference_frame))
        ) / reference_std
        target_frame = (target_frame - float(np.mean(target_frame))) / target_std
    return float(np.mean(np.abs(reference_frame - target_frame)))


def _get_nearest_sample(
    samples: list[_VideoFrameSample],
    sample_times: list[float],
    time: float,
    tolerance: float,
) -> _VideoFrameSample | None:
    """Return the nearest sample within tolerance.

    Arguments:
        samples: ordered samples
        sample_times: ordered sample timestamps
        time: desired timestamp
        tolerance: maximum allowed timestamp difference
    Returns:
        nearest sample, if one is close enough
    """
    best_index = None
    best_delta = tolerance
    insertion_index = bisect_left(sample_times, time)
    for index in [insertion_index - 1, insertion_index]:
        if index < 0 or index >= len(samples):
            continue
        delta = abs(sample_times[index] - time)
        if delta <= best_delta:
            best_delta = delta
            best_index = index
    if best_index is None:
        return None
    return samples[best_index]


def _validate_positive(name: str, value: float | int):
    """Validate that a numeric value is positive.

    Arguments:
        name: value name for error messages
        value: numeric value
    Raises:
        ValueError: if value is not positive
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _validate_nonnegative(name: str, value: float | int):
    """Validate that a numeric value is nonnegative.

    Arguments:
        name: value name for error messages
        value: numeric value
    Raises:
        ValueError: if value is negative
    """
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
