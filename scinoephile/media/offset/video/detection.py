#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video offset detection from sampled frame comparisons.

This module contains logic adapted from `vs_align` by pifroggi:
https://github.com/pifroggi/vs_align

See `docs/THIRD_PARTY_NOTICES.md` for license details.
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Mapping
from fractions import Fraction
from logging import getLogger
from math import ceil, floor, nextafter
from pathlib import Path
from statistics import mean, median, pstdev
from typing import cast

import ffmpeg
import numpy as np

from scinoephile.common.validation import val_float, val_int
from scinoephile.core.exceptions import ScinoephileError

from .video_frame_sample import VideoFrameSample
from .video_metadata import VideoMetadata
from .video_offset_aggregate import VideoOffsetAggregate
from .video_offset_candidate import VideoOffsetCandidate
from .video_offset_result import VideoOffsetResult
from .video_offset_window_result import VideoOffsetWindowResult

__all__ = ["get_video_offset"]

logger = getLogger(__name__)


def get_video_offset(
    *,
    reference_infile_path: Path,
    target_infile_path: Path,
    max_offset: float = 10.0,
    sample_rate: float = 2.0,
    duration: float = 300.0,
    coarse_step: float = 0.25,
    sample_windows: int = 4,
    width: int = 160,
    height: int = 90,
) -> VideoOffsetResult:
    """Estimate the constant visual offset between two video files.

    Arguments:
        reference_infile_path: reference media input path
        target_infile_path: target media input path
        max_offset: maximum absolute offset to search, in seconds
        sample_rate: frame sample rate in samples per second
        duration: sampled window duration in seconds
        coarse_step: coarse search step in seconds
        sample_windows: number of sampled windows
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
    duration = val_float(duration, min_value=positive_float_min)
    coarse_step = val_float(coarse_step, min_value=positive_float_min)
    sample_windows = val_int(sample_windows, min_value=1)
    width = val_int(width, min_value=1)
    height = val_int(height, min_value=1)

    # Probe metadata needed for frame-grid search and automatic windows
    reference_metadata = _probe_video_metadata(
        reference_infile_path,
        label="reference",
        require_frame_rate=True,
    )
    target_metadata = _probe_video_metadata(
        target_infile_path,
        label="target",
        require_frame_rate=False,
    )
    frame_rate = reference_metadata.frame_rate
    if frame_rate is None:
        raise ScinoephileError("Could not probe reference video frame rate")
    frame_duration = float(Fraction(1, 1) / frame_rate)
    duration = min(
        duration,
        reference_metadata.duration,
        target_metadata.duration,
    )
    start_times = _get_sample_window_starts(
        duration=duration,
        sample_windows=sample_windows,
        reference_duration=reference_metadata.duration,
        target_duration=target_metadata.duration,
    )

    # Run one independent visual search per sampled window
    window_results = tuple(
        _get_video_offset_window(
            reference_infile_path=reference_infile_path,
            target_infile_path=target_infile_path,
            max_offset=max_offset,
            sample_rate=sample_rate,
            start_time=window_start_time,
            duration=duration,
            coarse_step=coarse_step,
            frame_duration=frame_duration,
            width=width,
            height=height,
        )
        for window_start_time in start_times
    )

    if len(window_results) == 1:
        window = window_results[0]
        return VideoOffsetResult(
            offset=window.offset,
            confidence=window.confidence,
            best=window.best,
            second_best=window.second_best,
            offset_frames=window.offset_frames,
        )

    aggregate = _aggregate_window_results(
        window_results,
        frame_duration=frame_duration,
    )
    best_window = min(
        window_results,
        key=lambda window: (
            abs(window.offset_frames - aggregate.offset_frames),
            window.best.score,
        ),
    )
    return VideoOffsetResult(
        offset=aggregate.offset,
        confidence=_get_aggregate_confidence(window_results, aggregate),
        best=best_window.best,
        second_best=best_window.second_best,
        offset_frames=aggregate.offset_frames,
        windows=window_results,
        aggregate=aggregate,
    )


def _aggregate_window_results(
    windows: tuple[VideoOffsetWindowResult, ...],
    *,
    frame_duration: float,
) -> VideoOffsetAggregate:
    """Aggregate window results in reference frame units.

    Arguments:
        windows: per-window results
        frame_duration: reference frame duration in seconds
    Returns:
        aggregate result
    """
    offset_frames = [window.offset_frames for window in windows]
    if not offset_frames:
        raise ScinoephileError("Could not aggregate video offsets without frames")

    median_frames = int(round(median(offset_frames)))
    return VideoOffsetAggregate(
        offset=median_frames * frame_duration,
        offset_frames=median_frames,
        mean_frames=mean(offset_frames),
        median_frames=median_frames,
        stdev_frames=pstdev(offset_frames),
        min_frames=min(offset_frames),
        max_frames=max(offset_frames),
        agreeing_count=sum(
            offset_frame == median_frames for offset_frame in offset_frames
        ),
        total_count=len(offset_frames),
    )


def _get_aggregate_confidence(
    windows: tuple[VideoOffsetWindowResult, ...],
    aggregate: VideoOffsetAggregate,
) -> str:
    """Return aggregate confidence from window agreement.

    Arguments:
        windows: per-window results
        aggregate: aggregate result
    Returns:
        aggregate confidence label
    """
    if aggregate.agreeing_count == aggregate.total_count:
        if any(window.confidence == "high" for window in windows):
            return "high"
        return "medium"
    if aggregate.agreeing_count > aggregate.total_count / 2:
        return "medium"
    return "low"


def _get_candidate_confidence(
    *,
    best: VideoOffsetCandidate,
    second_best: VideoOffsetCandidate | None,
) -> str:
    """Classify confidence from match support and score separation.

    Arguments:
        best: best candidate
        second_best: second-best distinct candidate
    Returns:
        confidence label
    """
    if second_best is None:
        return "low"
    if best.score <= 0:
        if second_best.score > 0:
            return "high"
        return "low"

    ratio = second_best.score / best.score
    if ratio >= 4.0:
        return "high"
    if ratio >= 2.0:
        return "medium"
    return "low"


def _get_frame_grid_offsets(
    *,
    best_coarse_offset: float,
    coarse_step: float,
    max_offset: float,
    frame_duration: float,
) -> list[float]:
    """Return frame-grid fine offsets around a coarse winner.

    Arguments:
        best_coarse_offset: best coarse candidate offset in seconds
        coarse_step: coarse search step in seconds
        max_offset: maximum absolute offset to search in seconds
        frame_duration: reference frame duration in seconds
    Returns:
        frame-grid candidate offsets
    """
    fine_start = max(-max_offset, best_coarse_offset - coarse_step)
    fine_end = min(max_offset, best_coarse_offset + coarse_step)
    first_frame = ceil(fine_start / frame_duration)
    last_frame = floor(fine_end / frame_duration)
    return [
        round(frame * frame_duration, 9) for frame in range(first_frame, last_frame + 1)
    ]


def _get_sample_window_starts(
    *,
    duration: float,
    sample_windows: int,
    reference_duration: float,
    target_duration: float,
) -> list[float]:
    """Return sample window start times.

    Arguments:
        duration: per-window duration in seconds
        sample_windows: requested number of windows
        reference_duration: reference video duration in seconds
        target_duration: target video duration in seconds
    Returns:
        window start times in seconds
    """
    shared_duration = min(reference_duration, target_duration)
    duration = min(duration, shared_duration)
    max_start = shared_duration - duration
    if max_start <= 0 or sample_windows == 1:
        return [round(max_start / 2, 6)]

    start = 0.1 * max_start
    end = 0.9 * max_start
    step = (end - start) / (sample_windows - 1)
    return [round(start + step * index, 6) for index in range(sample_windows)]


def _get_video_offset_window(
    *,
    reference_infile_path: Path,
    target_infile_path: Path,
    max_offset: float,
    sample_rate: float,
    start_time: float,
    duration: float,
    coarse_step: float,
    frame_duration: float,
    width: int,
    height: int,
) -> VideoOffsetWindowResult:
    """Estimate video offset for one sample window.

    Arguments:
        reference_infile_path: reference media input path
        target_infile_path: target media input path
        max_offset: maximum absolute offset to search, in seconds
        sample_rate: frame sample rate in samples per second
        start_time: media timestamp at which sampling starts, in seconds
        duration: sampled window duration in seconds
        coarse_step: coarse search step in seconds
        frame_duration: reference frame duration in seconds
        width: sampled frame width in pixels
        height: sampled frame height in pixels
    Returns:
        window offset result
    """
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

    # Refine around the best coarse offset on the reference frame grid
    best_coarse = coarse_candidates[0]
    fine_offsets = _get_frame_grid_offsets(
        best_coarse_offset=best_coarse.offset,
        coarse_step=coarse_step,
        max_offset=max_offset,
        frame_duration=frame_duration,
    )
    candidates = _score_offsets(
        reference_samples,
        target_samples,
        offsets=fine_offsets,
        sample_rate=sample_rate,
        min_matches=min_matches,
        frame_duration=frame_duration,
    )
    if not candidates:
        raise ScinoephileError("Could not find enough matching video samples")

    # Find the best distinct comparison candidate
    best = candidates[0]
    offset_frames = best.offset_frames
    if offset_frames is None:
        raise ScinoephileError("Could not convert video offset to frames")
    second_best = None
    for candidate in candidates:
        if abs(candidate.offset - best.offset) >= coarse_step:
            second_best = candidate
            break

    return VideoOffsetWindowResult(
        start_time=start_time,
        offset=best.offset,
        confidence=_get_candidate_confidence(best=best, second_best=second_best),
        best=best,
        second_best=second_best,
        offset_frames=offset_frames,
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


def _probe_video_metadata(
    infile_path: Path,
    *,
    label: str,
    require_frame_rate: bool,
) -> VideoMetadata:
    """Probe video metadata needed for offset detection.

    Arguments:
        infile_path: media input path
        label: user-facing label for error messages
        require_frame_rate: whether frame rate is required
    Returns:
        probed video metadata
    Raises:
        ScinoephileError: if required metadata cannot be probed
    """
    try:
        probe = ffmpeg.probe(str(infile_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(f"Could not probe {label} video {infile_path}") from exc

    stream = _get_video_stream(probe)
    frame_rate = _get_frame_rate(stream)
    duration = _get_duration(stream)
    if duration is None:
        duration = _get_duration(probe.get("format"))

    if require_frame_rate and frame_rate is None:
        raise ScinoephileError(f"Could not probe {label} video frame rate")
    if duration is None:
        raise ScinoephileError(f"Could not probe {label} video duration")
    return VideoMetadata(duration=duration, frame_rate=frame_rate)


def _get_duration(data: object) -> float | None:
    """Return parsed duration from ffprobe data.

    Arguments:
        data: ffprobe stream or format data
    Returns:
        duration in seconds, if present and positive
    """
    if not isinstance(data, Mapping):
        return None
    data = cast("Mapping[str, object]", data)
    value = data.get("duration")
    if not isinstance(value, int | float | str):
        return None
    try:
        duration = float(value)
    except ValueError:
        return None
    if duration <= 0:
        return None
    return duration


def _get_frame_rate(stream: Mapping[str, object]) -> Fraction | None:
    """Return parsed frame rate from ffprobe stream data.

    Arguments:
        stream: ffprobe stream data
    Returns:
        frame rate, if present and positive
    """
    for key in ["avg_frame_rate", "r_frame_rate"]:
        value = stream.get(key)
        if not isinstance(value, int | float | str):
            continue
        try:
            frame_rate = Fraction(str(value))
        except (ValueError, ZeroDivisionError):
            continue
        if frame_rate > 0:
            return frame_rate
    return None


def _get_video_stream(probe: object) -> Mapping[str, object]:
    """Return first video stream from ffprobe output.

    Arguments:
        probe: ffprobe output
    Returns:
        first video stream
    Raises:
        ScinoephileError: if no video stream is present
    """
    if not isinstance(probe, Mapping):
        raise ScinoephileError("Could not find video stream")
    probe = cast("Mapping[str, object]", probe)
    streams = probe.get("streams")
    if not isinstance(streams, list):
        raise ScinoephileError("Could not find video stream")
    for stream in streams:
        if not isinstance(stream, Mapping):
            continue
        stream = cast("Mapping[str, object]", stream)
        if stream.get("codec_type") == "video":
            return stream
    raise ScinoephileError("Could not find video stream")


def _sample_video_frames(
    infile_path: Path,
    *,
    sample_rate: float,
    start_time: float,
    duration: float,
    width: int,
    height: int,
) -> list[VideoFrameSample]:
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
        VideoFrameSample(time=index / sample_rate, frame=array[index])
        for index in range(frame_count)
    ]


def _score_offsets(
    reference_samples: list[VideoFrameSample],
    target_samples: list[VideoFrameSample],
    *,
    offsets: list[float],
    sample_rate: float,
    min_matches: int,
    frame_duration: float | None = None,
) -> list[VideoOffsetCandidate]:
    """Score candidate offsets.

    Arguments:
        reference_samples: reference video samples
        target_samples: target video samples
        offsets: candidate offsets
        sample_rate: samples per second
        min_matches: minimum required match count
        frame_duration: reference frame duration in seconds
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
            offset_frames = None
            if frame_duration is not None:
                offset_frames = int(round(offset / frame_duration))
            candidates.append(
                VideoOffsetCandidate(
                    offset=offset,
                    matched_count=len(scores),
                    score=float(np.median(np.array(scores, dtype=np.float32))),
                    offset_frames=offset_frames,
                )
            )
    return sorted(candidates, key=lambda candidate: candidate.score)
