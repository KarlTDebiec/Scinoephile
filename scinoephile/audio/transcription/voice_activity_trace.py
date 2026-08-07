#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Uniform model-score trace for voice activity analysis."""

from __future__ import annotations

from math import ceil, floor

import numpy as np

__all__ = ["VoiceActivityTrace"]


class VoiceActivityTrace:
    """Uniform voice-activity model scores on an original audio timeline."""

    def __init__(
        self, scores: np.ndarray, *, start_ms: float, step_ms: float, duration_ms: int
    ):
        """Initialize.

        Arguments:
            scores: one-dimensional voice-activity model scores in [0, 1]
            start_ms: center timestamp of the first score in milliseconds
            step_ms: uniform time between consecutive scores in milliseconds
            duration_ms: duration of the source audio in milliseconds
        Raises:
            ValueError: if trace geometry or scores are invalid
        """
        score_array = np.asarray(scores, dtype=np.float32)
        if score_array.ndim != 1:
            raise ValueError("Voice activity scores must be one-dimensional.")
        if not np.all(np.isfinite(score_array)):
            raise ValueError("Voice activity scores must be finite.")
        if np.any(score_array < 0) or np.any(score_array > 1):
            raise ValueError("Voice activity scores must be between zero and one.")
        if start_ms < 0:
            raise ValueError("Voice activity trace start must be non-negative.")
        if step_ms <= 0:
            raise ValueError("Voice activity trace step must be positive.")
        if duration_ms < 0:
            raise ValueError("Voice activity trace duration must be non-negative.")

        self.scores = score_array.copy()
        """Read-only model scores in chronological order."""
        self.scores.setflags(write=False)
        self.start_ms = float(start_ms)
        """Center timestamp of the first score in milliseconds."""
        self.step_ms = float(step_ms)
        """Uniform time between consecutive scores in milliseconds."""
        self.duration_ms = duration_ms
        """Duration of the source audio in milliseconds."""

    def __len__(self) -> int:
        """Get the number of scores in the trace."""
        return len(self.scores)

    def get_coverage(
        self, start_seconds: float, end_seconds: float, threshold: float
    ) -> float | None:
        """Get the duration fraction whose score meets a threshold.

        Arguments:
            start_seconds: inclusive interval start in seconds
            end_seconds: exclusive interval end in seconds
            threshold: minimum score counted as voice activity
        Returns:
            duration-weighted fraction, or None when the interval has no trace data
        Raises:
            ValueError: if threshold is outside [0, 1]
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Voice activity threshold must be between zero and one.")
        overlap = self._get_overlap(start_seconds, end_seconds)
        if overlap is None:
            return None
        scores, weights = overlap
        active_weights = weights[scores >= threshold]
        return float(active_weights.sum() / weights.sum())

    def get_mean_score(self, start_seconds: float, end_seconds: float) -> float | None:
        """Get the duration-weighted mean score in a time interval.

        Arguments:
            start_seconds: inclusive interval start in seconds
            end_seconds: exclusive interval end in seconds
        Returns:
            duration-weighted mean score, or None when no trace data overlaps
        """
        overlap = self._get_overlap(start_seconds, end_seconds)
        if overlap is None:
            return None
        scores, weights = overlap
        return float(np.average(scores, weights=weights))

    def get_peak_score(self, start_seconds: float, end_seconds: float) -> float | None:
        """Get the maximum score in a time interval.

        Arguments:
            start_seconds: inclusive interval start in seconds
            end_seconds: exclusive interval end in seconds
        Returns:
            maximum overlapping score, or None when no trace data overlaps
        """
        overlap = self._get_overlap(start_seconds, end_seconds)
        if overlap is None:
            return None
        scores, _ = overlap
        return float(scores.max())

    def _get_overlap(
        self, start_seconds: float, end_seconds: float
    ) -> tuple[np.ndarray, np.ndarray] | None:
        """Get scores and their overlap durations for a time interval.

        Arguments:
            start_seconds: inclusive interval start in seconds
            end_seconds: exclusive interval end in seconds
        Returns:
            overlapping scores and millisecond weights, or None when unavailable
        """
        if not len(self.scores):
            return None
        start_ms = max(0.0, start_seconds * 1000)
        end_ms = min(float(self.duration_ms), end_seconds * 1000)
        if end_ms <= start_ms:
            return None

        first_bin_start_ms = self.start_ms - self.step_ms / 2
        last_bin_end_ms = first_bin_start_ms + len(self.scores) * self.step_ms
        if end_ms <= first_bin_start_ms:
            first_index = 0
            last_index = 1
        elif start_ms >= last_bin_end_ms:
            first_index = len(self.scores) - 1
            last_index = len(self.scores)
        else:
            first_index = max(
                0,
                min(
                    len(self.scores) - 1,
                    floor((start_ms - first_bin_start_ms) / self.step_ms),
                ),
            )
            last_index = max(
                first_index + 1,
                min(
                    len(self.scores), ceil((end_ms - first_bin_start_ms) / self.step_ms)
                ),
            )
        if last_index <= first_index:
            return None

        indexes = np.arange(first_index, last_index)
        bin_starts_ms = first_bin_start_ms + indexes * self.step_ms
        bin_ends_ms = bin_starts_ms + self.step_ms
        if first_index == 0:
            bin_starts_ms[0] = 0.0
        if last_index == len(self.scores):
            bin_ends_ms[-1] = float(self.duration_ms)
        weights = np.minimum(bin_ends_ms, end_ms) - np.maximum(bin_starts_ms, start_ms)
        positive = weights > 0
        if not np.any(positive):
            return None
        return self.scores[first_index:last_index][positive], weights[positive]
