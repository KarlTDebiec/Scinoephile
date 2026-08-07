#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typed language-identification and audio-event results."""

from __future__ import annotations

from collections.abc import Collection
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

__all__ = [
    "AudioClassificationMode",
    "AudioEvent",
    "AudioEventDetectionResult",
    "AudioEventSpan",
    "LanguageIdentificationResult",
    "LanguageSpan",
]


class AudioClassificationMode(StrEnum):
    """Optional source-wide audio-classification behavior."""

    AUTO = "auto"
    """Use classification when available and continue after failure."""
    ON = "on"
    """Require successful classification."""
    OFF = "off"
    """Do not run classification."""


class AudioEvent(StrEnum):
    """Independent event labels emitted by FireRed multi-label VAD."""

    SPEECH = "speech"
    SINGING = "singing"
    MUSIC = "music"


class LanguageSpan(BaseModel):
    """One source-timeline utterance assigned a spoken-language label."""

    start: float = Field(ge=0.0)
    """Utterance start relative to the complete source, in seconds."""
    end: float = Field(gt=0.0)
    """Utterance end relative to the complete source, in seconds."""
    language: str = Field(min_length=1)
    """FireRed language or Chinese-dialect code."""
    confidence: float = Field(ge=0.0, le=1.0)
    """FireRed utterance-level confidence."""

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        """Ensure the language span has positive duration."""
        if self.end <= self.start:
            raise ValueError("Language span end must be after its start.")
        return self


class LanguageIdentificationResult(BaseModel):
    """Ordered source-timeline spoken-language classifications."""

    spans: list[LanguageSpan]
    """VAD-derived utterance windows with FireRed language labels."""

    @model_validator(mode="after")
    def validate_span_order(self) -> Self:
        """Ensure language spans are ordered and do not overlap."""
        if self.spans != sorted(
            self.spans, key=lambda span: (span.start, span.end, span.language)
        ):
            raise ValueError("Language spans must be ordered.")
        for previous, current in zip(self.spans, self.spans[1:], strict=False):
            if current.start < previous.end:
                raise ValueError("Language spans must not overlap.")
        return self

    def get_language(self, start: float, end: float) -> str | None:
        """Get the language span with greatest overlap with an interval.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            language code, or None when no classified utterance overlaps
        """
        if start < 0.0 or end < start:
            raise ValueError("Language lookup interval is invalid.")
        interval_end = end if end > start else start + 1e-9
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
        return None if best_span is None else best_span.language

    def get_coverage(
        self,
        start: float,
        end: float,
        *,
        languages: Collection[str] | None = None,
        minimum_confidence: float = 0.0,
    ) -> float:
        """Get qualifying duration as a fraction of classified speech.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
            languages: optional accepted language codes
            minimum_confidence: minimum confidence for qualifying spans
        Returns:
            qualifying overlap divided by all classified overlap
        """
        if start < 0.0 or end < start:
            raise ValueError("Language coverage interval is invalid.")
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("Minimum language confidence must be in [0, 1].")
        total_overlap = self.get_duration(start, end)
        qualifying_overlap = self.get_duration(
            start, end, languages=languages, minimum_confidence=minimum_confidence
        )
        if total_overlap == 0.0:
            return 0.0
        return qualifying_overlap / total_overlap

    def get_duration(
        self,
        start: float,
        end: float,
        *,
        languages: Collection[str] | None = None,
        minimum_confidence: float = 0.0,
    ) -> float:
        """Get qualifying classified-speech duration within an interval.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
            languages: optional accepted language codes
            minimum_confidence: minimum confidence for qualifying spans
        Returns:
            qualifying classified-speech duration in seconds
        """
        if start < 0.0 or end < start:
            raise ValueError("Language duration interval is invalid.")
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("Minimum language confidence must be in [0, 1].")
        duration = 0.0
        for span in self.spans:
            if span.start >= end:
                break
            overlap = min(end, span.end) - max(start, span.start)
            if overlap <= 0.0:
                continue
            if span.confidence < minimum_confidence:
                continue
            if languages is not None and span.language not in languages:
                continue
            duration += overlap
        return duration


class AudioEventSpan(BaseModel):
    """One source-timeline interval containing an independently detected event."""

    start: float = Field(ge=0.0)
    """Event start relative to the complete source, in seconds."""
    end: float = Field(gt=0.0)
    """Event end relative to the complete source, in seconds."""
    event: AudioEvent
    """Detected event type."""

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        """Ensure the event span has positive duration."""
        if self.end <= self.start:
            raise ValueError("Audio event span end must be after its start.")
        return self


class AudioEventDetectionResult(BaseModel):
    """Independent speech, singing, and music intervals for a source."""

    spans: list[AudioEventSpan]
    """Ordered event intervals; different event types may overlap."""

    @model_validator(mode="after")
    def validate_span_order(self) -> Self:
        """Ensure spans are ordered and same-event intervals do not overlap."""
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

    def has_event(self, event: AudioEvent, start: float, end: float) -> bool:
        """Return whether an event covers the midpoint of an interval.

        Arguments:
            event: event type to look up
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            whether a matching event covers the interval midpoint
        """
        if start < 0.0 or end < start:
            raise ValueError("Audio event lookup interval is invalid.")
        midpoint = (start + end) / 2
        return any(
            span.event is event and span.start <= midpoint < span.end
            for span in self.spans
        )

    def get_coverage(self, event: AudioEvent, start: float, end: float) -> float:
        """Get the fraction of an interval covered by an event.

        Arguments:
            event: event type to look up
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            fraction of the interval covered by the event
        """
        if start < 0.0 or end < start:
            raise ValueError("Audio event coverage interval is invalid.")
        if end == start:
            return 0.0
        covered_duration = sum(
            max(0.0, min(end, span.end) - max(start, span.start))
            for span in self.spans
            if span.event is event and span.start < end and span.end > start
        )
        return covered_duration / (end - start)
