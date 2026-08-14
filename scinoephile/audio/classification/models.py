#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typed language-identification and audio-event results."""

from __future__ import annotations

from enum import StrEnum
from math import isfinite
from typing import Self

from pydantic import BaseModel, Field, model_validator

__all__ = [
    "AudioEvent",
    "AudioEventDetectionResult",
    "AudioEventSpan",
    "LanguageIdentificationResult",
    "LanguageSpan",
]


class AudioEvent(StrEnum):
    """Independent event labels emitted by FireRed multi-label VAD."""

    SPEECH = "speech"
    """Spoken voice."""
    SINGING = "singing"
    """Sung voice."""
    MUSIC = "music"
    """Music."""


class LanguageSpan(BaseModel):
    """One source-timeline utterance assigned a spoken-language label."""

    start: float = Field(ge=0.0, allow_inf_nan=False)
    """Utterance start relative to the complete source, in seconds."""
    end: float = Field(gt=0.0, allow_inf_nan=False)
    """Utterance end relative to the complete source, in seconds."""
    language: str = Field(min_length=1)
    """FireRed language or Chinese-dialect code."""
    confidence: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    """FireRed utterance-level confidence."""

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        """Ensure the language span has positive duration.

        Returns:
            validated language span
        Raises:
            ValueError: if the span has nonpositive duration
        """
        if self.end <= self.start:
            raise ValueError("Language span end must be after its start.")
        return self


class LanguageIdentificationResult(BaseModel):
    """Ordered source-timeline spoken-language classifications."""

    spans: list[LanguageSpan]
    """VAD-derived utterance windows with FireRed language labels."""

    def get_language(self, start: float, end: float) -> str | None:
        """Get the language span with greatest overlap with an interval.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            language code, or None when no classified utterance overlaps
        Raises:
            ValueError: if the lookup interval is invalid
        """
        if not isfinite(start) or not isfinite(end) or start < 0.0 or end < start:
            raise ValueError("Language lookup interval is invalid.")
        interval_end = end
        if interval_end == start:
            interval_end = start + 1e-9
        midpoint = (start + interval_end) / 2
        best_span = None
        best_overlap = 0.0
        for span in self.spans:
            if span.start >= interval_end:
                break
            overlap = min(interval_end, span.end) - max(start, span.start)
            if overlap <= 0.0:
                continue
            if overlap > best_overlap:
                best_span = span
                best_overlap = overlap
                continue
            if overlap == best_overlap and best_span is not None:
                if span.start <= midpoint < span.end and not (
                    best_span.start <= midpoint < best_span.end
                ):
                    best_span = span
        if best_span is None:
            return None
        return best_span.language

    @model_validator(mode="after")
    def validate_span_order(self) -> Self:
        """Ensure language spans are ordered and do not overlap.

        Returns:
            validated language identification result
        Raises:
            ValueError: if spans are unordered or overlap
        """
        if self.spans != sorted(
            self.spans, key=lambda span: (span.start, span.end, span.language)
        ):
            raise ValueError("Language spans must be ordered.")
        for previous, current in zip(self.spans, self.spans[1:], strict=False):
            if current.start < previous.end:
                raise ValueError("Language spans must not overlap.")
        return self


class AudioEventSpan(BaseModel):
    """One source-timeline interval containing an independently detected event."""

    start: float = Field(ge=0.0, allow_inf_nan=False)
    """Event start relative to the complete source, in seconds."""
    end: float = Field(gt=0.0, allow_inf_nan=False)
    """Event end relative to the complete source, in seconds."""
    event: AudioEvent
    """Detected event type."""

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        """Ensure the event span has positive duration.

        Returns:
            validated audio event span
        Raises:
            ValueError: if the span has nonpositive duration
        """
        if self.end <= self.start:
            raise ValueError("Audio event span end must be after its start.")
        return self


class AudioEventDetectionResult(BaseModel):
    """Independent speech, singing, and music intervals for a source."""

    spans: list[AudioEventSpan]
    """Ordered event intervals; different event types may overlap."""

    def has_event(self, event: AudioEvent, start: float, end: float) -> bool:
        """Return whether an event covers the midpoint of an interval.

        Arguments:
            event: event type to look up
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            whether a matching event covers the interval midpoint
        Raises:
            ValueError: if the lookup interval is invalid
        """
        if not isfinite(start) or not isfinite(end) or start < 0.0 or end < start:
            raise ValueError("Audio event lookup interval is invalid.")
        midpoint = (start + end) / 2
        return any(
            span.event is event and span.start <= midpoint < span.end
            for span in self.spans
        )

    @model_validator(mode="after")
    def validate_span_order(self) -> Self:
        """Ensure spans are ordered and same-event intervals do not overlap.

        Returns:
            validated audio event detection result
        Raises:
            ValueError: if spans are unordered or same-type spans overlap
        """
        if self.spans != sorted(
            self.spans, key=lambda span: (span.start, span.end, span.event)
        ):
            raise ValueError("Audio event spans must be ordered.")
        previous_by_event: dict[AudioEvent, AudioEventSpan] = {}
        for span in self.spans:
            previous = previous_by_event.get(span.event)
            if previous is not None and span.start < previous.end:
                raise ValueError("Same-type audio event spans must not overlap.")
            previous_by_event[span.event] = span
        return self
