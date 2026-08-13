#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Quality filtering for multi-source transcription evidence."""

from __future__ import annotations

from collections.abc import Sequence

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.whisper.transcriber import (
    SUBTITLE_CREDIT_HALLUCINATION_MARKERS,
)

__all__ = ["get_source_quality_issue"]

_AUDIO_END_TOLERANCE_SECONDS = 1.0
"""Maximum accepted ASR timestamp extension beyond the source audio."""
_MAX_COMPRESSION_RATIO = 2.4
"""Maximum backend-reported compression ratio accepted for alignment."""


def get_source_quality_issue(  # noqa: PLR0911
    segments: Sequence[TranscribedSegment], *, audio_duration_seconds: float
) -> str | None:
    """Get the first issue making one source unusable for block alignment.

    Arguments:
        segments: source transcription segments
        audio_duration_seconds: complete block duration
    Returns:
        first quality issue, or None when the source is usable
    """
    for segment in segments:
        if not segment.text.strip():
            continue
        normalized_text = segment.text.casefold()
        marker = next(
            (
                marker
                for marker in SUBTITLE_CREDIT_HALLUCINATION_MARKERS
                if marker in normalized_text
            ),
            None,
        )
        if marker is not None:
            return (
                f"Segment {segment.id} contains subtitle-credit hallucination "
                f"marker {marker!r}."
            )
        if not segment.words:
            return f"Segment {segment.id} has no word timings."
        if int(segment.end * 1000) <= int(segment.start * 1000):
            return (
                f"Segment {segment.id} has non-positive millisecond duration "
                f"({segment.start:.3f}s to {segment.end:.3f}s)."
            )
        for word in segment.words:
            if not word.text.strip():
                continue
            if int(word.end * 1000) <= int(word.start * 1000):
                return (
                    f"Segment {segment.id} word {word.text!r} has non-positive "
                    f"millisecond duration ({word.start:.3f}s to {word.end:.3f}s)."
                )
        if (
            segment.compression_ratio is not None
            and segment.compression_ratio > _MAX_COMPRESSION_RATIO
        ):
            return (
                f"Segment {segment.id} compression ratio "
                f"{segment.compression_ratio:.2f} exceeds maximum "
                f"{_MAX_COMPRESSION_RATIO:.2f}."
            )
        if segment.end > audio_duration_seconds + _AUDIO_END_TOLERANCE_SECONDS:
            return (
                f"Segment {segment.id} ends at {segment.end:.2f}s beyond "
                f"{audio_duration_seconds:.2f}s source audio."
            )
    if not any(segment.text.strip() for segment in segments):
        return "Source produced no nonblank text."
    return None
