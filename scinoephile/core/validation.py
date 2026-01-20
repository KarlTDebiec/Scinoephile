#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to validation."""

from __future__ import annotations

import difflib
import re
from enum import Enum

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series

__all__ = [
    "LineDiffKind",
    "get_series_diff",
]


class LineDiffKind(Enum):
    """Types of line-level differences."""

    DELETE = "delete"
    EDIT = "edit"
    INSERT = "insert"
    MERGE = "merge"
    MERGE_EDIT = "merge_edit"
    SHIFT = "shift"
    SPLIT = "split"
    SPLIT_EDIT = "split_edit"


class LineDiffer:
    """Compute line-level differences between subtitle series."""

    def __init__(
        self,
        one: Series,
        two: Series,
        *,
        one_label: str,
        two_label: str,
        similarity_cutoff: float,
    ) -> None:
        """Initialize line differ state.

        Arguments:
            one: First subtitle series
            two: Second subtitle series
            one_label: label for first series in messages
            two_label: label for second series in messages
            similarity_cutoff: similarity cutoff for pairing replacements
        """
        self.one_label = one_label
        self.two_label = two_label
        self.similarity_cutoff = similarity_cutoff
        self.one_lines = self._get_series_text_lines(one)
        self.two_lines = self._get_series_text_lines(two)
        self.one_keys = [self._normalize_line(line) for line in self.one_lines]
        self.two_keys = [self._normalize_line(line) for line in self.two_lines]

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def _add_missing_line_msgs(
        msgs: list[str],
        *,
        diff_type: LineDiffKind,
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

    def _add_delete_msgs(self, msgs: list[str], indices: list[int]) -> None:
        """Add messages for lines deleted from the second series."""
        self._add_missing_line_msgs(
            msgs,
            diff_type=LineDiffKind.DELETE,
            source_label=self.one_label,
            target_label=self.two_label,
            lines=self.one_lines,
            indices=indices,
        )

    def _add_insert_msgs(self, msgs: list[str], indices: list[int]) -> None:
        """Add messages for lines inserted in the second series."""
        self._add_missing_line_msgs(
            msgs,
            diff_type=LineDiffKind.INSERT,
            source_label=self.two_label,
            target_label=self.one_label,
            lines=self.two_lines,
            indices=indices,
        )

    def _append_block_msg(
        self,
        msgs: list[str],
        *,
        diff_type: LineDiffKind,
        one_slice: list[int],
        two_slice: list[int],
    ) -> None:
        """Append a block-level message."""
        one_text = [self.one_lines[idx] for idx in one_slice]
        two_text = [self.two_lines[idx] for idx in two_slice]
        one_start_idx = one_slice[0] + 1
        one_end_idx = one_slice[-1] + 1
        two_start_idx = two_slice[0] + 1
        two_end_idx = two_slice[-1] + 1
        one_idx_text = (
            f"{one_start_idx}"
            if len(one_slice) == 1
            else f"{one_start_idx}-{one_end_idx}"
        )
        two_idx_text = (
            f"{two_start_idx}"
            if len(two_slice) == 1
            else f"{two_start_idx}-{two_end_idx}"
        )
        msgs.append(
            f"{diff_type.value}: "
            f"{self.one_label}[{one_idx_text}] -> "
            f"{self.two_label}[{two_idx_text}]: "
            f"{one_text!r} -> {two_text!r}"
        )

    def _append_modified_msg(
        self,
        msgs: list[str],
        *,
        one_idx: int,
        two_idx: int,
    ) -> None:
        """Append an edited-line message."""
        msgs.append(
            f"{LineDiffKind.EDIT.value}: "
            f"{self.one_label}[{one_idx + 1}] -> "
            f"{self.two_label}[{two_idx + 1}]: "
            f"{self.one_lines[one_idx]!r} -> {self.two_lines[two_idx]!r}"
        )

    def _add_replace_block_equal_msgs(
        self,
        msgs: list[str],
        *,
        one_block: list[int],
        two_block: list[int],
    ) -> None:
        """Add messages for equal-sized replace blocks."""
        if len(one_block) == 2 and len(two_block) == 2:
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_block)
            )
            missing_key = self.one_keys[one_block[0]].casefold()
            merged_key = self.one_keys[one_block[1]].casefold()
            if merged_key == two_joined.casefold() and all(
                missing_key != self.two_keys[idx].casefold() for idx in two_block
            ):
                self._add_missing_line_msgs(
                    msgs,
                    diff_type=LineDiffKind.DELETE,
                    source_label=self.one_label,
                    target_label=self.two_label,
                    lines=self.one_lines,
                    indices=[one_block[0]],
                )
                self._append_block_msg(
                    msgs,
                    diff_type=LineDiffKind.SPLIT,
                    one_slice=[one_block[1]],
                    two_slice=two_block,
                )
                return
        if len(one_block) > 1:
            one_joined = self._normalize_line(
                " ".join(self.one_lines[idx] for idx in one_block)
            )
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_block)
            )
            joined_ratio = difflib.SequenceMatcher(
                None, one_joined, two_joined, autojunk=False
            ).ratio()
            line_shift_cutoff = 0.85
            line_ratios = [
                difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
                ).ratio()
                for one_idx, two_idx in zip(one_block, two_block, strict=False)
            ]
            if joined_ratio >= self.similarity_cutoff and any(
                ratio < line_shift_cutoff for ratio in line_ratios
            ):
                self._append_block_msg(
                    msgs,
                    diff_type=LineDiffKind.SHIFT,
                    one_slice=one_block,
                    two_slice=two_block,
                )
                return
        for one_idx, two_idx in zip(one_block, two_block, strict=False):
            self._append_modified_msg(msgs, one_idx=one_idx, two_idx=two_idx)

    def _add_replace_block_unequal_msgs(  # noqa: PLR0912, PLR0915
        self,
        msgs: list[str],
        *,
        one_block: list[int],
        two_block: list[int],
    ) -> None:
        """Add messages for unequal-sized replace blocks."""
        i = 0
        j = 0
        last_was_split = False
        while i < len(one_block) and j < len(two_block):
            one_idx = one_block[i]
            two_idx = two_block[j]
            if len(two_block) == 1 and i + 1 < len(one_block):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_block[i]]} {self.one_lines[one_block[i + 1]]}"
                )
                if one_joined == self.two_keys[two_idx]:
                    self._append_block_msg(
                        msgs,
                        diff_type=LineDiffKind.MERGE,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=[two_idx],
                    )
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
                merged_ratio = difflib.SequenceMatcher(
                    None, one_joined, self.two_keys[two_idx], autojunk=False
                ).ratio()
                ratio_curr = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
                ).ratio()
                ratio_next = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_block[i + 1]],
                    self.two_keys[two_idx],
                    autojunk=False,
                ).ratio()
                if merged_ratio >= self.similarity_cutoff and merged_ratio > max(
                    ratio_curr, ratio_next
                ):
                    self._append_block_msg(
                        msgs,
                        diff_type=LineDiffKind.MERGE_EDIT,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=[two_idx],
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
                two_joined_first = self._normalize_line(
                    f"{self.two_lines[two_block[j]]} {self.two_lines[two_block[j + 1]]}"
                )
                two_joined_second = self._normalize_line(
                    f"{self.two_lines[two_block[j + 2]]} "
                    f"{self.two_lines[two_block[j + 3]]}"
                )
                first_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined_first, autojunk=False
                ).ratio()
                second_ratio = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_block[i + 1]],
                    two_joined_second,
                    autojunk=False,
                ).ratio()
                if (
                    first_ratio >= self.similarity_cutoff
                    and second_ratio >= self.similarity_cutoff
                ):
                    first_type = (
                        LineDiffKind.SPLIT
                        if self.one_keys[one_idx] == two_joined_first
                        else LineDiffKind.SPLIT_EDIT
                    )
                    second_type = (
                        LineDiffKind.SPLIT
                        if self.one_keys[one_block[i + 1]] == two_joined_second
                        else LineDiffKind.SPLIT_EDIT
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=first_type,
                        one_slice=[one_idx],
                        two_slice=[two_block[j], two_block[j + 1]],
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=second_type,
                        one_slice=[one_block[i + 1]],
                        two_slice=[two_block[j + 2], two_block[j + 3]],
                    )
                    i += 2
                    j += 4
                    last_was_split = True
                    continue
            if len(one_block) == 1 and j + 1 < len(two_block):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_block[j]]} {self.two_lines[two_block[j + 1]]}"
                )
                two_joined_rev = self._normalize_line(
                    f"{self.two_lines[two_block[j + 1]]} {self.two_lines[two_block[j]]}"
                )
                merged_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined, autojunk=False
                ).ratio()
                merged_ratio_rev = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined_rev, autojunk=False
                ).ratio()
                best_joined = (
                    two_joined_rev if merged_ratio_rev > merged_ratio else two_joined
                )
                if max(merged_ratio, merged_ratio_rev) >= self.similarity_cutoff:
                    diff_type = (
                        LineDiffKind.SPLIT
                        if self.one_keys[one_idx] == best_joined
                        else LineDiffKind.SPLIT_EDIT
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=diff_type,
                        one_slice=[one_idx],
                        two_slice=[two_block[j], two_block[j + 1]],
                    )
                    i += 1
                    j += 2
                    last_was_split = True
                    continue
            if j + 2 < len(two_block) and i + 1 < len(one_block):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_block[j]]} {self.two_lines[two_block[j + 1]]}"
                )
                merged_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined, autojunk=False
                ).ratio()
                split_join_cutoff = 0.95
                next_ratio = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_block[i + 1]],
                    self.two_keys[two_block[j + 2]],
                    autojunk=False,
                ).ratio()
                if (
                    merged_ratio >= split_join_cutoff
                    and next_ratio >= self.similarity_cutoff
                ):
                    diff_type = (
                        LineDiffKind.SPLIT
                        if self.one_keys[one_idx] == two_joined
                        else LineDiffKind.SPLIT_EDIT
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=diff_type,
                        one_slice=[one_idx],
                        two_slice=[two_block[j], two_block[j + 1]],
                    )
                    i += 1
                    j += 2
                    last_was_split = True
                    continue
            ratio = difflib.SequenceMatcher(
                None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
            ).ratio()
            if ratio >= self.similarity_cutoff:
                self._append_modified_msg(msgs, one_idx=one_idx, two_idx=two_idx)
                i += 1
                j += 1
                last_was_split = False
                continue
            if j + 1 < len(two_block):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_block[j]]} {self.two_lines[two_block[j + 1]]}"
                )
                merged_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined, autojunk=False
                ).ratio()
                if merged_ratio >= self.similarity_cutoff:
                    one_slice = [one_idx]
                    two_slice = [two_block[j], two_block[j + 1]]
                    if self.one_keys[one_idx] == two_joined:
                        split_type = LineDiffKind.SPLIT
                        merged_type = LineDiffKind.MERGE
                    else:
                        split_type = LineDiffKind.SPLIT_EDIT
                        merged_type = LineDiffKind.MERGE_EDIT
                    if self.one_keys[one_idx] == two_joined or i == 0 or last_was_split:
                        diff_type = split_type
                        last_was_split = True
                    else:
                        diff_type = merged_type
                        last_was_split = False
                    self._append_block_msg(
                        msgs,
                        diff_type=diff_type,
                        one_slice=one_slice,
                        two_slice=two_slice,
                    )
                    i += 1
                    j += 2
                    continue
            if len(two_block) == 1 and i + 1 < len(one_block):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_block[i]]} {self.one_lines[one_block[i + 1]]}"
                )
                if one_joined == self.two_keys[two_idx]:
                    self._append_block_msg(
                        msgs,
                        diff_type=LineDiffKind.MERGE,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=[two_idx],
                    )
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
                ratio_next = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_block[i + 1]],
                    self.two_keys[two_idx],
                    autojunk=False,
                ).ratio()
                ratio_curr = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
                ).ratio()
                if ratio_next >= self.similarity_cutoff and ratio_next > ratio_curr:
                    self._add_missing_line_msgs(
                        msgs,
                        diff_type=LineDiffKind.DELETE,
                        source_label=self.one_label,
                        target_label=self.two_label,
                        lines=self.one_lines,
                        indices=[one_idx],
                    )
                    self._append_modified_msg(
                        msgs,
                        one_idx=one_block[i + 1],
                        two_idx=two_idx,
                    )
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_block[i]]} {self.one_lines[one_block[i + 1]]}"
                )
                split_ratio = difflib.SequenceMatcher(
                    None, one_joined, self.two_keys[two_idx], autojunk=False
                ).ratio()
                if split_ratio >= self.similarity_cutoff:
                    diff_type = (
                        LineDiffKind.SPLIT
                        if one_joined == self.two_keys[two_idx]
                        else LineDiffKind.SPLIT_EDIT
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=diff_type,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=[two_idx],
                    )
                    i += 2
                    j += 1
                    last_was_split = True
                    continue
            if len(two_block) >= 2 and i + 1 < len(one_block):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_block[i]]} {self.one_lines[one_block[i + 1]]}"
                )
                two_joined = self._normalize_line(
                    " ".join(self.two_lines[idx] for idx in two_block[j:])
                )
                if one_joined == two_joined:
                    self._append_block_msg(
                        msgs,
                        diff_type=LineDiffKind.SPLIT,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=two_block[j:],
                    )
                    return
            if i + 1 < len(one_block):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_block[i]]} {self.one_lines[one_block[i + 1]]}"
                )
                split_ratio = difflib.SequenceMatcher(
                    None, one_joined, self.two_keys[two_idx], autojunk=False
                ).ratio()
                if split_ratio >= self.similarity_cutoff:
                    diff_type = (
                        LineDiffKind.SPLIT
                        if one_joined == self.two_keys[two_idx]
                        else LineDiffKind.SPLIT_EDIT
                    )
                    self._append_block_msg(
                        msgs,
                        diff_type=diff_type,
                        one_slice=[one_block[i], one_block[i + 1]],
                        two_slice=[two_idx],
                    )
                    i += 2
                    j += 1
                    last_was_split = True
                    continue
            self._append_modified_msg(msgs, one_idx=one_idx, two_idx=two_idx)
            i += 1
            j += 1
            last_was_split = False
        if i < len(one_block) and j < len(two_block):
            one_slice = one_block[i:]
            two_slice = two_block[j:]
            one_joined = self._normalize_line(
                " ".join(self.one_lines[idx] for idx in one_slice)
            )
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_slice)
            )
            if len(one_slice) < len(two_slice):
                diff_type = (
                    LineDiffKind.SPLIT
                    if one_joined == two_joined
                    else LineDiffKind.SPLIT_EDIT
                )
            else:
                diff_type = (
                    LineDiffKind.MERGE
                    if one_joined == two_joined
                    else LineDiffKind.MERGE_EDIT
                )
            self._append_block_msg(
                msgs,
                diff_type=diff_type,
                one_slice=one_slice,
                two_slice=two_slice,
            )
            return
        if i < len(one_block):
            self._add_missing_line_msgs(
                msgs,
                diff_type=LineDiffKind.DELETE,
                source_label=self.one_label,
                target_label=self.two_label,
                lines=self.one_lines,
                indices=one_block[i:],
            )
            return
        if j < len(two_block):
            self._add_missing_line_msgs(
                msgs,
                diff_type=LineDiffKind.INSERT,
                source_label=self.two_label,
                target_label=self.one_label,
                lines=self.two_lines,
                indices=two_block[j:],
            )

    def _add_replace_block_msgs(
        self,
        msgs: list[str],
        *,
        one_start: int,
        one_end: int,
        two_start: int,
        two_end: int,
    ) -> None:
        """Add messages for a replace opcode block."""
        one_block = list(range(one_start, one_end))
        two_block = list(range(two_start, two_end))
        if len(one_block) == len(two_block):
            self._add_replace_block_equal_msgs(
                msgs,
                one_block=one_block,
                two_block=two_block,
            )
            return
        self._add_replace_block_unequal_msgs(
            msgs,
            one_block=one_block,
            two_block=two_block,
        )

    def diff(self) -> list[str]:
        """Compare subtitle series by line content.

        Returns:
            list of difference messages
        """
        matcher = difflib.SequenceMatcher(
            None, self.one_keys, self.two_keys, autojunk=False
        )
        msgs: list[str] = []
        for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            if tag == "delete":
                self._add_delete_msgs(msgs, list(range(one_start, one_end)))
                continue
            if tag == "insert":
                self._add_insert_msgs(msgs, list(range(two_start, two_end)))
                continue
            if tag != "replace":
                raise ScinoephileError(f"Unhandled opcode: {tag}")
            self._add_replace_block_msgs(
                msgs,
                one_start=one_start,
                one_end=one_end,
                two_start=two_start,
                two_end=two_end,
            )
        return msgs


def get_series_diff(
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
    return LineDiffer(
        one,
        two,
        one_label=one_label,
        two_label=two_label,
        similarity_cutoff=similarity_cutoff,
    ).diff()
