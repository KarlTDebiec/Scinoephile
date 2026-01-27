#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio subtitle data structures and helpers."""

from __future__ import annotations

from warnings import catch_warnings, filterwarnings

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    filterwarnings("ignore", category=RuntimeWarning)
    from pydub import AudioSegment

from scinoephile.audio.transcription import (
    TranscribedSegment,
    get_segment_merged,
    get_segment_split_at_idx,
)

from .block import AudioBlock
from .series import AudioSeries
from .subtitle import AudioSubtitle

__all__ = [
    "AudioBlock",
    "AudioSeries",
    "AudioSubtitle",
    "get_series_from_segments",
    "get_series_with_sub_split_at_idx",
    "get_sub_merged",
    "get_sub_split_at_idx",
]


def get_series_from_segments(
    segments: list[TranscribedSegment], audio: AudioSegment, offset: int = 0
) -> AudioSeries:
    """Compile transcribed segments to a subtitle series.

    Arguments:
        segments: Transcribed segments to compile
        audio: Series audio
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

    return AudioSeries(audio=audio, events=events)


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
    return AudioSeries(
        audio=series.audio,
        events=series.events[:sub_idx] + [one, two] + series.events[sub_idx + 1 :],
    )


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
