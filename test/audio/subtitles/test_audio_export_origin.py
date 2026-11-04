#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Round-trip timing and staging regressions for cropped audio subtitle exports."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment
from pydub.generators import Sine
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core import ScinoephileError
from test.helpers import parametrize


def test_audio_export_cropped_origin_round_trip(tmp_path: Path):
    """Restore absolute cue timing and the exact cropped audio across repeated loads.

    Arguments:
        tmp_path: temporary directory for the exported series
    """
    audio = AudioSegment.silent(duration=15000, frame_rate=44100).overlay(
        Sine(440).to_audio_segment(duration=2000), position=10000
    )
    series = AudioSeries(
        audio=audio, events=[AudioSubtitle(start=10000, end=12000, text="Cue")]
    )
    output_dir_path = tmp_path / "first"
    series.slice(0, 1).save(output_dir_path)

    loaded = AudioSeries.load(output_dir_path, buffer=0)

    assert [(event.start, event.end) for event in loaded] == [(10000, 12000)]
    assert loaded.audio.raw_data == audio[10000:12000].raw_data
    assert loaded.events[0].audio.raw_data == loaded.audio.raw_data
    assert loaded.slice(0, 1).audio.raw_data == loaded.audio.raw_data
    block = loaded.blocks[0]
    assert (block.buffered_start, block.buffered_end) == (10000, 12000)
    assert block.audio.raw_data == loaded.audio.raw_data

    repeated_dir_path = tmp_path / "second"
    loaded.slice(0, 1).slice(0, 1).save(repeated_dir_path)
    repeated = AudioSeries.load(repeated_dir_path, buffer=0)
    assert repeated.events == loaded.events
    assert repeated.audio.raw_data == loaded.audio.raw_data
    assert repeated.events[0].audio.raw_data == loaded.events[0].audio.raw_data


def test_audio_export_empty_cropped_series_round_trip(tmp_path: Path):
    """Retain an empty audio slice's origin without inventing subtitle events.

    Arguments:
        tmp_path: temporary directory for the exported series
    """
    series = (
        AudioSeries(
            audio=AudioSegment.silent(duration=15000),
            events=[AudioSubtitle(start=10000, end=12000, text="Cue")],
        )
        .slice(0, 1)
        .slice(0, 0)
    )
    output_dir_path = tmp_path / "empty"

    series.save(output_dir_path)
    loaded = AudioSeries.load(output_dir_path)

    assert loaded.events == []
    assert len(loaded.audio) == 0
    assert loaded.blocks == []
    repeated_dir_path = tmp_path / "repeated-empty"
    loaded.save(repeated_dir_path)
    metadata_path = repeated_dir_path / ".scinoephile-audio.json"
    assert json.loads(metadata_path.read_text(encoding="utf-8")) == {
        "version": 1,
        "audio_start_ms": 10000,
    }


def test_audio_export_legacy_directory_defaults_to_zero_origin(tmp_path: Path):
    """Continue loading directories created before origin metadata was introduced.

    Arguments:
        tmp_path: temporary directory for the legacy series
    """
    audio = Sine(440).to_audio_segment(duration=3000)
    series = AudioSeries(
        audio=audio, events=[AudioSubtitle(start=1000, end=2000, text="Cue")]
    )
    output_dir_path = tmp_path / "legacy"
    series.save(output_dir_path)
    (output_dir_path / ".scinoephile-audio.json").unlink()

    loaded = AudioSeries.load(output_dir_path, buffer=0)

    assert [(event.start, event.end) for event in loaded] == [(1000, 2000)]
    assert loaded.audio.raw_data == audio.raw_data
    assert loaded.events[0].audio.raw_data == audio[1000:2000].raw_data
    assert loaded.slice(0, 1).audio.raw_data == audio[1000:2000].raw_data


