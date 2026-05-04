#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache statistics models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = ["CacheStats"]


@dataclass(frozen=True)
class CacheStats:
    """Aggregate cache statistics."""

    namespace: str
    """Cache namespace or total label."""
    entry_count: int
    """Number of cache entries."""
    total_bytes: int
    """Total size in bytes."""
    oldest_modified_at: datetime | None
    """Oldest entry modification time."""
    newest_modified_at: datetime | None
    """Newest entry modification time."""
    oldest_accessed_at: datetime | None
    """Oldest entry access time."""
    newest_accessed_at: datetime | None
    """Newest entry access time."""
