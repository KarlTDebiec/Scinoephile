#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Convert transcribed segments into timed alignment sequences."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite

from scinoephile.analysis.alignment.timed_msa.models import AlignmentSequence

from .transcribed_segment import TranscribedSegment

__all__ = ["get_transcription_sequence"]


def get_transcription_sequence(
    name: str, segments: Sequence[TranscribedSegment], *, offset_seconds: float = 0.0
) -> AlignmentSequence:
    """Convert timestamped transcription output into alignable characters.

    Arguments:
        name: stable transcription source name
        segments: timestamped transcription segments
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        named sequence of timestamped lexical characters
    Raises:
        ValueError: if timing is invalid or the offset exceeds segment timings
    """
    if not isfinite(offset_seconds) or offset_seconds < 0.0:
        raise ValueError(
            "Transcription alignment offset must be finite and non-negative."
        )
    timed_texts = []
    for segment in segments:
        if segment.words:
            timed_texts.extend(
                (word.text, word.start - offset_seconds, word.end - offset_seconds)
                for word in segment.words
            )
        else:
            timed_texts.append(
                (
                    segment.text,
                    segment.start - offset_seconds,
                    segment.end - offset_seconds,
                )
            )
    if any(start_seconds < 0.0 for _, start_seconds, _ in timed_texts):
        raise ValueError("Transcription alignment offset exceeds segment timing.")
    return AlignmentSequence.from_timed_texts(name, timed_texts)
