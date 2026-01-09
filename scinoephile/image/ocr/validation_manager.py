#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validates OCRed subtitle text using source images."""

from __future__ import annotations

from dataclasses import dataclass
from logging import debug, info, warning
from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.bboxes import get_bboxes, get_merged_bbox
from scinoephile.image.drawing import get_img_with_bboxes
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .char_dims import get_dims_tuple, load_char_dims, save_char_dims
from .char_grp_dims import load_char_grp_dims, save_char_grp_dims
from .char_pair_gaps import (
    get_default_char_pair_cutoffs,
    get_expected_space,
    get_expected_tab,
    load_char_pair_gaps,
    save_char_pair_gaps,
)

__all__ = ["ValidationManager"]


@dataclass
class CharCursor:
    """Tracks cursor state while validating character bboxes.

    Arguments:
        sub: subtitle being validated
        sub_idx: subtitle index for logging
        char_idx: current character index
        bbox_idx: current bbox index
    """

    sub: ImageSubtitle
    sub_idx: int
    char_idx: int = 0
    bbox_idx: int = 0

    def advance(self, *, n_chars: int, n_bboxes: int):
        """Advance cursor indices.

        Arguments:
            n_chars: number of characters to advance
            n_bboxes: number of bboxes to advance
        """
        self.char_idx += n_chars
        self.bbox_idx += n_bboxes

    def char_grp(self, n_chars: int) -> str:
        """Current character group.

        Arguments:
            n_chars: number of characters to include
        Returns:
            character group
        """
        return self.sub.text_with_newline[self.char_idx : self.char_idx + n_chars]

    def bbox_grp(self, n_bboxes: int) -> list[Bbox]:
        """Current bbox group.

        Arguments:
            n_bboxes: number of bboxes to include
        Returns:
            bbox group
        """
        return self.sub.bboxes[self.bbox_idx : self.bbox_idx + n_bboxes]

    @property
    def char(self) -> str:
        """Current character."""
        return self.sub.text_with_newline[self.char_idx]

    @property
    def intro_msg(self) -> str:
        """Message intro for the current character index."""
        text = self.sub.text_with_newline.replace(chr(10), "\\n")
        return f"Sub {self.sub_idx + 1:4d} | Char {self.char_idx + 1:2d} | {text}"


