#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of DemucsCache."""

from __future__ import annotations

from pathlib import Path

from pydub import AudioSegment
from pytest import MonkeyPatch, raises

from scinoephile.audio.transcription.demucs_cache import DemucsCache
from scinoephile.core.exceptions import ScinoephileError


def test_get_path_separates_model_configuration(tmp_path: Path):
    """Test Demucs cache paths differ by model configuration."""
    audio = AudioSegment.silent(duration=100)

    first_cache_path = DemucsCache(tmp_path, "model-one").get_path(audio)
    second_cache_path = DemucsCache(tmp_path, "model-two").get_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path != second_cache_path


def test_remove_deletes_matching_cached_vocals(tmp_path: Path):
    """Test removal deletes matching cached vocals."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    cache_path = cache.save(audio, audio)
    assert cache_path is not None

    removed_path = cache.remove(audio)

    assert removed_path == cache_path
    assert not cache_path.exists()


def test_save_and_load_cached_vocals(tmp_path: Path):
    """Test separated vocals can be saved and loaded."""
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    vocals = AudioSegment.silent(duration=80, frame_rate=8000)
    cache = DemucsCache(tmp_path, "model")

    cache_path = cache.save(audio, vocals)
    loaded_vocals = cache.load(audio)

    assert cache_path is not None
    assert cache_path.exists()
    assert loaded_vocals is not None
    assert len(loaded_vocals) == len(vocals)
    assert loaded_vocals.frame_rate == vocals.frame_rate


def test_save_failure_preserves_existing_cached_vocals(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test failed replacement leaves an existing cache file intact."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    cache_path = cache.save(audio, audio)
    assert cache_path is not None
    existing_payload = cache_path.read_bytes()

    def fail_export(*_args: object, **_kwargs: object):
        """Raise a simulated audio export failure."""
        raise OSError("simulated failure")

    monkeypatch.setattr(AudioSegment, "export", fail_export)

    with raises(ScinoephileError, match="Unable to write Demucs vocals cache"):
        cache.save(audio, audio)
    assert cache_path.read_bytes() == existing_payload
