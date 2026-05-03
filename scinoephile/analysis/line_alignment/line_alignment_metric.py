#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Dynamic-programming metrics for line alignment."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["LineAlignmentMetric"]


@dataclass(init=False, slots=True)
class LineAlignmentMetric:
    """Dynamic-programming metric state for one alignment cell."""

    distance: int
    """Total edit distance."""

    gap_runs: int
    """Number of contiguous insert/delete runs."""

    substitutions: int
    """Number of substitute operations."""

    deletions: int
    """Number of delete operations."""

    insertions: int
    """Number of insert operations."""

    def __init__(
        self,
        distance: int,
        gap_runs: int,
        substitutions: int,
        deletions: int,
        insertions: int,
    ):
        """Initialize metric state.

        Arguments:
            distance: total edit distance
            gap_runs: number of contiguous insert/delete runs
            substitutions: number of substitute operations
            deletions: number of delete operations
            insertions: number of insert operations
        """
        self.distance = distance
        self.gap_runs = gap_runs
        self.substitutions = substitutions
        self.deletions = deletions
        self.insertions = insertions

    @classmethod
    def for_deletes(cls, count: int) -> LineAlignmentMetric:
        """Build an edge metric for forced deletes.

        Arguments:
            count: number of deleted characters
        Returns:
            metric for a prefix aligned only by deletes
        """
        if count == 0:
            return cls.empty()
        return cls(count, 1, 0, count, 0)

    @classmethod
    def for_inserts(cls, count: int) -> LineAlignmentMetric:
        """Build an edge metric for forced inserts.

        Arguments:
            count: number of inserted characters
        Returns:
            metric for a prefix aligned only by inserts
        """
        if count == 0:
            return cls.empty()
        return cls(count, 1, 0, 0, count)

    @classmethod
    def empty(cls) -> LineAlignmentMetric:
        """Build the metric for two empty prefixes.

        Returns:
            zero-valued metric
        """
        return cls(0, 0, 0, 0, 0)
