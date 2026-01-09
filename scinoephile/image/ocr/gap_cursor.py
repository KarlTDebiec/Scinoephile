#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Gap cursor for OCR validation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.drawing import get_img_with_bboxes
from scinoephile.image.subtitles import ImageSubtitle

from .char_pair_gaps import get_expected_space, get_expected_tab

__all__ = ["GapCursor"]


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
