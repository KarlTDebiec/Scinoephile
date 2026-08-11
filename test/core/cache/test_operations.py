#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache operations."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from time import time

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.cache.cache_namespace import CacheNamespace
from scinoephile.core.cache.cache_registry import CacheRegistry
from scinoephile.core.cache.operations import (
    clear_cache,
    get_cache_entries,
    get_cache_stats,
    prune_cache,
)
from test.helpers.files import set_mtime, write_cache_file


class _CacheNamespace(CacheNamespace):
    """Cache namespace declarations for maintenance operation tests."""

    AUDIO_CLASSIFICATION_OPERATION = "audio/classification/<operation>"
    """Operation-specific audio classification artifacts."""
    AUDIO_DIARIZATION = "audio/diarization"
    """Audio diarization artifacts."""
    AUDIO_SEPARATION_DEMUCS = "audio/separation/demucs"
    """Demucs-separated audio."""
    AUDIO_TRANSCRIPTION_WHISPER = "audio/transcription/whisper"
    """Whisper transcription results."""
    AUDIO_VAD = "audio/vad"
    """Voice activity detection traces."""
    LANG_ZHO_SUBTITLES_ANALYSIS = "lang/zho/subtitles/analysis"
    """Chinese subtitle script analysis results."""
    LLMS_OPERATION = "llms/<operation>"
    """Operation-specific LLM responses."""
    MEDIA_SUBTITLES = "media/subtitles"
    """Extracted subtitle streams and image series."""


_CACHE_REGISTRY = CacheRegistry(_CacheNamespace)
"""Cache namespace registry for maintenance operation tests."""


def test_cache_registry_discovers_namespaces(tmp_path: Path):
    """Test registry-backed namespace discovery.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llms/test/one.json")
    write_cache_file(tmp_path / "audio/transcription/whisper/two.json")
    write_cache_file(tmp_path / "huggingface/hub/model/data.json")
    write_cache_file(tmp_path / "torch/hub/model/data.json")
    write_cache_file(tmp_path / "root.json")

    assert _CACHE_REGISTRY.discover_names(tmp_path) == [
        "audio/transcription/whisper",
        "llms/test",
    ]


def test_get_cache_entries_filters_namespace(tmp_path: Path):
    """Test cache entry inspection with namespace filtering.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llms/test/one.json", "one")
    write_cache_file(tmp_path / "audio/transcription/whisper/two.json", "two")

    entries = get_cache_entries(tmp_path, _CACHE_REGISTRY, namespace="llms/test")

    assert len(entries) == 1
    assert entries[0].namespace == "llms/test"
    assert entries[0].relative_path == Path("llms/test/one.json")
    assert entries[0].size_bytes == 3


def test_get_cache_entries_separates_subtitles_by_owner(tmp_path: Path):
    """Test media artifacts and language analysis use independent namespaces.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt", "one")
    write_cache_file(tmp_path / "media/subtitles/second/3.sup", "two")
    write_cache_file(
        tmp_path / "media/subtitles/second/image-series/index.html", "index"
    )
    write_cache_file(tmp_path / "lang/zho/subtitles/analysis/first.json", "analysis")

    assert _CACHE_REGISTRY.discover_names(tmp_path) == [
        "lang/zho/subtitles/analysis",
        "media/subtitles",
    ]

    subtitle_entries = get_cache_entries(
        tmp_path, _CACHE_REGISTRY, namespace="media/subtitles"
    )
    analysis_entries = get_cache_entries(
        tmp_path, _CACHE_REGISTRY, namespace="lang/zho/subtitles/analysis"
    )

    assert [entry.relative_path for entry in subtitle_entries] == [
        Path("media/subtitles/first"),
        Path("media/subtitles/second"),
    ]
    assert [entry.file_count for entry in subtitle_entries] == [1, 2]
    assert [entry.relative_path for entry in analysis_entries] == [
        Path("lang/zho/subtitles/analysis/first.json")
    ]


def test_get_cache_entries_supports_grouped_llm_namespaces(tmp_path: Path):
    """Test each LLM operation is exposed as an independent namespace."""
    write_cache_file(tmp_path / "llms/translation/one.json", "one")
    write_cache_file(tmp_path / "llms/review/two.json", "two")

    assert _CACHE_REGISTRY.discover_names(tmp_path) == [
        "llms/review",
        "llms/translation",
    ]
    entries = get_cache_entries(tmp_path, _CACHE_REGISTRY, namespace="llms/translation")

    assert [entry.relative_path for entry in entries] == [
        Path("llms/translation/one.json")
    ]


def test_get_cache_entries_supports_grouped_audio_namespaces(tmp_path: Path):
    """Test audio analyses are exposed as independent cache namespaces."""
    write_cache_file(tmp_path / "audio/classification/language/one.json", "one")
    write_cache_file(tmp_path / "audio/diarization/one.json", "one")
    write_cache_file(tmp_path / "audio/separation/demucs/one.wav", "one")
    write_cache_file(tmp_path / "audio/vad/one.npz", "one")

    assert _CACHE_REGISTRY.discover_names(tmp_path) == [
        "audio/classification/language",
        "audio/diarization",
        "audio/separation/demucs",
        "audio/vad",
    ]
    entries = get_cache_entries(
        tmp_path, _CACHE_REGISTRY, namespace="audio/classification/language"
    )

    assert [entry.relative_path for entry in entries] == [
        Path("audio/classification/language/one.json")
    ]


def test_prune_cache_prunes_individual_directory_entries(tmp_path: Path):
    """Test directory-based cache entries preserve entry-level pruning.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    old_path = write_cache_file(tmp_path / "media/subtitles/old/2.srt")
    new_path = write_cache_file(tmp_path / "media/subtitles/new/3.srt")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(old_path, old_timestamp)
    set_mtime(old_path.parent, old_timestamp)

    deleted_entries = prune_cache(
        tmp_path,
        _CACHE_REGISTRY,
        older_than=timedelta(days=30),
        namespace="media/subtitles",
    )

    assert [entry.relative_path for entry in deleted_entries] == [
        Path("media/subtitles/old")
    ]
    assert not old_path.exists()
    assert new_path.exists()


