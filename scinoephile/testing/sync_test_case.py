#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.synchronization import SyncGroupList


@dataclass
class SyncTestCase:
    hanzi_start: int
    hanzi_end: int
    english_start: int
    english_end: int
    sync_groups: SyncGroupList | None = None
