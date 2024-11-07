#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from dataclasses import dataclass

from scinoephile.open_ai import (
    SubtitleSeriesResponse,
    SyncGroupNotesResponse,
    SyncNotesResponse,
)


@dataclass
class SyncTestCase:
    hanzi_start: int
    hanzi_end: int
    english_start: int
    english_end: int
    example_sync_notes: SyncNotesResponse | None = None
    example_sync_group_notes: SyncGroupNotesResponse | None = None
    expected_sync: SubtitleSeriesResponse | None = None
