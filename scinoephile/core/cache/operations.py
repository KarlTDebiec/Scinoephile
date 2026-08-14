#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Directory-based cache inspection and invalidation operations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

from scinoephile.core.exceptions import ScinoephileError

from .artifact import remove_cache_artifact
from .cache_entry import CacheEntry
from .cache_registry import CacheRegistry
from .cache_stats import CacheStats

__all__ = [
    "CacheEntry",
    "CacheStats",
    "clear_cache",
    "get_cache_entries",
    "get_cache_stats",
]


def clear_cache(
    cache_root_path: Path,
    cache_registry: CacheRegistry,
    *,
    namespace: str | None = None,
    entire_cache: bool = False,
    older_than: timedelta | None = None,
    dry_run: bool = False,
) -> list[CacheEntry]:
    """Clear matching entries from one namespace or the whole cache root.

    Arguments:
        cache_root_path: cache root directory path
        cache_registry: namespaces available to cache maintenance operations
        namespace: optional namespace to clear
        entire_cache: whether to clear all cache root contents
        older_than: optional entry age threshold
        dry_run: whether to return matching entries without deleting them
    Returns:
        matching entries, deleted unless dry_run is enabled
    Raises:
        ScinoephileError: if the arguments are invalid
    """
    if namespace is None and not entire_cache:
        raise ScinoephileError("--namespace is required unless --all is specified")
    if namespace is not None and entire_cache:
        raise ScinoephileError("--namespace and --all may not be used together")

    # An unfiltered all-scope operation treats the cache root as disposable
    if entire_cache and older_than is None:
        entries = _get_cache_root_entries(cache_root_path)
        if not dry_run:
            for entry in entries:
                remove_cache_artifact(entry.path)
        return entries

    return _clear_registered_cache_entries(
        cache_root_path,
        cache_registry,
        namespace=namespace,
        older_than=older_than,
        dry_run=dry_run,
    )


def get_cache_entries(
    cache_root_path: Path,
    cache_registry: CacheRegistry,
    *,
    namespace: str | None = None,
    older_than: timedelta | None = None,
) -> list[CacheEntry]:
    """Get direct cache entries for one or more namespaces.

    Arguments:
        cache_root_path: cache root directory path
        cache_registry: namespaces available to cache maintenance operations
        namespace: optional namespace filter
        older_than: optional entry age threshold
    Returns:
        cache entries
    Raises:
        ScinoephileError: if an explicit namespace does not exist
    """
    discovered_namespace_names = cache_registry.discover_names(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )
    return _filter_cache_entries(entries, older_than=older_than)


def get_cache_stats(
    cache_root_path: Path,
    cache_registry: CacheRegistry,
    *,
    namespace: str | None = None,
    older_than: timedelta | None = None,
) -> list[CacheStats]:
    """Get per-namespace and total cache statistics.

    Arguments:
        cache_root_path: cache root directory path
        cache_registry: namespaces available to cache maintenance operations
        namespace: optional namespace filter
        older_than: optional entry age threshold
    Returns:
        aggregate cache statistics
    """
    discovered_namespace_names = cache_registry.discover_names(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )
    entries = _filter_cache_entries(entries, older_than=older_than)
    stats = [
        _aggregate_cache_stats(
            namespace_name,
            [entry for entry in entries if entry.namespace == namespace_name],
        )
        for namespace_name in namespace_names
    ]
    stats.append(_aggregate_cache_stats("total", entries))
    return stats


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
    size_bytes, file_count, modified_at = _measure_path(entry_path)
    return CacheEntry(
        namespace=namespace,
        path=entry_path,
        relative_path=entry_path.relative_to(cache_root_path),
        size_bytes=size_bytes,
        file_count=file_count,
        modified_at=modified_at,
        is_dir=entry_path.is_dir() and not entry_path.is_symlink(),
    )


