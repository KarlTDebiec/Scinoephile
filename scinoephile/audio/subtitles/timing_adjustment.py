#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Adjust subtitle timings using detected speech activity."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scinoephile.audio.speech_activity import (
    SpeechInterval,
    get_speech_intervals_cleaned,
    get_speech_overlap_duration,
)
from scinoephile.core.subtitles import Series

from .series import AudioSeries
from .subtitle import AudioSubtitle

if TYPE_CHECKING:
    from pydub import AudioSegment

__all__ = [
    "SubtitleTimingAdjustmentBlockDiagnostics",
    "SubtitleTimingAdjustmentConfig",
    "SubtitleTimingAdjustmentCueDiagnostics",
    "SubtitleTimingAdjustmentResult",
    "get_series_timing_adjusted",
    "get_series_timing_adjustment",
]


@dataclass(frozen=True)
class SubtitleTimingAdjustmentConfig:
    """Configuration for subtitle timing adjustment."""

    block_pause_length_ms: int = 3000
    """Pause length that separates subtitle blocks in milliseconds."""
    block_audio_buffer_ms: int = 2000
    """Audio buffer to include before and after each block in milliseconds."""
    max_start_expansion_ms: int = 750
    """Maximum amount by which a cue may move earlier in milliseconds."""
    max_end_expansion_ms: int = 1500
    """Maximum amount by which a cue may move later in milliseconds."""
    merge_gap_ms: int = 150
    """Merge speech intervals separated by at most this gap in milliseconds."""
    min_speech_duration_ms: int = 100
    """Discard speech intervals shorter than this duration in milliseconds."""

    def __post_init__(self):
        """Validate configuration."""
        values_by_name = {
            "block_pause_length_ms": self.block_pause_length_ms,
            "block_audio_buffer_ms": self.block_audio_buffer_ms,
            "max_start_expansion_ms": self.max_start_expansion_ms,
            "max_end_expansion_ms": self.max_end_expansion_ms,
            "merge_gap_ms": self.merge_gap_ms,
            "min_speech_duration_ms": self.min_speech_duration_ms,
        }
        for name, value in values_by_name.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True)
class SubtitleTimingAdjustmentCueDiagnostics:
    """Diagnostics for one subtitle cue timing adjustment."""

    cue_idx: int
    """Zero-based cue index within the full series."""
    text: str
    """Cue text."""
    original_start_ms: int
    """Original cue start in milliseconds."""
    original_end_ms: int
    """Original cue end in milliseconds."""
    adjusted_start_ms: int
    """Adjusted cue start in milliseconds."""
    adjusted_end_ms: int
    """Adjusted cue end in milliseconds."""
    speech_duration_ms: int
    """Total relevant speech duration in milliseconds."""
    speech_coverage_before_ms: int
    """Speech duration covered before adjustment in milliseconds."""
    speech_coverage_after_ms: int
    """Speech duration covered after adjustment in milliseconds."""
    silence_overhang_before_ms: int
    """Cue duration not covering speech before adjustment in milliseconds."""
    silence_overhang_after_ms: int
    """Cue duration not covering speech after adjustment in milliseconds."""
    start_delta_ms: int
    """Adjusted start minus original start in milliseconds."""
    end_delta_ms: int
    """Adjusted end minus original end in milliseconds."""
    blocked_start_expansion_ms: int
    """Start expansion blocked by previous cue boundary in milliseconds."""
    blocked_end_expansion_ms: int
    """End expansion blocked by next cue boundary in milliseconds."""
    unchanged: bool
    """Whether cue timing was unchanged."""


@dataclass(frozen=True)
class SubtitleTimingAdjustmentBlockDiagnostics:
    """Diagnostics for one adjusted subtitle block."""

    start_idx: int
    """Zero-based start cue index, inclusive."""
    end_idx: int
    """Zero-based end cue index, exclusive."""
    buffered_start_ms: int
    """Buffered block start in full-series time."""
    buffered_end_ms: int
    """Buffered block end in full-series time."""
    cues: list[SubtitleTimingAdjustmentCueDiagnostics]
    """Cue diagnostics for this block."""


