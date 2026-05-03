#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.cache.operations."""

from __future__ import annotations

import os
import time
from datetime import timedelta
from pathlib import Path

import pytest

from scinoephile.core.cache.operations import (
    clear_entries,
    discover_namespaces,
    get_stats,
    list_entries,
    prune_entries,
)


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory with test entries.

    Arguments:
        tmp_path: pytest temporary directory
    Returns:
        populated cache directory path
    """
    llm_dir = tmp_path / "llm"
    llm_dir.mkdir()
    (llm_dir / "abc123.json").write_text('{"result": 1}')
    (llm_dir / "def456.json").write_text('{"result": 2}')

    transcription_dir = tmp_path / "transcription"
    transcription_dir.mkdir()
    (transcription_dir / "xyz789.json").write_text('{"segments": []}')

    return tmp_path


def test_discover_namespaces(cache_dir: Path):
    """Test that namespace discovery finds all subdirectories.

    Arguments:
        cache_dir: populated cache directory
    """
    namespaces = discover_namespaces(cache_dir)
    assert namespaces == ["llm", "transcription"]


def test_discover_namespaces_missing_dir(tmp_path: Path):
    """Test that discovery on a non-existent directory returns empty list.

    Arguments:
        tmp_path: pytest temporary directory
    """
    missing = tmp_path / "nonexistent"
    assert discover_namespaces(missing) == []


def test_list_entries_all_namespaces(cache_dir: Path):
    """Test listing all entries across namespaces.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = list_entries(cache_dir)
    namespaces = {e.namespace for e in entries}
    assert "llm" in namespaces
    assert "transcription" in namespaces
    assert len(entries) == 3


def test_list_entries_filtered_namespace(cache_dir: Path):
    """Test listing entries filtered to a single namespace.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = list_entries(cache_dir, namespace="llm")
    assert all(e.namespace == "llm" for e in entries)
    assert len(entries) == 2


def test_list_entries_invalid_namespace(cache_dir: Path):
    """Test that requesting a non-existent namespace raises ValueError.

    Arguments:
        cache_dir: populated cache directory
    """
    with pytest.raises(ValueError, match="not found"):
        list_entries(cache_dir, namespace="nonexistent")


def test_list_entries_missing_cache_dir(tmp_path: Path):
    """Test that listing from a non-existent cache dir returns empty list.

    Arguments:
        tmp_path: pytest temporary directory
    """
    missing = tmp_path / "nonexistent"
    assert list_entries(missing) == []


def test_list_entries_sort_by_name(cache_dir: Path):
    """Test that entries are sorted by name by default.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = list_entries(cache_dir, sort="name")
    keys = [(e.namespace, str(e.rel_path)) for e in entries]
    assert keys == sorted(keys)


def test_list_entries_sort_by_size(cache_dir: Path):
    """Test that entries can be sorted by size.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = list_entries(cache_dir, sort="size")
    sizes = [e.size for e in entries]
    assert sizes == sorted(sizes)


def test_list_entries_limit(cache_dir: Path):
    """Test that limit constrains the number of entries returned.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = list_entries(cache_dir, limit=2)
    assert len(entries) == 2


def test_get_stats_all(cache_dir: Path):
    """Test aggregate stats across all namespaces.

    Arguments:
        cache_dir: populated cache directory
    """
    stats = get_stats(cache_dir)
    assert stats["total"]["count"] == 3
    assert stats["total"]["size"] > 0
    ns_names = {ns["namespace"] for ns in stats["namespaces"]}
    assert ns_names == {"llm", "transcription"}


def test_get_stats_namespace(cache_dir: Path):
    """Test aggregate stats filtered to one namespace.

    Arguments:
        cache_dir: populated cache directory
    """
    stats = get_stats(cache_dir, namespace="llm")
    assert stats["total"]["count"] == 2
    assert len(stats["namespaces"]) == 1
    assert stats["namespaces"][0]["namespace"] == "llm"


def test_get_stats_missing_cache_dir(tmp_path: Path):
    """Test that stats on a missing directory returns zero counts.

    Arguments:
        tmp_path: pytest temporary directory
    """
    missing = tmp_path / "nonexistent"
    stats = get_stats(missing)
    assert stats["total"]["count"] == 0
    assert stats["namespaces"] == []


def test_prune_dry_run(cache_dir: Path):
    """Test that dry-run prune reports entries without deleting them.

    Arguments:
        cache_dir: populated cache directory
    """
    # All entries were just created; set mtime back in time so prune finds them
    llm_file = cache_dir / "llm" / "abc123.json"
    old_time = time.time() - 10 * 24 * 3600  # 10 days ago
    os.utime(llm_file, (old_time, old_time))

    entries = prune_entries(cache_dir, older_than=timedelta(days=7), dry_run=True)
    assert any(str(e.rel_path) == "abc123.json" for e in entries)
    # File should still exist (dry-run)
    assert llm_file.exists()


def test_prune_confirmed(cache_dir: Path):
    """Test that confirmed prune actually deletes old entries.

    Arguments:
        cache_dir: populated cache directory
    """
    llm_file = cache_dir / "llm" / "abc123.json"
    old_time = time.time() - 10 * 24 * 3600
    os.utime(llm_file, (old_time, old_time))

    entries = prune_entries(cache_dir, older_than=timedelta(days=7), dry_run=False)
    assert any(str(e.rel_path) == "abc123.json" for e in entries)
    assert not llm_file.exists()


def test_prune_no_matches(cache_dir: Path):
    """Test that prune with a very short cutoff finds nothing to delete.

    Arguments:
        cache_dir: populated cache directory
    """
    # Entries were just created; a 1-second cutoff should find nothing old
    entries = prune_entries(cache_dir, older_than=timedelta(seconds=1), dry_run=True)
    assert entries == []


def test_clear_dry_run(cache_dir: Path):
    """Test that dry-run clear reports entries without deleting them.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = clear_entries(cache_dir, namespace="llm", dry_run=True)
    assert len(entries) == 2
    assert (cache_dir / "llm" / "abc123.json").exists()


def test_clear_confirmed(cache_dir: Path):
    """Test that confirmed clear removes all entries from the namespace.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = clear_entries(cache_dir, namespace="llm", dry_run=False)
    assert len(entries) == 2
    assert not (cache_dir / "llm" / "abc123.json").exists()
    assert not (cache_dir / "llm" / "def456.json").exists()


def test_clear_all_namespaces(cache_dir: Path):
    """Test clearing every namespace at once.

    Arguments:
        cache_dir: populated cache directory
    """
    entries = clear_entries(cache_dir, all_namespaces=True, dry_run=False)
    assert len(entries) == 3
    assert list_entries(cache_dir) == []


def test_clear_missing_namespace(cache_dir: Path):
    """Test that clearing a non-existent namespace raises ValueError.

    Arguments:
        cache_dir: populated cache directory
    """
    with pytest.raises(ValueError, match="not found"):
        clear_entries(cache_dir, namespace="nonexistent", dry_run=True)


def test_clear_missing_cache_dir(tmp_path: Path):
    """Test that clearing on a missing directory returns empty list.

    Arguments:
        tmp_path: pytest temporary directory
    """
    missing = tmp_path / "nonexistent"
    entries = clear_entries(missing, all_namespaces=True, dry_run=True)
    assert entries == []


def test_clear_requires_namespace_or_all(cache_dir: Path):
    """Test that clear raises ValueError when no namespace or all_namespaces given.

    Arguments:
        cache_dir: populated cache directory
    """
    with pytest.raises(ValueError, match="namespace or all_namespaces"):
        clear_entries(cache_dir, dry_run=True)
