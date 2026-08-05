#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""End-to-end audio blocks inferred from long speech-free gaps."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from .voice_activity_trace import VoiceActivityTrace

__all__ = ["SpeechBlock", "SpeechBlockSettings", "SpeechBlockSplitter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class SpeechBlockSettings:
    """Configuration for splitting audio at long speech-free gaps."""

    speech_free_gap_seconds: float = 3.0
    """Minimum speech-free duration that separates adjacent blocks."""
    context_padding_seconds: float = 1.0
    """Additional ASR context supplied before and after each block core."""
    voice_activity_threshold: float = 0.9
    """Minimum model score treated as voice activity."""
    min_speech_duration_seconds: float = 0.3
    """Minimum active run retained when locating speech-free gaps."""

    def __post_init__(self):
        """Validate block-splitting configuration."""
        if self.speech_free_gap_seconds <= 0.0:
            raise ValueError("Speech-free block gap must be positive.")
        if self.context_padding_seconds < 0.0:
            raise ValueError("Speech-block context padding must be non-negative.")
        if not 0.0 <= self.voice_activity_threshold <= 1.0:
            raise ValueError(
                "Speech-block voice threshold must be between zero and one."
            )
        if self.min_speech_duration_seconds < 0.0:
            raise ValueError("Minimum speech-block activity must be non-negative.")


@dataclass(frozen=True, slots=True, kw_only=True)
class SpeechBlock:
    """One core audio range plus optional neighboring ASR context."""

    index: int
    """Zero-based stable block index."""
    start_ms: int
    """Inclusive core start on the complete source timeline."""
    end_ms: int
    """Exclusive core end on the complete source timeline."""
    buffered_start_ms: int
    """Inclusive padded audio start supplied to ASR."""
    buffered_end_ms: int
    """Exclusive padded audio end supplied to ASR."""


class SpeechBlockSplitter:
    """Split a VAD trace into end-to-end blocks at long inactive runs."""

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
        """Split a complete source timeline into stable blocks.

        Arguments:
            trace: full-source voice-activity score trace
        Returns:
            blocks whose core ranges exactly tile the source duration
        """
        if trace.duration_ms == 0:
            return []

        active_runs = self._get_active_runs(trace)
        cuts_ms = []
        for (_, left_end_idx), (right_start_idx, _) in zip(
            active_runs, active_runs[1:], strict=False
        ):
            gap_start_ms = self._get_frame_boundary_ms(trace, left_end_idx)
            gap_end_ms = self._get_frame_boundary_ms(trace, right_start_idx)
            if gap_end_ms - gap_start_ms < self.settings.speech_free_gap_seconds * 1000:
                continue
            cut_ms = round((gap_start_ms + gap_end_ms) / 2)
            if 0 < cut_ms < trace.duration_ms:
                cuts_ms.append(cut_ms)

        padding_ms = round(self.settings.context_padding_seconds * 1000)
        core_edges_ms = [0, *cuts_ms, trace.duration_ms]
        return [
            SpeechBlock(
                index=index,
                start_ms=start_ms,
                end_ms=end_ms,
                buffered_start_ms=max(0, start_ms - padding_ms),
                buffered_end_ms=min(trace.duration_ms, end_ms + padding_ms),
            )
            for index, (start_ms, end_ms) in enumerate(
                zip(core_edges_ms, core_edges_ms[1:], strict=False)
            )
        ]

    def _get_active_runs(self, trace: VoiceActivityTrace) -> list[tuple[int, int]]:
        """Get significant half-open runs of active trace frames.

        Arguments:
            trace: full-source voice-activity score trace
        Returns:
            retained active frame-index ranges
        """
        minimum_active_frames = ceil(
            self.settings.min_speech_duration_seconds * 1000 / trace.step_ms
        )
        runs = []
        run_start_idx = None
        for frame_idx, score in enumerate(trace.scores):
            if score >= self.settings.voice_activity_threshold:
                if run_start_idx is None:
                    run_start_idx = frame_idx
                continue
            if run_start_idx is None:
                continue
            if frame_idx - run_start_idx >= minimum_active_frames:
                runs.append((run_start_idx, frame_idx))
            run_start_idx = None
        if (
            run_start_idx is not None
            and len(trace) - run_start_idx >= minimum_active_frames
        ):
            runs.append((run_start_idx, len(trace)))
        return runs

    @staticmethod
    def _get_frame_boundary_ms(trace: VoiceActivityTrace, frame_idx: int) -> float:
        """Get a trace-frame boundary on the source timeline.

        Arguments:
            trace: full-source voice-activity score trace
            frame_idx: half-open frame boundary index
        Returns:
            boundary time in milliseconds, clipped to the source duration
        """
        first_frame_start_ms = trace.start_ms - trace.step_ms / 2
        boundary_ms = first_frame_start_ms + frame_idx * trace.step_ms
        return max(0.0, min(float(trace.duration_ms), boundary_ms))
