#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np
from PIL import Image

from scinoephile.core import Subtitle
from scinoephile.core.text import whitespace_chars
from scinoephile.image.base64 import get_base64_image
from scinoephile.image.char_pair import CharPair
from scinoephile.image.drawing import get_img_with_bboxes, get_img_with_white_bg


class ImageSubtitle(Subtitle):
    """Individual subtitle with image."""

    def __init__(self, img: Image.Image, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            img: Image of subtitle
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.img = img
        self._arr: np.ndarray | None = None
        self._base64: str | None = None
        self._bboxes: list[tuple[int, int]] | None = None
        self._char_pairs: list[CharPair] | None = None
        self._img_with_bboxes: Image.Image | None = None
        self._img_with_white_bg: Image.Image | None = None

    @property
    def base64(self) -> str:
        """Image encoded as base64."""
        if self._base64 is None:
            self._base64 = get_base64_image(self.img)
        return self._base64

    @property
    def bbox_widths(self) -> list[int]:
        """Widths of bounding boxes of characters in image."""
        if self._bboxes is None:
            return None
        return [
            self._bboxes[i][2] - self._bboxes[i][0] for i in range(len(self._bboxes))
        ]

    @property
    def bbox_heights(self) -> list[int]:
        """Heights of bounding boxes of characters in image."""
        if self._bboxes is None:
            return None
        return [
            self._bboxes[i][3] - self._bboxes[i][1] for i in range(len(self._bboxes))
        ]

    @property
    def bbox_gaps(self) -> list[int]:
        """Gaps between bounding boxes of characters in image."""
        if self._bboxes is None:
            return None
        return [
            self._bboxes[i + 1][0] - self._bboxes[i][2]
            for i in range(len(self._bboxes) - 1)
        ]

    @property
    def bboxes(self) -> list[tuple[int, int]]:
        """Bounding boxes of characters in image."""
        return self._bboxes

    @bboxes.setter
    def bboxes(self, bboxes: list[tuple[int, int]]) -> None:
        """Set bounding boxes of characters in image.

        Arguments:
            bboxes: Bounding boxes of characters in image
        """
        self._bboxes = bboxes

    @property
    def char_pairs(self) -> list[CharPair]:
        """Pairs of characters in image."""
        if self._char_pairs is None:
            self._init_char_pairs()
        return self._char_pairs

    @char_pairs.setter
    def char_pairs(self, char_pairs: list[CharPair]) -> None:
        """Set pairs of characters in image.

        Arguments:
            char_pairs: Character pairs
        """
        new_text = ""
        for char_pair in char_pairs:
            new_text += char_pair.char_1 + char_pair.whitespace
        new_text += char_pairs[-1].char_2
        self.text = new_text
        self._char_pairs = char_pairs

    @property
    def arr(self) -> np.ndarray:
        """Image as numpy array."""
        if self._arr is None:
            self._arr = np.array(self.img)
        return self._arr

    @property
    def img(self) -> Image.Image:
        """Image of subtitle."""
        return self._img

    @img.setter
    def img(self, img: Image.Image) -> None:
        """Set image of subtitle.

        Arguments:
            img: Image of subtitle
        """
        self._img = img
        self._arr = None
        self._base64 = None
        self._bboxes = None
        self._char_pairs = None
        self._img_with_bboxes = None
        self._img_with_white_bg = None

    @property
    def img_with_bboxes(self) -> Image.Image:
        """Image with bounding boxes."""
        if self._img_with_bboxes is None:
            self._img_with_bboxes = get_img_with_bboxes(
                self.img_with_white_bg,
                self.bboxes,
            )
        return self._img_with_bboxes

    @property
    def img_with_white_bg(self) -> Image.Image:
        """Image with white background."""
        if self._img_with_white_bg is None:
            self._img_with_white_bg = get_img_with_white_bg(self.img)
        return self._img_with_white_bg

    @property
    def text_excluding_whitespace(self) -> str:
        """Text excluding whitespace."""
        return "".join([c for c in self.text if c not in whitespace_chars])

    def _init_char_pairs(self) -> list[CharPair]:
        """Initialize character pairs."""
        char_1_i = 0
        width_1_i = 0
        gap_i = 0
        char_pairs = []
        while True:
            if char_1_i > len(self.text) - 2:
                break

            # Get char 1 and its width
            char_1 = self.text[char_1_i]
            width_1 = self.bbox_widths[width_1_i]

            # Get provisional char 2 and its width
            char_2_i = char_1_i + 1
            char_2 = self.text[char_2_i]
            width_2_i = width_1_i + 1
            width_2 = self.bbox_widths[width_2_i]

            # If char 2 is whitespace, iterate to next real char and track whitespace
            gap_whitespace = ""
            while char_2_i < len(self.text):
                char_2 = self.text[char_2_i]
                if char_2 in whitespace_chars:
                    gap_whitespace += char_2
                    char_2_i += 1
                    continue
                else:
                    break

            # Get gap between char 1 and char 2, and maximum expected gap
            gap = self.bbox_gaps[gap_i]
            pair = CharPair(char_1, char_2, width_1, width_2, gap, gap_whitespace)
            char_pairs.append(pair)

            char_1_i = char_2_i
            width_1_i = width_2_i
            gap_i += 1

        self._char_pairs = char_pairs
