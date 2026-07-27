#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of TranscriptionCache."""

from __future__ import annotations

import json
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.transcription import (
    TranscribedSegment,
    TranscriptionCache,
)


def test_transcription_cache_round_trip(tmp_path: Path):
    """Test timestamped transcription output round-trips through the cache.

    Arguments:
        tmp_path: temporary cache directory path
    """
    cache = TranscriptionCache(tmp_path, "test", "Test")
    audio = AudioSegment.silent(duration=100)
    metadata = {"model_name": "test/model"}
    segments = [
        TranscribedSegment(
            id=0,
            seek=0,
            start=0.0,
            end=0.1,
            text="test",
        )
    ]

    cache_path = cache.save(audio, metadata, segments)
    cached_transcription = cache.load(audio, metadata)

    assert cache_path is not None
    assert cache_path.parent == tmp_path / "test"
    assert cached_transcription == (cache_path, segments)
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["metadata"]["backend"] == "test"
    assert payload["metadata"]["audio_frame_rate"] == audio.frame_rate


def test_transcription_cache_discards_mismatched_metadata(tmp_path: Path):
    """Test cached payload metadata mismatch is discarded as a cache miss.

    Arguments:
        tmp_path: temporary cache directory path
    """
    cache = TranscriptionCache(tmp_path, "test", "Test")
    audio = AudioSegment.silent(duration=100)
    metadata = {"model_name": "test/model"}
    cache_path = cache.save(audio, metadata, [])
    assert cache_path is not None
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["metadata"]["model_name"] = "other/model"
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(audio, metadata) is None
    assert not cache_path.exists()


def test_transcription_cache_can_be_disabled():
    """Test cache operations are no-ops when no directory is configured."""
    cache = TranscriptionCache(None, "test", "Test")
    audio = AudioSegment.silent(duration=100)
    metadata = {"model_name": "test/model"}

    assert cache.get_path(audio, metadata) is None
    assert cache.load(audio, metadata) is None
    assert cache.remove(audio, metadata) is None
    assert cache.save(audio, metadata, []) is None
