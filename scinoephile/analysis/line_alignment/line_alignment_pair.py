#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligned character pairs for line alignment."""

from __future__ import annotations

from dataclasses import dataclass

from .line_alignment_operation import LineAlignmentOperation

__all__ = ["LineAlignmentPair"]


@dataclass(frozen=True)
class LineAlignmentPair:
    """A single aligned output column."""

    one: str | None
    """Character from the first string, if present."""

    two: str | None
    """Character from the second string, if present."""

    operation: LineAlignmentOperation
    """Alignment operation describing this output column."""
