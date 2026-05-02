#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level alignment helpers.

This module centralizes character alignment so that:

- visual diffs can render per-character operations (match/insert/delete/substitute)
- CER calculations can derive edit counts from the same alignment path
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "AlignmentOp",
    "AlignmentPolicy",
    "AlignedChar",
    "align_chars",
    "count_edits",
]


class AlignmentOp(Enum):
    """Alignment operation for a single output column."""

    MATCH = "match"
    SUBSTITUTE = "substitute"
    INSERT = "insert"
    DELETE = "delete"


class AlignmentPolicy(Enum):
    """Tie-breaking policy for alignment."""

    HUMAN = "human"
    CER_LEGACY = "cer_legacy"


@dataclass(frozen=True)
class AlignedChar:
    """A single aligned output column."""

    one: str | None
    two: str | None
    op: AlignmentOp


_metric_t = tuple[int, int, int, int, int]
"""Internal DP metric tuple.

Order: (distance, gap_runs, ins, dels, subs)
"""


def _op_pref(op: AlignmentOp, *, policy: AlignmentPolicy) -> int:
    """Return operation tie-break preference.

    Arguments:
        op: operation to rank
        policy: alignment policy
    Returns:
        integer where lower is preferred
    """
    if policy == AlignmentPolicy.CER_LEGACY:
        # Mirror legacy CER DP behavior: when ranked metrics tie, prefer the first
        # candidate in the legacy order (substitute, insert, delete).
        return {
            AlignmentOp.MATCH: 0,
            AlignmentOp.SUBSTITUTE: 1,
            AlignmentOp.INSERT: 2,
            AlignmentOp.DELETE: 3,
        }[op]
    return {
        AlignmentOp.MATCH: 0,
        AlignmentOp.SUBSTITUTE: 1,
        AlignmentOp.DELETE: 2,
        AlignmentOp.INSERT: 3,
    }[op]


def _rank(metric: _metric_t, *, policy: AlignmentPolicy) -> tuple[int, ...]:
    """Return tuple used to rank candidate DP states.

    Arguments:
        metric: DP metric tuple
        policy: alignment policy
    Returns:
        tuple used for lexicographic comparison
    """
    distance, gap_runs, ins, dels, subs = metric
    if policy == AlignmentPolicy.CER_LEGACY:
        return (distance, ins, dels, subs)
    return (distance, gap_runs, subs, dels, ins)


def _init_tables(
    one: str, two: str
) -> tuple[
    list[list[_metric_t]],
    list[list[tuple[int, int, AlignmentOp] | None]],
    list[list[AlignmentOp | None]],
]:
    """Initialize DP tables for alignment.

    Arguments:
        one: first string
        two: second string
    Returns:
        dp metric table, backpointer table, last-gap table
    """
    rows = len(one) + 1
    cols = len(two) + 1
    dp: list[list[_metric_t]] = [
        [(0, 0, 0, 0, 0) for _ in range(cols)] for _ in range(rows)
    ]
    back: list[list[tuple[int, int, AlignmentOp] | None]] = [
        [None for _ in range(cols)] for _ in range(rows)
    ]
    last_gap: list[list[AlignmentOp | None]] = [
        [None for _ in range(cols)] for _ in range(rows)
    ]
    return dp, back, last_gap


def _initialize_edges(
    one: str,
    two: str,
    dp: list[list[_metric_t]],
    back: list[list[tuple[int, int, AlignmentOp] | None]],
    last_gap: list[list[AlignmentOp | None]],
) -> None:
    """Initialize DP edge conditions.

    Arguments:
        one: first string
        two: second string
        dp: DP metric table
        back: backpointer table
        last_gap: last-gap table
    Returns:
        None.
    """
    rows = len(one) + 1
    cols = len(two) + 1

    for i in range(1, rows):
        distance, gap_runs, ins, dels, subs = dp[i - 1][0]
        add_run = 1 if last_gap[i - 1][0] != AlignmentOp.DELETE else 0
        dp[i][0] = (distance + 1, gap_runs + add_run, ins, dels + 1, subs)
        back[i][0] = (i - 1, 0, AlignmentOp.DELETE)
        last_gap[i][0] = AlignmentOp.DELETE

    for j in range(1, cols):
        distance, gap_runs, ins, dels, subs = dp[0][j - 1]
        add_run = 1 if last_gap[0][j - 1] != AlignmentOp.INSERT else 0
        dp[0][j] = (distance + 1, gap_runs + add_run, ins + 1, dels, subs)
        back[0][j] = (0, j - 1, AlignmentOp.INSERT)
        last_gap[0][j] = AlignmentOp.INSERT