@dataclass(frozen=True)
class SubtitleTimingAdjustmentResult:
    """Result of subtitle timing adjustment."""

    series: AudioSeries
    """Adjusted audio subtitle series."""
    blocks: list[SubtitleTimingAdjustmentBlockDiagnostics]
    """Block-level diagnostics."""

    @property
    def cues(self) -> list[SubtitleTimingAdjustmentCueDiagnostics]:
        """Cue-level diagnostics."""
        return [cue for block in self.blocks for cue in block.cues]


@dataclass(frozen=True)
class _SubtitleTimingAdjustmentBlockSpec:
    """Block timing specification for adjustment."""

    start_idx: int
    """Zero-based start cue index, inclusive."""
    end_idx: int
    """Zero-based end cue index, exclusive."""
    buffered_start_ms: int
    """Buffered block start in full-series time."""
    buffered_end_ms: int
    """Buffered block end in full-series time."""


def get_series_timing_adjusted(
    series: AudioSeries,
    *,
    speech_detector: Callable[[AudioSegment], Sequence[SpeechInterval]],
    config: SubtitleTimingAdjustmentConfig | None = None,
) -> AudioSeries:
    """Get a subtitle series with timings adjusted against speech.

    Arguments:
        series: audio subtitle series to adjust
        speech_detector: callable that detects speech intervals in block audio
        config: adjustment configuration
    Returns:
        adjusted audio subtitle series
    """
    return get_series_timing_adjustment(
        series,
        speech_detector=speech_detector,
        config=config,
    ).series


def get_series_timing_adjustment(
    series: AudioSeries,
    *,
    speech_detector: Callable[[AudioSegment], Sequence[SpeechInterval]],
    config: SubtitleTimingAdjustmentConfig | None = None,
) -> SubtitleTimingAdjustmentResult:
    """Get adjusted subtitle timings and diagnostics.

    Arguments:
        series: audio subtitle series to adjust
        speech_detector: callable that detects speech intervals in block audio
        config: adjustment configuration
    Returns:
        adjusted series and timing diagnostics
    """
    if config is None:
        config = SubtitleTimingAdjustmentConfig()

    adjusted_series = _get_series_copy(series)
    block_diagnostics: list[SubtitleTimingAdjustmentBlockDiagnostics] = []
    for block_spec in _get_block_specs(series, config=config):
        block_audio = series.audio[
            block_spec.buffered_start_ms : block_spec.buffered_end_ms
        ]
        speech_intervals = _get_block_speech_intervals(
            speech_detector(block_audio),
            block_spec=block_spec,
            config=config,
        )
        cue_diagnostics: list[SubtitleTimingAdjustmentCueDiagnostics] = []
        for cue_idx in range(block_spec.start_idx, block_spec.end_idx):
            cue_diagnostic = _adjust_event_timing(
                original_event=series.events[cue_idx],
                adjusted_event=adjusted_series.events[cue_idx],
                cue_idx=cue_idx,
                series=series,
                adjusted_series=adjusted_series,
                speech_intervals=speech_intervals,
                block_spec=block_spec,
                config=config,
            )
            cue_diagnostics.append(cue_diagnostic)

        block_diagnostics.append(
            SubtitleTimingAdjustmentBlockDiagnostics(
                start_idx=block_spec.start_idx,
                end_idx=block_spec.end_idx,
                buffered_start_ms=block_spec.buffered_start_ms,
                buffered_end_ms=block_spec.buffered_end_ms,
                cues=cue_diagnostics,
            )
        )

    return SubtitleTimingAdjustmentResult(
        series=adjusted_series,
        blocks=block_diagnostics,
    )


