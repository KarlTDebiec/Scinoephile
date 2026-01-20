#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing."""

from __future__ import annotations

import difflib
import re

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.validation.line_diff import LineDiff
from scinoephile.core.validation.line_diff_kind import LineDiffKind

__all__ = ["SeriesDiff"]


class SeriesDiff:
    """Compute line-level differences between subtitle series."""

    def __init__(
        self,
        one: Series,
        two: Series,
        *,
        one_lbl: str = "one",
        two_lbl: str = "two",
        similarity_cutoff: float = 0.6,
    ):
        """Initialize series diff state.

        Arguments:
            one: First subtitle series
            two: Second subtitle series
            one_lbl: label for first series in messages
            two_lbl: label for second series in messages
            similarity_cutoff: similarity cutoff for pairing replacements
        """
        self.one_lbl = one_lbl
        self.two_lbl = two_lbl
        self.similarity_cutoff = similarity_cutoff
        self.one_lines = self._get_series_text_lines(one)
        self.two_lines = self._get_series_text_lines(two)
        self.one_keys = [self._normalize_line(line) for line in self.one_lines]
        self.two_keys = [self._normalize_line(line) for line in self.two_lines]
        self.msgs: list[LineDiff] = []
        self._diff()

    def _diff(self) -> list[LineDiff]:
        """Compare subtitle series by line content.

        Returns:
            list of difference messages
        """
        matcher = difflib.SequenceMatcher(
            None, self.one_keys, self.two_keys, autojunk=False
        )
        for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            if tag == "delete":
                self._process_delete(one_start, one_end)
                continue
            if tag == "insert":
                self._process_insert(two_start, two_end)
                continue
            if tag == "replace":
                self._process_replace(one_start, one_end, two_start, two_end)
                continue
            raise ScinoephileError(f"Unhandled opcode: {tag}")

        return self.msgs

    def _process_delete(self, one_start: int, one_end: int):
        """Process delete opcode block."""
        for idx in range(one_start, one_end):
            msg = LineDiff(
                kind=LineDiffKind.DELETE,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                one_idxs=[idx],
                one_texts=[self.one_lines[idx]],
            )
            self.msgs.append(msg)

    def _process_insert(self, two_start: int, two_end: int):
        """Process insert opcode block."""
        for idx in range(two_start, two_end):
            msg = LineDiff(
                kind=LineDiffKind.INSERT,
                one_lbl=self.two_lbl,
                two_lbl=self.one_lbl,
                one_idxs=[idx],
                one_texts=[self.two_lines[idx]],
            )
            self.msgs.append(msg)

    def _process_replace(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process replace opcode block."""
        one_blk = list(range(one_start, one_end))
        two_blk = list(range(two_start, two_end))
        if len(one_blk) == len(two_blk):
            self._process_replace_equal(one_blk, two_blk)
            return
        self._process_replace_unequal(one_blk, two_blk)

    def _process_replace_equal(self, one_blk: list[int], two_blk: list[int]):
        """Add messages for equal-sized replace blocks."""
        if len(one_blk) == 2 and len(two_blk) == 2:
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_blk)
            )
            missing_key = self.one_keys[one_blk[0]].casefold()
            merged_key = self.one_keys[one_blk[1]].casefold()
            if merged_key == two_joined.casefold() and all(
                missing_key != self.two_keys[idx].casefold() for idx in two_blk
            ):
                self._process_delete(one_start=one_blk[0], one_end=one_blk[0] + 1)
                self._process_split(
                    one_blk[1], one_blk[1] + 1, two_blk[0], two_blk[-1] + 1
                )
                return
        if len(one_blk) > 1:
            one_joined = self._normalize_line(
                " ".join(self.one_lines[idx] for idx in one_blk)
            )
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_blk)
            )
            joined_ratio = difflib.SequenceMatcher(
                None, one_joined, two_joined, autojunk=False
            ).ratio()
            line_shift_cutoff = 0.85
            line_ratios = [
                difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
                ).ratio()
                for one_idx, two_idx in zip(one_blk, two_blk, strict=False)
            ]
            if joined_ratio >= self.similarity_cutoff and any(
                ratio < line_shift_cutoff for ratio in line_ratios
            ):
                self._process_shift(
                    one_blk[0], one_blk[-1] + 1, two_blk[0], two_blk[-1] + 1
                )
                return
        for one_idx, two_idx in zip(one_blk, two_blk, strict=False):
            self._process_edit(one_idx, two_idx)

    def _process_replace_unequal(self, one_blk: list[int], two_blk: list[int]):
        """Add messages for unequal-sized replace blocks."""
        i = 0
        j = 0
        last_was_split = False
        while i < len(one_blk) and j < len(two_blk):
            one_idx = one_blk[i]
            two_idx = two_blk[j]
            if len(two_blk) == 1 and i + 1 < len(one_blk):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_blk[i]]} {self.one_lines[one_blk[i + 1]]}"
                )
                if one_joined == self.two_keys[two_idx]:
                    self._process_merge(
                        one_blk[i], one_blk[i + 1] + 1, two_idx, two_idx + 1
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
                    self.one_keys[one_blk[i + 1]],
                    self.two_keys[two_idx],
                    autojunk=False,
                ).ratio()
                if merged_ratio >= self.similarity_cutoff and merged_ratio > max(
                    ratio_curr, ratio_next
                ):
                    self._process_merge_edit(
                        one_blk[i], one_blk[i + 1] + 1, two_idx, two_idx + 1
                    )
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
            if (
                j + 3 < len(two_blk)
                and i + 1 < len(one_blk)
                and len(one_blk) - i == 2
                and len(two_blk) - j == 4
            ):
                two_joined_first = self._normalize_line(
                    f"{self.two_lines[two_blk[j]]} {self.two_lines[two_blk[j + 1]]}"
                )
                two_joined_second = self._normalize_line(
                    f"{self.two_lines[two_blk[j + 2]]} {self.two_lines[two_blk[j + 3]]}"
                )
                first_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined_first, autojunk=False
                ).ratio()
                second_ratio = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_blk[i + 1]],
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
                        if self.one_keys[one_blk[i + 1]] == two_joined_second
                        else LineDiffKind.SPLIT_EDIT
                    )
                    if first_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    if second_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_blk[i + 1],
                            one_blk[i + 1] + 1,
                            two_blk[j + 2],
                            two_blk[j + 3] + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_blk[i + 1],
                            one_blk[i + 1] + 1,
                            two_blk[j + 2],
                            two_blk[j + 3] + 1,
                        )
                    i += 2
                    j += 4
                    last_was_split = True
                    continue
            if len(one_blk) == 1 and j + 1 < len(two_blk):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_blk[j]]} {self.two_lines[two_blk[j + 1]]}"
                )
                two_joined_rev = self._normalize_line(
                    f"{self.two_lines[two_blk[j + 1]]} {self.two_lines[two_blk[j]]}"
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
                    if diff_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    i += 1
                    j += 2
                    last_was_split = True
                    continue
            if j + 2 < len(two_blk) and i + 1 < len(one_blk):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_blk[j]]} {self.two_lines[two_blk[j + 1]]}"
                )
                merged_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined, autojunk=False
                ).ratio()
                split_join_cutoff = 0.95
                next_ratio = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_blk[i + 1]],
                    self.two_keys[two_blk[j + 2]],
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
                    if diff_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_idx,
                            one_idx + 1,
                            two_blk[j],
                            two_blk[j + 1] + 1,
                        )
                    i += 1
                    j += 2
                    last_was_split = True
                    continue
            ratio = difflib.SequenceMatcher(
                None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
            ).ratio()
            if ratio >= self.similarity_cutoff:
                self._process_edit(one_idx, two_idx)
                i += 1
                j += 1
                last_was_split = False
                continue
            if j + 1 < len(two_blk):
                two_joined = self._normalize_line(
                    f"{self.two_lines[two_blk[j]]} {self.two_lines[two_blk[j + 1]]}"
                )
                merged_ratio = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], two_joined, autojunk=False
                ).ratio()
                if merged_ratio >= self.similarity_cutoff:
                    one_slc = [one_idx]
                    two_slc = [two_blk[j], two_blk[j + 1]]
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
                    if diff_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_slc[0],
                            one_slc[-1] + 1,
                            two_slc[0],
                            two_slc[-1] + 1,
                        )
                    elif diff_type == LineDiffKind.SPLIT_EDIT:
                        self._process_split_edit(
                            one_slc[0],
                            one_slc[-1] + 1,
                            two_slc[0],
                            two_slc[-1] + 1,
                        )
                    elif diff_type == LineDiffKind.MERGE:
                        self._process_merge(
                            one_slc[0],
                            one_slc[-1] + 1,
                            two_slc[0],
                            two_slc[-1] + 1,
                        )
                    else:
                        self._process_merge_edit(
                            one_slc[0],
                            one_slc[-1] + 1,
                            two_slc[0],
                            two_slc[-1] + 1,
                        )
                    i += 1
                    j += 2
                    continue
            if len(two_blk) == 1 and i + 1 < len(one_blk):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_blk[i]]} {self.one_lines[one_blk[i + 1]]}"
                )
                if one_joined == self.two_keys[two_idx]:
                    self._process_merge(
                        one_blk[i], one_blk[i + 1] + 1, two_idx, two_idx + 1
                    )
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
                ratio_next = difflib.SequenceMatcher(
                    None,
                    self.one_keys[one_blk[i + 1]],
                    self.two_keys[two_idx],
                    autojunk=False,
                ).ratio()
                ratio_curr = difflib.SequenceMatcher(
                    None, self.one_keys[one_idx], self.two_keys[two_idx], autojunk=False
                ).ratio()
                if ratio_next >= self.similarity_cutoff and ratio_next > ratio_curr:
                    self._process_delete(one_start=one_idx, one_end=one_idx + 1)
                    self._process_edit(one_blk[i + 1], two_idx)
                    i += 2
                    j += 1
                    last_was_split = False
                    continue
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_blk[i]]} {self.one_lines[one_blk[i + 1]]}"
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
                    if diff_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_blk[i],
                            one_blk[i + 1] + 1,
                            two_idx,
                            two_idx + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_blk[i],
                            one_blk[i + 1] + 1,
                            two_idx,
                            two_idx + 1,
                        )
                    i += 2
                    j += 1
                    last_was_split = True
                    continue
            if len(two_blk) >= 2 and i + 1 < len(one_blk):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_blk[i]]} {self.one_lines[one_blk[i + 1]]}"
                )
                two_joined = self._normalize_line(
                    " ".join(self.two_lines[idx] for idx in two_blk[j:])
                )
                if one_joined == two_joined:
                    self._process_split(
                        one_blk[i],
                        one_blk[i + 1] + 1,
                        two_blk[j],
                        two_blk[-1] + 1,
                    )
                    return
            if i + 1 < len(one_blk):
                one_joined = self._normalize_line(
                    f"{self.one_lines[one_blk[i]]} {self.one_lines[one_blk[i + 1]]}"
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
                    if diff_type == LineDiffKind.SPLIT:
                        self._process_split(
                            one_blk[i],
                            one_blk[i + 1] + 1,
                            two_idx,
                            two_idx + 1,
                        )
                    else:
                        self._process_split_edit(
                            one_blk[i],
                            one_blk[i + 1] + 1,
                            two_idx,
                            two_idx + 1,
                        )
                    i += 2
                    j += 1
                    last_was_split = True
                    continue
            self._process_edit(one_idx, two_idx)
            i += 1
            j += 1
            last_was_split = False
        if i < len(one_blk) and j < len(two_blk):
            one_slc = one_blk[i:]
            two_slc = two_blk[j:]
            one_joined = self._normalize_line(
                " ".join(self.one_lines[idx] for idx in one_slc)
            )
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_slc)
            )
            if len(one_slc) < len(two_slc):
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
            if diff_type == LineDiffKind.SPLIT:
                self._process_split(
                    one_slc[0],
                    one_slc[-1] + 1,
                    two_slc[0],
                    two_slc[-1] + 1,
                )
            elif diff_type == LineDiffKind.SPLIT_EDIT:
                self._process_split_edit(
                    one_slc[0],
                    one_slc[-1] + 1,
                    two_slc[0],
                    two_slc[-1] + 1,
                )
            elif diff_type == LineDiffKind.MERGE:
                self._process_merge(
                    one_slc[0],
                    one_slc[-1] + 1,
                    two_slc[0],
                    two_slc[-1] + 1,
                )
            else:
                self._process_merge_edit(
                    one_slc[0],
                    one_slc[-1] + 1,
                    two_slc[0],
                    two_slc[-1] + 1,
                )
            return
        if i < len(one_blk):
            self._process_delete(one_start=one_blk[i], one_end=one_blk[-1] + 1)
            return
        if j < len(two_blk):
            self._process_insert(two_start=two_blk[j], two_end=two_blk[-1] + 1)

    def _process_edit(self, one_idx: int, two_idx: int):
        """Process edit opcode block."""
        self.msgs.append(
            LineDiff(
                kind=LineDiffKind.EDIT,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                one_idxs=[one_idx],
                two_idxs=[two_idx],
                one_texts=[self.one_lines[one_idx]],
                two_texts=[self.two_lines[two_idx]],
            )
        )

    def _process_merge(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process merge opcode block."""
        one_slc = list(range(one_start, one_end))
        two_slc = list(range(two_start, two_end))
        msg = LineDiff(
            kind=LineDiffKind.MERGE,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=one_slc,
            two_idxs=two_slc,
            one_texts=[self.one_lines[idx] for idx in one_slc],
            two_texts=[self.two_lines[idx] for idx in two_slc],
        )
        self.msgs.append(msg)

    def _process_merge_edit(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process merge-edit opcode block."""
        one_slc = list(range(one_start, one_end))
        two_slc = list(range(two_start, two_end))
        msg = LineDiff(
            kind=LineDiffKind.MERGE_EDIT,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=one_slc,
            two_idxs=two_slc,
            one_texts=[self.one_lines[idx] for idx in one_slc],
            two_texts=[self.two_lines[idx] for idx in two_slc],
        )
        self.msgs.append(msg)

    def _process_shift(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process shift opcode block."""
        one_slc = list(range(one_start, one_end))
        two_slc = list(range(two_start, two_end))
        msg = LineDiff(
            kind=LineDiffKind.SHIFT,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=one_slc,
            two_idxs=two_slc,
            one_texts=[self.one_lines[idx] for idx in one_slc],
            two_texts=[self.two_lines[idx] for idx in two_slc],
        )
        self.msgs.append(msg)

    def _process_split(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process split opcode block."""
        one_slc = list(range(one_start, one_end))
        two_slc = list(range(two_start, two_end))
        msg = LineDiff(
            kind=LineDiffKind.SPLIT,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=one_slc,
            two_idxs=two_slc,
            one_texts=[self.one_lines[idx] for idx in one_slc],
            two_texts=[self.two_lines[idx] for idx in two_slc],
        )
        self.msgs.append(msg)

    def _process_split_edit(
        self, one_start: int, one_end: int, two_start: int, two_end: int
    ):
        """Process split-edit opcode block."""
        one_slc = list(range(one_start, one_end))
        two_slc = list(range(two_start, two_end))
        msg = LineDiff(
            kind=LineDiffKind.SPLIT_EDIT,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=one_slc,
            two_idxs=two_slc,
            one_texts=[self.one_lines[idx] for idx in one_slc],
            two_texts=[self.two_lines[idx] for idx in two_slc],
        )
        self.msgs.append(msg)

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
