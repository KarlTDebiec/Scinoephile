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


class LineDifferenceType(Enum):
    """Types of line-level differences."""

    MISSING = "missing"
    ADDED = "added"
    SPLIT = "split"
    SPLIT_MODIFIED = "split_modified"
    MERGED = "merged"
    MERGED_MODIFIED = "merged_modified"
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
    stripped = re.sub(r"(?:^|\s)(?:[-–])\s+", " ", text.strip())
    normalized = re.sub(r"\s+", " ", stripped).strip()
    return normalized


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


def _append_block_msg(
    msgs: list[str],
    *,
    diff_type: LineDifferenceType,
    one_slice: list[int],
    two_slice: list[int],
    one_lines: list[str],
    two_lines: list[str],
    one_label: str,
    two_label: str,
) -> None:
    """Append a block-level message."""
    one_text = [one_lines[idx] for idx in one_slice]
    two_text = [two_lines[idx] for idx in two_slice]
    one_start_idx = one_slice[0] + 1
    one_end_idx = one_slice[-1] + 2
    two_start_idx = two_slice[0] + 1
    two_end_idx = two_slice[-1] + 2
    msgs.append(
        f"{diff_type.value}: "
        f"{one_label}[{one_start_idx}:{one_end_idx}] != "
        f"{two_label}[{two_start_idx}:{two_end_idx}]: "
        f"{one_text!r} != {two_text!r}"
    )


def _append_modified_msg(
    msgs: list[str],
    *,
    one_idx: int,
    two_idx: int,
    one_lines: list[str],
    two_lines: list[str],
    one_label: str,
    two_label: str,
) -> None:
    """Append a modified-line message."""
    msgs.append(
        f"{LineDifferenceType.MODIFIED.value}: "
        f"{one_label}[{one_idx + 1}] != "
        f"{two_label}[{two_idx + 1}]: "
        f"{one_lines[one_idx]!r} != {two_lines[two_idx]!r}"
    )


def _add_replace_block_equal_msgs(
    msgs: list[str],
    *,
    one_lines: list[str],
    two_lines: list[str],
    one_keys: list[str],
    two_keys: list[str],
    one_block: list[int],
    two_block: list[int],
    one_label: str,
    two_label: str,
    similarity_cutoff: float,
) -> None:
    """Add messages for equal-sized replace blocks."""
    if len(one_block) == 2 and len(two_block) == 2:
        two_joined = _normalize_line(" ".join(two_lines[idx] for idx in two_block))
        missing_key = one_keys[one_block[0]].casefold()
        merged_key = one_keys[one_block[1]].casefold()
        if merged_key == two_joined.casefold() and all(
            missing_key != two_keys[idx].casefold() for idx in two_block
        ):
            _add_missing_line_msgs(
                msgs,
                diff_type=LineDifferenceType.MISSING,
                source_label=one_label,
                target_label=two_label,
                lines=one_lines,
                indices=[one_block[0]],
            )
            _append_block_msg(
                msgs,
                diff_type=LineDifferenceType.SPLIT,
                one_slice=[one_block[1]],
                two_slice=two_block,
                one_lines=one_lines,
                two_lines=two_lines,
                one_label=one_label,
                two_label=two_label,
            )
            return
    if len(one_block) > 1:
        one_joined = _normalize_line(" ".join(one_lines[idx] for idx in one_block))
        two_joined = _normalize_line(" ".join(two_lines[idx] for idx in two_block))
        joined_ratio = difflib.SequenceMatcher(
            None, one_joined, two_joined, autojunk=False
        ).ratio()
        line_shift_cutoff = 0.85
        line_ratios = [
            difflib.SequenceMatcher(
                None, one_keys[one_idx], two_keys[two_idx], autojunk=False
            ).ratio()
            for one_idx, two_idx in zip(one_block, two_block, strict=False)
        ]
        if joined_ratio >= similarity_cutoff and any(
            ratio < line_shift_cutoff for ratio in line_ratios
        ):
            _append_block_msg(
                msgs,
                diff_type=LineDifferenceType.SHIFTED,
                one_slice=one_block,
                two_slice=two_block,
                one_lines=one_lines,
                two_lines=two_lines,
                one_label=one_label,
                two_label=two_label,
            )
            return
    for one_idx, two_idx in zip(one_block, two_block, strict=False):
        _append_modified_msg(
            msgs,
            one_idx=one_idx,
            two_idx=two_idx,
            one_lines=one_lines,
            two_lines=two_lines,
            one_label=one_label,
            two_label=two_label,
        )