def test_clear_cache_removes_empty_grouping_directory(tmp_path: Path):
    """Test clearing the last grouped namespace removes its grouping directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt")

    clear_cache(tmp_path, _CACHE_REGISTRY, namespace="media/subtitles")

    assert not (tmp_path / "media").exists()


def test_clear_cache_preserves_other_owner_namespace(tmp_path: Path):
    """Test clearing media subtitles preserves language analysis.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt")
    analysis_path = write_cache_file(
        tmp_path / "lang/zho/subtitles/analysis/first.json"
    )

    clear_cache(tmp_path, _CACHE_REGISTRY, namespace="media/subtitles")

    assert analysis_path.exists()
    assert _CACHE_REGISTRY.discover_names(tmp_path) == ["lang/zho/subtitles/analysis"]


def test_clear_cache_removes_empty_parent_directories(tmp_path: Path):
    """Test clearing a namespace removes empty grouping directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "lang/zho/subtitles/analysis/first.json")

    clear_cache(tmp_path, _CACHE_REGISTRY, namespace="lang/zho/subtitles/analysis")

    assert not (tmp_path / "lang").exists()


def test_clear_cache_all_removes_all_registered_namespaces(tmp_path: Path):
    """Test clearing all namespaces removes every registered namespace.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt")
    write_cache_file(tmp_path / "lang/zho/subtitles/analysis/first.json")
    external_path = write_cache_file(tmp_path / "huggingface/hub/model/data.json")

    clear_cache(tmp_path, _CACHE_REGISTRY, all_namespaces=True)

    assert not (tmp_path / "media").exists()
    assert not (tmp_path / "lang").exists()
    assert external_path.exists()


def test_get_cache_entries_missing_root_is_empty(tmp_path: Path):
    """Test that missing cache roots produce empty entries.

    Arguments:
        tmp_path: temporary directory
    """
    assert get_cache_entries(tmp_path / "missing", _CACHE_REGISTRY) == []


def test_get_cache_entries_invalid_namespace(tmp_path: Path):
    """Test that explicit invalid namespaces fail clearly.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llms/test/one.json")

    with raises(ScinoephileError, match="was not found"):
        get_cache_entries(tmp_path, _CACHE_REGISTRY, namespace="ocr")


def test_get_cache_stats(tmp_path: Path):
    """Test aggregate cache statistics.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llms/test/one.json", "one")
    write_cache_file(tmp_path / "llms/test/two.json", "two")
    write_cache_file(tmp_path / "audio/transcription/whisper/three.json", "three")

    stats_by_namespace = get_cache_stats(tmp_path, _CACHE_REGISTRY)
    stats = {
        namespace_stats.namespace: namespace_stats
        for namespace_stats in stats_by_namespace
    }

    assert stats["llms/test"].entry_count == 2
    assert stats["llms/test"].total_bytes == 6
    assert stats["audio/transcription/whisper"].entry_count == 1
    assert stats["total"].entry_count == 3
    assert stats["total"].total_bytes == 11


def test_prune_cache(tmp_path: Path):
    """Test confirmed cache pruning.

    Arguments:
        tmp_path: temporary directory
    """
    old_path = write_cache_file(tmp_path / "llms/test/old.json")
    new_path = write_cache_file(tmp_path / "llms/test/new.json")
    old_timestamp = time() - 60 * 60 * 24 * 40
    old_path.touch()
    new_path.touch()
    set_mtime(old_path, old_timestamp)

    deleted_entries = prune_cache(
        tmp_path, _CACHE_REGISTRY, older_than=timedelta(days=30)
    )

    assert [entry.relative_path for entry in deleted_entries] == [
        Path("llms/test/old.json")
    ]
    assert not old_path.exists()
    assert new_path.exists()


def test_clear_cache_namespace(tmp_path: Path):
    """Test confirmed namespace clearing.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llms/test/one.json")
    whisper_path = write_cache_file(tmp_path / "audio/transcription/whisper/two.json")

    deleted_entries = clear_cache(tmp_path, _CACHE_REGISTRY, namespace="llms/test")

    assert [entry.relative_path for entry in deleted_entries] == [
        Path("llms/test/one.json")
    ]
    assert not (tmp_path / "llms").exists()
    assert whisper_path.exists()
