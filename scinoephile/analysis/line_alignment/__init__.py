#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level alignment helpers.

This module centralizes character alignment so that:

- visual diffs can render per-character operations (match/insert/delete/substitute)
- CER calculations can derive edit counts from the same alignment path
"""

from __future__ import annotations

from .alignment_backpointer import AlignmentBackpointer
from .alignment_metric import AlignmentMetric
from .alignment_operation import AlignmentOperation
from .alignment_pair import AlignmentPair

__all__ = [
    "AlignmentOperation",
    "AlignmentPair",
    "get_aligned_chars",
    "count_edits",
]


def get_aligned_chars(one: str, two: str) -> list[AlignmentPair]:
    """Align two strings at the character level.

    Uses Levenshtein-style dynamic programming with backtrace.

    Arguments:
        one: first string
        two: second string
    Returns:
        list of aligned columns
    """
    # Allocate the DP tables and bookkeeping needed for alignment.
    metrics, backpointers, last_gap_operations = _init_tables(one, two)

    # Seed the first row and column for leading insert/delete runs.
    _init_edges(one, two, metrics, backpointers, last_gap_operations)

    # Fill the interior DP cells using match/substitute/insert/delete candidates.
    _fill_tables(
        one,
        two,
        metrics=metrics,
        backpointers=backpointers,
        last_gap_operations=last_gap_operations,
    )

    # Reconstruct the chosen alignment path from the backpointers.
    alignment = _backtrace(one, two, backpointers)

    return alignment


def count_edits(alignment: list[AlignmentPair]) -> tuple[int, int, int, int]:
    """Count edit operations in an alignment.

    Arguments:
        alignment: aligned character columns
    Returns:
        substitutions, insertions, deletions, correct
    """
    substitutions = 0
    insertions = 0
    deletions = 0
    correct = 0
    for col in alignment:
        if col.operation == AlignmentOperation.MATCH:
            correct += 1
        elif col.operation == AlignmentOperation.SUBSTITUTE:
            substitutions += 1
        elif col.operation == AlignmentOperation.INSERT:
            insertions += 1
        else:
            deletions += 1
    return substitutions, insertions, deletions, correct


def _init_tables(
    one: str, two: str
) -> tuple[
    list[list[AlignmentMetric]],
    list[list[AlignmentBackpointer | None]],
    list[list[AlignmentOperation | None]],
]:
    """Initialize DP tables for alignment.

    Arguments:
        one: first string
        two: second string
    Returns:
        metric table, backpointer table, last-gap-operation table
    """
    metrics: list[list[AlignmentMetric]] = []
    backpointers: list[list[AlignmentBackpointer | None]] = []
    last_gap_operations: list[list[AlignmentOperation | None]] = []
    for _ in range(len(one) + 1):
        metric_row: list[AlignmentMetric] = []
        backpointer_row: list[AlignmentBackpointer | None] = []
        last_gap_operation_row: list[AlignmentOperation | None] = []
        for _ in range(len(two) + 1):
            metric_row.append(AlignmentMetric(0, 0, 0, 0, 0))
            backpointer_row.append(None)
            last_gap_operation_row.append(None)
        metrics.append(metric_row)
        backpointers.append(backpointer_row)
        last_gap_operations.append(last_gap_operation_row)
    return metrics, backpointers, last_gap_operations


def _init_edges(
    one: str,
    two: str,
    metrics: list[list[AlignmentMetric]],
    backpointers: list[list[AlignmentBackpointer | None]],
    last_gap_operations: list[list[AlignmentOperation | None]],
):
    """Initialize DP boundary conditions before filling interior cells.

    The DP grid compares prefixes of `one` and `two`. Cell `(0, 0)` is the
    empty-prefix base case created in `_init_tables()`. Before the interior of
    the grid can be filled, the top row and left column need explicit values:

    - the left column represents aligning a non-empty prefix of `one` against an
      empty prefix of `two`, which can only be reached by deletes
    - the top row represents aligning an empty prefix of `one` against a
      non-empty prefix of `two`, which can only be reached by inserts

    This function writes those forced edge paths into the metric, backpointer,
    and trailing-gap tables.

    Arguments:
        one: first string
        two: second string
        metrics: metric table
        backpointers: backpointer table
        last_gap_operations: last-gap-operation table
    """
    # Seed the first column with leading deletes from the first string
    for i in range(1, len(one) + 1):
        previous_metric = metrics[i - 1][0]
        add_run = 0
        if last_gap_operations[i - 1][0] != AlignmentOperation.DELETE:
            add_run = 1
        metrics[i][0] = AlignmentMetric(
            distance=previous_metric.distance + 1,
            gap_runs=previous_metric.gap_runs + add_run,
            insertions=previous_metric.insertions,
            deletions=previous_metric.deletions + 1,
            substitutions=previous_metric.substitutions,
        )
        backpointers[i][0] = AlignmentBackpointer(
            previous_i=i - 1,
            previous_j=0,
            operation=AlignmentOperation.DELETE,
        )
        last_gap_operations[i][0] = AlignmentOperation.DELETE

    # Seed the first row with leading inserts from the second string
    for j in range(1, len(two) + 1):
        previous_metric = metrics[0][j - 1]
        add_run = 0
        if last_gap_operations[0][j - 1] != AlignmentOperation.INSERT:
            add_run = 1
        metrics[0][j] = AlignmentMetric(
            distance=previous_metric.distance + 1,
            gap_runs=previous_metric.gap_runs + add_run,
            insertions=previous_metric.insertions + 1,
            deletions=previous_metric.deletions,
            substitutions=previous_metric.substitutions,
        )
        backpointers[0][j] = AlignmentBackpointer(
            previous_i=0,
            previous_j=j - 1,
            operation=AlignmentOperation.INSERT,
        )
        last_gap_operations[0][j] = AlignmentOperation.INSERT


def _fill_tables(
    one: str,
    two: str,
    metrics: list[list[AlignmentMetric]],
    backpointers: list[list[AlignmentBackpointer | None]],
    last_gap_operations: list[list[AlignmentOperation | None]],
) -> None:
    """Fill DP tables for alignment.

    Arguments:
        one: first string
        two: second string
        metrics: metric table
        backpointers: backpointer table
        last_gap_operations: last-gap-operation table
    Returns:
        None.
    """
    rows = len(one) + 1
    cols = len(two) + 1

    for i in range(1, rows):
        for j in range(1, cols):
            previous_metric = metrics[i - 1][j - 1]
            if one[i - 1] == two[j - 1]:
                best = (
                    previous_metric,
                    AlignmentBackpointer(
                        previous_i=i - 1,
                        previous_j=j - 1,
                        operation=AlignmentOperation.MATCH,
                    ),
                    None,
                )
            else:
                best = (
                    AlignmentMetric(
                        distance=previous_metric.distance + 1,
                        gap_runs=previous_metric.gap_runs,
                        insertions=previous_metric.insertions,
                        deletions=previous_metric.deletions,
                        substitutions=previous_metric.substitutions + 1,
                    ),
                    AlignmentBackpointer(
                        previous_i=i - 1,
                        previous_j=j - 1,
                        operation=AlignmentOperation.SUBSTITUTE,
                    ),
                    None,
                )

            previous_metric = metrics[i][j - 1]
            add_run = 0
            if last_gap_operations[i][j - 1] != AlignmentOperation.INSERT:
                add_run = 1
            ins_cand = (
                AlignmentMetric(
                    distance=previous_metric.distance + 1,
                    gap_runs=previous_metric.gap_runs + add_run,
                    insertions=previous_metric.insertions + 1,
                    deletions=previous_metric.deletions,
                    substitutions=previous_metric.substitutions,
                ),
                AlignmentBackpointer(
                    previous_i=i,
                    previous_j=j - 1,
                    operation=AlignmentOperation.INSERT,
                ),
                AlignmentOperation.INSERT,
            )
            if ins_cand[0].comparison_key() < best[0].comparison_key() or (
                ins_cand[0].comparison_key() == best[0].comparison_key()
                and ins_cand[1].operation < best[1].operation
            ):
                best = ins_cand

            previous_metric = metrics[i - 1][j]
            add_run = 0
            if last_gap_operations[i - 1][j] != AlignmentOperation.DELETE:
                add_run = 1
            del_cand = (
                AlignmentMetric(
                    distance=previous_metric.distance + 1,
                    gap_runs=previous_metric.gap_runs + add_run,
                    insertions=previous_metric.insertions,
                    deletions=previous_metric.deletions + 1,
                    substitutions=previous_metric.substitutions,
                ),
                AlignmentBackpointer(
                    previous_i=i - 1,
                    previous_j=j,
                    operation=AlignmentOperation.DELETE,
                ),
                AlignmentOperation.DELETE,
            )
            if del_cand[0].comparison_key() < best[0].comparison_key() or (
                del_cand[0].comparison_key() == best[0].comparison_key()
                and del_cand[1].operation < best[1].operation
            ):
                best = del_cand

            metrics[i][j] = best[0]
            backpointers[i][j] = best[1]
            last_gap_operations[i][j] = best[2]


def _backtrace(
    one: str,
    two: str,
    backpointers: list[list[AlignmentBackpointer | None]],
) -> list[AlignmentPair]:
    """Reconstruct alignment path by backtracing DP pointers.

    Arguments:
        one: first string
        two: second string
        backpointers: backpointer table
    Returns:
        list of aligned output columns
    """
    i = len(one)
    j = len(two)
    out: list[AlignmentPair] = []
    while i != 0 or j != 0:
        backpointer = backpointers[i][j]
        if backpointer is None:
            break
        operation = backpointer.operation
        if operation in (AlignmentOperation.MATCH, AlignmentOperation.SUBSTITUTE):
            out.append(
                AlignmentPair(one=one[i - 1], two=two[j - 1], operation=operation)
            )
        elif operation == AlignmentOperation.INSERT:
            out.append(AlignmentPair(one=None, two=two[j - 1], operation=operation))
        else:
            out.append(AlignmentPair(one=one[i - 1], two=None, operation=operation))
        i = backpointer.previous_i
        j = backpointer.previous_j
    out.reverse()
    return out