def _clear_registered_cache_entries(
    cache_root_path: Path,
    cache_registry: CacheRegistry,
    *,
    namespace: str | None,
    older_than: timedelta | None,
    dry_run: bool,
) -> list[CacheEntry]:
    """Clear matching entries from registered cache namespaces.

    Arguments:
        cache_root_path: cache root directory path
        cache_registry: namespaces available to cache maintenance operations
        namespace: optional namespace to clear
        older_than: optional entry age threshold
        dry_run: whether to return matching entries without deleting them
    Returns:
        matching entries, deleted unless dry_run is enabled
    """
    discovered_namespace_names = cache_registry.discover_names(cache_root_path)
    namespace_names = _get_namespace_names(
        discovered_namespace_names, namespace=namespace
    )
    entries = _get_cache_entries(
        cache_root_path, namespace_names, discovered_namespace_names
    )
    entries = _filter_cache_entries(entries, older_than=older_than)
    if dry_run:
        return entries
    for entry in entries:
        remove_cache_artifact(entry.path)

    # Preserve nested namespaces that were not selected for clearing
    protected_namespace_paths = {
        PurePosixPath(namespace_name)
        for namespace_name in discovered_namespace_names
        if namespace_name not in namespace_names
    }
    removable_namespace_names = namespace_names
    if older_than is not None:
        removable_namespace_names = []
        for namespace_name in namespace_names:
            namespace_dir_path = _get_namespace_dir_path(
                cache_root_path, namespace_name
            )
            if (
                namespace_dir_path.is_dir()
                and not namespace_dir_path.is_symlink()
                and not any(namespace_dir_path.iterdir())
            ):
                removable_namespace_names.append(namespace_name)
    removable_namespace_names.sort(
        key=lambda namespace_name: len(PurePosixPath(namespace_name).parts),
        reverse=True,
    )
    for namespace_name in removable_namespace_names:
        namespace_path = PurePosixPath(namespace_name)
        if any(
            namespace_path in protected_namespace_path.parents
            for protected_namespace_path in protected_namespace_paths
        ):
            continue
        namespace_dir_path = _get_namespace_dir_path(cache_root_path, namespace_name)
        if namespace_dir_path.exists():
            remove_cache_artifact(namespace_dir_path)

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


def _filter_cache_entries(
    entries: list[CacheEntry], *, older_than: timedelta | None
) -> list[CacheEntry]:
    """Filter cache entries by age.

    Arguments:
        entries: entries to filter
        older_than: optional entry age threshold
    Returns:
        filtered entries
    """
    if older_than is None:
        return entries
    cutoff = datetime.now().astimezone() - older_than
    return [entry for entry in entries if entry.modified_at < cutoff]


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


def _get_cache_root_entries(cache_root_path: Path) -> list[CacheEntry]:
    """Get direct entries beneath a cache root.

    Arguments:
        cache_root_path: cache root directory path
    Returns:
        direct cache root entries
    Raises:
        NotADirectoryError: if the cache root exists but is not a directory
    """
    if not cache_root_path.exists():
        return []
    if not cache_root_path.is_dir():
        raise NotADirectoryError(f"{cache_root_path} is not a directory")
    return [
        _build_cache_entry(cache_root_path, "cache root", child_path)
        for child_path in sorted(cache_root_path.iterdir())
    ]


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


def _measure_path(entry_path: Path) -> tuple[int, int, datetime]:
    """Measure a cache entry without following symlinked directories.

    Arguments:
        entry_path: path to measure
    Returns:
        size, file count, and newest modification time
    """
    stat = entry_path.lstat()
    is_directory = entry_path.is_dir() and not entry_path.is_symlink()
    size_bytes = 0 if is_directory else stat.st_size
    file_count = 0 if is_directory else 1
    modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone()
    if is_directory:
        for child_path in entry_path.rglob("*"):
            child_stat = child_path.lstat()
            if not child_path.is_dir() or child_path.is_symlink():
                size_bytes += child_stat.st_size
                file_count += 1
            child_modified_at = datetime.fromtimestamp(child_stat.st_mtime).astimezone()
            modified_at = max(modified_at, child_modified_at)
    return size_bytes, file_count, modified_at
