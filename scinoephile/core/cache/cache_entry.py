#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache entry models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

__all__ = ["CacheEntry"]


@dataclass(frozen=True)
class CacheEntry:
    """A direct cache entry within a namespace."""

    namespace: str
    """Cache namespace."""
    path: Path
    """Absolute cache entry path."""
    relative_path: Path
    """Path relative to the cache root."""
    size_bytes: int
    """Total entry size in bytes."""
    file_count: int
    """Number of filesystem objects included in the entry."""
    modified_at: datetime
    """Most recent entry modification time."""
    accessed_at: datetime
    """Most recent entry access time."""
    is_dir: bool
    """Whether the entry is a directory."""