def _adjust_event_timing(
    *,
    original_event: AudioSubtitle,
    adjusted_event: AudioSubtitle,
    cue_idx: int,
    series: AudioSeries,
    adjusted_series: AudioSeries,
    speech_intervals: Sequence[SpeechInterval],
    block_spec: _SubtitleTimingAdjustmentBlockSpec,
    config: SubtitleTimingAdjustmentConfig,
) -> SubtitleTimingAdjustmentCueDiagnostics:
    """Adjust one event and return diagnostics.

    Arguments:
        original_event: event before adjustment
        adjusted_event: mutable event in the output series
        cue_idx: event index in the full series
        series: original full series
        adjusted_series: output full series
        speech_intervals: speech intervals in full-series time
        block_spec: block specification
        config: adjustment configuration
    Returns:
        cue-level timing diagnostics
    """
    relevant_start_ms = max(
        block_spec.buffered_start_ms,
        original_event.start - config.max_start_expansion_ms,
    )
    relevant_end_ms = min(
        block_spec.buffered_end_ms,
        original_event.end + config.max_end_expansion_ms,
    )
    relevant_intervals = _get_overlapping_intervals(
        speech_intervals,
        start_ms=relevant_start_ms,
        end_ms=relevant_end_ms,
    )

    desired_start_ms = original_event.start
    desired_end_ms = original_event.end
    if relevant_intervals:
        speech_start_ms = min(interval.start_ms for interval in relevant_intervals)
        speech_end_ms = max(interval.end_ms for interval in relevant_intervals)
        desired_end_ms = max(
            original_event.end,
            min(speech_end_ms, original_event.end + config.max_end_expansion_ms),
        )
        desired_start_ms = min(
            original_event.start,
            max(speech_start_ms, original_event.start - config.max_start_expansion_ms),
        )

    min_start_ms = _get_previous_event_boundary(cue_idx, adjusted_series)
    max_end_ms = _get_next_event_boundary(cue_idx, series)
    adjusted_start_ms = desired_start_ms
    adjusted_end_ms = desired_end_ms
    blocked_start_expansion_ms = 0
    blocked_end_expansion_ms = 0
    if adjusted_start_ms < min_start_ms:
        blocked_start_expansion_ms = min_start_ms - adjusted_start_ms
        adjusted_start_ms = min_start_ms
    if adjusted_end_ms > max_end_ms:
        blocked_end_expansion_ms = adjusted_end_ms - max_end_ms
        adjusted_end_ms = max_end_ms
    adjusted_end_ms = max(adjusted_end_ms, adjusted_start_ms)

    adjusted_event.start = adjusted_start_ms
    adjusted_event.end = adjusted_end_ms

    speech_duration_ms = sum(interval.duration_ms for interval in relevant_intervals)
    speech_coverage_before_ms = get_speech_overlap_duration(
        original_event.start,
        original_event.end,
        relevant_intervals,
    )
    speech_coverage_after_ms = get_speech_overlap_duration(
        adjusted_start_ms,
        adjusted_end_ms,
        relevant_intervals,
    )
    return SubtitleTimingAdjustmentCueDiagnostics(
        cue_idx=cue_idx,
        text=original_event.text,
        original_start_ms=original_event.start,
        original_end_ms=original_event.end,
        adjusted_start_ms=adjusted_start_ms,
        adjusted_end_ms=adjusted_end_ms,
        speech_duration_ms=speech_duration_ms,
        speech_coverage_before_ms=speech_coverage_before_ms,
        speech_coverage_after_ms=speech_coverage_after_ms,
        silence_overhang_before_ms=max(
            0,
            original_event.end - original_event.start - speech_coverage_before_ms,
        ),
        silence_overhang_after_ms=max(
            0,
            adjusted_end_ms - adjusted_start_ms - speech_coverage_after_ms,
        ),
        start_delta_ms=adjusted_start_ms - original_event.start,
        end_delta_ms=adjusted_end_ms - original_event.end,
        blocked_start_expansion_ms=blocked_start_expansion_ms,
        blocked_end_expansion_ms=blocked_end_expansion_ms,
        unchanged=(
            adjusted_start_ms == original_event.start
            and adjusted_end_ms == original_event.end
        ),
    )


