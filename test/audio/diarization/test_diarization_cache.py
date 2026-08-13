#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of persistent speaker diarization caching."""

from __future__ import annotations

import json
from os import utime
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.diarization import (
    SpeakerDiarizationCache,
    SpeakerDiarizationResult,
    SpeakerTurn,
)


def test_diarization_cache_round_trip(tmp_path: Path):
    """Persist diarization output in its registered namespace without loss.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = SpeakerDiarizationCache(tmp_path)
    audio = AudioSegment.silent(duration=100)
    metadata = {"model": "test/model"}
    result = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=0.0, end=0.1, speaker="SPEAKER_00")],
        exclusive_turns=[SpeakerTurn(start=0.0, end=0.1, speaker="SPEAKER_00")],
    )

    cache_path = cache.save(audio, metadata, result)
    utime(cache_path, (1, 1))
    loaded = cache.load(audio, metadata)

    assert cache_path.parent == tmp_path / "audio/diarization"
    assert loaded == result
    assert cache_path.stat().st_mtime > 1


def test_diarization_cache_discards_invalid_payload(tmp_path: Path):
    """Remove malformed cache data and allow regeneration.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = SpeakerDiarizationCache(tmp_path)
    audio = AudioSegment.silent(duration=100)
    metadata = {"model": "test/model"}
    cache_path = cache.get_path(audio, metadata)
    cache_path.write_text("not JSON", encoding="utf-8")

    assert cache.load(audio, metadata) is None
    assert not cache_path.exists()


def test_diarization_cache_discards_unsupported_version(tmp_path: Path):
    """Remove cache data written with an unsupported format version.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = SpeakerDiarizationCache(tmp_path)
    audio = AudioSegment.silent(duration=100)
    metadata = {"model": "test/model"}
    result = SpeakerDiarizationResult(turns=[], exclusive_turns=[])
    cache_path = cache.save(audio, metadata, result)
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_version"] = 0
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(audio, metadata) is None
    assert not cache_path.exists()


def test_diarization_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Refresh a requested entry once, then reuse its replacement.

    Arguments:
        tmp_path: temporary cache root path
    """
    audio = AudioSegment.silent(duration=100)
    metadata = {"model": "test/model"}
    result = SpeakerDiarizationResult(turns=[], exclusive_turns=[])
    SpeakerDiarizationCache(tmp_path).save(audio, metadata, result)
    overwrite_cache = SpeakerDiarizationCache(tmp_path, overwrite=True)

    assert overwrite_cache.load(audio, metadata) is None
    overwrite_cache.save(audio, metadata, result)

    assert overwrite_cache.load(audio, metadata) == result


def test_diarization_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Use the runtime cache root when none is configured.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = SpeakerDiarizationCache(None)

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.cache_dir_path == runtime_cache_root_path / "audio/diarization"
