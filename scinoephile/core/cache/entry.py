#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache entry dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["CacheEntry"]


@dataclass
class CacheEntry:
    """A single entry (file or directory) within a cache namespace."""

    namespace: str
    """Namespace (subdirectory name) this entry belongs to."""
    rel_path: Path
    """Path relative to the namespace directory."""
    size: int
    """Total size in bytes (summed recursively for directory entries)."""
    mtime: float
    """Modification time as a POSIX timestamp."""
    atime: float
    """Access time as a POSIX timestamp."""
    file_count: int
    """Number of files (1 for file entries, recursive count for directories)."""
