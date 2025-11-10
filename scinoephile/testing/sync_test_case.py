#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for synchronization."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.synchronization import SyncGroup


@dataclass(slots=True)
class SyncTestCase:
    """Test case for synchronization."""

    one_start: int
    """Start index of series one."""
    one_end: int
    """End index of series one."""
    two_start: int
    """Start index of series two."""
    two_end: int
    """End index of series two."""
    sync_groups: list[SyncGroup] | None = None
    """Expected synchronization groups."""
