#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache operations."""

from __future__ import annotations

from datetime import timedelta
from os import utime
from pathlib import Path
from time import time

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import (
    clear_cache,
    discover_cache_namespaces,
    get_cache_entries,
    get_cache_stats,
    prune_cache,
)


def test_discover_cache_namespaces(tmp_path: Path):
    """Test dynamic namespace discovery.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json")
    _write_cache_file(tmp_path / "whisper" / "two.json")
    _write_cache_file(tmp_path / "root.json")

    assert discover_cache_namespaces(tmp_path) == ["llm", "whisper"]


def test_get_cache_entries_filters_namespace(tmp_path: Path):
    """Test cache entry inspection with namespace filtering.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json", "one")
    _write_cache_file(tmp_path / "whisper" / "two.json", "two")

    entries = get_cache_entries(tmp_path, namespace="llm")

    assert len(entries) == 1
    assert entries[0].namespace == "llm"
    assert entries[0].relative_path == Path("llm/one.json")
    assert entries[0].size_bytes == 3


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
    _write_cache_file(tmp_path / "llm" / "one.json")

    with pytest.raises(ScinoephileError, match="was not found"):
        get_cache_entries(tmp_path, namespace="ocr")


def test_get_cache_stats(tmp_path: Path):
    """Test aggregate cache statistics.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json", "one")
    _write_cache_file(tmp_path / "llm" / "two.json", "two")
    _write_cache_file(tmp_path / "whisper" / "three.json", "three")

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
    old_path = _write_cache_file(tmp_path / "llm" / "old.json")
    new_path = _write_cache_file(tmp_path / "llm" / "new.json")
    old_timestamp = time() - 60 * 60 * 24 * 40
    old_path.touch()
    new_path.touch()
    _set_mtime(old_path, old_timestamp)

    deleted_entries = prune_cache(tmp_path, older_than=timedelta(days=30))

    assert [entry.relative_path for entry in deleted_entries] == [Path("llm/old.json")]
    assert not old_path.exists()
    assert new_path.exists()


def test_clear_cache_namespace(tmp_path: Path):
    """Test confirmed namespace clearing.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json")
    whisper_path = _write_cache_file(tmp_path / "whisper" / "two.json")

    deleted_entries = clear_cache(tmp_path, namespace="llm")

    assert [entry.relative_path for entry in deleted_entries] == [Path("llm/one.json")]
    assert not (tmp_path / "llm").exists()
    assert whisper_path.exists()


def _set_mtime(path: Path, timestamp: float):
    """Set a path modification and access time.

    Arguments:
        path: path to modify
        timestamp: timestamp to set
    """
    utime(path, (timestamp, timestamp))


def _write_cache_file(path: Path, text: str = "{}") -> Path:
    """Write a cache file.

    Arguments:
        path: path to write
        text: text to write
    Returns:
        written path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
