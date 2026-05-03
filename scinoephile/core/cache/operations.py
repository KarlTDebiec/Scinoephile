#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache inspection and manipulation operations."""

from __future__ import annotations

import os
import time
from datetime import timedelta
from os import getenv
from pathlib import Path
from platform import system
from typing import Literal

from .entry import CacheEntry

__all__ = [
    "clear_entries",
    "discover_namespaces",
    "get_default_cache_dir_path",
    "get_stats",
    "list_entries",
    "prune_entries",
]


def get_default_cache_dir_path() -> Path:
    """Get the default Scinoephile cache root directory path without creating it.

    Honors SCINOEPHILE_CACHE_DIR if set; otherwise uses the OS-appropriate cache base.

    Returns:
        default Scinoephile cache root path
    """
    if configured := getenv("SCINOEPHILE_CACHE_DIR"):
        return Path(configured) / "scinoephile"
    if system() == "Darwin":
        return Path.home() / "Library" / "Caches" / "scinoephile"
    if system() == "Windows":
        base = getenv("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "scinoephile"
    base = getenv("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "scinoephile"


def discover_namespaces(cache_dir_path: Path) -> list[str]:
    """Discover cache namespaces as direct subdirectories of the cache root.

    Arguments:
        cache_dir_path: cache root directory
    Returns:
        sorted list of namespace names
    """
    if not cache_dir_path.exists():
        return []
    return sorted(p.name for p in cache_dir_path.iterdir() if p.is_dir())


def list_entries(
    cache_dir_path: Path,
    *,
    namespace: str | None = None,
    limit: int | None = None,
    sort: Literal["name", "size", "mtime", "atime"] = "name",
    reverse: bool = False,
) -> list[CacheEntry]:
    """List cache entries discovered under the cache root.

    Arguments:
        cache_dir_path: cache root directory
        namespace: optional namespace filter; if None, all namespaces are included
        limit: maximum number of entries to return; if None, all entries are returned
        sort: field to sort by
        reverse: whether to reverse sort order
    Returns:
        list of cache entries
    Raises:
        ValueError: if namespace is specified but does not exist
    """
    if not cache_dir_path.exists():
        return []

    if namespace is not None:
        namespaces = _resolve_namespace(cache_dir_path, namespace)
    else:
        namespaces = discover_namespaces(cache_dir_path)

    entries: list[CacheEntry] = []
    for ns in namespaces:
        ns_dir = cache_dir_path / ns
        if not ns_dir.is_dir():
            continue
        for child in ns_dir.iterdir():
            entry = _entry_from_path(ns, ns_dir, child)
            if entry is not None:
                entries.append(entry)

    sort_key = _make_sort_key(sort)
    entries.sort(key=sort_key, reverse=reverse)

    if limit is not None:
        entries = entries[:limit]
    return entries


def get_stats(
    cache_dir_path: Path,
    *,
    namespace: str | None = None,
) -> dict[str, object]:
    """Aggregate cache statistics grouped by namespace.

    Arguments:
        cache_dir_path: cache root directory
        namespace: optional namespace filter; if None, all namespaces are included
    Returns:
        dict with per-namespace stats and totals
    Raises:
        ValueError: if namespace is specified but does not exist
    """
    entries = list_entries(cache_dir_path, namespace=namespace)

    by_namespace: dict[str, list[CacheEntry]] = {}
    for entry in entries:
        by_namespace.setdefault(entry.namespace, []).append(entry)

    namespace_stats: list[dict[str, object]] = []
    total_count = 0
    total_size = 0
    overall_oldest_mtime: float | None = None
    overall_newest_mtime: float | None = None
    overall_oldest_atime: float | None = None
    overall_newest_atime: float | None = None

    for ns, ns_entries in sorted(by_namespace.items()):
        count = len(ns_entries)
        size = sum(e.size for e in ns_entries)
        mtimes = [e.mtime for e in ns_entries]
        atimes = [e.atime for e in ns_entries]
        oldest_mtime = min(mtimes) if mtimes else None
        newest_mtime = max(mtimes) if mtimes else None
        oldest_atime = min(atimes) if atimes else None
        newest_atime = max(atimes) if atimes else None

        namespace_stats.append(
            {
                "namespace": ns,
                "count": count,
                "size": size,
                "oldest_mtime": oldest_mtime,
                "newest_mtime": newest_mtime,
                "oldest_atime": oldest_atime,
                "newest_atime": newest_atime,
            }
        )

        total_count += count
        total_size += size
        if oldest_mtime is not None:
            overall_oldest_mtime = (
                oldest_mtime
                if overall_oldest_mtime is None
                else min(overall_oldest_mtime, oldest_mtime)
            )
        if newest_mtime is not None:
            overall_newest_mtime = (
                newest_mtime
                if overall_newest_mtime is None
                else max(overall_newest_mtime, newest_mtime)
            )
        if oldest_atime is not None:
            overall_oldest_atime = (
                oldest_atime
                if overall_oldest_atime is None
                else min(overall_oldest_atime, oldest_atime)
            )
        if newest_atime is not None:
            overall_newest_atime = (
                newest_atime
                if overall_newest_atime is None
                else max(overall_newest_atime, newest_atime)
            )

    return {
        "namespaces": namespace_stats,
        "total": {
            "count": total_count,
            "size": total_size,
            "oldest_mtime": overall_oldest_mtime,
            "newest_mtime": overall_newest_mtime,
            "oldest_atime": overall_oldest_atime,
            "newest_atime": overall_newest_atime,
        },
    }


def prune_entries(
    cache_dir_path: Path,
    *,
    older_than: timedelta,
    namespace: str | None = None,
    dry_run: bool = True,
) -> list[CacheEntry]:
    """Prune cache entries older than a given duration.

    Arguments:
        cache_dir_path: cache root directory
        older_than: delete entries with mtime older than this duration ago
        namespace: optional namespace filter; if None, all namespaces are affected
        dry_run: if True, return what would be deleted without deleting anything
    Returns:
        list of entries that were (or would be) deleted
    Raises:
        ValueError: if namespace is specified but does not exist
    """
    if not cache_dir_path.exists():
        return []

    cutoff = time.time() - older_than.total_seconds()
    entries = list_entries(cache_dir_path, namespace=namespace)
    to_delete = [e for e in entries if e.mtime < cutoff]

    if not dry_run:
        for entry in to_delete:
            ns_dir = cache_dir_path / entry.namespace
            target = ns_dir / entry.rel_path
            _safe_delete(cache_dir_path, target)

    return to_delete


def clear_entries(
    cache_dir_path: Path,
    *,
    namespace: str | None = None,
    all_namespaces: bool = False,
    dry_run: bool = True,
) -> list[CacheEntry]:
    """Clear cache entries from one or all namespaces.

    Arguments:
        cache_dir_path: cache root directory
        namespace: namespace to clear; required unless all_namespaces is True
        all_namespaces: if True, clear every discovered namespace
        dry_run: if True, return what would be deleted without deleting anything
    Returns:
        list of entries that were (or would be) deleted
    Raises:
        ValueError: if namespace is specified but does not exist, or neither
          namespace nor all_namespaces is provided
    """
    if not all_namespaces and namespace is None:
        raise ValueError("Either namespace or all_namespaces=True must be provided.")

    if not cache_dir_path.exists():
        return []

    ns_filter = None if all_namespaces else namespace
    entries = list_entries(cache_dir_path, namespace=ns_filter)

    if not dry_run:
        for entry in entries:
            ns_dir = cache_dir_path / entry.namespace
            target = ns_dir / entry.rel_path
            _safe_delete(cache_dir_path, target)

    return entries


def _resolve_namespace(cache_dir_path: Path, namespace: str) -> list[str]:
    """Resolve a namespace name, raising ValueError if it does not exist.

    Arguments:
        cache_dir_path: cache root directory
        namespace: requested namespace name
    Returns:
        list containing the single resolved namespace name
    Raises:
        ValueError: if namespace does not exist
    """
    ns_path = cache_dir_path / namespace
    if not ns_path.is_dir():
        available = discover_namespaces(cache_dir_path)
        available_str = ", ".join(available) if available else "(none)"
        raise ValueError(
            f"Namespace {namespace!r} not found in {cache_dir_path}. "
            f"Available namespaces: {available_str}."
        )
    return [namespace]


def _entry_from_path(
    namespace: str, namespace_dir: Path, path: Path
) -> CacheEntry | None:
    """Build a CacheEntry from a filesystem path.

    Symlinks outside the namespace directory are skipped.

    Arguments:
        namespace: namespace name
        namespace_dir: root directory of the namespace
        path: path to the entry (file or directory)
    Returns:
        CacheEntry, or None if the path should be skipped
    """
    if path.is_symlink():
        try:
            resolved = path.resolve()
            namespace_dir.resolve()
        except OSError:
            return None
        if not str(resolved).startswith(str(namespace_dir.resolve())):
            return None

    try:
        stat = path.stat()
    except OSError:
        return None

    rel_path = path.relative_to(namespace_dir)

    if path.is_file():
        return CacheEntry(
            namespace=namespace,
            rel_path=rel_path,
            size=stat.st_size,
            mtime=stat.st_mtime,
            atime=stat.st_atime,
            file_count=1,
        )

    if path.is_dir():
        total_size = 0
        file_count = 0
        oldest_mtime = stat.st_mtime
        oldest_atime = stat.st_atime
        for dirpath, dirnames, filenames in os.walk(path):
            for fname in filenames:
                fpath = Path(dirpath) / fname
                try:
                    fstat = fpath.stat()
                    total_size += fstat.st_size
                    file_count += 1
                    oldest_mtime = min(oldest_mtime, fstat.st_mtime)
                    oldest_atime = min(oldest_atime, fstat.st_atime)
                except OSError:
                    pass
        return CacheEntry(
            namespace=namespace,
            rel_path=rel_path,
            size=total_size,
            mtime=stat.st_mtime,
            atime=stat.st_atime,
            file_count=max(file_count, 1),
        )

    return None


def _make_sort_key(
    sort: Literal["name", "size", "mtime", "atime"],
):
    """Build a sort key function for a list of CacheEntry objects.

    Arguments:
        sort: sort field name
    Returns:
        key function for use with list.sort
    """
    if sort == "name":
        return lambda e: (e.namespace, str(e.rel_path))
    if sort == "size":
        return lambda e: e.size
    if sort == "mtime":
        return lambda e: e.mtime
    if sort == "atime":
        return lambda e: e.atime
    raise ValueError(f"Unknown sort field: {sort!r}")


def _safe_delete(cache_dir_path: Path, target: Path):
    """Delete a file or directory, refusing to follow symlinks outside the cache root.

    Arguments:
        cache_dir_path: cache root directory
        target: path to delete
    """
    import shutil

    try:
        resolved_target = target.resolve()
        resolved_root = cache_dir_path.resolve()
    except OSError:
        return

    if not str(resolved_target).startswith(str(resolved_root)):
        return

    if target.is_symlink() or target.is_file():
        target.unlink(missing_ok=True)
    elif target.is_dir():
        shutil.rmtree(target)
