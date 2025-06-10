"""Tests for :mod:`scinoephile.audio`."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub.generators import Sine

from scinoephile.audio import AudioSubtitleSeries
from scinoephile.core import Series, Subtitle


@pytest.fixture()
def sample_audio_file(tmp_path: Path) -> Path:
    """Create a small sine wave audio file for testing."""
    path = tmp_path / "sample.wav"
    tone = Sine(440).to_audio_segment(duration=3000)
    tone.export(path, format="wav")
    return path


@pytest.fixture()
def sample_series() -> Series:
    """Series of three one-second subtitles."""
    series = Series()
    series.events = [
        Subtitle(start=0, end=1000, text="one", series=series),
        Subtitle(start=1000, end=2000, text="two", series=series),
        Subtitle(start=2000, end=3000, text="three", series=series),
    ]
    return series


def test_audio_subtitle_series_creation(
    sample_audio_file: Path, sample_series: Series
) -> None:
    """Audio clips match subtitle durations."""
    audio_series = AudioSubtitleSeries.from_video(str(sample_audio_file), sample_series)
    assert len(audio_series.events) == 3
    for event in audio_series.events:
        assert abs(len(event.audio) - 1000) <= 1


def test_audio_subtitle_series_save(
    tmp_path: Path, sample_audio_file: Path, sample_series: Series
) -> None:
    """Saving produces individual clips and an ``.srt`` file."""
    audio_series = AudioSubtitleSeries.from_video(str(sample_audio_file), sample_series)
    out_dir = tmp_path / "clips"
    audio_series.save(out_dir, format_="wav")

    files = list(out_dir.glob("*.wav"))
    assert len(files) == 3
    srt_file = out_dir / f"{out_dir.stem}.srt"
    assert srt_file.exists()
    assert srt_file.stat().st_size > 0
