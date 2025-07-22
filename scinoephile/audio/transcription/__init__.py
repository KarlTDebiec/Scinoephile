#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from copy import deepcopy

from scinoephile.audio.transcription.models import TranscribedSegment
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.core.hanzi import OpenCCConfig, get_hanzi_converter


def get_hanzi_converted_segment(
    segment: TranscribedSegment, config: OpenCCConfig = OpenCCConfig.t2s
) -> TranscribedSegment:
    """Convert Hanzi between character sets.

    Arguments:
        segment: Transcribed segment to convert
        config: OpenCC configuration for conversion
    Returns:
        Transcribed segment with converted Hanzi text
    """
    converter = get_hanzi_converter(config)

    converted_segment = deepcopy(segment)
    converted_segment.text = converter.convert(converted_segment.text)

    if converted_segment.words:
        i = 0
        for word in converted_segment.words:
            word_length = len(word.text)
            word.text = converted_segment.text[i : i + word_length]
            i += word_length

    return converted_segment


def get_merged_segment(segments: list[TranscribedSegment]) -> TranscribedSegment:
    """Merge transcribed segments into a single segment.

    Arguments:
        segments: Segments to merge
    Returns:
        Merged segment
    """
    if len(segments) == 1:
        return segments[0]
    return TranscribedSegment(
        id=segments[0].id,
        seek=segments[0].seek,
        start=segments[0].start,
        end=segments[-1].end,
        text="".join([s.text for s in segments]),
        words=[word for segment in segments for word in segment.words],
    )


__all__ = [
    "WhisperTranscriber",
    "get_hanzi_converted_segment",
    "get_merged_segment",
]
