#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff kinds."""

from __future__ import annotations

from enum import Enum

__all__ = ["LineDiffKind"]


class LineDiffKind(Enum):
    """Types of line-level differences."""

    DELETE = "delete"
    """Line deleted from the second sequence."""

    EDIT = "edit"
    """Line edited between sequences."""

    EQUAL = "equal"
    """Line equal between sequences."""

    INSERT = "insert"
    """Line inserted into the second sequence."""

    MERGE = "merge"
    """Multiple lines merged into one line."""

    MERGE_EDIT = "merge_edit"
    """Multiple lines merged into one edited line."""

    SHIFT = "shift"
    """Line shifted within the sequence."""

    SPLIT = "split"
    """One line split into multiple lines."""

    SPLIT_EDIT = "split_edit"
    """One line split into multiple edited lines."""