@dataclass
class GapCursor:
    """Tracks state while validating a single gap.

    Arguments:
        sub: subtitle being validated
        sub_idx: subtitle index for logging
        char_1_idx: first character index
        char_2_idx: second character index
        bbox_1_idx: first bbox index
        bbox_2_idx: second bbox index
        char_1: first character
        char_2: second character
        gap: gap size
        gap_chars: observed gap characters
    """

    sub: ImageSubtitle
    sub_idx: int
    char_1_idx: int = 0
    char_2_idx: int = 0
    bbox_1_idx: int = 0
    bbox_2_idx: int = 0
    char_1: str = ""
    char_2: str = ""
    bbox_1: Bbox | None = None
    bbox_2: Bbox | None = None
    gap: int = 0
    gap_chars: str = ""

    @property
    def expected_space(self) -> str:
        """Expected space between characters."""
        return get_expected_space(self.char_1, self.char_2)

    @property
    def expected_tab(self) -> str:
        """Expected tab between characters."""
        return get_expected_tab(self.char_1, self.char_2)

    @property
    def gap_msg(self) -> str:
        """Gap text."""
        return f"'{self.char_1},{self.char_2}' -> {self.gap}"

    @property
    def intro_msg(self) -> str:
        """Message intro for the first character index."""
        text = self.sub.text_with_newline.replace(chr(10), "\\n")
        return f"Sub {self.sub_idx + 1:4d} | Char {self.char_1_idx + 1:2d} | {text}"

    @property
    def char_pair(self) -> tuple[str, str]:
        """Character pair for this gap."""
        return self.char_1, self.char_2

    def seek_char_1(self) -> bool:
        """Seek next non-whitespace character for char_1.

        Returns:
            whether a character was found
        """
        text = self.sub.text_with_newline
        while self.char_1_idx < len(text) and (
            text[self.char_1_idx] in whitespace_chars or text[self.char_1_idx] == "\n"
        ):
            self.char_1_idx += 1
        if self.char_1_idx >= len(text) - 1:
            return False
        self.char_1 = text[self.char_1_idx]
        return True

    def seek_char_2(self) -> bool:
        """Seek next non-whitespace character for char_2.

        Returns:
            whether a character was found
        """
        text = self.sub.text_with_newline
        self.char_2_idx = self.char_1_idx + 1
        while self.char_2_idx < len(text) and (
            text[self.char_2_idx] in whitespace_chars or text[self.char_2_idx] == "\n"
        ):
            self.char_2_idx += 1
        if self.char_2_idx >= len(text):
            return False
        self.char_2 = text[self.char_2_idx]
        return True

    def gap_slice(self) -> str:
        """Gap substring between char_1 and char_2."""
        return self.sub.text_with_newline[self.char_1_idx + 1 : self.char_2_idx]

    def advance(self):
        """Advance to the next gap."""
        self.char_1_idx = self.char_2_idx
        self.bbox_1_idx = self.bbox_2_idx

    def annotated_img(self, n_bboxes: int) -> object:
        """Annotated image for current bbox group.

        Arguments:
            n_bboxes: number of bboxes to include
        Returns:
            annotated image
        """
        return get_img_with_bboxes(self.sub.img, self.bbox_grp(n_bboxes))

    def bbox_grp(self, n_bboxes: int) -> list[Bbox]:
        """Current bbox group.

        Arguments:
            n_bboxes: number of bboxes to include
        Returns:
            bbox group
        """
        return self.sub.bboxes[self.bbox_1_idx : self.bbox_1_idx + n_bboxes]

    def get_bbox_1(self) -> Bbox | None:
        """Get the current bbox_1.

        Returns:
            bbox_1 or None if out of range
        """
        if self.bbox_1_idx >= len(self.sub.bboxes):
            return None
        return self.sub.bboxes[self.bbox_1_idx]

    def get_bbox_2(self) -> Bbox | None:
        """Get the current bbox_2.

        Returns:
            bbox_2 or None if out of range
        """
        self.bbox_2_idx = self.bbox_1_idx + 1
        if self.bbox_2_idx >= len(self.sub.bboxes):
            return None
        return self.sub.bboxes[self.bbox_2_idx]

    def prepare_gap(self) -> tuple[Bbox, Bbox] | None:
        """Prepare gap by seeking characters and bboxes.

        Returns:
            bbox_1 and bbox_2, or None if not available
        """
        if not self.seek_char_1():
            return None
        if not self.seek_char_2():
            return None
        self.gap_chars = self.gap_slice()
        self.bbox_1 = self.get_bbox_1()
        if self.bbox_1 is None:
            return None
        self.bbox_2 = self.get_bbox_2()
        if self.bbox_2 is None:
            return None
        return self.bbox_1, self.bbox_2

    def gap_chars_escaped(self) -> str:
        """Gap chars with newlines escaped."""
        return self.gap_chars.replace(chr(10), "\\n")


