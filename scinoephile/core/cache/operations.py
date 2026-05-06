#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Directory-based cache inspection and invalidation operations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

from scinoephile.core.exceptions import ScinoephileError

from .cache_entry import CacheEntry
from .cache_stats import CacheStats

__all__ = [
    "CacheEntry",
    "CacheStats",
    "clear_cache",
    "discover_cache_namespaces",
    "get_cache_entries",
    "get_cache_stats",
    "prune_cache",
]


def clear_cache(
    cache_dir_path: Path, *, namespace: str | None = None, all_namespaces: bool = False
) -> list[CacheEntry]:
    """Clear one namespace or every discovered namespace.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: optional namespace to clear
        all_namespaces: whether to clear every discovered namespace
    Returns:
        entries that were deleted
    Raises:
        ScinoephileError: if the arguments are invalid
    """
    if namespace is None and not all_namespaces:
        raise ScinoephileError("--namespace is required unless --all is specified")
    if namespace is not None and all_namespaces:
        raise ScinoephileError("--namespace and --all may not be used together")

    entries = get_cache_entries(cache_dir_path, namespace=namespace)
    for entry in entries:
        _delete_entry(entry.path)
    for namespace_name in _namespaces_to_clear(
        cache_dir_path, namespace=namespace, all_namespaces=all_namespaces
    ):
        namespace_dir_path = cache_dir_path / namespace_name
        if namespace_dir_path.exists():
            _delete_entry(namespace_dir_path)
    return entries


def discover_cache_namespaces(cache_dir_path: Path) -> list[str]:
    """Discover direct child directory names under a cache root.

    Arguments:
        cache_dir_path: cache root directory path
    Returns:
        sorted namespace names
    """
    if not cache_dir_path.exists():
        return []
    if not cache_dir_path.is_dir():
        raise NotADirectoryError(f"{cache_dir_path} is not a directory")
    namespaces = [
        child.name
        for child in cache_dir_path.iterdir()
        if child.is_dir() and not child.is_symlink()
    ]
    return sorted(namespaces)


def get_cache_entries(
    cache_dir_path: Path, *, namespace: str | None = None
) -> list[CacheEntry]:
    """Get direct cache entries for one or more namespaces.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: optional namespace filter
    Returns:
        cache entries
    Raises:
        ScinoephileError: if an explicit namespace does not exist
    """
    namespace_names = _get_namespace_names(cache_dir_path, namespace=namespace)
    entries: list[CacheEntry] = []
    for namespace_name in namespace_names:
        namespace_dir_path = cache_dir_path / namespace_name
        entries.extend(
            [
                _build_cache_entry(cache_dir_path, namespace_name, child_path)
                for child_path in namespace_dir_path.iterdir()
            ]
        )
    return entries


def get_cache_stats(
    cache_dir_path: Path, *, namespace: str | None = None
) -> list[CacheStats]:
    """Get per-namespace and total cache statistics.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: optional namespace filter
    Returns:
        aggregate cache statistics
    """
    entries = get_cache_entries(cache_dir_path, namespace=namespace)
    namespace_names = _get_namespace_names(cache_dir_path, namespace=namespace)
    stats = [
        _aggregate_cache_stats(
            namespace_name,
            [entry for entry in entries if entry.namespace == namespace_name],
        )
        for namespace_name in namespace_names
    ]
    stats.append(_aggregate_cache_stats("total", entries))
    return stats


def prune_cache(
    cache_dir_path: Path, *, older_than: timedelta, namespace: str | None = None
) -> list[CacheEntry]:
    """Prune cache entries older than a duration.

    Arguments:
        cache_dir_path: cache root directory path
        older_than: entry age threshold
        namespace: optional namespace filter
    Returns:
        entries that were deleted
    """
    cutoff = datetime.now().astimezone() - older_than
    entries = [
        entry
        for entry in get_cache_entries(cache_dir_path, namespace=namespace)
        if entry.modified_at < cutoff
    ]
    for entry in entries:
        _delete_entry(entry.path)
    return entries


