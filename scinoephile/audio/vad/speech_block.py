#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Complete-source audio blocks inferred from long speech-free gaps."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from math import ceil

from .intervals import get_active_frame_intervals, get_frame_boundary_ms
from .trace import VoiceActivityTrace

__all__ = ["SpeechBlock", "SpeechBlockSettings", "SpeechBlockSplitter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class SpeechBlockSettings:
    """Configuration for splitting audio at long speech-free gaps."""

    speech_free_gap_seconds: float = 3.0
    """Minimum speech-free duration eligible for a hard cut."""
    voice_activity_threshold: float = 0.9
    """Minimum model score treated as voice activity."""
    min_silence_duration_seconds: float = 0.1
    """Below-threshold gap bridged before minimum speech filtering."""
    min_speech_duration_seconds: float = 0.3
    """Minimum active run retained when locating speech-free gaps."""

    def __post_init__(self):
        """Validate block-splitting configuration."""
        if self.speech_free_gap_seconds <= 0.0:
            raise ValueError("Speech-free block gap must be positive.")
        if not 0.0 <= self.voice_activity_threshold <= 1.0:
            raise ValueError(
                "Block-planning voice threshold must be between zero and one."
            )
        if self.min_silence_duration_seconds < 0.0:
            raise ValueError("Minimum block-planning silence must be non-negative.")
        if self.min_speech_duration_seconds < 0.0:
            raise ValueError("Minimum block-planning activity must be non-negative.")


@dataclass(frozen=True, slots=True, kw_only=True)
class SpeechBlock:
    """One complete-source audio partition inferred from voice activity."""

    index: int
    """Zero-based stable block index."""
    start_ms: int
    """Inclusive start on the complete source timeline."""
    end_ms: int
    """Exclusive end on the complete source timeline."""


class SpeechBlockSplitter:
    """Partition complete audio at long inactive runs."""

    def __init__(self, settings: SpeechBlockSettings | None = None):
        """Initialize.

        Arguments:
            settings: block-splitting configuration
        """
        if settings is None:
            settings = SpeechBlockSettings()
        self.settings = settings
        """Block-splitting configuration."""

    def __call__(self, trace: VoiceActivityTrace) -> list[SpeechBlock]:
        """Partition the complete source into stable hard-cut blocks.

        Arguments:
            trace: full-source voice-activity score trace
        Returns:
            contiguous blocks covering the complete source
        """
        if trace.duration_ms == 0:
            return []

        active_runs = self._get_active_runs(trace)
        if not active_runs:
            return [SpeechBlock(index=0, start_ms=0, end_ms=trace.duration_ms)]

        cut_points_ms = [0]
        previous_run_end_idx = active_runs[0][1]
        for run_start_idx, run_end_idx in active_runs[1:]:
            gap_start_ms = get_frame_boundary_ms(trace, previous_run_end_idx)
            gap_end_ms = get_frame_boundary_ms(trace, run_start_idx)
            if gap_end_ms - gap_start_ms >= (
                self.settings.speech_free_gap_seconds * 1000
            ):
                cut_points_ms.append(round((gap_start_ms + gap_end_ms) / 2))
            previous_run_end_idx = run_end_idx
        cut_points_ms.append(trace.duration_ms)

        return [
            SpeechBlock(index=index, start_ms=start_ms, end_ms=end_ms)
            for index, (start_ms, end_ms) in enumerate(pairwise(cut_points_ms))
        ]

    def _get_active_runs(self, trace: VoiceActivityTrace) -> list[tuple[int, int]]:
        """Get significant half-open runs of active trace frames.

        Arguments:
            trace: full-source voice-activity score trace
        Returns:
            retained active frame-index ranges
        """
        minimum_inactive_frames = ceil(
            self.settings.min_silence_duration_seconds * 1000 / trace.step_ms
        )
        minimum_active_frames = ceil(
            self.settings.min_speech_duration_seconds * 1000 / trace.step_ms
        )
        return get_active_frame_intervals(
            trace.scores,
            self.settings.voice_activity_threshold,
            minimum_inactive_frames,
            minimum_active_frames,
        )
