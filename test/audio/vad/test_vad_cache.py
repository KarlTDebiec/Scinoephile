#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of persistent voice activity trace caching."""

from __future__ import annotations

from os import utime
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.vad import VoiceActivityCache, VoiceActivityTrace


def test_vad_cache_round_trip(tmp_path: Path):
    """Persist score values and original-timeline geometry without loss."""
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=300, frame_rate=16000)
    metadata = {"implementation": "test", "model": "one"}
    trace = VoiceActivityTrace(
        np.asarray([0.1, 0.7, 0.2], dtype=np.float32),
        start_ms=50,
        step_ms=100,
        duration_ms=300,
    )

    cache_path = cache.save(audio, metadata, trace)
    utime(cache_path, (1, 1))
    loaded = cache.load(audio, metadata)

    assert cache_path.parent == tmp_path / "audio/vad"
    assert loaded is not None
    np.testing.assert_array_equal(loaded.scores, trace.scores)
    assert loaded.start_ms == trace.start_ms
    assert loaded.step_ms == trace.step_ms
    assert loaded.duration_ms == trace.duration_ms
    assert cache_path.stat().st_mtime > 1


def test_vad_cache_separates_audio_and_model_identity(tmp_path: Path):
    """Use both source audio and inference metadata in cache keys."""
    cache = VoiceActivityCache(tmp_path)
    first_audio = AudioSegment.silent(duration=100, frame_rate=16000)
    second_audio = AudioSegment.silent(duration=200, frame_rate=16000)

    first_path = cache.get_path(first_audio, {"model": "one"})
    second_path = cache.get_path(second_audio, {"model": "one"})
    other_model_path = cache.get_path(first_audio, {"model": "two"})

    assert first_path != second_path
    assert first_path != other_model_path


def test_vad_cache_discards_invalid_payload(tmp_path: Path):
    """Remove a malformed trace cache and allow regeneration."""
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    metadata = {"model": "one"}
    cache_path = cache.get_path(audio, metadata)
    cache_path.write_bytes(b"not an npz archive")

    assert cache.load(audio, metadata) is None
    assert not cache_path.exists()


def test_vad_cache_rejects_trace_for_different_audio_duration(tmp_path: Path):
    """Reject a trace whose timeline does not match its source audio."""
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    trace = VoiceActivityTrace(
        np.asarray([0.5], dtype=np.float32), start_ms=50, step_ms=100, duration_ms=200
    )

    with pytest.raises(ValueError, match="duration does not match"):
        cache.save(audio, {"model": "one"}, trace)


def test_vad_cache_overwrites_each_entry_once(tmp_path: Path):
    """Refresh a requested entry once, then reuse the replacement."""
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    metadata = {"model": "one"}
    first_trace = VoiceActivityTrace(
        np.asarray([0.1], dtype=np.float32), start_ms=50, step_ms=100, duration_ms=100
    )
    second_trace = VoiceActivityTrace(
        np.asarray([0.9], dtype=np.float32), start_ms=50, step_ms=100, duration_ms=100
    )
    VoiceActivityCache(tmp_path).save(audio, metadata, first_trace)
    overwrite_cache = VoiceActivityCache(tmp_path, overwrite=True)

    assert overwrite_cache.load(audio, metadata) is None
    overwrite_cache.save(audio, metadata, second_trace)
    loaded = overwrite_cache.load(audio, metadata)

    assert loaded is not None
    np.testing.assert_array_equal(loaded.scores, second_trace.scores)


def test_vad_cache_atomic_write_failure_preserves_existing_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Leave a valid cache entry intact when staging serialization fails."""
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    metadata = {"model": "one"}
    trace = VoiceActivityTrace(
        np.asarray([0.4], dtype=np.float32), start_ms=50, step_ms=100, duration_ms=100
    )
    cache.save(audio, metadata, trace)
    monkeypatch.setattr(np, "savez_compressed", Mock(side_effect=OSError("failed")))

    with pytest.raises(OSError, match="failed"):
        cache.save(audio, metadata, trace)

    loaded = cache.load(audio, metadata)
    assert loaded is not None
    np.testing.assert_array_equal(loaded.scores, trace.scores)
