#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the Demucs separation cache."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pytest import MonkeyPatch, raises

from scinoephile.audio.separation.demucs.cache import DemucsCache
from scinoephile.core.exceptions import ScinoephileError


def test_demucs_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = DemucsCache(None, "model")

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.cache_dir_path == runtime_cache_root_path / "audio/separation/demucs"


def test_get_path_separates_model_configuration(tmp_path: Path):
    """Test Demucs cache paths differ by model configuration."""
    audio = AudioSegment.silent(duration=100)

    first_cache_path = DemucsCache(tmp_path, "model-one").get_path(audio)
    second_cache_path = DemucsCache(tmp_path, "model-two").get_path(audio)

    assert first_cache_path.parent == tmp_path / "audio/separation/demucs"
    assert second_cache_path.parent == tmp_path / "audio/separation/demucs"
    assert first_cache_path != second_cache_path


def test_get_path_separates_runtime_versions(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test Demucs cache paths differ by installed runtime version."""
    audio = AudioSegment.silent(duration=100)
    monkeypatch.setattr(
        "scinoephile.audio.separation.demucs.cache.get_distribution_identity",
        Mock(return_value={"distribution": "demucs-infer", "version": "4.2.2"}),
    )
    first_cache_path = DemucsCache(tmp_path, "model").get_path(audio)
    monkeypatch.setattr(
        "scinoephile.audio.separation.demucs.cache.get_distribution_identity",
        Mock(return_value={"distribution": "demucs-infer", "version": "4.3.0"}),
    )
    second_cache_path = DemucsCache(tmp_path, "model").get_path(audio)

    assert first_cache_path != second_cache_path


def test_get_path_includes_cache_version(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test Demucs identities and cache paths differ between cache versions."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    first_identity = cache.cache_identity
    first_cache_path = cache.get_path(audio)

    monkeypatch.setattr("scinoephile.audio.separation.demucs.cache._CACHE_VERSION", 2)

    assert cache.cache_identity != first_identity
    assert cache.get_path(audio) != first_cache_path


def test_load_discards_decode_failure(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test malformed cached vocals are discarded as a cache miss."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    cache_path = cache.get_path(audio)
    cache_path.write_bytes(b"not audio")
    monkeypatch.setattr(
        "scinoephile.audio.separation.demucs.cache.AudioSegment.from_file",
        Mock(side_effect=CouldntDecodeError("invalid audio")),
    )

    assert cache.load(audio) is None
    assert not cache_path.exists()


def test_remove_deletes_matching_cached_vocals(tmp_path: Path):
    """Test removal deletes matching cached vocals."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    cache_path = cache.save(audio, audio)

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

    assert cache_path.exists()
    assert loaded_vocals is not None
    assert len(loaded_vocals) == len(vocals)
    assert loaded_vocals.frame_rate == vocals.frame_rate


def test_demucs_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes matching separated vocals once per instance."""
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    DemucsCache(tmp_path, "model").save(audio, audio)
    overwrite_cache = DemucsCache(tmp_path, "model", True)

    assert overwrite_cache.load(audio) is None
    overwrite_cache.save(audio, audio)

    assert overwrite_cache.load(audio) is not None


def test_save_failure_preserves_existing_cached_vocals(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test failed replacement leaves an existing cache file intact."""
    audio = AudioSegment.silent(duration=100)
    cache = DemucsCache(tmp_path, "model")
    cache_path = cache.save(audio, audio)
    existing_payload = cache_path.read_bytes()

    def fail_export(*_args: object, **_kwargs: object):
        """Raise a simulated audio export failure."""
        raise OSError("simulated failure")

    monkeypatch.setattr(AudioSegment, "export", fail_export)

    with raises(ScinoephileError, match="Unable to write Demucs vocals cache"):
        cache.save(audio, audio)
    assert cache_path.read_bytes() == existing_payload
