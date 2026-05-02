#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Backpointer records for line alignment."""

from __future__ import annotations

from dataclasses import dataclass

from .alignment_operation import AlignmentOperation

__all__ = ["AlignmentBackpointer"]


@dataclass(frozen=True)
class AlignmentBackpointer:
    """Backpointer to a previous dynamic-programming cell."""

    previous_i: int
    """Previous row index in the metric table."""

    previous_j: int
    """Previous column index in the metric table."""

    operation: AlignmentOperation
    """Alignment operation used to reach the current cell."""
