#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio."""

from __future__ import annotations

from scinoephile.audio.audio_block import AudioBlock
from scinoephile.audio.audio_series import AudioSeries
from scinoephile.audio.audio_subtitle import AudioSubtitle
from scinoephile.audio.transcription import get_segment_split_on_whitespace
from scinoephile.audio.transcription.models import TranscribedSegment


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


def get_sub_split_at_idx(
    sub: AudioSubtitle, idx: int
) -> tuple[AudioSubtitle, AudioSubtitle]:
    """Get two subtitles split from this one at provided index.

    Arguments:
        idx: Index at which to split
    Returns:
        Two subtitles split from this one at the provided index
    """
    one_segment, two_segment = get_segment_split_on_whitespace(sub.segment)
    one = AudioSubtitle(
        start=sub.start,
        end=sub.segment.words[idx].end,
        text=sub.text[:idx],
        segment=one_segment,
        # TODO: Audio
    )
    two = AudioSubtitle(
        start=sub.segment.words[idx].start,
        end=sub.end,
        text=sub.text[idx:],
        segment=two_segment,
        # TODO: Audio
    )
    return one, two


__all__ = [
    "AudioBlock",
    "AudioSeries",
    "AudioSubtitle",
    "get_series_from_segments",
    "get_sub_split_at_idx",
]
