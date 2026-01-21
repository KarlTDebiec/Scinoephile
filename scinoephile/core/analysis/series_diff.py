#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing."""

from __future__ import annotations

import difflib
import re
from collections.abc import Callable
from typing import TypedDict

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series

from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind
from .replace_cursor import ReplaceCursor

__all__ = ["SeriesDiff", "SeriesDiffKwargs"]


class SeriesDiffKwargs(TypedDict, total=False):
    """Keyword arguments for SeriesDiff."""

    one_lbl: str
    two_lbl: str
    similarity_cutoff: float


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
            one: first subtitle series
            two: second subtitle series
            one_lbl: label for first series in messages
            two_lbl: label for second series in messages
            similarity_cutoff: similarity cutoff for pairing replacements
        Returns:
            None.
        """
        self.one_lbl = one_lbl
        self.two_lbl = two_lbl
        self.similarity_cutoff = similarity_cutoff
        self.one_lines = self._get_series_text_lines(one)
        self.two_lines = self._get_series_text_lines(two)
        self.one_normlines = [self._normalize_line(line) for line in self.one_lines]
        self.two_normlines = [self._normalize_line(line) for line in self.two_lines]
        self.msgs: list[LineDiff] = []
        self._diff()

    def _diff(self) -> list[LineDiff]:
        """Compare subtitle series by line content.

        Arguments:
            None.
        Returns:
            list of difference messages
        """
        matcher = difflib.SequenceMatcher(
            None, self.one_normlines, self.two_normlines, autojunk=False
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
        """Process delete opcode block.

        Arguments:
            one_start: start index for the delete block
            one_end: end index for the delete block
        Returns:
            None.
        """
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
        """Process insert opcode block.

        Arguments:
            two_start: start index for the insert block
            two_end: end index for the insert block
        Returns:
            None.
        """
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
        """Process replace opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
        one_blk = list(range(one_start, one_end))
        two_blk = list(range(two_start, two_end))
        if len(one_blk) == len(two_blk):
            self._process_replace_equal(one_blk, two_blk)
            return
        self._process_replace_unequal(one_blk, two_blk)

    def _process_replace_equal(self, one_blk: list[int], two_blk: list[int]):
        """Add messages for equal-sized replace blocks.

        Arguments:
            one_blk: indices for the first block
            two_blk: indices for the second block
        Returns:
            None.
        """
        if len(one_blk) == 2 and len(two_blk) == 2:
            two_joined = self._normalize_line(
                " ".join(self.two_lines[idx] for idx in two_blk)
            )
            missing_key = self.one_normlines[one_blk[0]].casefold()
            merged_key = self.one_normlines[one_blk[1]].casefold()
            if merged_key == two_joined.casefold() and all(
                missing_key != self.two_normlines[idx].casefold() for idx in two_blk
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
                    None,
                    self.one_normlines[one_idx],
                    self.two_normlines[two_idx],
                    autojunk=False,
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
        """Add messages for unequal-sized replace blocks.

        Arguments:
            one_blk: indices for the first block
            two_blk: indices for the second block
        Returns:
            None.
        """
        cursor = ReplaceCursor(one_blk=one_blk, two_blk=two_blk)
        handlers: tuple[Callable[[ReplaceCursor], bool], ...] = (
            self._process_replace_unequal_merge,
            self._process_replace_unequal_two_to_four,
            self._process_replace_unequal_one_to_two,
            self._process_replace_unequal_two_to_three,
            self._process_replace_unequal_similarity_edit,
            self._process_replace_unequal_joined_split_or_merge,
            self._process_replace_unequal_many_to_one_followup,
        )

        while cursor.i < len(one_blk) and cursor.j < len(two_blk):
            handled = False
            for handler in handlers:
                if handler(cursor):
                    handled = True
                    break
            if not handled:
                self._process_edit(cursor.one_idx, cursor.two_idx)
                cursor.advance(n_one=1, n_two=1, last_was_split=False)
                continue
            if cursor.should_return:
                return
        self._process_replace_unequal_tail(one_blk, two_blk, cursor.i, cursor.j)

    def _process_replace_unequal_merge(self, cursor: ReplaceCursor) -> bool:
        """Process unequal replace when a merge is strongly indicated.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          [
            "Why couldn't you find out",
            "they cheated during the examination?",
          ]
          -> ["Why couldn't you find out they cheated during the examination?"]
        """
        # If this cannot be a merge, skip it.
        if len(cursor.two_blk) != 1 or not cursor.one_has_next:
            return False

        one_joined = self._normalize_line(
            f"{self.one_lines[cursor.one_blk[cursor.i]]} "
            f"{self.one_lines[cursor.one_blk[cursor.i + 1]]}"
        )

        # Exact merged match: emit a merge without edits.
        if one_joined == self.two_normlines[cursor.two_idx]:
            self._process_merge(
                cursor.one_blk[cursor.i],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_idx,
                cursor.two_idx + 1,
            )
            cursor.advance(n_one=2, n_two=1, last_was_split=False)
            return True

        # Otherwise, compare merged vs. individual similarity to decide on merge_edit.
        merged_ratio = difflib.SequenceMatcher(
            None, one_joined, self.two_normlines[cursor.two_idx], autojunk=False
        ).ratio()
        ratio_curr = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_idx],
            self.two_normlines[cursor.two_idx],
            autojunk=False,
        ).ratio()
        ratio_next = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_blk[cursor.i + 1]],
            self.two_normlines[cursor.two_idx],
            autojunk=False,
        ).ratio()

        # Use merge_edit when the combined line fits better than either single line.
        if merged_ratio >= self.similarity_cutoff and merged_ratio > max(
            ratio_curr, ratio_next
        ):
            self._process_merge_edit(
                cursor.one_blk[cursor.i],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_idx,
                cursor.two_idx + 1,
            )
            cursor.advance(n_one=2, n_two=1, last_was_split=False)
            return True

        return False

    def _process_replace_unequal_two_to_four(self, cursor: ReplaceCursor) -> bool:
        """Process unequal replace for a two-to-four split pattern.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          [
            "- Kill me    - No, kill me",
            "- Kill me.    - Your Majesty, you'd better kill me",
          ]
          -> [
            "Kill me",
            "No, kill me",
            "Kill me",
            "Your Majesty, you'd better kill me",
          ]
        """
        # Only consider the exact 2-line -> 4-line situation at the tail.
        if not (
            cursor.j + 3 < len(cursor.two_blk)
            and cursor.one_has_next
            and cursor.one_remaining == 2
            and cursor.two_remaining == 4
        ):
            return False
        two_joined_first = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j + 1]]}"
        )
        two_joined_second = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j + 2]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j + 3]]}"
        )
        # Verify each one-line entry roughly matches its corresponding two-line join.
        first_ratio = difflib.SequenceMatcher(
            None, self.one_normlines[cursor.one_idx], two_joined_first, autojunk=False
        ).ratio()
        second_ratio = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_blk[cursor.i + 1]],
            two_joined_second,
            autojunk=False,
        ).ratio()
        if not (
            first_ratio >= self.similarity_cutoff
            and second_ratio >= self.similarity_cutoff
        ):
            return False
        # Emit split/split_edit for each side based on exact normalized equality.
        first_type = (
            LineDiffKind.SPLIT
            if self.one_normlines[cursor.one_idx] == two_joined_first
            else LineDiffKind.SPLIT_EDIT
        )
        second_type = (
            LineDiffKind.SPLIT
            if self.one_normlines[cursor.one_blk[cursor.i + 1]] == two_joined_second
            else LineDiffKind.SPLIT_EDIT
        )
        if first_type == LineDiffKind.SPLIT:
            self._process_split(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        else:
            self._process_split_edit(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        if second_type == LineDiffKind.SPLIT:
            self._process_split(
                cursor.one_blk[cursor.i + 1],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_blk[cursor.j + 2],
                cursor.two_blk[cursor.j + 3] + 1,
            )
        else:
            self._process_split_edit(
                cursor.one_blk[cursor.i + 1],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_blk[cursor.j + 2],
                cursor.two_blk[cursor.j + 3] + 1,
            )
        cursor.advance(n_one=2, n_two=4, last_was_split=True)
        return True

    def _process_replace_unequal_one_to_two(self, cursor: ReplaceCursor) -> bool:
        """Process unequal replace when one line may split into two.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          ["- Please give me some money    - Kidding? Damn you beggar!"]
          -> [
            "Please give me some money",
            "Kidding? Damn you beggar!",
          ]
        """
        if len(cursor.one_blk) != 1 or not cursor.two_has_pair:
            return False
        two_joined = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j + 1]]}"
        )
        two_joined_rev = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j + 1]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j]]}"
        )
        merged_ratio = difflib.SequenceMatcher(
            None, self.one_normlines[cursor.one_idx], two_joined, autojunk=False
        ).ratio()
        merged_ratio_rev = difflib.SequenceMatcher(
            None, self.one_normlines[cursor.one_idx], two_joined_rev, autojunk=False
        ).ratio()
        best_joined = two_joined_rev if merged_ratio_rev > merged_ratio else two_joined
        if max(merged_ratio, merged_ratio_rev) < self.similarity_cutoff:
            return False
        diff_type = (
            LineDiffKind.SPLIT
            if self.one_normlines[cursor.one_idx] == best_joined
            else LineDiffKind.SPLIT_EDIT
        )
        if diff_type == LineDiffKind.SPLIT:
            self._process_split(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        else:
            self._process_split_edit(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        cursor.advance(n_one=1, n_two=2, last_was_split=True)
        return True

    def _process_replace_unequal_two_to_three(self, cursor: ReplaceCursor) -> bool:
        """Process unequal replace when two lines map onto three.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          ["Although you have taken 2 months' rest,",
          "your legs and hands have not been totally recovered"]
          -> [
            "Although you have taken",
            "2 months' rest,",
            "your legs and hands have not been totally recovered.",
          ]
        """
        if cursor.j + 2 >= len(cursor.two_blk) or not cursor.one_has_next:
            return False
        two_joined = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j + 1]]}"
        )
        merged_ratio = difflib.SequenceMatcher(
            None, self.one_normlines[cursor.one_idx], two_joined, autojunk=False
        ).ratio()
        split_join_cutoff = 0.95
        next_ratio = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_blk[cursor.i + 1]],
            self.two_normlines[cursor.two_blk[cursor.j + 2]],
            autojunk=False,
        ).ratio()
        if merged_ratio < split_join_cutoff or next_ratio < self.similarity_cutoff:
            return False
        diff_type = (
            LineDiffKind.SPLIT
            if self.one_normlines[cursor.one_idx] == two_joined
            else LineDiffKind.SPLIT_EDIT
        )
        if diff_type == LineDiffKind.SPLIT:
            self._process_split(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        else:
            self._process_split_edit(
                cursor.one_idx,
                cursor.one_idx + 1,
                cursor.two_blk[cursor.j],
                cursor.two_blk[cursor.j + 1] + 1,
            )
        cursor.advance(n_one=1, n_two=2, last_was_split=True)
        return True

    def _process_replace_unequal_similarity_edit(self, cursor: ReplaceCursor) -> bool:
        """Process unequal replace when a simple edit matches well.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          ["Leave here first"]
          -> ["Leave here first."]
        """
        ratio = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_idx],
            self.two_normlines[cursor.two_idx],
            autojunk=False,
        ).ratio()
        if ratio < self.similarity_cutoff:
            return False
        self._process_edit(cursor.one_idx, cursor.two_idx)
        cursor.advance(n_one=1, n_two=1, last_was_split=False)
        return True

    def _process_replace_unequal_joined_split_or_merge(
        self, cursor: ReplaceCursor
    ) -> bool:
        """Process unequal replace for joined split/merge candidates.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          ["- Miss Seven…    - Just accept this"]
          -> [
            "Miss Seven…",
            "Just accept this.",
          ]
        """
        if not cursor.two_has_pair:
            return False
        two_joined = self._normalize_line(
            f"{self.two_lines[cursor.two_blk[cursor.j]]} "
            f"{self.two_lines[cursor.two_blk[cursor.j + 1]]}"
        )
        merged_ratio = difflib.SequenceMatcher(
            None, self.one_normlines[cursor.one_idx], two_joined, autojunk=False
        ).ratio()
        if merged_ratio < self.similarity_cutoff:
            return False
        one_slc = [cursor.one_idx]
        two_slc = [cursor.two_blk[cursor.j], cursor.two_blk[cursor.j + 1]]
        if self.one_normlines[cursor.one_idx] == two_joined:
            split_type = LineDiffKind.SPLIT
            merged_type = LineDiffKind.MERGE
        else:
            split_type = LineDiffKind.SPLIT_EDIT
            merged_type = LineDiffKind.MERGE_EDIT
        if (
            self.one_normlines[cursor.one_idx] == two_joined
            or cursor.i == 0
            or cursor.last_was_split
        ):
            diff_type = split_type
            last_was_split = True
        else:
            diff_type = merged_type
            last_was_split = False
        if diff_type == LineDiffKind.SPLIT:
            self._process_split(
                one_slc[0], one_slc[-1] + 1, two_slc[0], two_slc[-1] + 1
            )
        elif diff_type == LineDiffKind.SPLIT_EDIT:
            self._process_split_edit(
                one_slc[0], one_slc[-1] + 1, two_slc[0], two_slc[-1] + 1
            )
        elif diff_type == LineDiffKind.MERGE:
            self._process_merge(
                one_slc[0], one_slc[-1] + 1, two_slc[0], two_slc[-1] + 1
            )
        else:
            self._process_merge_edit(
                one_slc[0], one_slc[-1] + 1, two_slc[0], two_slc[-1] + 1
            )
        cursor.advance(n_one=1, n_two=2, last_was_split=last_was_split)
        return True

    def _process_replace_unequal_many_to_one_followup(
        self, cursor: ReplaceCursor
    ) -> bool:
        """Process unequal replace for follow-up many-to-one checks.

        Arguments:
            cursor: replace cursor state
        Returns:
            whether the cursor was handled

        Example:
          ["OK", "I want to take a statement from you as record"]
          -> ["I want to take some statements from you as record"]
        """
        if len(cursor.two_blk) != 1 or not cursor.one_has_next:
            return False
        ratio_next = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_blk[cursor.i + 1]],
            self.two_normlines[cursor.two_idx],
            autojunk=False,
        ).ratio()
        ratio_curr = difflib.SequenceMatcher(
            None,
            self.one_normlines[cursor.one_idx],
            self.two_normlines[cursor.two_idx],
            autojunk=False,
        ).ratio()
        if ratio_next >= self.similarity_cutoff and ratio_next > ratio_curr:
            self._process_delete(one_start=cursor.one_idx, one_end=cursor.one_idx + 1)
            self._process_edit(cursor.one_blk[cursor.i + 1], cursor.two_idx)
            cursor.advance(n_one=2, n_two=1, last_was_split=False)
            return True
        one_joined = self._normalize_line(
            " ".join(
                self.one_lines[idx] for idx in cursor.one_blk[cursor.i : cursor.i + 2]
            )
        )
        split_ratio = difflib.SequenceMatcher(
            None, one_joined, self.two_normlines[cursor.two_idx], autojunk=False
        ).ratio()
        if split_ratio < self.similarity_cutoff:
            return False
        diff_type = (
            LineDiffKind.SPLIT
            if one_joined == self.two_normlines[cursor.two_idx]
            else LineDiffKind.SPLIT_EDIT
        )
        if diff_type == LineDiffKind.SPLIT:
            self._process_split(
                cursor.one_blk[cursor.i],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_idx,
                cursor.two_idx + 1,
            )
        else:
            self._process_split_edit(
                cursor.one_blk[cursor.i],
                cursor.one_blk[cursor.i + 1] + 1,
                cursor.two_idx,
                cursor.two_idx + 1,
            )
        cursor.advance(n_one=2, n_two=1, last_was_split=True)
        return True

    def _process_replace_unequal_tail(
        self, one_blk: list[int], two_blk: list[int], i: int, j: int
    ):
        """Process remaining unequal replace block tail cases.

        Arguments:
            one_blk: indices for the first block
            two_blk: indices for the second block
            i: current index within the first block
            j: current index within the second block
        Returns:
            None.
        """
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
        """Process edit opcode block.

        Arguments:
            one_idx: index for the first series
            two_idx: index for the second series
        Returns:
            None.
        """
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
        """Process merge opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
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
        """Process merge-edit opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
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
        """Process shift opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
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
        """Process split opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
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
        """Process split-edit opcode block.

        Arguments:
            one_start: start index for the first block
            one_end: end index for the first block
            two_start: start index for the second block
            two_end: end index for the second block
        Returns:
            None.
        """
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
            series: subtitle series to extract text lines from
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
            text: subtitle line to normalize
        Returns:
            normalized line
        """
        stripped = re.sub(r"(?:^|\s)(?:[-–])\s+", " ", text.strip())
        normalized = re.sub(r"\s+", " ", stripped).strip()
        return normalized
