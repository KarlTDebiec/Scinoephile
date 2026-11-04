#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regressions for audio slices containing overlapping and nested subtitle cues."""

from __future__ import annotations

from pydub import AudioSegment
from pydub.generators import Sine

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from test.helpers import parametrize


def test_audio_slice_empty_selection_retains_metadata_from_cropped_series():
    """An empty selection from cropped audio remains a valid independent series."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=10000),
        events=[AudioSubtitle(start=5000, end=9000, text="Cue")],
    )
    series.info["Title"] = "Example"

    empty = series.slice(0, 1).slice(0, 0)

    assert len(empty.audio) == 0
    assert empty.events == []
    assert empty.blocks == []
    assert empty.info == series.info
    assert empty.info is not series.info
    assert len(empty.slice(0, 0).audio) == 0


@parametrize(
    "event_bounds",
    [[(1000, 9000), (2000, 3000)], [(5000, 6000), (1000, 9000), (2000, 3000)]],
)
def test_audio_slice_includes_all_selected_cue_audio(
    event_bounds: list[tuple[int, int]],
):
    """Retain the earliest start and latest end even for nested or unordered cues.

    Arguments:
        event_bounds: selected cue intervals in their original event order
    """
    audio = AudioSegment.silent(duration=10000, frame_rate=44100).overlay(
        Sine(440).to_audio_segment(duration=1000), position=8000
    )
    series = AudioSeries(
        audio=audio,
        events=[AudioSubtitle(start=start, end=end) for start, end in event_bounds],
    )

    sliced = series.slice(0, len(series))

    assert len(sliced.audio) == 8000
    assert sliced.audio.raw_data == audio[1000:9000].raw_data
    assert [(event.start, event.end) for event in sliced] == event_bounds
    assert all(event is not original for event, original in zip(sliced, series))


def test_audio_slice_repeated_selection_preserves_absolute_audio_origin():
    """Further selections from cropped audio keep nested and shorter cues aligned."""
    audio = Sine(440).to_audio_segment(duration=10000)
    series = AudioSeries(
        audio=audio,
        events=[
            AudioSubtitle(start=5000, end=6000, text="Later"),
            AudioSubtitle(start=1000, end=9000, text="Long"),
            AudioSubtitle(start=2000, end=3000, text="Short"),
        ],
    )

    cropped = series.slice(0, 3)
    repeated = cropped.slice(0, 2).slice(1, 2)
    short = cropped.slice(2, 3).slice(0, 1)

    assert repeated.audio.raw_data == audio[1000:9000].raw_data
    assert [(event.start, event.end) for event in repeated] == [(1000, 9000)]
    assert short.audio.raw_data == audio[2000:3000].raw_data
    assert [(event.start, event.end) for event in short] == [(2000, 3000)]
