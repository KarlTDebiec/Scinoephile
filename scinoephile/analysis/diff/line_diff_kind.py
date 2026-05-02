#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff kinds."""

from __future__ import annotations

from enum import Enum

__all__ = ["LineDiffKind"]


class LineDiffKind(Enum):
    """Types of line-level differences."""

    DELETE = "delete"
    EDIT = "edit"
    INSERT = "insert"
    MERGE = "merge"
    MERGE_EDIT = "merge_edit"
    SHIFT = "shift"
    SPLIT = "split"
    SPLIT_EDIT = "split_edit"