def _add_replace_block_unequal_msgs(  # noqa: PLR0912, PLR0915
    msgs: list[str],
    *,
    one_lines: list[str],
    two_lines: list[str],
    one_keys: list[str],
    two_keys: list[str],
    one_block: list[int],
    two_block: list[int],
    one_label: str,
    two_label: str,
    similarity_cutoff: float,
) -> None:
    """Add messages for unequal-sized replace blocks."""
    i = 0
    j = 0
    last_was_split = False
    while i < len(one_block) and j < len(two_block):
        one_idx = one_block[i]
        two_idx = two_block[j]
        if len(two_block) == 1 and i + 1 < len(one_block):
            one_joined = _normalize_line(
                f"{one_lines[one_block[i]]} {one_lines[one_block[i + 1]]}"
            )
            if one_joined == two_keys[two_idx]:
                _append_block_msg(
                    msgs,
                    diff_type=LineDifferenceType.MERGED,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=[two_idx],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = False
                continue
            merged_ratio = difflib.SequenceMatcher(
                None, one_joined, two_keys[two_idx], autojunk=False
            ).ratio()
            ratio_curr = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_keys[two_idx], autojunk=False
            ).ratio()
            ratio_next = difflib.SequenceMatcher(
                None, one_keys[one_block[i + 1]], two_keys[two_idx], autojunk=False
            ).ratio()
            if merged_ratio >= similarity_cutoff and merged_ratio > max(
                ratio_curr, ratio_next
            ):
                _append_block_msg(
                    msgs,
                    diff_type=LineDifferenceType.MERGED_MODIFIED,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=[two_idx],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = False
                continue
        if (
            j + 3 < len(two_block)
            and i + 1 < len(one_block)
            and len(one_block) - i == 2
            and len(two_block) - j == 4
        ):
            two_joined_first = _normalize_line(
                f"{two_lines[two_block[j]]} {two_lines[two_block[j + 1]]}"
            )
            two_joined_second = _normalize_line(
                f"{two_lines[two_block[j + 2]]} {two_lines[two_block[j + 3]]}"
            )
            first_ratio = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_joined_first, autojunk=False
            ).ratio()
            second_ratio = difflib.SequenceMatcher(
                None, one_keys[one_block[i + 1]], two_joined_second, autojunk=False
            ).ratio()
            if first_ratio >= similarity_cutoff and second_ratio >= similarity_cutoff:
                first_type = (
                    LineDifferenceType.SPLIT
                    if one_keys[one_idx] == two_joined_first
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                second_type = (
                    LineDifferenceType.SPLIT
                    if one_keys[one_block[i + 1]] == two_joined_second
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                _append_block_msg(
                    msgs,
                    diff_type=first_type,
                    one_slice=[one_idx],
                    two_slice=[two_block[j], two_block[j + 1]],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                _append_block_msg(
                    msgs,
                    diff_type=second_type,
                    one_slice=[one_block[i + 1]],
                    two_slice=[two_block[j + 2], two_block[j + 3]],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 4
                last_was_split = True
                continue
        if len(one_block) == 1 and j + 1 < len(two_block):
            two_joined = _normalize_line(
                f"{two_lines[two_block[j]]} {two_lines[two_block[j + 1]]}"
            )
            two_joined_rev = _normalize_line(
                f"{two_lines[two_block[j + 1]]} {two_lines[two_block[j]]}"
            )
            merged_ratio = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_joined, autojunk=False
            ).ratio()
            merged_ratio_rev = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_joined_rev, autojunk=False
            ).ratio()
            best_joined = (
                two_joined_rev if merged_ratio_rev > merged_ratio else two_joined
            )
            if max(merged_ratio, merged_ratio_rev) >= similarity_cutoff:
                diff_type = (
                    LineDifferenceType.SPLIT
                    if one_keys[one_idx] == best_joined
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                _append_block_msg(
                    msgs,
                    diff_type=diff_type,
                    one_slice=[one_idx],
                    two_slice=[two_block[j], two_block[j + 1]],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 1
                j += 2
                last_was_split = True
                continue
        if j + 2 < len(two_block) and i + 1 < len(one_block):
            two_joined = _normalize_line(
                f"{two_lines[two_block[j]]} {two_lines[two_block[j + 1]]}"
            )
            merged_ratio = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_joined, autojunk=False
            ).ratio()
            split_join_cutoff = 0.95
            next_ratio = difflib.SequenceMatcher(
                None,
                one_keys[one_block[i + 1]],
                two_keys[two_block[j + 2]],
                autojunk=False,
            ).ratio()
            if merged_ratio >= split_join_cutoff and next_ratio >= similarity_cutoff:
                diff_type = (
                    LineDifferenceType.SPLIT
                    if one_keys[one_idx] == two_joined
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                _append_block_msg(
                    msgs,
                    diff_type=diff_type,
                    one_slice=[one_idx],
                    two_slice=[two_block[j], two_block[j + 1]],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 1
                j += 2
                last_was_split = True
                continue
        ratio = difflib.SequenceMatcher(
            None, one_keys[one_idx], two_keys[two_idx], autojunk=False
        ).ratio()
        if ratio >= similarity_cutoff:
            _append_modified_msg(
                msgs,
                one_idx=one_idx,
                two_idx=two_idx,
                one_lines=one_lines,
                two_lines=two_lines,
                one_label=one_label,
                two_label=two_label,
            )
            i += 1
            j += 1
            last_was_split = False
            continue
        if j + 1 < len(two_block):
            two_joined = _normalize_line(
                f"{two_lines[two_block[j]]} {two_lines[two_block[j + 1]]}"
            )
            merged_ratio = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_joined, autojunk=False
            ).ratio()
            if merged_ratio >= similarity_cutoff:
                one_slice = [one_idx]
                two_slice = [two_block[j], two_block[j + 1]]
                if one_keys[one_idx] == two_joined:
                    split_type = LineDifferenceType.SPLIT
                    merged_type = LineDifferenceType.MERGED
                else:
                    split_type = LineDifferenceType.SPLIT_MODIFIED
                    merged_type = LineDifferenceType.MERGED_MODIFIED
                if one_keys[one_idx] == two_joined or i == 0 or last_was_split:
                    diff_type = split_type
                    last_was_split = True
                else:
                    diff_type = merged_type
                    last_was_split = False
                _append_block_msg(
                    msgs,
                    diff_type=diff_type,
                    one_slice=one_slice,
                    two_slice=two_slice,
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 1
                j += 2
                continue
        if len(two_block) == 1 and i + 1 < len(one_block):
            one_joined = _normalize_line(
                f"{one_lines[one_block[i]]} {one_lines[one_block[i + 1]]}"
            )
            if one_joined == two_keys[two_idx]:
                _append_block_msg(
                    msgs,
                    diff_type=LineDifferenceType.MERGED,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=[two_idx],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = False
                continue
            ratio_next = difflib.SequenceMatcher(
                None, one_keys[one_block[i + 1]], two_keys[two_idx], autojunk=False
            ).ratio()
            ratio_curr = difflib.SequenceMatcher(
                None, one_keys[one_idx], two_keys[two_idx], autojunk=False
            ).ratio()
            if ratio_next >= similarity_cutoff and ratio_next > ratio_curr:
                _add_missing_line_msgs(
                    msgs,
                    diff_type=LineDifferenceType.MISSING,
                    source_label=one_label,
                    target_label=two_label,
                    lines=one_lines,
                    indices=[one_idx],
                )
                _append_modified_msg(
                    msgs,
                    one_idx=one_block[i + 1],
                    two_idx=two_idx,
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = False
                continue
            one_joined = _normalize_line(
                f"{one_lines[one_block[i]]} {one_lines[one_block[i + 1]]}"
            )
            split_ratio = difflib.SequenceMatcher(
                None, one_joined, two_keys[two_idx], autojunk=False
            ).ratio()
            if split_ratio >= similarity_cutoff:
                diff_type = (
                    LineDifferenceType.SPLIT
                    if one_joined == two_keys[two_idx]
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                _append_block_msg(
                    msgs,
                    diff_type=diff_type,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=[two_idx],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = True
                continue
        if len(two_block) >= 2 and i + 1 < len(one_block):
            one_joined = _normalize_line(
                f"{one_lines[one_block[i]]} {one_lines[one_block[i + 1]]}"
            )
            two_joined = _normalize_line(
                " ".join(two_lines[idx] for idx in two_block[j:])
            )
            if one_joined == two_joined:
                _append_block_msg(
                    msgs,
                    diff_type=LineDifferenceType.SPLIT,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=two_block[j:],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                return
        if i + 1 < len(one_block):
            one_joined = _normalize_line(
                f"{one_lines[one_block[i]]} {one_lines[one_block[i + 1]]}"
            )
            split_ratio = difflib.SequenceMatcher(
                None, one_joined, two_keys[two_idx], autojunk=False
            ).ratio()
            if split_ratio >= similarity_cutoff:
                diff_type = (
                    LineDifferenceType.SPLIT
                    if one_joined == two_keys[two_idx]
                    else LineDifferenceType.SPLIT_MODIFIED
                )
                _append_block_msg(
                    msgs,
                    diff_type=diff_type,
                    one_slice=[one_block[i], one_block[i + 1]],
                    two_slice=[two_idx],
                    one_lines=one_lines,
                    two_lines=two_lines,
                    one_label=one_label,
                    two_label=two_label,
                )
                i += 2
                j += 1
                last_was_split = True
                continue
        _append_modified_msg(
            msgs,
            one_idx=one_idx,
            two_idx=two_idx,
            one_lines=one_lines,
            two_lines=two_lines,
            one_label=one_label,
            two_label=two_label,
        )
        i += 1
        j += 1
        last_was_split = False
    if i < len(one_block) and j < len(two_block):
        one_slice = one_block[i:]
        two_slice = two_block[j:]
        one_joined = _normalize_line(" ".join(one_lines[idx] for idx in one_slice))
        two_joined = _normalize_line(" ".join(two_lines[idx] for idx in two_slice))
        if len(one_slice) < len(two_slice):
            diff_type = (
                LineDifferenceType.SPLIT
                if one_joined == two_joined
                else LineDifferenceType.SPLIT_MODIFIED
            )
        else:
            diff_type = (
                LineDifferenceType.MERGED
                if one_joined == two_joined
                else LineDifferenceType.MERGED_MODIFIED
            )
        _append_block_msg(
            msgs,
            diff_type=diff_type,
            one_slice=one_slice,
            two_slice=two_slice,
            one_lines=one_lines,
            two_lines=two_lines,
            one_label=one_label,
            two_label=two_label,
        )
        return
    if i < len(one_block):
        _add_missing_line_msgs(
            msgs,
            diff_type=LineDifferenceType.MISSING,
            source_label=one_label,
            target_label=two_label,
            lines=one_lines,
            indices=one_block[i:],
        )
        return
    if j < len(two_block):
        _add_missing_line_msgs(
            msgs,
            diff_type=LineDifferenceType.ADDED,
            source_label=two_label,
            target_label=one_label,
            lines=two_lines,
            indices=two_block[j:],
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
    """Add messages for a replace opcode block."""
    one_block = list(range(one_start, one_end))
    two_block = list(range(two_start, two_end))
    if len(one_block) == len(two_block):
        _add_replace_block_equal_msgs(
            msgs,
            one_lines=one_lines,
            two_lines=two_lines,
            one_keys=one_keys,
            two_keys=two_keys,
            one_block=one_block,
            two_block=two_block,
            one_label=one_label,
            two_label=two_label,
            similarity_cutoff=similarity_cutoff,
        )
        return
    _add_replace_block_unequal_msgs(
        msgs,
        one_lines=one_lines,
        two_lines=two_lines,
        one_keys=one_keys,
        two_keys=two_keys,
        one_block=one_block,
        two_block=two_block,
        one_label=one_label,
        two_label=two_label,
        similarity_cutoff=similarity_cutoff,
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
