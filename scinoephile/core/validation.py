#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to validation."""

from __future__ import annotations

import difflib
import re
from enum import Enum

from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_groups

__all__ = [
    "LineDifferenceType",
    "get_series_text_differences",
    "get_series_text_line_differences",
]

_WS_RE = re.compile(r"\s+")


class LineDifferenceType(Enum):
    """Types of line-level differences."""

    MISSING = "missing"
    ADDED = "added"
    SPLIT = "split"
    MERGED = "merged"
    MODIFIED = "modified"
    SHIFTED = "shifted"


def _get_series_text_lines(series: Series) -> list[str]:
    """Extract raw text lines from a subtitle series.

    Arguments:
        series: Subtitle series to extract text lines from
    Returns:
        list of text lines
    """
    lines: list[str] = []
    for subtitle in series:
        text = subtitle.text.replace("\\N", "\n")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
    return lines


def _normalize_line(text: str) -> str:
    """Normalize a subtitle line for approximate matching.

    Arguments:
        text: Subtitle line to normalize
    Returns:
        Normalized line
    """
    normalized = _WS_RE.sub(" ", text.strip())
    return normalized.replace("…", "...")


def _add_missing_line_msgs(
    msgs: list[str],
    *,
    diff_type: LineDifferenceType,
    source_label: str,
    target_label: str,
    lines: list[str],
    indices: list[int],
) -> None:
    """Add messages for lines missing from another series.

    Arguments:
        msgs: List of messages to append to
        diff_type: difference type to label messages
        source_label: Label for the source series
        target_label: Label for the target series
        lines: Lines to reference
        indices: Indices of lines in the source list
    """
    msgs.extend(
        [
            (
                f"{diff_type.value}: {source_label}[{idx + 1}] {lines[idx]!r} "
                f"not present in {target_label}"
            )
            for idx in indices
        ]
    )


def _add_replace_block_msgs(
    msgs: list[str],
    *,
    one_lines: list[str],
    two_lines: list[str],
    one_keys: list[str],
    two_keys: list[str],
    one_start: int,
    one_end: int,
    two_start: int,
    two_end: int,
    one_label: str,
    two_label: str,
    similarity_cutoff: float,
) -> None:
    """Add messages for a replace opcode block.

    Arguments:
        msgs: list of messages to append to
        one_lines: raw lines from first series
        two_lines: raw lines from second series
        one_keys: normalized lines from first series
        two_keys: normalized lines from second series
        one_start: starting index in first series
        one_end: ending index in first series
        two_start: starting index in second series
        two_end: ending index in second series
        one_label: label for first series in messages
        two_label: label for second series in messages
        similarity_cutoff: similarity cutoff for pairing replacements
    """
    one_block = list(range(one_start, one_end))
    two_block = list(range(two_start, two_end))
    if len(one_block) == len(two_block):
        if len(one_block) > 1:
            one_joined = _normalize_line(" ".join(one_lines[idx] for idx in one_block))
            two_joined = _normalize_line(" ".join(two_lines[idx] for idx in two_block))
            joined_ratio = difflib.SequenceMatcher(
                None, one_joined, two_joined, autojunk=False
            ).ratio()
            if joined_ratio >= similarity_cutoff:
                one_text = [one_lines[idx] for idx in one_block]
                two_text = [two_lines[idx] for idx in two_block]
                msgs.append(
                    f"{LineDifferenceType.SHIFTED.value}: "
                    f"{one_label}[{one_start + 1}:{one_end + 1}] != "
                    f"{two_label}[{two_start + 1}:{two_end + 1}]: "
                    f"{one_text!r} != {two_text!r}"
                )
                return
        for one_idx, two_idx in zip(one_block, two_block, strict=False):
            ratio = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_keys[two_idx], autojunk=False
            ).ratio()
            if ratio >= similarity_cutoff:
                msgs.append(
                    f"{LineDifferenceType.MODIFIED.value}: "
                    f"{one_label}[{one_idx + 1}] != "
                    f"{two_label}[{two_idx + 1}]: "
                    f"{one_lines[one_idx]!r} != {two_lines[two_idx]!r}"
                )
            else:
                msgs.append(
                    f"{LineDifferenceType.MODIFIED.value}: "
                    f"{one_label}[{one_idx + 1}] != "
                    f"{two_label}[{two_idx + 1}]: "
                    f"{one_lines[one_idx]!r} != {two_lines[two_idx]!r}"
                )
        return
    one_text = [one_lines[idx] for idx in one_block]
    two_text = [two_lines[idx] for idx in two_block]
    one_joined = _normalize_line(" ".join(one_lines[idx] for idx in one_block))
    two_joined = _normalize_line(" ".join(two_lines[idx] for idx in two_block))
    joined_ratio = difflib.SequenceMatcher(
        None, one_joined, two_joined, autojunk=False
    ).ratio()
    if joined_ratio >= similarity_cutoff:
        msgs.append(
            f"{LineDifferenceType.MODIFIED.value}: "
            f"{one_label}[{one_start + 1}:{one_end + 1}] != "
            f"{two_label}[{two_start + 1}:{two_end + 1}]: "
            f"{one_text!r} != {two_text!r}"
        )
        return
    if len(one_block) < len(two_block):
        diff_type = LineDifferenceType.SPLIT
    else:
        diff_type = LineDifferenceType.MERGED
    msgs.append(
        f"{diff_type.value}: "
        f"{one_label}[{one_start + 1}:{one_end + 1}] != "
        f"{two_label}[{two_start + 1}:{two_end + 1}]: "
        f"{one_text!r} != {two_text!r}"
    )