def test_audio_export_metadata_directory_conflict_preserves_prior_files(tmp_path: Path):
    """Check metadata destinations before replacing existing WAV or subtitle files.

    Arguments:
        tmp_path: temporary directory for the existing export
    """
    output_dir_path = tmp_path / "output"
    output_dir_path.mkdir()
    prior_audio_path = output_dir_path / "output.wav"
    prior_audio_path.write_bytes(b"prior audio")
    prior_srt_path = output_dir_path / "output.srt"
    prior_srt_path.write_bytes(b"prior subtitles")
    metadata_path = output_dir_path / ".scinoephile-audio.json"
    metadata_path.mkdir()
    unrelated_path = metadata_path / "notes.txt"
    unrelated_path.write_text("Keep", encoding="utf-8")
    series = AudioSeries(audio=AudioSegment.silent(duration=1000))

    with raises(ScinoephileError, match="is a directory"):
        series.save(output_dir_path)

    assert prior_audio_path.read_bytes() == b"prior audio"
    assert prior_srt_path.read_bytes() == b"prior subtitles"
    assert unrelated_path.read_text(encoding="utf-8") == "Keep"


def test_audio_export_metadata_staging_failure_preserves_prior_files(tmp_path: Path):
    """Leave prior metadata, audio, subtitles, and unrelated files intact on failure.

    Arguments:
        tmp_path: temporary directory for the existing export
    """
    output_dir_path = tmp_path / "output"
    output_dir_path.mkdir()
    existing_names = [
        "output.wav",
        "output.srt",
        ".scinoephile-audio.json",
        "notes.txt",
    ]
    for name in existing_names:
        (output_dir_path / name).write_bytes(b"prior contents")
    series = AudioSeries(audio=AudioSegment.silent(duration=1000))

    with patch.object(Path, "write_text", side_effect=OSError("metadata write failed")):
        with raises(ScinoephileError, match="metadata write failed"):
            series.save(output_dir_path)

    assert sorted(path.name for path in output_dir_path.iterdir()) == sorted(
        existing_names
    )
    for name in existing_names:
        assert (output_dir_path / name).read_bytes() == b"prior contents"
    assert list(tmp_path.iterdir()) == [output_dir_path]


@parametrize(
    "metadata_text",
    [
        "not JSON",
        "[]",
        "{}",
        '{"version": 2, "audio_start_ms": 0}',
        '{"version": true, "audio_start_ms": 0}',
        '{"version": 1, "audio_start_ms": -1}',
        '{"version": 1, "audio_start_ms": true}',
        '{"version": 1, "audio_start_ms": "10000"}',
        '{"version": 1, "audio_start_ms": 0.5}',
        '{"version": 1, "audio_start_ms": null}',
    ],
)
def test_audio_export_rejects_malformed_metadata(tmp_path: Path, metadata_text: str):
    """Reject malformed or unsupported origin metadata as a user-facing load error.

    Arguments:
        tmp_path: temporary directory for the exported series
        metadata_text: malformed metadata contents
    """
    output_dir_path = tmp_path / "output"
    AudioSeries(audio=AudioSegment.silent(duration=1000)).save(output_dir_path)
    (output_dir_path / ".scinoephile-audio.json").write_text(
        metadata_text, encoding="utf-8"
    )

    with raises(ScinoephileError, match="Unable to load AudioSeries"):
        AudioSeries.load(output_dir_path)


def test_audio_export_zero_origin_replaces_stale_metadata(tmp_path: Path):
    """A full-timeline export overwrites an earlier cropped export's metadata.

    Arguments:
        tmp_path: temporary directory for successive exports
    """
    audio = Sine(440).to_audio_segment(duration=13000)
    series = AudioSeries(
        audio=audio, events=[AudioSubtitle(start=10000, end=12000, text="Cue")]
    )
    output_dir_path = tmp_path / "output"
    series.slice(0, 1).save(output_dir_path)
    unrelated_path = output_dir_path / "notes.txt"
    unrelated_path.write_text("Keep", encoding="utf-8")

    series.save(output_dir_path)
    loaded = AudioSeries.load(output_dir_path, buffer=0)

    assert loaded.audio.raw_data == audio.raw_data
    assert loaded.events[0].audio.raw_data == audio[10000:12000].raw_data
    assert unrelated_path.read_text(encoding="utf-8") == "Keep"
