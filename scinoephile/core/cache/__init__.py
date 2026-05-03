#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache inspection and manipulation utilities."""

from __future__ import annotations

from .duration import parse_duration
from .entry import CacheEntry
from .operations import (
    clear_entries,
    discover_namespaces,
    get_default_cache_dir_path,
    get_stats,
    list_entries,
    prune_entries,
)

__all__: list[str] = [
    "CacheEntry",
    "clear_entries",
    "discover_namespaces",
    "get_default_cache_dir_path",
    "get_stats",
    "list_entries",
    "parse_duration",
    "prune_entries",
]
