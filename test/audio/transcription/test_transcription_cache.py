#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of TranscriptionCache."""

from __future__ import annotations

import json
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription import TranscribedSegment, TranscriptionCache
from scinoephile.core.cache.identity import CacheIdentity


def test_transcription_cache_round_trip(tmp_path: Path):
    """Test timestamped transcription output round-trips through the cache.

    Arguments:
        tmp_path: temporary cache directory path
    """
    cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity: CacheIdentity = {"model_name": "test/model"}
    segments = [TranscribedSegment(id=0, seek=0, start=0.0, end=0.1, text="test")]

    cache_path = cache.save(audio, cache_identity, segments)
    cached_transcription = cache.load(audio, cache_identity)

    assert cache_path.parent == tmp_path / "audio/transcription/whisper"
    assert cached_transcription == (cache_path, segments)
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert payload["cache_version"] == 2
    assert payload["cache_identity"]["backend"] == "test"
    assert payload["cache_identity"]["audio_frame_rate"] == audio.frame_rate


def test_transcription_cache_discards_mismatched_cache_identity(tmp_path: Path):
    """Test cached payload cache_identity mismatch is discarded as a cache miss.

    Arguments:
        tmp_path: temporary cache directory path
    """
    cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity: CacheIdentity = {"model_name": "test/model"}
    cache_path = cache.save(audio, cache_identity, [])
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_identity"]["model_name"] = "other/model"
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(audio, cache_identity) is None
    assert not cache_path.exists()


def test_transcription_cache_discards_mismatched_version(tmp_path: Path):
    """Test cached payload version mismatch is discarded as a cache miss.

    Arguments:
        tmp_path: temporary cache directory path
    """
    cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity: CacheIdentity = {"model_name": "test/model"}
    cache_path = cache.save(audio, cache_identity, [])
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_version"] = 0
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(audio, cache_identity) is None
    assert not cache_path.exists()


def test_transcription_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes a matching transcription once per instance."""
    audio = AudioSegment.silent(duration=100)
    cache_identity: CacheIdentity = {"model_name": "test/model"}
    cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    cache.save(audio, cache_identity, [])
    overwrite_cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test", True
    )

    assert overwrite_cache.load(audio, cache_identity) is None
    cache_path = overwrite_cache.save(audio, cache_identity, [])

    assert overwrite_cache.load(audio, cache_identity) == (cache_path, [])


def test_transcription_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = TranscriptionCache(
        None, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity: CacheIdentity = {"model_name": "test/model"}

    cache_path = cache.save(audio, cache_identity, [])

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache_path.parent == runtime_cache_root_path / "audio/transcription/whisper"
    assert cache_path.exists()
    assert cache.load(audio, cache_identity) == (cache_path, [])
    assert cache.remove(audio, cache_identity) == cache_path
    assert not cache_path.exists()
