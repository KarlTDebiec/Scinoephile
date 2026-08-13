#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models for pairwise character alignment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

__all__ = ["Column", "Operation"]


class Operation(IntEnum):
    """Alignment operation for a single output column."""

    MATCH = 0
    """Characters match exactly."""

    SUBSTITUTE = 1
    """Characters differ and are aligned as a substitution."""

    DELETE = 2
    """A character is present only in the first string."""

    INSERT = 3
    """A character is present only in the second string."""


@dataclass(frozen=True)
class Column:
    """A single aligned output column."""

    one: str | None
    """Character from the first string, if present."""

    two: str | None
    """Character from the second string, if present."""

    operation: Operation
    """Alignment operation describing this output column."""
