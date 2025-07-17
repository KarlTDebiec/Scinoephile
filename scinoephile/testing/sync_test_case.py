#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for synchronization."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.synchronization import SyncGroup


@dataclass(slots=True)
class SyncTestCase:
    """Test case for synchronization."""

    hanzi_start: int
    """Start index of Hanzi subtitles."""
    hanzi_end: int
    """End index of Hanzi subtitles."""
    english_start: int
    """Start index of English subtitles."""
    english_end: int
    """End index of English subtitles."""
    sync_groups: list[SyncGroup] | None = None
    """Expected synchronization groups."""