def _fill_tables(
    one: str,
    two: str,
    *,
    policy: AlignmentPolicy,
    dp: list[list[_metric_t]],
    back: list[list[tuple[int, int, AlignmentOp] | None]],
    last_gap: list[list[AlignmentOp | None]],
) -> None:
    """Fill DP tables for alignment.

    Arguments:
        one: first string
        two: second string
        policy: alignment policy
        dp: DP metric table
        back: backpointer table
        last_gap: last-gap table
    Returns:
        None.
    """
    rows = len(one) + 1
    cols = len(two) + 1

    for i in range(1, rows):
        for j in range(1, cols):
            pdist, pgap_runs, pins, pdels, psubs = dp[i - 1][j - 1]
            if one[i - 1] == two[j - 1]:
                best = (
                    (pdist, pgap_runs, pins, pdels, psubs),
                    (i - 1, j - 1, AlignmentOp.MATCH),
                    None,
                )
            else:
                best = (
                    (pdist + 1, pgap_runs, pins, pdels, psubs + 1),
                    (i - 1, j - 1, AlignmentOp.SUBSTITUTE),
                    None,
                )

            pdist, pgap_runs, pins, pdels, psubs = dp[i][j - 1]
            add_run = 1 if last_gap[i][j - 1] != AlignmentOp.INSERT else 0
            ins_cand = (
                (pdist + 1, pgap_runs + add_run, pins + 1, pdels, psubs),
                (i, j - 1, AlignmentOp.INSERT),
                AlignmentOp.INSERT,
            )
            if _rank(ins_cand[0], policy=policy) < _rank(best[0], policy=policy) or (
                _rank(ins_cand[0], policy=policy) == _rank(best[0], policy=policy)
                and _op_pref(ins_cand[1][2], policy=policy)
                < _op_pref(best[1][2], policy=policy)
            ):
                best = ins_cand

            pdist, pgap_runs, pins, pdels, psubs = dp[i - 1][j]
            add_run = 1 if last_gap[i - 1][j] != AlignmentOp.DELETE else 0
            del_cand = (
                (pdist + 1, pgap_runs + add_run, pins, pdels + 1, psubs),
                (i - 1, j, AlignmentOp.DELETE),
                AlignmentOp.DELETE,
            )
            if _rank(del_cand[0], policy=policy) < _rank(best[0], policy=policy) or (
                _rank(del_cand[0], policy=policy) == _rank(best[0], policy=policy)
                and _op_pref(del_cand[1][2], policy=policy)
                < _op_pref(best[1][2], policy=policy)
            ):
                best = del_cand

            dp[i][j] = best[0]
            back[i][j] = best[1]
            last_gap[i][j] = best[2]


def _backtrace(
    one: str,
    two: str,
    back: list[list[tuple[int, int, AlignmentOp] | None]],
) -> list[AlignedChar]:
    """Reconstruct alignment path by backtracing DP pointers.

    Arguments:
        one: first string
        two: second string
        back: backpointer table
    Returns:
        list of aligned output columns
    """
    i = len(one)
    j = len(two)
    out: list[AlignedChar] = []
    while i != 0 or j != 0:
        bp = back[i][j]
        if bp is None:
            break
        pi, pj, op = bp
        if op in (AlignmentOp.MATCH, AlignmentOp.SUBSTITUTE):
            out.append(AlignedChar(one=one[i - 1], two=two[j - 1], op=op))
        elif op == AlignmentOp.INSERT:
            out.append(AlignedChar(one=None, two=two[j - 1], op=op))
        else:
            out.append(AlignedChar(one=one[i - 1], two=None, op=op))
        i, j = pi, pj
    out.reverse()
    return out


def count_edits(alignment: list[AlignedChar]) -> tuple[int, int, int, int]:
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
        if col.op == AlignmentOp.MATCH:
            correct += 1
        elif col.op == AlignmentOp.SUBSTITUTE:
            substitutions += 1
        elif col.op == AlignmentOp.INSERT:
            insertions += 1
        else:
            deletions += 1
    return substitutions, insertions, deletions, correct


def align_chars(
    one: str,
    two: str,
    *,
    policy: AlignmentPolicy = AlignmentPolicy.HUMAN,
) -> list[AlignedChar]:
    """Align two strings at the character level.

    Uses Levenshtein-style dynamic programming with backtrace.

    Arguments:
        one: first string
        two: second string
        policy: tie-breaking policy
    Returns:
        list of aligned columns
    """
    dp, back, last_gap = _init_tables(one, two)
    _initialize_edges(one, two, dp, back, last_gap)
    _fill_tables(one, two, policy=policy, dp=dp, back=back, last_gap=last_gap)
    return _backtrace(one, two, back)
