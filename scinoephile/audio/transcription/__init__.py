#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from copy import deepcopy
from logging import error

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.core.hanzi import OpenCCConfig, get_hanzi_text_converted


def get_segment_hanzi_converted(
    segment: TranscribedSegment,
    config: OpenCCConfig = OpenCCConfig.t2s,
    apply_exclusions: bool = True,
) -> TranscribedSegment:
    """Convert Hanzi between character sets.

    Arguments:
        segment: Transcribed segment to convert
        config: OpenCC configuration for conversion
        apply_exclusions: Whether to apply character exclusions during conversion
    Returns:
        Transcribed segment with converted Hanzi text
    """
    converted_segment = deepcopy(segment)
    converted_segment.text = get_hanzi_text_converted(
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


def get_series_from_segments(
    segments: list[TranscribedSegment], offset: int = 0
) -> AudioSeries:
    """Compile transcribed segments to a subtitle series.

    Arguments:
        segments: Transcribed segments to compile
        offset: Time offset to apply
    Returns:
        Compiled subtitle series
    """
    events = []
    for segment in segments:
        event = AudioSubtitle(
            start=offset + int(segment.start * 1000),
            end=offset + int(segment.end * 1000),
            text=segment.text.strip(),
            segment=segment,
        )
        events.append(event)

    series = AudioSeries()
    series.events = events
    return series


def get_series_with_sub_split_at_idx(
    series: AudioSeries, sub_idx: int, char_idx: int
) -> AudioSeries:
    """Get a series with a subtitle split at the provided index.

    Arguments:
        series: Audio series to split
        sub_idx: Index of subtitle to split
        char_idx: Character index at which to split the subtitle
    Returns:
        Audio series with the subtitle split at the provided index
    """
    sub = series.events[sub_idx]
    one, two = get_sub_split_at_idx(sub, char_idx)
    new_series = AudioSeries(audio=series.audio)
    new_series.events = (
        series.events[:sub_idx] + [one, two] + series.events[sub_idx + 1 :]
    )
    return new_series


def get_sub_merged(
    subs: list[AudioSubtitle], *, text: str | None = None
) -> AudioSubtitle:
    """Merge audio subtitles into a single subtitle.

    Arguments:
        subs: Subtitles to merge
        text: Text to use for the merged subtitle, defaults to simple concatenation
    Returns:
        Merged subtitle
    """
    if text is None:
        text = "".join(sub.text for sub in subs)

    return AudioSubtitle(
        start=subs[0].start,
        end=subs[-1].end,
        text=text,
        segment=get_segment_merged([sub.segment for sub in subs]),
        # TODO: Audio
    )


def get_sub_split_at_idx(
    sub: AudioSubtitle, idx: int
) -> tuple[AudioSubtitle, AudioSubtitle]:
    """Get two subtitles split from this one at provided index.

    Arguments:
        sub: Subtitle to split
        idx: Index at which to split subtitle text
    Returns:
        Two subtitles split from this one at the provided index
    """
    one_segment, two_segment = get_segment_split_at_idx(sub.segment, idx)
    one = AudioSubtitle(
        start=sub.start,
        end=int(sub.start + ((one_segment.end - one_segment.start) * 1000)),
        text=sub.text[:idx],
        segment=one_segment,
        # TODO: Audio
    )
    two = AudioSubtitle(
        start=int(sub.end - ((two_segment.end - two_segment.start) * 1000)),
        end=sub.end,
        text=sub.text[idx:],
        segment=two_segment,
        # TODO: Audio
    )
    return one, two


__all__ = [
    "TranscribedSegment",
    "TranscribedWord",
    "WhisperTranscriber",
    "get_segment_hanzi_converted",
    "get_segment_merged",
    "get_segment_split_at_idx",
    "get_segment_split_on_whitespace",
    "get_series_from_segments",
    "get_series_with_sub_split_at_idx",
    "get_sub_merged",
    "get_sub_split_at_idx",
]