class ValidationManager:
    """Validates OCRed subtitle text using source images."""

    char_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
    """Data structure for characters in one or more bboxes.

    First key is the number of bboxes.
    Second key is the character.
    Values are a set of approved bbox width, heights, and gaps for that character.
    """

    char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
    """Data structure for bboxes containing two or more characters.

    First key is the number of characters in the group.
    Second key is the character group.
    Values are a set of approved bbox width and heights for that character group.
    """

    char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
    """Data structure for gaps between bboxes.

    Key is a pair of characters.
    Value is a tuple of four ints, representing cutoffs:
      * Upper bound for 'adjacent' characters
      * Lower bound for 'space' characters
      * Upper bound for 'space' characters
      * Lower bound for 'tab' characters
    """

    def __init__(self):
        """Initialize."""
        # Initalize char_dims_by_n
        for n in range(1, 6):
            file_path = self._char_dims_path(n)
            self.char_dims_by_n[n] = {}
            if file_path.exists():
                self.char_dims_by_n[n] = load_char_dims(file_path)

        # Initialize char_grp_dims_by_n
        file_path = self._char_grp_dims_path()
        if file_path.exists():
            self.char_grp_dims_by_n = load_char_grp_dims(file_path)

        # Initialize char_pair_gaps
        file_path = self._char_pair_gaps_path()
        if file_path.exists():
            self.char_pair_gaps = load_char_pair_gaps(file_path)

    def validate(
        self,
        series: ImageSeries,
        stop_at_idx: int | None = None,
        interactive: bool = True,
    ) -> ImageSeries:
        """Validate all subtitles in an image series.

        Arguments:
            series: image series to validate
            stop_at_idx: stop validating at this index
            interactive: whether to prompt user for confirmations
        Returns:
            validated image series
        """
        output_series = ImageSeries()
        if stop_at_idx is None:
            stop_at_idx = len(series) - 1
        messages = []
        for sub_idx, sub in enumerate(series.events):
            if sub_idx > stop_at_idx:
                break
            messages.extend(self._validate_sub(sub, sub_idx, interactive))
            annotated_img = get_img_with_bboxes(sub.img, sub.bboxes)
            output_series.events.append(
                ImageSubtitle(
                    img=annotated_img,
                    start=sub.start,
                    end=sub.end,
                    text=sub.text,
                    series=output_series,
                )
            )
        for message in messages:
            warning(message)
        return output_series

    def _validate_sub(
        self, sub: ImageSubtitle, sub_idx: int, interactive: bool = True
    ) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            list of validation messages
        """
        sub.bboxes = get_bboxes(sub.img)

        char_messages = self._validate_chars(sub, sub_idx, interactive)
        if len(char_messages) > 0:
            return char_messages

        gap_messages = self._validate_gaps(sub, sub_idx, interactive)

        return char_messages + gap_messages

    def _validate_chars(
        self,
        sub: ImageSubtitle,
        sub_idx: int,
        interactive: bool = True,
    ) -> list[str]:
        """Merge bboxes per character and collect validation messages.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            validation messages
        """
        messages = []

        cursor = CharCursor(sub=sub, sub_idx=sub_idx)
        while cursor.char_idx < len(sub.text_with_newline):
            # No validation to perform for whitespace
            if cursor.char in whitespace_chars or cursor.char == "\n":
                cursor.advance(n_chars=1, n_bboxes=0)
                continue

            # Cannot validate without bboxes
            if cursor.bbox_idx >= len(sub.bboxes):
                messages.append(
                    f"{cursor.intro_msg} | ran out of bboxes at '{cursor.char}'"
                )
                break

            # Check if next bbox matches two or more characters
            matched = self._match_grouped_chars(cursor)
            if matched:
                continue

            # Check if next one or more bboxes matches single character
            matched = self._match_char_dims(cursor)
            if matched:
                continue

            # Prompt user to assign bbox(es) to character(s)
            if not interactive:
                messages.append(
                    f"{cursor.intro_msg} | "
                    f"no approved or automatic match for '{cursor.char}'"
                )
                break
            matched, new_messages = self._prompt_char_dims(cursor)
            messages.extend(new_messages)
            if matched:
                continue

            # May or may not be reachable
            messages.append(f"{cursor.intro_msg} | unexpected state at '{cursor.char}'")

        # Cannot have leftover bboxes
        if cursor.bbox_idx != len(sub.bboxes):
            messages.append(
                f"{cursor.intro_msg} | "
                f"{len(sub.bboxes) - cursor.bbox_idx} leftover bboxes"
            )

        return messages

    def _match_grouped_chars(self, cursor: CharCursor) -> bool:
        """Match grouped characters against approved dimensions.

        Arguments:
            cursor: character cursor
        Returns:
            whether a match was found
        """
        for n_chars in self.char_grp_dims_by_n.keys():
            if cursor.char_idx + n_chars > len(cursor.sub.text_with_newline):
                continue
            char_grp = cursor.char_grp(n_chars)
            if any(c in whitespace_chars for c in char_grp) or "\n" in char_grp:
                continue
            dims = get_dims_tuple(cursor.sub.bboxes[cursor.bbox_idx])
            ok_dims = self.char_grp_dims_by_n[n_chars].get(char_grp, set())

            # Exact match
            if dims in ok_dims:
                cursor.advance(n_chars=n_chars, n_bboxes=1)
                return True

            # Fuzzy match
            for ok_dim in ok_dims:
                diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                max_diff = max(diffs)
                if max_diff <= 2:
                    self._update_char_grp_dims(char_grp, dims)
                    cursor.advance(n_chars=n_chars, n_bboxes=1)
                    return True
        return False

    def _match_char_dims(self, cursor: CharCursor) -> bool:
        """Match character against approved dimensions.

        Arguments:
            cursor: character cursor
        Returns:
            whether a match was found
        """
        for n_bboxes in self.char_dims_by_n.keys():
            if cursor.bbox_idx + n_bboxes > len(cursor.sub.bboxes):
                break
            dims = get_dims_tuple(cursor.bbox_grp(n_bboxes))
            ok_dims = self.char_dims_by_n[n_bboxes].get(cursor.char, set())

            # Exact match
            if dims in ok_dims:
                bbox_grp = cursor.bbox_grp(n_bboxes)
                merged_bbox = get_merged_bbox(bbox_grp)
                cursor.sub.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [
                    merged_bbox
                ]
                cursor.advance(n_chars=1, n_bboxes=n_bboxes)
                return True

            # Fuzzy match
            for ok_dim in ok_dims:
                diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                max_diff = max(diffs)
                if max_diff <= 2:
                    bbox_grp = cursor.bbox_grp(n_bboxes)
                    merged_bbox = get_merged_bbox(bbox_grp)
                    cursor.sub.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [
                        merged_bbox
                    ]
                    self._update_char_dims(cursor.char, dims)
                    cursor.advance(n_chars=1, n_bboxes=n_bboxes)
                    return True
        return False

    def _prompt_char_dims(self, cursor: CharCursor) -> tuple[bool, list[str]]:
        """Prompt user to confirm character dimensions.

        Arguments:
            cursor: character cursor
        Returns:
            tuple of (matched, validation messages)
        """
        messages: list[str] = []

        for n_bboxes in self.char_dims_by_n.keys():
            if cursor.bbox_idx + n_bboxes > len(cursor.sub.bboxes):
                break
            dims = get_dims_tuple(cursor.bbox_grp(n_bboxes))

            n_chars = 0
            annotated = get_img_with_bboxes(cursor.sub.img, cursor.bbox_grp(n_bboxes))
            annotated.show()
            response = input(
                f"{cursor.intro_msg} | "
                f"'{cursor.char}' bbox dims {dims} | extend/group? (y/n): "
            )
            extend = not response.lower().startswith("y")
            if n_bboxes == 1:
                try:
                    n_chars = int(response)
                    if n_chars > 1:
                        extend = False
                except ValueError:
                    pass

            if extend:
                bbox_grp = cursor.bbox_grp(n_bboxes)
                merged_bbox = get_merged_bbox(bbox_grp)
                cursor.sub.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [
                    merged_bbox
                ]
                self._update_char_dims(cursor.char, dims)
                cursor.advance(n_chars=1, n_bboxes=1)
                return True, messages

            if n_chars > 1:
                if cursor.char_idx + n_chars > len(cursor.sub.text_with_newline):
                    messages.append(
                        f"{cursor.intro_msg} | "
                        f"cannot group {n_chars} chars starting at '{cursor.char}' "
                        "beyond text length"
                    )
                    continue
                char_grp = cursor.char_grp(n_chars)
                if any(c in whitespace_chars for c in char_grp):
                    messages.append(
                        f"{cursor.intro_msg} | "
                        f"cannot group '{char_grp}' due to whitespace"
                    )
                    continue
                dims = get_dims_tuple(cursor.bbox_grp(1))
                self._update_char_grp_dims(char_grp, dims)
                cursor.advance(n_chars=n_chars, n_bboxes=1)
                return True, messages
        return False, messages

    def _validate_gaps(  # noqa: PLR0912, PLR0915
        self,
        sub: ImageSubtitle,
        sub_idx: int,
        interactive: bool = True,
    ) -> list[str]:
        """Validate gaps between bboxes and collect validation messages.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            validation messages
        """
        messages = []

        cursor = GapCursor(sub=sub, sub_idx=sub_idx)
        while cursor.char_1_idx < len(sub.text_with_newline) - 1:
            if cursor.prepare_gap() is None:
                if cursor.bbox_1_idx >= len(sub.bboxes) and cursor.char_1:
                    messages.append(
                        f"{cursor.intro_msg} | ran out of bboxes at '{cursor.char_1}'"
                    )
                elif cursor.bbox_2_idx >= len(sub.bboxes) and cursor.char_2:
                    messages.append(
                        f"{cursor.intro_msg} | "
                        f"Ran out of bboxes when checking gap between "
                        f"'{cursor.char_1}' and '{cursor.char_2}'"
                    )
                break

            # If char 1 and char 2 and bbox_1 are all together, obviously adjacent
            if len(cursor.gap_chars) == 0:
                char_grp = f"{cursor.char_1}{cursor.char_2}"
                dims = get_dims_tuple(cursor.bbox_1)
                ok_dims = self.char_grp_dims_by_n[2].get(char_grp, set())
                if dims in ok_dims:
                    debug(
                        f"|{cursor.char_1_idx}|{cursor.char_2_idx}|"
                        f"{cursor.bbox_1_idx}| -> |"
                        f"{cursor.char_1}|{cursor.char_2}|group|"
                    )
                    cursor.char_1_idx += 1
                    continue

            # get gap
            cursor.gap = cursor.bbox_2.x1 - cursor.bbox_1.x2
            debug(
                f"|{cursor.char_1_idx}|{cursor.char_2_idx}|"
                f"{cursor.bbox_1_idx}|{cursor.bbox_2_idx}| -> |"
                f"{cursor.char_1}|{cursor.char_2}|{cursor.gap}|"
                f"{cursor.gap_chars_escaped()}|"
            )

            # If gap is negative, ensure that gap_chars is a newline
            if cursor.gap < 0:
                if cursor.gap_chars != "\n":
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        f"expected '\\n' "
                        f"observed '{cursor.gap_chars_escaped()}'"
                    )
                cursor.advance()
                continue

            # Validate
            cutoffs = self.char_pair_gaps.get(cursor.char_pair)
            if not cutoffs:
                cutoffs = get_default_char_pair_cutoffs(cursor.char_1, cursor.char_2)
                self._update_pair_gaps(cursor.char_pair, cutoffs)

            # Adjacent
            if cursor.gap <= cutoffs[0]:
                if cursor.gap_chars != "":
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        "expected '' observed "
                        f"'{cursor.gap_chars_escaped()}'"
                    )
                cursor.advance()
                continue

            # Adjacent or space? Prompt the user
            if cutoffs[0] < cursor.gap < cutoffs[1]:
                if not interactive:
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        "no approved or automatic match for gap"
                    )
                    return messages
                messages.extend(self._prompt_space_gap(cursor, cutoffs))
                cursor.advance()
                continue

            # Space
            if cutoffs[1] <= cursor.gap <= cutoffs[2]:
                if cursor.gap_chars != cursor.expected_space:
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        f"expected '{cursor.expected_space}' "
                        f"observed '{cursor.gap_chars_escaped()}'"
                    )
                cursor.advance()
                continue

            # Space or tab? Prompt the user
            if cutoffs[2] < cursor.gap < cutoffs[3]:
                if not interactive:
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        "no approved or automatic match for gap"
                    )
                    return messages
                messages.extend(self._prompt_tab_gap(cursor, cutoffs))
                cursor.advance()
                continue

            # Tab
            if cutoffs[3] <= cursor.gap:
                if cursor.gap_chars not in (cursor.expected_tab, "\n"):
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        f"expected '{cursor.expected_tab}' "
                        f"observed '{cursor.gap_chars_escaped()}'"
                    )
                cursor.advance()
                continue

        return messages

    def _prompt_space_gap(
        self, cursor: GapCursor, cutoffs: tuple[int, int, int, int]
    ) -> list[str]:
        """Prompt user to confirm a space gap.

        Arguments:
            cursor: gap cursor
            cutoffs: gap cutoffs for this character pair
        Returns:
            validation messages
        """
        messages: list[str] = []

        cursor.annotated_img(2).show()
        response = input(
            f"{cursor.intro_msg} | {cursor.gap_msg} | "
            f"observed '{cursor.gap_chars_escaped()}', "
            f"should be '{cursor.expected_space}'? (y/n): "
        )
        approved = response.lower().startswith("y")
        if approved:
            self._update_pair_gaps(
                (cursor.char_1, cursor.char_2),
                (cutoffs[0], cursor.gap, cutoffs[2], cutoffs[3]),
            )
            expected_gap_chars = cursor.expected_space
        else:
            self._update_pair_gaps(
                (cursor.char_1, cursor.char_2),
                (cursor.gap, cutoffs[1], cutoffs[2], cutoffs[3]),
            )
            expected_gap_chars = ""
        if cursor.gap_chars != expected_gap_chars:
            messages.append(
                f"{cursor.intro_msg} | {cursor.gap_msg} | "
                f"expected '{expected_gap_chars}' "
                f"observed '{cursor.gap_chars_escaped()}'"
            )
        return messages

    def _prompt_tab_gap(
        self, cursor: GapCursor, cutoffs: tuple[int, int, int, int]
    ) -> list[str]:
        """Prompt user to confirm a tab gap.

        Arguments:
            cursor: gap cursor
            cutoffs: gap cutoffs for this character pair
        Returns:
            validation messages
        """
        messages: list[str] = []

        cursor.annotated_img(2).show()
        response = input(
            f"{cursor.intro_msg} | {cursor.gap_msg} | "
            f"observed '{cursor.gap_chars_escaped()}', "
            f"should be '{cursor.expected_tab}'? (y/n): "
        )
        approved = response.lower().startswith("y")
        if approved:
            self._update_pair_gaps(
                (cursor.char_1, cursor.char_2),
                (cutoffs[0], cutoffs[1], cutoffs[2], cursor.gap),
            )
            expected_gap_chars = cursor.expected_tab
        else:
            self._update_pair_gaps(
                (cursor.char_1, cursor.char_2),
                (cutoffs[0], cutoffs[1], cursor.gap, cutoffs[3]),
            )
            expected_gap_chars = cursor.expected_space
        if cursor.gap_chars != expected_gap_chars:
            messages.append(
                f"{cursor.intro_msg} | {cursor.gap_msg} | "
                f"expected '{expected_gap_chars}' "
                f"observed '{cursor.gap_chars_escaped()}'"
            )
        return messages

    def _update_char_dims(self, char: str, dims: tuple[int, ...]):
        """Update char dims and save.

        Arguments:
            char: Character
            dims: Dimensions including width, height, gap values
        """
        n = (len(dims) + 1) // 3
        dims_set = self.char_dims_by_n[n].setdefault(char, set())
        if dims in dims_set:
            return
        dims_set.add(dims)
        info(f"Added ({char}, {dims})")
        save_char_dims(self.char_dims_by_n[n], self._char_dims_path(n))

    def _update_char_grp_dims(self, group: str, dims: tuple[int, ...]):
        """Update char group dims and save.

        Arguments:
            group: Group of characters
            dims: Dimensions including width and height
        """
        n = len(group)
        dims_set = self.char_grp_dims_by_n.setdefault(n, {}).setdefault(group, set())
        if dims in dims_set:
            return
        dims_set.add(dims)
        info(f"Added ({group}, {dims})")
        save_char_grp_dims(self.char_grp_dims_by_n, self._char_grp_dims_path())

    def _update_pair_gaps(
        self, char_pair: tuple[str, str], cutoffs: tuple[int, int, int, int]
    ):
        """Update char pair gaps and save.

        Arguments:
            char_pair: character pair
            cutoffs: cutoffs
        """
        if self.char_pair_gaps.get(char_pair) == cutoffs:
            return
        self.char_pair_gaps[char_pair] = cutoffs
        info(f"Added ({char_pair}, {cutoffs})")
        save_char_pair_gaps(self.char_pair_gaps, self._char_pair_gaps_path())

    @staticmethod
    def _char_dims_path(n: int) -> Path:
        """Path to character dimensions csv file."""
        return package_root / "data" / "ocr" / f"char_dims_{n}.csv"

    @staticmethod
    def _char_grp_dims_path() -> Path:
        """Path to character group dimensions csv file."""
        return package_root / "data" / "ocr" / "char_grp_dims.csv"

    @staticmethod
    def _char_pair_gaps_path() -> Path:
        """Path to character pair gap csv file."""
        return package_root / "data" / "ocr" / "char_pair_gaps.csv"
