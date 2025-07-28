#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from copy import deepcopy
from logging import error

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.core.hanzi import OpenCCConfig, get_hanzi_converter


def get_segment_hanzi_converted(
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


def get_segment_merged(segments: list[TranscribedSegment]) -> TranscribedSegment:
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


def get_segment_split_at_idx(
    segment: TranscribedSegment, idx: int
) -> tuple[TranscribedSegment, TranscribedSegment]:
    """Split a transcribed segment into two segments at the specified index.

    Arguments:
        segment: Segment to split
        idx: Index at which to split the segment
    Returns:
        Tuple of two new segments created by splitting the original segment
    """
    first_segment = TranscribedSegment(
        id=segment.id,
        seek=segment.seek,
        start=segment.start,
        end=segment.words[idx - 1].end,
        text=segment.text[:idx],
        words=segment.words[:idx],
    )

    try:
        second_segment = TranscribedSegment(
            id=segment.id + 1,
            seek=segment.seek,
            start=segment.words[idx].start,
            end=segment.end,
            text=segment.text[idx:],
            words=segment.words[idx:],
        )
    except IndexError as exc:
        error(exc)
        print()

    return first_segment, second_segment


def get_segment_split_on_whitespace(
    segment: TranscribedSegment,
) -> list[TranscribedSegment]:
    """Split transcribed segment into multiple segments on whitespace.

    Arguments:
        segment: Transcribed segment to split
    Returns:
        Transcribed segments split on whitespace
    """
    if segment.words is None or len(segment.words) == 0:
        return [segment]

    split_segments = []
    nascent_words = []
    # Groups of words
    segment_id = 0
    for word in segment.words:
        if word.text.startswith(" "):
            if nascent_words:
                nascent_segment = TranscribedSegment(
                    id=segment_id,
                    seek=0,
                    start=nascent_words[0].start,
                    end=nascent_words[-1].end,
                    text="".join([word.text for word in nascent_words]),
                    words=nascent_words,
                )
                split_segments.append(nascent_segment)
                segment_id += 1
                nascent_words = []
            word.text = word.text[1:]
        if word.text != "":
            nascent_words.append(word)

    # Final group of words
    if nascent_words:
        nascent_segment = TranscribedSegment(
            id=segment_id,
            seek=0,
            start=nascent_words[0].start,
            end=nascent_words[-1].end,
            text="".join([word.text for word in nascent_words]),
            words=nascent_words,
        )
        split_segments.append(nascent_segment)

    return split_segments


__all__ = [
    "TranscribedSegment",
    "TranscribedWord",
    "WhisperTranscriber",
    "get_segment_hanzi_converted",
    "get_segment_merged",
    "get_segment_split_at_idx",
    "get_segment_split_on_whitespace",
]
