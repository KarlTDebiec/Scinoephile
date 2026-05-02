#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Alignment operations for line alignment."""

from __future__ import annotations

from enum import IntEnum

__all__ = ["AlignmentOperation"]


class AlignmentOperation(IntEnum):
    """Alignment operation for a single output column."""

    MATCH = 0
    """Characters match exactly."""

    SUBSTITUTE = 1
    """Characters differ and are aligned as a substitution."""

    DELETE = 2
    """A character is present only in the first string."""

    INSERT = 3
    """A character is present only in the second string."""
