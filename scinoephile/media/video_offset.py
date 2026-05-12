#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video offset detection from sampled frame comparisons.

This module contains logic adapted from `vs_align` by pifroggi:
https://github.com/pifroggi/vs_align

See `docs/THIRD_PARTY_NOTICES.md` for license details.
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from logging import getLogger
from math import nextafter
from pathlib import Path

import ffmpeg
import numpy as np

from scinoephile.common.validation import val_float, val_int
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
    # Validate numeric search parameters
    positive_float_min = nextafter(0.0, 1.0)
    max_offset = val_float(max_offset, min_value=positive_float_min)
    sample_rate = val_float(sample_rate, min_value=positive_float_min)
    start_time = val_float(start_time, min_value=0.0)
    duration = val_float(duration, min_value=positive_float_min)
    coarse_step = val_float(coarse_step, min_value=positive_float_min)
    fine_step = val_float(fine_step, min_value=positive_float_min)
    width = val_int(width, min_value=1)
    height = val_int(height, min_value=1)

    # Sample comparable grayscale frames from both videos
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

    # Search the full offset range at coarse resolution
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

    # Refine around the best coarse offset
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

    # Find the best distinct fallback candidate
    best = candidates[0]
    second_best = None
    for candidate in candidates:
        if abs(candidate.offset - best.offset) >= coarse_step:
            second_best = candidate
            break

    # Classify confidence from match support and score separation
    confidence = "low"
    if second_best is None:
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

    return VideoOffsetResult(
        offset=best.offset,
        confidence=confidence,
        best=best,
        second_best=second_best,
    )


def _get_offsets(start: float, end: float, step: float) -> list[float]:
    """Return inclusive candidate offsets.

    Arguments:
        start: first offset
        end: last offset
        step: offset interval
    Returns:
        candidate offsets
    """
    offsets = []
    offset = start
    epsilon = step / 1_000_000
    while offset <= end + epsilon:
        offsets.append(round(offset, 6))
        offset += step
    if offsets[-1] > end:
        offsets[-1] = round(end, 6)
    elif offsets[-1] < end:
        offsets.append(round(end, 6))
    return offsets


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

    # Build ffmpeg input options for the requested sample window
    input_kwargs = {}
    if start_time > 0:
        input_kwargs["ss"] = start_time
    if duration > 0:
        input_kwargs["t"] = duration

    # Decode scaled grayscale frames as raw bytes
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

    # Reshape raw frame bytes into sample objects
    array = np.frombuffer(output[: frame_count * frame_size], dtype=np.uint8)
    array = array.reshape((frame_count, height, width)).astype(np.float32)

    # Normalize brightness once per sampled frame
    for index in range(frame_count):
        frame = array[index]
        frame_std = float(np.std(frame))
        if frame_std > 0:
            array[index] = (frame - float(np.mean(frame))) / frame_std

    return [
        _VideoFrameSample(time=index / sample_rate, frame=array[index])
        for index in range(frame_count)
    ]


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
    tolerance = 0.49 / sample_rate

    # Precompute target timestamps for nearest-frame lookup
    target_times = [sample.time for sample in target_samples]

    for offset in offsets:
        scores = []
        for reference_sample in reference_samples:
            # Match each reference sample to the nearest target sample
            target_time = reference_sample.time + offset
            best_index = None
            best_delta = tolerance
            insertion_index = bisect_left(target_times, target_time)
            for index in [insertion_index - 1, insertion_index]:
                if index < 0 or index >= len(target_samples):
                    continue
                delta = abs(target_times[index] - target_time)
                if delta <= best_delta:
                    best_delta = delta
                    best_index = index
            if best_index is None:
                continue

            target_sample = target_samples[best_index]
            reference_frame = reference_sample.frame
            target_frame = target_sample.frame
            scores.append(float(np.mean(np.abs(reference_frame - target_frame))))

        # Keep candidate offsets with enough matched samples
        if len(scores) >= min_matches:
            candidates.append(
                VideoOffsetCandidate(
                    offset=offset,
                    matched_count=len(scores),
                    score=float(np.median(np.array(scores, dtype=np.float32))),
                )
            )
    return sorted(candidates, key=lambda candidate: candidate.score)
