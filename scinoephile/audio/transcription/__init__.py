#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from copy import deepcopy

from scinoephile.audio.models import TranscribedSegment
from scinoephile.audio.transcription.cantonese_merger import CantoneseMerger
from scinoephile.audio.transcription.cantonese_splitter import (
    CantoneseSplitter,
)
from scinoephile.audio.transcription.cantonese_sync_grouper import CantoneseSyncGrouper
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.core import Series, Subtitle
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


def get_series_from_segments(segments: list[TranscribedSegment], offset=0) -> Series:
    """Compile transcribed segments to a subtitle series.

    Arguments:
        segments: Transcribed segments to compile
        offset: Time offset to apply
    Returns:
        Compiled subtitle series
    """
    events = []
    for segment in segments:
        event = Subtitle(
            start=offset + int(segment.start * 1000),
            end=offset + int(segment.end * 1000),
            text=segment.text.strip(),
        )
        events.append(event)

    series = Series()
    series.events = events
    return series


def get_split_segment(segment: TranscribedSegment) -> list[TranscribedSegment]:
    """Split transcribed segment into multiple segments on whitespace.

    Arguments:
        segment: Transcribed segment to split
    Returns:
        Transcribed segments split on whitespace
    """
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
        nascent_words.append(word)

    # Final group of words
    if nascent_words:
        nascent_segment = TranscribedSegment(
            id=segment_id,
            seek=0,
            start=nascent_words[0].start,
            end=nascent_words[-1].end,
            text="".join([word.text for word in nascent_words]),
        )
        split_segments.append(nascent_segment)
        segment_id += 1
        nascent_words = []

    return split_segments


__all__ = [
    "CantoneseMerger",
    "CantoneseSplitter",
    "CantoneseSyncGrouper",
    "WhisperTranscriber",
    "get_hanzi_converted_segment",
    "get_series_from_segments",
    "get_split_segment",
]
