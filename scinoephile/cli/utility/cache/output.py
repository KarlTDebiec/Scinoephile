#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Formatting helpers for cache CLI output."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from scinoephile.core.cache import CacheEntry, CacheStats

__all__ = [
    "format_cache_entry",
    "format_cache_stats",
    "print_entries",
    "print_stats",
    "sort_entries",
]


def format_cache_entry(entry: CacheEntry) -> dict[str, Any]:
    """Format a cache entry for structured output.

    Arguments:
        entry: cache entry to format
    Returns:
        JSON-serializable object
    """
    return {
        "namespace": entry.namespace,
        "path": str(entry.relative_path),
        "size_bytes": entry.size_bytes,
        "file_count": entry.file_count,
        "modified_at": _format_datetime(entry.modified_at),
        "accessed_at": _format_datetime(entry.accessed_at),
        "type": "directory" if entry.is_dir else "file",
    }


def format_cache_stats(stats: CacheStats) -> dict[str, Any]:
    """Format cache statistics for structured output.

    Arguments:
        stats: cache statistics to format
    Returns:
        JSON-serializable object
    """
    return {
        "namespace": stats.namespace,
        "entry_count": stats.entry_count,
        "total_bytes": stats.total_bytes,
        "oldest_modified_at": _format_datetime(stats.oldest_modified_at),
        "newest_modified_at": _format_datetime(stats.newest_modified_at),
        "oldest_accessed_at": _format_datetime(stats.oldest_accessed_at),
        "newest_accessed_at": _format_datetime(stats.newest_accessed_at),
    }


def print_entries(entries: list[CacheEntry], output_format: str):
    """Print cache entries.

    Arguments:
        entries: entries to print
        output_format: output format
    """
    objects = [format_cache_entry(entry) for entry in entries]
    if output_format == "json":
        print(json.dumps(objects, indent=2))
    elif output_format == "jsonl":
        for entry_object in objects:
            print(json.dumps(entry_object))
    else:
        if not objects:
            print("No cache entries found.")
            return
        for entry_object in objects:
            print(
                f"{entry_object['namespace']}\t{entry_object['path']}\t"
                f"{entry_object['size_bytes']} bytes\t"
                f"{entry_object['file_count']} file(s)\t"
                f"mtime {entry_object['modified_at']}\t"
                f"atime {entry_object['accessed_at']}"
            )


def print_stats(stats: list[CacheStats], output_format: str):
    """Print cache statistics.

    Arguments:
        stats: statistics to print
        output_format: output format
    """
    objects = [format_cache_stats(namespace_stats) for namespace_stats in stats]
    if output_format == "json":
        print(json.dumps(objects, indent=2))
        return
    for stats_object in objects:
        print(
            f"{stats_object['namespace']}\t"
            f"{stats_object['entry_count']} entries\t"
            f"{stats_object['total_bytes']} bytes\t"
            f"mtime {stats_object['oldest_modified_at']}.."
            f"{stats_object['newest_modified_at']}\t"
            f"atime {stats_object['oldest_accessed_at']}.."
            f"{stats_object['newest_accessed_at']}"
        )


def sort_entries(
    entries: list[CacheEntry], *, sort: str, reverse: bool
) -> list[CacheEntry]:
    """Sort cache entries.

    Arguments:
        entries: entries to sort
        sort: sort field
        reverse: whether to reverse sort order
    Returns:
        sorted entries
    """
    if sort == "size":
        return sorted(entries, key=lambda entry: entry.size_bytes, reverse=reverse)
    if sort == "mtime":
        return sorted(entries, key=lambda entry: entry.modified_at, reverse=reverse)
    if sort == "atime":
        return sorted(entries, key=lambda entry: entry.accessed_at, reverse=reverse)
    return sorted(entries, key=lambda entry: str(entry.relative_path), reverse=reverse)


def _format_datetime(value: datetime | None) -> str | None:
    """Format a datetime for CLI output.

    Arguments:
        value: datetime to format
    Returns:
        ISO 8601 string or None
    """
    if value is None:
        return None
    return value.isoformat(timespec="seconds")
