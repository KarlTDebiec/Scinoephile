#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from copy import deepcopy
from logging import error

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.lang.zho.conversion import OpenCCConfig, get_zho_text_converted

__all__ = [
    "TranscribedSegment",
    "TranscribedWord",
    "WhisperTranscriber",
    "get_segment_merged",
    "get_segment_split_at_idx",
    "get_segment_split_on_whitespace",
    "get_segment_zho_converted",
]


def get_segment_zho_converted(
    segment: TranscribedSegment,
    config: OpenCCConfig = OpenCCConfig.t2s,
    apply_exclusions: bool = True,
) -> TranscribedSegment:
    """Convert 中文 between character sets.

    Arguments:
        segment: Transcribed segment to convert
        config: OpenCC configuration for conversion
        apply_exclusions: Whether to apply character exclusions during conversion
    Returns:
        Transcribed segment with converted 中文 text
    """
    converted_segment = deepcopy(segment)
    converted_segment.text = get_zho_text_converted(
        converted_segment.text, config, apply_exclusions
    )

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
        words=[word for segment in segments for word in (segment.words or [])],
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
    if segment.words is None or len(segment.words) == 0:
        message = "Cannot split segment without word timing data."
        error(message)
        raise ValueError(message)
    if idx <= 0 or idx >= len(segment.text):
        message = f"Split index {idx} out of range for {len(segment.text)} chars."
        error(message)
        raise ValueError(message)

    first_words: list[TranscribedWord] = []
    second_words: list[TranscribedWord] = []
    consumed_chars = 0
    split_done = False
    for word in segment.words:
        word_length = len(word.text)
        next_consumed = consumed_chars + word_length
        if idx == consumed_chars:
            second_words.append(word)
            split_done = True
        elif idx == next_consumed:
            first_words.append(word)
            split_done = True
        elif consumed_chars < idx < next_consumed:
            split_pos = idx - consumed_chars
            first_text = word.text[:split_pos]
            second_text = word.text[split_pos:]
            word_duration = word.end - word.start
            ratio = split_pos / word_length if word_length else 0.0
            split_time = word.start + (word_duration * ratio)
            if first_text:
                first_words.append(
                    TranscribedWord(
                        text=first_text,
                        start=word.start,
                        end=split_time,
                        confidence=word.confidence,
                    )
                )
            if second_text:
                second_words.append(
                    TranscribedWord(
                        text=second_text,
                        start=split_time,
                        end=word.end,
                        confidence=word.confidence,
                    )
                )
            split_done = True
        elif not split_done:
            first_words.append(word)
        else:
            second_words.append(word)
        consumed_chars = next_consumed

    if not split_done:
        message = (
            f"Split index {idx} does not align with segment words ({consumed_chars})."
        )
        error(message)
        raise ValueError(message)

    first_segment = TranscribedSegment(
        id=segment.id,
        seek=segment.seek,
        start=segment.start,
        end=first_words[-1].end,
        text=segment.text[:idx],
        words=first_words,
    )

    second_segment = TranscribedSegment(
        id=segment.id + 1,
        seek=segment.seek,
        start=second_words[0].start,
        end=segment.end,
        text=segment.text[idx:],
        words=second_words,
    )

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
