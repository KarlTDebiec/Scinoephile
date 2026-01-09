#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character cursor for OCR validation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSubtitle

__all__ = ["CharCursor"]


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

    def bbox_grp(self, n_bboxes: int) -> list[Bbox]:
        """Current bbox group.

        Arguments:
            n_bboxes: number of bboxes to include
        Returns:
            bbox group
        """
        return self.sub.bboxes[self.bbox_idx : self.bbox_idx + n_bboxes]

    def char_grp(self, n_chars: int) -> str:
        """Current character group.

        Arguments:
            n_chars: number of characters to include
        Returns:
            character group
        """
        return self.sub.text_with_newline[self.char_idx : self.char_idx + n_chars]

    @property
    def char(self) -> str:
        """Current character."""
        return self.sub.text_with_newline[self.char_idx]

    @property
    def intro_msg(self) -> str:
        """Message intro for the current character index."""
        text = self.sub.text_with_newline.replace(chr(10), "\\n")
        return f"Sub {self.sub_idx + 1:4d} | Char {self.char_idx + 1:2d} | {text}"
