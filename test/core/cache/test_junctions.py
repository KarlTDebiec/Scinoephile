#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Windows junction containment regressions for cache maintenance."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.cache_namespace import CacheNamespace
from scinoephile.core.cache.cache_registry import CacheRegistry
from scinoephile.core.cache.operations import clear_cache, get_cache_entries

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows junction behavior")


class _CacheNamespace(CacheNamespace):
    """Namespace declarations for junction containment tests."""

    OPERATION = "llms/<operation>"
    """Operation-specific cache namespaces."""
    STATIC = "media/subtitles/analysis"
    """Nested static cache namespace."""


def test_cache_clear_does_not_follow_junction_entries(tmp_path: Path):
    """Remove direct and nested junction entries while preserving their targets.

    Arguments:
        tmp_path: temporary directory containing all test paths
    """
    cache_root_path = tmp_path / "cache"
    outside_dir_path = tmp_path / "authored"
    outside_dir_path.mkdir()
    authored_path = outside_dir_path / "subtitles.srt"
    authored_path.write_text("authored subtitles", encoding="utf-8")
    nested_dir_path = outside_dir_path / "nested"
    nested_dir_path.mkdir()
    (nested_dir_path / "notes.txt").write_text("authored notes", encoding="utf-8")
    registry = CacheRegistry(_CacheNamespace)

    for relative_link_path in (Path("linked"), Path("legacy/nested/linked")):
        link_path = cache_root_path / relative_link_path
        link_path.parent.mkdir(parents=True, exist_ok=True)
        with _junction(link_path, outside_dir_path):
            entries = clear_cache(
                cache_root_path, registry, entire_cache=True, dry_run=True
            )
            assert len(entries) == 1
            assert entries[0].file_count == 1

            clear_cache(cache_root_path, registry, entire_cache=True)

            assert not link_path.is_junction()
            assert authored_path.read_text(encoding="utf-8") == "authored subtitles"
            assert (nested_dir_path / "notes.txt").read_text(encoding="utf-8") == (
                "authored notes"
            )


@pytest.mark.parametrize("relative_link_path", ["entry", "entry/nested/link"])
def test_cache_clear_does_not_follow_registered_junction_entries(
    tmp_path: Path, relative_link_path: str
):
    """Clear registered entries without following direct or nested junctions.

    Arguments:
        tmp_path: temporary directory containing all test paths
        relative_link_path: junction location within the cache namespace
    """
    cache_root_path = tmp_path / "cache"
    namespace_dir_path = _CacheNamespace.STATIC.get_dir_path(cache_root_path)
    link_path = namespace_dir_path / relative_link_path
    link_path.parent.mkdir(parents=True, exist_ok=True)
    outside_dir_path = tmp_path / "authored"
    outside_dir_path.mkdir()
    authored_path = outside_dir_path / "subtitles.srt"
    authored_path.write_text("authored subtitles", encoding="utf-8")
    registry = CacheRegistry([_CacheNamespace.STATIC])

    with _junction(link_path, outside_dir_path):
        entries = get_cache_entries(cache_root_path, registry)
        assert len(entries) == 1
        assert entries[0].file_count == 1

        clear_cache(cache_root_path, registry, namespace=_CacheNamespace.STATIC)

        assert not namespace_dir_path.exists()
        assert authored_path.read_text(encoding="utf-8") == "authored subtitles"


