#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to subtitle synchronization.

Package hierarchy (modules may import from any above):
* comparison / overlap
* groups
* offsets
"""

from __future__ import annotations

from .comparison import are_series_one_to_one
from .groups import SyncGroup, get_sync_groups, get_sync_groups_string
from .offsets import SyncOffsetDatum, SyncOffsetStats, get_sync_offset_stats
from .overlap import get_overlap_string, get_sync_overlap_matrix

__all__ = [
    "SyncGroup",
    "SyncOffsetDatum",
    "SyncOffsetStats",
    "are_series_one_to_one",
    "get_overlap_string",
    "get_sync_groups",
    "get_sync_groups_string",
    "get_sync_offset_stats",
    "get_sync_overlap_matrix",
]