def _aggregate_cache_stats(namespace: str, entries: Iterable[CacheEntry]) -> CacheStats:
    """Aggregate entries into cache statistics.

    Arguments:
        namespace: namespace name or total label
        entries: cache entries to aggregate
    Returns:
        aggregate cache statistics
    """
    entry_list = list(entries)
    return CacheStats(
        namespace=namespace,
        entry_count=len(entry_list),
        total_bytes=sum(entry.size_bytes for entry in entry_list),
        oldest_modified_at=min(
            (entry.modified_at for entry in entry_list), default=None
        ),
        newest_modified_at=max(
            (entry.modified_at for entry in entry_list), default=None
        ),
        oldest_accessed_at=min(
            (entry.accessed_at for entry in entry_list), default=None
        ),
        newest_accessed_at=max(
            (entry.accessed_at for entry in entry_list), default=None
        ),
    )


def _build_cache_entry(
    cache_dir_path: Path, namespace: str, entry_path: Path
) -> CacheEntry:
    """Build a cache entry from a filesystem path.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: namespace containing the entry
        entry_path: cache entry path
    Returns:
        cache entry
    """
    size_bytes, file_count, modified_at, accessed_at = _measure_path(entry_path)
    return CacheEntry(
        namespace=namespace,
        path=entry_path,
        relative_path=entry_path.relative_to(cache_dir_path),
        size_bytes=size_bytes,
        file_count=file_count,
        modified_at=modified_at,
        accessed_at=accessed_at,
        is_dir=entry_path.is_dir() and not entry_path.is_symlink(),
    )


def _delete_entry(entry_path: Path):
    """Delete a cache entry without following symlinks.

    Arguments:
        entry_path: entry to delete
    """
    if entry_path.is_symlink() or entry_path.is_file():
        entry_path.unlink(missing_ok=True)
    elif entry_path.is_dir():
        rmtree(entry_path)


def _get_namespace_names(cache_dir_path: Path, *, namespace: str | None) -> list[str]:
    """Get namespace names to inspect.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: optional namespace filter
    Returns:
        namespace names
    Raises:
        ScinoephileError: if an explicit namespace does not exist
    """
    namespace_names = discover_cache_namespaces(cache_dir_path)
    if namespace is None:
        return namespace_names
    if namespace not in namespace_names:
        raise ScinoephileError(f"Cache namespace {namespace!r} was not found")
    return [namespace]


def _measure_path(entry_path: Path) -> tuple[int, int, datetime, datetime]:
    """Measure a cache entry without following symlinked directories.

    Arguments:
        entry_path: path to measure
    Returns:
        size, file count, newest modification time, and newest access time
    """
    stat = entry_path.lstat()
    size_bytes = stat.st_size
    file_count = 1
    modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone()
    accessed_at = datetime.fromtimestamp(stat.st_atime).astimezone()
    if entry_path.is_dir() and not entry_path.is_symlink():
        for child_path in entry_path.rglob("*"):
            child_stat = child_path.lstat()
            size_bytes += child_stat.st_size
            file_count += 1
            child_modified_at = datetime.fromtimestamp(child_stat.st_mtime).astimezone()
            child_accessed_at = datetime.fromtimestamp(child_stat.st_atime).astimezone()
            modified_at = max(modified_at, child_modified_at)
            accessed_at = max(accessed_at, child_accessed_at)
    return size_bytes, file_count, modified_at, accessed_at


def _namespaces_to_clear(
    cache_dir_path: Path, *, namespace: str | None, all_namespaces: bool
) -> list[str]:
    """Get namespaces whose directories should be removed.

    Arguments:
        cache_dir_path: cache root directory path
        namespace: optional namespace to clear
        all_namespaces: whether every namespace should be cleared
    Returns:
        namespace names
    """
    if namespace is not None:
        return [namespace]
    if all_namespaces:
        return discover_cache_namespaces(cache_dir_path)
    return []