@pytest.mark.parametrize(
    "relative_link_path", ["media", "media/subtitles", "media/subtitles/analysis"]
)
def test_cache_namespace_rejects_junction_ancestors(
    tmp_path: Path, relative_link_path: str
):
    """Reject linked namespace ancestors before discovering, writing, or clearing.

    Arguments:
        tmp_path: temporary directory containing all test paths
        relative_link_path: namespace component replaced with a junction
    """
    cache_root_path = tmp_path / "cache"
    link_path = cache_root_path / relative_link_path
    link_path.parent.mkdir(parents=True)
    outside_dir_path = tmp_path / "authored"
    namespace_suffix_path = Path(_CacheNamespace.STATIC.value).relative_to(
        relative_link_path
    )
    authored_path = outside_dir_path / namespace_suffix_path / "subtitles.srt"
    authored_path.parent.mkdir(parents=True)
    authored_path.write_text("authored subtitles", encoding="utf-8")
    registry = CacheRegistry([_CacheNamespace.STATIC])

    with _junction(link_path, outside_dir_path):
        assert _CacheNamespace.STATIC.discover_names(cache_root_path) == []
        with pytest.raises(ValueError, match="traverses symbolic link or junction"):
            _CacheNamespace.STATIC.get_dir_path(cache_root_path)
        assert get_cache_entries(cache_root_path, registry) == []
        with pytest.raises(ScinoephileError, match="was not found"):
            clear_cache(cache_root_path, registry, namespace=_CacheNamespace.STATIC)
        assert (
            clear_cache(
                cache_root_path, registry, entire_cache=True, older_than=timedelta(0)
            )
            == []
        )
        assert authored_path.read_text(encoding="utf-8") == "authored subtitles"


def test_cache_namespace_rejects_junction_operation(tmp_path: Path):
    """Ignore operation junctions and refuse to create namespaces through them.

    Arguments:
        tmp_path: temporary directory containing all test paths
    """
    cache_root_path = tmp_path / "cache"
    link_path = cache_root_path / "llms/review"
    link_path.parent.mkdir(parents=True)
    outside_dir_path = tmp_path / "authored"
    outside_dir_path.mkdir()
    authored_path = outside_dir_path / "review.json"
    authored_path.write_text("authored review", encoding="utf-8")
    registry = CacheRegistry([_CacheNamespace.OPERATION])

    with _junction(link_path, outside_dir_path):
        assert _CacheNamespace.OPERATION.discover_names(cache_root_path) == []
        with pytest.raises(ValueError, match="traverses symbolic link or junction"):
            _CacheNamespace.OPERATION.get_dir_path(cache_root_path, operation="review")
        assert get_cache_entries(cache_root_path, registry) == []
        clear_cache(cache_root_path, registry, entire_cache=True)
        assert authored_path.read_text(encoding="utf-8") == "authored review"


def test_cache_root_may_be_a_deliberately_selected_junction(tmp_path: Path):
    """Preserve support for a selected cache root located through a junction.

    Arguments:
        tmp_path: temporary directory containing all test paths
    """
    cache_root_path = tmp_path / "cache"
    target_dir_path = tmp_path / "cache-storage"
    target_dir_path.mkdir()
    registry = CacheRegistry([_CacheNamespace.STATIC])

    with _junction(cache_root_path, target_dir_path):
        namespace_dir_path = _CacheNamespace.STATIC.get_dir_path(cache_root_path)
        entry_path = namespace_dir_path / "entry.json"
        entry_path.write_text("cached", encoding="utf-8")
        assert registry.discover_names(cache_root_path) == [_CacheNamespace.STATIC]

        clear_cache(cache_root_path, registry, namespace=_CacheNamespace.STATIC)

        assert not entry_path.exists()
        assert cache_root_path.is_junction()
        assert target_dir_path.is_dir()


def test_remove_cache_artifact_unlinks_junction(tmp_path: Path):
    """Remove a junction artifact without removing its target contents.

    Arguments:
        tmp_path: temporary directory containing all test paths
    """
    target_dir_path = tmp_path / "authored"
    target_dir_path.mkdir()
    authored_path = target_dir_path / "subtitles.srt"
    authored_path.write_text("authored subtitles", encoding="utf-8")
    link_path = tmp_path / "entry"

    with _junction(link_path, target_dir_path):
        assert remove_cache_artifact(link_path)
        assert not link_path.is_junction()
        assert authored_path.read_text(encoding="utf-8") == "authored subtitles"


@contextmanager
def _junction(link_path: Path, target_dir_path: Path) -> Generator[Path]:
    """Create a test junction and remove only its link during cleanup.

    Arguments:
        link_path: temporary junction path
        target_dir_path: temporary target directory
    Yields:
        created junction path
    """
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link_path), str(target_dir_path)],
        check=True,
        capture_output=True,
    )
    try:
        yield link_path
    finally:
        if link_path.is_junction():
            link_path.rmdir()
