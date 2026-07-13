#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.subtitles.series."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import assert_series_equal, test_data_root


def test_series_round_trips_srt():
    """Test loading and saving an SRT series."""
    path = test_data_root / "kob/input/eng.srt"

    series = Series.load(path)
    with get_temp_file_path(".srt") as output_path:
        series.save(output_path)
        output = Series.load(output_path)

    assert_series_equal(output, series)


def test_series_blocks_refresh_after_event_list_mutation():
    """Test cached blocks refresh after inherited list mutations."""
    series = Series(events=[Subtitle(start=0, end=1000, text="First")])
    initial_blocks = series.blocks

    series.append(Subtitle(start=5000, end=6000, text="Second"))
    refreshed_blocks = series.blocks

    assert refreshed_blocks is not initial_blocks
    assert len(refreshed_blocks) == 2
    assert [block.events[0].text for block in refreshed_blocks] == [
        "First",
        "Second",
    ]


def test_series_blocks_refresh_after_direct_event_mutation():
    """Test cached blocks refresh after direct event field mutations."""
    series = Series(
        events=[
            Subtitle(start=0, end=1000, text="First"),
            Subtitle(start=5000, end=6000, text="Second"),
        ]
    )
    initial_blocks = series.blocks

    series.events[1].start = 1500
    series.events[1].end = 2500
    series.events[1].text = "Changed"
    refreshed_blocks = series.blocks

    assert refreshed_blocks is not initial_blocks
    assert len(refreshed_blocks) == 1
    assert [event.text for event in refreshed_blocks[0]] == ["First", "Changed"]


def test_series_load_wraps_input_path_errors(tmp_path: Path):
    """Test subtitle loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    path = tmp_path / "missing.srt"

    with raises(
        ScinoephileError,
        match="Unable to load Series from .*missing.srt",
    ) as excinfo:
        Series.load(path)

    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_series_from_string_wraps_parser_errors():
    """Test subtitle parsing errors are user-facing."""
    with raises(
        ScinoephileError,
        match="Unable to parse Series from string",
    ):
        Series.from_string("text", format_="unsupported")


def test_series_save_wraps_output_path_errors(tmp_path: Path):
    """Test subtitle saving path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    series = Series(events=[Subtitle(start=1000, end=2000, text="Text")])

    with raises(
        ScinoephileError,
        match="Unable to save Series to ",
    ) as excinfo:
        series.save(tmp_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_series_slice_preserves_metadata_and_copies_events():
    """Test slicing preserves series metadata and independently copies events."""
    series = Series(
        events=[
            Subtitle(start=1000, end=2000, text="First"),
            Subtitle(start=3000, end=4000, text="Second"),
        ]
    )
    series.info["Title"] = "Example"
    series.format = "ass"
    series.fps = 23.976
    series.fonts_opaque["font.ttf"] = ["encoded font"]

    sliced = series.slice(1, 2)

    assert type(sliced) is Series
    assert sliced.events == [series.events[1]]
    assert sliced.events[0] is not series.events[1]
    assert sliced.styles == series.styles
    assert sliced.styles is not series.styles
    assert sliced.info == series.info
    assert sliced.info is not series.info
    assert sliced.format == series.format
    assert sliced.fps == series.fps
    assert sliced.fonts_opaque == series.fonts_opaque
    assert sliced.fonts_opaque is not series.fonts_opaque

    sliced.events[0].text = "Changed"
    assert series.events[1].text == "Second"


def test_series_to_string_wraps_serializer_errors():
    """Test subtitle string serialization errors are user-facing."""
    series = Series(events=[Subtitle(start=1000, end=2000, text="Text")])

    with raises(
        ScinoephileError,
        match="Unable to serialize Series to string",
    ):
        series.to_string(format_="unsupported")
