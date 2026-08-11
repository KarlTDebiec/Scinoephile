#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache operations."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from time import time

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import (
    clear_cache,
    discover_cache_namespaces,
    get_cache_entries,
    get_cache_stats,
    prune_cache,
)
from test.helpers.files import set_mtime, write_cache_file


def test_discover_cache_namespaces(tmp_path: Path):
    """Test dynamic namespace discovery.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/one.json")
    write_cache_file(tmp_path / "whisper/two.json")
    write_cache_file(tmp_path / "root.json")

    assert discover_cache_namespaces(tmp_path) == ["llm", "whisper"]


def test_get_cache_entries_filters_namespace(tmp_path: Path):
    """Test cache entry inspection with namespace filtering.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/one.json", "one")
    write_cache_file(tmp_path / "whisper/two.json", "two")

    entries = get_cache_entries(tmp_path, namespace="llm")

    assert len(entries) == 1
    assert entries[0].namespace == "llm"
    assert entries[0].relative_path == Path("llm/one.json")
    assert entries[0].size_bytes == 3


def test_get_cache_entries_supports_nested_media_namespaces(tmp_path: Path):
    """Test nested media namespaces retain individual cache entries.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt", "one")
    write_cache_file(tmp_path / "media/subtitles/second/3.sup", "two")
    write_cache_file(
        tmp_path / "media/subtitles/second/image-series/index.html", "index"
    )
    write_cache_file(tmp_path / "media/subtitles/analysis/first.json", "analysis")

    assert discover_cache_namespaces(tmp_path) == [
        "media/subtitles",
        "media/subtitles/analysis",
    ]

    subtitle_entries = get_cache_entries(tmp_path, namespace="media/subtitles")
    analysis_entries = get_cache_entries(tmp_path, namespace="media/subtitles/analysis")

    assert [entry.relative_path for entry in subtitle_entries] == [
        Path("media/subtitles/first"),
        Path("media/subtitles/second"),
    ]
    assert [entry.file_count for entry in subtitle_entries] == [1, 2]
    assert [entry.relative_path for entry in analysis_entries] == [
        Path("media/subtitles/analysis/first.json")
    ]


def test_get_cache_entries_supports_grouped_llm_namespaces(tmp_path: Path):
    """Test each LLM operation is exposed as an independent namespace."""
    write_cache_file(tmp_path / "llm/translation/one.json", "one")
    write_cache_file(tmp_path / "llm/review/two.json", "two")

    assert discover_cache_namespaces(tmp_path) == ["llm/review", "llm/translation"]
    entries = get_cache_entries(tmp_path, namespace="llm/translation")

    assert [entry.relative_path for entry in entries] == [
        Path("llm/translation/one.json")
    ]


def test_prune_cache_prunes_individual_nested_namespace_entries(tmp_path: Path):
    """Test nested cache namespaces preserve entry-level pruning.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    old_path = write_cache_file(tmp_path / "media/subtitles/old/2.srt")
    new_path = write_cache_file(tmp_path / "media/subtitles/new/3.srt")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(old_path, old_timestamp)
    set_mtime(old_path.parent, old_timestamp)

    deleted_entries = prune_cache(
        tmp_path, older_than=timedelta(days=30), namespace="media/subtitles"
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

    clear_cache(tmp_path, namespace="media/subtitles")

    assert not (tmp_path / "media").exists()


def test_clear_cache_preserves_nested_namespace(tmp_path: Path):
    """Test clearing a namespace preserves its nested namespaces.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt")
    analysis_path = write_cache_file(tmp_path / "media/subtitles/analysis/first.json")

    clear_cache(tmp_path, namespace="media/subtitles")

    assert analysis_path.exists()
    assert discover_cache_namespaces(tmp_path) == [
        "media/subtitles",
        "media/subtitles/analysis",
    ]


def test_clear_cache_removes_empty_parent_namespaces(tmp_path: Path):
    """Test clearing a nested namespace removes empty grouping directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/analysis/first.json")

    clear_cache(tmp_path, namespace="media/subtitles/analysis")

    assert not (tmp_path / "media").exists()


def test_clear_cache_all_removes_nested_namespaces(tmp_path: Path):
    """Test clearing all namespaces handles nested namespaces deepest first.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    write_cache_file(tmp_path / "media/subtitles/first/2.srt")
    write_cache_file(tmp_path / "media/subtitles/analysis/first.json")

    clear_cache(tmp_path, all_namespaces=True)

    assert not (tmp_path / "media").exists()


def test_get_cache_entries_missing_root_is_empty(tmp_path: Path):
    """Test that missing cache roots produce empty entries.

    Arguments:
        tmp_path: temporary directory
    """
    assert get_cache_entries(tmp_path / "missing") == []


def test_get_cache_entries_invalid_namespace(tmp_path: Path):
    """Test that explicit invalid namespaces fail clearly.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/one.json")

    with raises(ScinoephileError, match="was not found"):
        get_cache_entries(tmp_path, namespace="ocr")


def test_get_cache_stats(tmp_path: Path):
    """Test aggregate cache statistics.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/one.json", "one")
    write_cache_file(tmp_path / "llm/two.json", "two")
    write_cache_file(tmp_path / "whisper/three.json", "three")

    stats_by_namespace = get_cache_stats(tmp_path)
    stats = {
        namespace_stats.namespace: namespace_stats
        for namespace_stats in stats_by_namespace
    }

    assert stats["llm"].entry_count == 2
    assert stats["llm"].total_bytes == 6
    assert stats["whisper"].entry_count == 1
    assert stats["total"].entry_count == 3
    assert stats["total"].total_bytes == 11


def test_prune_cache(tmp_path: Path):
    """Test confirmed cache pruning.

    Arguments:
        tmp_path: temporary directory
    """
    old_path = write_cache_file(tmp_path / "llm/old.json")
    new_path = write_cache_file(tmp_path / "llm/new.json")
    old_timestamp = time() - 60 * 60 * 24 * 40
    old_path.touch()
    new_path.touch()
    set_mtime(old_path, old_timestamp)

    deleted_entries = prune_cache(tmp_path, older_than=timedelta(days=30))

    assert [entry.relative_path for entry in deleted_entries] == [Path("llm/old.json")]
    assert not old_path.exists()
    assert new_path.exists()


def test_clear_cache_namespace(tmp_path: Path):
    """Test confirmed namespace clearing.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/one.json")
    whisper_path = write_cache_file(tmp_path / "whisper/two.json")

    deleted_entries = clear_cache(tmp_path, namespace="llm")

    assert [entry.relative_path for entry in deleted_entries] == [Path("llm/one.json")]
    assert not (tmp_path / "llm").exists()
    assert whisper_path.exists()
