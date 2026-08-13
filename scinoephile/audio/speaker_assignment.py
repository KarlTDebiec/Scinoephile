#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Speaker assignment across diarization and transcription results."""

from __future__ import annotations

from .diarization.models import SpeakerDiarizationResult
from .transcription.transcribed_segment import TranscribedSegment

__all__ = ["assign_speakers"]


def assign_speakers(
    diarization: SpeakerDiarizationResult,
    segments: list[TranscribedSegment],
    *,
    offset_seconds: float = 0.0,
) -> list[TranscribedSegment]:
    """Assign source-wide speakers to copied transcription word timings.

    Arguments:
        diarization: source-wide speaker diarization result
        segments: transcription segments timed relative to an audio slice
        offset_seconds: audio-slice start relative to the complete source
    Returns:
        copied segments whose timed words carry anonymous speaker labels
    Raises:
        ValueError: if the offset is negative
    """
    if offset_seconds < 0.0:
        raise ValueError("Speaker-assignment offset cannot be negative.")

    assigned_segments = []
    for segment in segments:
        if segment.words is None:
            assigned_segments.append(segment.model_copy(deep=True))
            continue
        assigned_words = []
        for word in segment.words:
            speaker = diarization.get_exclusive_speaker(
                word.start + offset_seconds, word.end + offset_seconds
            )
            assigned_words.append(word.model_copy(update={"speaker": speaker}))
        assigned_segments.append(
            segment.model_copy(update={"words": assigned_words}, deep=True)
        )
    return assigned_segments
