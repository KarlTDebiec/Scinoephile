#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Dynamic-programming metrics for line alignment."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["LineAlignmentMetric"]


@dataclass(frozen=True)
class LineAlignmentMetric:
    """Dynamic-programming metric state for one alignment cell."""

    distance: int
    """Total edit distance."""

    gap_runs: int
    """Number of contiguous insert/delete runs."""

    insertions: int
    """Number of insert operations."""

    deletions: int
    """Number of delete operations."""

    substitutions: int
    """Number of substitute operations."""

    def comparison_key(self) -> tuple[int, ...]:
        """Return lexicographic comparison key for this metric.

        Arguments:
            None.
        Returns:
            lexicographic key used to compare candidates
        """
        return (
            self.distance,
            self.gap_runs,
            self.substitutions,
            self.deletions,
            self.insertions,
        )
