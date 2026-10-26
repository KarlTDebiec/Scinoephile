#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.subtitles.series."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pytest import raises

from scinoephile.audio.subtitles import (
    AudioSeries,
    AudioSubtitle,
    get_series_from_segments,
)
from scinoephile.audio.transcription import TranscribedSegment
from scinoephile.core import ScinoephileError


def test_get_series_from_segments_rounds_millisecond_bounds():
    """Segment conversion should use the repository millisecond convention."""
    segment = TranscribedSegment(id=0, seek=0, start=0.1006, end=0.2006, text="Text")

    series = get_series_from_segments(
        [segment], audio=AudioSegment.silent(duration=1_000)
    )

    assert (series.events[0].start, series.events[0].end) == (101, 201)


def test_audio_series_load_wraps_input_path_errors(tmp_path: Path):
    """Test audio subtitle loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "missing"

    with raises(
        ScinoephileError, match="Unable to load AudioSeries from .*missing"
    ) as excinfo:
        AudioSeries.load(input_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_audio_series_load_wraps_decode_errors(tmp_path: Path):
    """Test audio subtitle loading decode errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "input"
    input_path.mkdir()
    (input_path / "input.srt").write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nText\n", encoding="utf-8"
    )
    (input_path / "input.wav").touch()

    with patch(
        "scinoephile.audio.subtitles.series.AudioSegment.from_wav",
        side_effect=CouldntDecodeError("invalid audio"),
    ):
        with raises(
            ScinoephileError,
            match="Unable to load AudioSeries from .*input: invalid audio",
        ) as excinfo:
            AudioSeries.load(input_path)

    assert isinstance(excinfo.value.__cause__, CouldntDecodeError)


def test_audio_series_blocks_cover_long_nested_subtitle():
    """Include all of a long cue in its buffered audio block."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=16000),
        events=[
            AudioSubtitle(start=0, end=10000, text="Long"),
            AudioSubtitle(start=1000, end=2000, text="Short"),
            AudioSubtitle(start=14000, end=15000, text="After pause"),
        ],
    )

    first, second = series.blocks
    assert [event.text for event in first] == ["Long", "Short"]
    assert first.buffered_start == 0
    assert first.buffered_end == 11000
    assert len(first.audio) == 11000
    assert [event.text for event in second] == ["After pause"]


def test_audio_series_save_wraps_output_path_errors(tmp_path: Path):
    """Test audio subtitle saving path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    output_path = tmp_path / "audio_output"
    output_path.touch()
    series = AudioSeries(audio=AudioSegment.silent(duration=1000))

    with raises(
        ScinoephileError, match="Unable to save AudioSeries to .*audio_output"
    ) as excinfo:
        series.save(output_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_audio_series_save_preserves_unrelated_files(tmp_path: Path):
    """Replacing WAV output removes only stale files owned by the export.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    output_dir_path = tmp_path / "audio_output"
    output_dir_path.mkdir()
    unrelated_path = output_dir_path / "notes.txt"
    unrelated_path.write_text("Keep this note", encoding="utf-8")
    stale_block_path = output_dir_path / "0001-0002_00000000-00001000.wav"
    stale_block_path.write_bytes(b"old block")
    series = AudioSeries(
        audio=AudioSegment.silent(duration=2000),
        events=[AudioSubtitle(start=0, end=1000, text="Text")],
    )

    series.save(output_dir_path)

    assert unrelated_path.read_text(encoding="utf-8") == "Keep this note"
    assert not stale_block_path.exists()
    assert (output_dir_path / "audio_output.wav").is_file()
    assert (output_dir_path / "audio_output.srt").is_file()
    assert len(list(output_dir_path.glob("0001-0001_*.wav"))) == 1


def test_audio_series_save_failure_retains_existing_output(tmp_path: Path):
    """A failed block export leaves prior files and unrelated data untouched.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    output_dir_path = tmp_path / "audio_output"
    output_dir_path.mkdir()
    prior_audio_path = output_dir_path / "audio_output.wav"
    prior_audio_path.write_bytes(b"prior audio")
    prior_srt_path = output_dir_path / "audio_output.srt"
    prior_srt_path.write_text("prior subtitles", encoding="utf-8")
    unrelated_path = output_dir_path / "notes.txt"
    unrelated_path.write_text("Keep this note", encoding="utf-8")
    series = AudioSeries(
        audio=AudioSegment.silent(duration=2000),
        events=[AudioSubtitle(start=0, end=1000, text="Text")],
    )

    with patch.object(series.blocks[0].audio, "export", side_effect=OSError("failed")):
        with raises(ScinoephileError, match="failed"):
            series.save(output_dir_path)

    assert prior_audio_path.read_bytes() == b"prior audio"
    assert prior_srt_path.read_text(encoding="utf-8") == "prior subtitles"
    assert unrelated_path.read_text(encoding="utf-8") == "Keep this note"


def test_audio_series_slice_preserves_audio_subtitle_payloads():
    """Test audio series slicing retains series and subtitle audio."""
    event_audio = AudioSegment.silent(duration=1000)
    series = AudioSeries(
        audio=AudioSegment.silent(duration=4000),
        events=[AudioSubtitle(start=1000, end=2000, text="Text", audio=event_audio)],
    )
    series.info["Title"] = "Example"

    sliced = series.slice(0, 1)

    assert type(sliced) is AudioSeries
    assert len(sliced.audio) == 1000
    assert sliced.events[0] is not series.events[0]
    assert len(sliced.events[0].audio) == len(event_audio)
    assert sliced.info == series.info
    assert sliced.info is not series.info


def test_audio_series_slice_supports_empty_ranges():
    """Test audio series slicing can produce an empty series."""
    series = AudioSeries(audio=AudioSegment.silent(duration=1000))

    sliced = series.slice(0, 0)

    assert type(sliced) is AudioSeries
    assert len(sliced) == 0
    assert len(sliced.audio) == 0