def _get_block_specs(
    series: AudioSeries,
    *,
    config: SubtitleTimingAdjustmentConfig,
) -> list[_SubtitleTimingAdjustmentBlockSpec]:
    """Get block specs for a series.

    Arguments:
        series: audio subtitle series
        config: adjustment configuration
    Returns:
        block specifications
    """
    block_indexes = Series.get_block_indexes_by_pause(
        series,
        pause_length=config.block_pause_length_ms,
    )
    block_specs: list[_SubtitleTimingAdjustmentBlockSpec] = []
    for block_idx, (start_idx, end_idx) in enumerate(block_indexes):
        block_start_ms = series.events[start_idx].start
        block_end_ms = series.events[end_idx - 1].end

        if block_idx == 0:
            buffered_start_ms = max(0, block_start_ms - config.block_audio_buffer_ms)
        else:
            previous_end_idx = block_indexes[block_idx - 1][1] - 1
            previous_end_ms = series.events[previous_end_idx].end
            midpoint_ms = (previous_end_ms + block_start_ms) // 2
            buffered_start_ms = max(
                midpoint_ms,
                block_start_ms - config.block_audio_buffer_ms,
            )

        if block_idx < len(block_indexes) - 1:
            next_start_idx = block_indexes[block_idx + 1][0]
            next_start_ms = series.events[next_start_idx].start
            midpoint_ms = (block_end_ms + next_start_ms) // 2
            buffered_end_ms = min(
                block_end_ms + config.block_audio_buffer_ms,
                midpoint_ms,
            )
        else:
            buffered_end_ms = min(
                len(series.audio),
                block_end_ms + config.block_audio_buffer_ms,
            )

        block_specs.append(
            _SubtitleTimingAdjustmentBlockSpec(
                start_idx=start_idx,
                end_idx=end_idx,
                buffered_start_ms=buffered_start_ms,
                buffered_end_ms=buffered_end_ms,
            )
        )

    return block_specs


def _get_block_speech_intervals(
    intervals: Sequence[SpeechInterval],
    *,
    block_spec: _SubtitleTimingAdjustmentBlockSpec,
    config: SubtitleTimingAdjustmentConfig,
) -> list[SpeechInterval]:
    """Get cleaned block speech intervals in full-series time.

    Arguments:
        intervals: raw detector intervals, block-relative or absolute
        block_spec: block specification
        config: adjustment configuration
    Returns:
        cleaned speech intervals in full-series time
    """
    block_duration_ms = block_spec.buffered_end_ms - block_spec.buffered_start_ms
    if all(
        0 <= interval.start_ms and interval.end_ms <= block_duration_ms
        for interval in intervals
    ):
        shifted_intervals = [
            interval.shifted(block_spec.buffered_start_ms) for interval in intervals
        ]
    else:
        shifted_intervals = list(intervals)

    return get_speech_intervals_cleaned(
        shifted_intervals,
        merge_gap_ms=config.merge_gap_ms,
        min_duration_ms=config.min_speech_duration_ms,
        clip_start_ms=block_spec.buffered_start_ms,
        clip_end_ms=block_spec.buffered_end_ms,
    )


def _get_next_event_boundary(cue_idx: int, series: AudioSeries) -> int:
    """Get the next subtitle boundary.

    Arguments:
        cue_idx: event index in the full series
        series: original full series
    Returns:
        maximum allowed cue end in milliseconds
    """
    if cue_idx + 1 < len(series.events):
        return series.events[cue_idx + 1].start
    return len(series.audio)


def _get_overlapping_intervals(
    intervals: Sequence[SpeechInterval],
    *,
    start_ms: int,
    end_ms: int,
) -> list[SpeechInterval]:
    """Get intervals overlapping a window.

    Arguments:
        intervals: speech intervals
        start_ms: inclusive window start in milliseconds
        end_ms: exclusive window end in milliseconds
    Returns:
        intervals overlapping the window
    """
    return [
        interval
        for interval in intervals
        if interval.end_ms > start_ms and interval.start_ms < end_ms
    ]


def _get_previous_event_boundary(cue_idx: int, series: AudioSeries) -> int:
    """Get the previous subtitle boundary.

    Arguments:
        cue_idx: event index in the full series
        series: adjusted full series
    Returns:
        minimum allowed cue start in milliseconds
    """
    if cue_idx > 0:
        return series.events[cue_idx - 1].end
    return 0


def _get_series_copy(series: AudioSeries) -> AudioSeries:
    """Get a shallow audio series copy with copied subtitle events.

    Arguments:
        series: series to copy
    Returns:
        copied series
    """
    copied_series = type(series)(
        audio=series.audio,
        events=[series.event_class(**event.as_dict()) for event in series.events],
    )
    copied_series.styles = deepcopy(series.styles)
    copied_series.info = deepcopy(series.info)
    copied_series.format = series.format
    return copied_series