def get_series_text_line_differences(
    one: Series,
    two: Series,
    *,
    one_label: str = "one",
    two_label: str = "two",
    similarity_cutoff: float = 0.6,
) -> list[str]:
    """Compare two subtitle series by line content.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
        one_label: label for first series in messages
        two_label: label for second series in messages
        similarity_cutoff: similarity cutoff for pairing replacements
    Returns:
        list of difference messages
    """
    one_lines = _get_series_text_lines(one)
    two_lines = _get_series_text_lines(two)
    one_keys = [_normalize_line(line) for line in one_lines]
    two_keys = [_normalize_line(line) for line in two_lines]

    matcher = difflib.SequenceMatcher(None, one_keys, two_keys, autojunk=False)
    msgs: list[str] = []
    for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            _add_missing_line_msgs(
                msgs,
                diff_type=LineDifferenceType.MISSING,
                source_label=one_label,
                target_label=two_label,
                lines=one_lines,
                indices=list(range(one_start, one_end)),
            )
            continue
        if tag == "insert":
            _add_missing_line_msgs(
                msgs,
                diff_type=LineDifferenceType.ADDED,
                source_label=two_label,
                target_label=one_label,
                lines=two_lines,
                indices=list(range(two_start, two_end)),
            )
            continue
        if tag != "replace":
            raise ScinoephileError(f"Unhandled opcode: {tag}")
        _add_replace_block_msgs(
            msgs,
            one_lines=one_lines,
            two_lines=two_lines,
            one_keys=one_keys,
            two_keys=two_keys,
            one_start=one_start,
            one_end=one_end,
            two_start=two_start,
            two_end=two_end,
            one_label=one_label,
            two_label=two_label,
            similarity_cutoff=similarity_cutoff,
        )

    return msgs


def get_series_text_differences(
    one: Series,
    two: Series,
    *,
    pause_length: int = 3000,
    cutoff: float = 0.16,
) -> list[str]:
    """Compare two subtitle series and log textual differences.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
        pause_length: pause length for block splitting
        cutoff: overlap cutoff for sync grouping
    Returns:
        list of difference messages
    """
    msgs: list[str] = []
    blk_pairs = get_block_pairs_by_pause(one, two, pause_length=pause_length)
    one_blk_start_idx = 1
    two_blk_start_idx = 1
    for one_blk, two_blk in blk_pairs:
        for one_idxs, two_idxs in get_sync_groups(one_blk, two_blk, cutoff=cutoff):
            if len(one_idxs) == 1 and len(two_idxs) == 0:
                one_text = one_blk[one_idxs[0]].text
                one_idx = one_blk_start_idx + one_idxs[0]
                msgs.append(f"one[{one_idx}] missing in two: {one_text!r}")
                continue
            if len(one_idxs) == 0 and len(two_idxs) == 1:
                two_text = two_blk[two_idxs[0]].text
                two_idx = two_blk_start_idx + two_idxs[0]
                msgs.append(f"one missing two[{two_idx}]: {two_text!r}")
                continue
            if len(one_idxs) == 1 and len(two_idxs) == 1:
                one_text = one_blk[one_idxs[0]].text
                two_text = two_blk[two_idxs[0]].text
                one_idx = one_blk_start_idx + one_idxs[0]
                two_idx = two_blk_start_idx + two_idxs[0]
                if one_text != two_text:
                    msgs.append(
                        f"one[{one_idx}] != two[{two_idx}]: "
                        f"{one_text!r} != {two_text!r}"
                    )
                continue
            if len(one_idxs) > 1 and len(two_idxs) == 1:
                one_text = str([one_blk[i].text for i in one_idxs])
                two_text = two_blk[two_idxs[0]].text
                one_start_idx = one_blk_start_idx + one_idxs[0]
                one_end_idx = one_blk_start_idx + one_idxs[-1]
                two_idx = two_blk_start_idx + two_idxs[0]
                msgs.append(
                    f"one[{one_start_idx}:{one_end_idx + 1}] != two[{two_idx}]: "
                    f"{one_text!r} != {two_text!r}"
                )
                continue
            if len(one_idxs) == 1 and len(two_idxs) > 1:
                one_text = one_blk[one_idxs[0]].text
                two_text = str([two_blk[i].text for i in two_idxs])
                one_idx = one_blk_start_idx + one_idxs[0]
                two_start_idx = two_blk_start_idx + two_idxs[0]
                two_end_idx = two_blk_start_idx + two_idxs[-1]
                msgs.append(
                    f"one[{one_idx}] != two[{two_start_idx}:{two_end_idx + 1}]: "
                    f"{one_text!r} != {two_text!r}"
                )
                continue
            raise ScinoephileError(
                f"Unhandled sync group: one={one_idxs}, two={two_idxs}"
            )
        one_blk_start_idx += len(one_blk)
        two_blk_start_idx += len(two_blk)

    return msgs
