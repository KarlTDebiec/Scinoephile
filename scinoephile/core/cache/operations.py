#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Directory-based cache inspection and invalidation operations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
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

_CACHE_NAMESPACE_GROUP_NAMES = ("llm", "media")
"""Root directory names whose direct children are cache namespaces."""
_NESTED_CACHE_NAMESPACE_NAMES = ("media/subtitles/analysis",)
"""Cache namespaces nested beneath another cache namespace."""


def clear_cache(
    cache_root_path: Path, *, namespace: str | None = None, all_namespaces: bool = False
) -> list[CacheEntry]:
    """Clear one namespace or every discovered namespace.

    Arguments:
        cache_root_path: cache root directory path
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

    discovered_namespace_names = discover_cache_namespaces(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )
    for entry in entries:
        _delete_entry(entry.path)

    # Preserve nested namespaces that were not selected for clearing
    protected_namespace_paths = {
        PurePosixPath(namespace_name)
        for namespace_name in discovered_namespace_names
        if namespace_name not in namespace_names
    }
    namespace_names.sort(
        key=lambda namespace_name: len(PurePosixPath(namespace_name).parts),
        reverse=True,
    )
    for namespace_name in namespace_names:
        namespace_path = PurePosixPath(namespace_name)
        if any(
            namespace_path in protected_namespace_path.parents
            for protected_namespace_path in protected_namespace_paths
        ):
            continue
        namespace_dir_path = _get_namespace_dir_path(cache_root_path, namespace_name)
        if namespace_dir_path.exists():
            _delete_entry(namespace_dir_path)

            # Remove empty grouping directories up to the cache root
            parent_dir_path = namespace_dir_path.parent
            while (
                parent_dir_path != cache_root_path
                and parent_dir_path.is_dir()
                and not parent_dir_path.is_symlink()
                and not any(parent_dir_path.iterdir())
            ):
                parent_dir_path.rmdir()
                parent_dir_path = parent_dir_path.parent
    return entries


def discover_cache_namespaces(cache_root_path: Path) -> list[str]:
    """Discover cache namespaces under a cache root.

    Arguments:
        cache_root_path: cache root directory path
    Returns:
        sorted namespace names
    """
    if not cache_root_path.exists():
        return []
    if not cache_root_path.is_dir():
        raise NotADirectoryError(f"{cache_root_path} is not a directory")
    namespace_names = []

    # Discover top-level namespaces and direct children of grouping directories
    for child_path in cache_root_path.iterdir():
        if not child_path.is_dir() or child_path.is_symlink():
            continue
        if child_path.name not in _CACHE_NAMESPACE_GROUP_NAMES:
            namespace_names.append(child_path.name)
            continue
        if any(
            grouped_child_path.is_file() or grouped_child_path.is_symlink()
            for grouped_child_path in child_path.iterdir()
        ):
            namespace_names.append(child_path.name)
        namespace_names.extend(
            f"{child_path.name}/{grouped_child_path.name}"
            for grouped_child_path in child_path.iterdir()
            if grouped_child_path.is_dir() and not grouped_child_path.is_symlink()
        )

    # Add recognized namespaces nested beneath another namespace
    for nested_namespace_name in sorted(
        _NESTED_CACHE_NAMESPACE_NAMES, key=lambda name: len(PurePosixPath(name).parts)
    ):
        nested_namespace_path = PurePosixPath(nested_namespace_name)
        if nested_namespace_path.parent.as_posix() not in namespace_names:
            continue
        nested_namespace_dir_path = _get_namespace_dir_path(
            cache_root_path, nested_namespace_name
        )
        if (
            nested_namespace_dir_path.is_dir()
            and not nested_namespace_dir_path.is_symlink()
        ):
            namespace_names.append(nested_namespace_name)
    return sorted(namespace_names)


def get_cache_entries(
    cache_root_path: Path, *, namespace: str | None = None
) -> list[CacheEntry]:
    """Get direct cache entries for one or more namespaces.

    Arguments:
        cache_root_path: cache root directory path
        namespace: optional namespace filter
    Returns:
        cache entries
    Raises:
        ScinoephileError: if an explicit namespace does not exist
    """
    discovered_namespace_names = discover_cache_namespaces(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    return _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )


def get_cache_stats(
    cache_root_path: Path, *, namespace: str | None = None
) -> list[CacheStats]:
    """Get per-namespace and total cache statistics.

    Arguments:
        cache_root_path: cache root directory path
        namespace: optional namespace filter
    Returns:
        aggregate cache statistics
    """
    discovered_namespace_names = discover_cache_namespaces(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )
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
    cache_root_path: Path, *, older_than: timedelta, namespace: str | None = None
) -> list[CacheEntry]:
    """Prune cache entries older than a duration.

    Arguments:
        cache_root_path: cache root directory path
        older_than: entry age threshold
        namespace: optional namespace filter
    Returns:
        entries that were deleted
    """
    cutoff = datetime.now().astimezone() - older_than
    discovered_namespace_names = discover_cache_namespaces(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = [
        entry
        for entry in _get_cache_entries(
            cache_root_path, namespace_names, discovered_namespace_names
        )
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
    cache_root_path: Path, namespace: str, entry_path: Path
) -> CacheEntry:
    """Build a cache entry from a filesystem path.

    Arguments:
        cache_root_path: cache root directory path
        namespace: namespace containing the entry
        entry_path: cache entry path
    Returns:
        cache entry
    """
    size_bytes, file_count, modified_at, accessed_at = _measure_path(entry_path)
    return CacheEntry(
        namespace=namespace,
        path=entry_path,
        relative_path=entry_path.relative_to(cache_root_path),
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


def _get_cache_entries(
    cache_root_path: Path,
    namespace_names: Iterable[str],
    discovered_namespace_names: Iterable[str],
) -> list[CacheEntry]:
    """Get cache entries from selected namespaces.

    Arguments:
        cache_root_path: cache root directory path
        namespace_names: selected namespace names
        discovered_namespace_names: all discovered namespace names
    Returns:
        cache entries
    """
    discovered_namespace_paths = {
        PurePosixPath(namespace_name) for namespace_name in discovered_namespace_names
    }
    entries = []
    for namespace_name in namespace_names:
        namespace_path = PurePosixPath(namespace_name)
        namespace_dir_path = _get_namespace_dir_path(cache_root_path, namespace_name)
        nested_namespace_dir_names = {
            discovered_namespace_path.name
            for discovered_namespace_path in discovered_namespace_paths
            if discovered_namespace_path.parent == namespace_path
        }
        entries.extend(
            _build_cache_entry(cache_root_path, namespace_name, child_path)
            for child_path in sorted(namespace_dir_path.iterdir())
            if child_path.name not in nested_namespace_dir_names
        )
    return entries


def _get_namespace_dir_path(cache_root_path: Path, namespace_name: str) -> Path:
    """Get a namespace directory path from its portable name.

    Arguments:
        cache_root_path: cache root directory path
        namespace_name: portable cache namespace name
    Returns:
        cache namespace directory path
    """
    return cache_root_path.joinpath(*PurePosixPath(namespace_name).parts)


def _get_namespace_names(
    discovered_namespace_names: list[str], *, namespace: str | None
) -> list[str]:
    """Filter discovered namespace names.

    Arguments:
        discovered_namespace_names: all discovered namespace names
        namespace: optional namespace filter
    Returns:
        selected namespace names
    Raises:
        ScinoephileError: if an explicit namespace does not exist
    """
    if namespace is None:
        return list(discovered_namespace_names)
    if namespace not in discovered_namespace_names:
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
    is_directory = entry_path.is_dir() and not entry_path.is_symlink()
    size_bytes = 0 if is_directory else stat.st_size
    file_count = 0 if is_directory else 1
    modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone()
    accessed_at = datetime.fromtimestamp(stat.st_atime).astimezone()
    if is_directory:
        for child_path in entry_path.rglob("*"):
            child_stat = child_path.lstat()
            if not child_path.is_dir() or child_path.is_symlink():
                size_bytes += child_stat.st_size
                file_count += 1
            child_modified_at = datetime.fromtimestamp(child_stat.st_mtime).astimezone()
            child_accessed_at = datetime.fromtimestamp(child_stat.st_atime).astimezone()
            modified_at = max(modified_at, child_modified_at)
            accessed_at = max(accessed_at, child_accessed_at)
    return size_bytes, file_count, modified_at, accessed_at
