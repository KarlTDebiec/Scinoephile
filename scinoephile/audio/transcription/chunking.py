#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for recombining overlapping transcription chunks."""

from __future__ import annotations

from collections.abc import Sequence

from .exceptions import TranscriptionAlignmentError
from .transcribed_segment import TranscribedSegment

__all__ = ["get_offset_core_segments"]


def get_offset_core_segments(
    segments: Sequence[TranscribedSegment],
    offset_seconds: float,
    core_start_seconds: float,
    core_end_seconds: float,
    start_id: int,
) -> list[TranscribedSegment]:
    """Offset chunk-local segments and keep only core-window words.

    Arguments:
        segments: chunk-local timestamped segments
        offset_seconds: offset from chunk-local time to original audio time
        core_start_seconds: inclusive start of non-overlap core
        core_end_seconds: exclusive end of non-overlap core
        start_id: first segment id to assign
    Returns:
        offset segments containing only words assigned to the core window
    Raises:
        TranscriptionAlignmentError: if a nonblank segment lacks word timings
    """
    offset_segments = []
    for segment in segments:
        if not segment.words:
            if not segment.text.strip():
                continue
            raise TranscriptionAlignmentError(
                "Transcription chunk cannot be trimmed without word timings."
            )
        words = []
        for word in segment.words:
            global_start = word.start + offset_seconds
            global_end = word.end + offset_seconds
            midpoint = (global_start + global_end) / 2
            if midpoint < core_start_seconds or midpoint >= core_end_seconds:
                continue
            words.append(
                word.model_copy(
                    update={
                        "start": max(global_start, core_start_seconds),
                        "end": min(global_end, core_end_seconds),
                    }
                )
            )
        if not words:
            continue
        offset_segments.append(
            segment.model_copy(
                update={
                    "id": start_id + len(offset_segments),
                    "start": words[0].start,
                    "end": words[-1].end,
                    "text": "".join(word.text for word in words),
                    "words": words,
                }
            )
        )
    return offset_segments
