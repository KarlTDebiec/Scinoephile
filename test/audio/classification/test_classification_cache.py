#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of persistent audio classification caching."""

from __future__ import annotations

import json
from os import utime
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.classification import (
    AudioClassificationCache,
    LanguageIdentificationResult,
)


def test_classification_cache_discards_invalid_payload(tmp_path: Path):
    """Remove malformed cache data and allow regeneration.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = AudioClassificationCache(tmp_path, AudioCacheNamespace.CLASSIFICATION_EVENT)
    audio = AudioSegment.silent(duration=100)
    cache_identity = {"model": "test/model"}
    cache_path = cache.get_path(audio, cache_identity)
    cache_path.write_text("not JSON", encoding="utf-8")

    assert cache.load(audio, cache_identity, LanguageIdentificationResult) is None
    assert not cache_path.exists()


def test_classification_cache_discards_unsupported_version(tmp_path: Path):
    """Remove cache data written with an unsupported format version.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = AudioClassificationCache(
        tmp_path, AudioCacheNamespace.CLASSIFICATION_LANGUAGE
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity = {"model": "test/model"}
    result = LanguageIdentificationResult(spans=[])
    cache_path = cache.save(audio, cache_identity, result)
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_version"] = 0
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(audio, cache_identity, LanguageIdentificationResult) is None
    assert not cache_path.exists()


def test_classification_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Refresh a requested entry once, then reuse its replacement.

    Arguments:
        tmp_path: temporary cache root path
    """
    audio = AudioSegment.silent(duration=100)
    cache_identity = {"model": "test/model"}
    result = LanguageIdentificationResult(spans=[])
    AudioClassificationCache(
        tmp_path, AudioCacheNamespace.CLASSIFICATION_LANGUAGE
    ).save(audio, cache_identity, result)
    overwrite_cache = AudioClassificationCache(
        tmp_path, AudioCacheNamespace.CLASSIFICATION_LANGUAGE, overwrite=True
    )

    assert (
        overwrite_cache.load(audio, cache_identity, LanguageIdentificationResult)
        is None
    )
    overwrite_cache.save(audio, cache_identity, result)

    assert (
        overwrite_cache.load(audio, cache_identity, LanguageIdentificationResult)
        == result
    )


def test_classification_cache_round_trip(tmp_path: Path):
    """Persist a result in its registered namespace without loss.

    Arguments:
        tmp_path: temporary cache root path
    """
    cache = AudioClassificationCache(
        tmp_path, AudioCacheNamespace.CLASSIFICATION_LANGUAGE
    )
    audio = AudioSegment.silent(duration=100)
    cache_identity = {"model": "test/model"}
    result = LanguageIdentificationResult(spans=[])

    cache_path = cache.save(audio, cache_identity, result)
    utime(cache_path, (1, 1))
    loaded = cache.load(audio, cache_identity, LanguageIdentificationResult)

    assert cache_path.parent == tmp_path / "audio/classification/language"
    assert loaded == result
    assert cache_path.stat().st_mtime > 1


def test_classification_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Use the runtime cache root when none is configured.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = AudioClassificationCache(None, AudioCacheNamespace.CLASSIFICATION_LANGUAGE)

    assert cache.cache_root_path == runtime_cache_root_path
    assert (
        cache.cache_dir_path
        == runtime_cache_root_path / "audio/classification/language"
    )
