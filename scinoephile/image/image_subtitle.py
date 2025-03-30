#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np
from PIL import Image

from scinoephile.core import Subtitle
from scinoephile.core.text import whitespace
from scinoephile.image.base64 import get_base64_image
from scinoephile.image.drawing import get_img_with_bboxes, get_img_with_white_bg


class ImageSubtitle(Subtitle):
    """Individual subtitle with image."""

    def __init__(self, img: Image, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.img = img
        self._arr: np.ndarray | None = None
        self._base64: str | None = None
        self._bboxes: list[tuple[int, int]] | None = None
        self._img_with_bboxes: Image.Image | None = None
        self._img_on_white_bg: Image.Image | None = None

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
        """Set bounding boxes of characters in image."""
        self._bboxes = bboxes

    @property
    def arr(self) -> np.ndarray:
        """Image as numpy array."""
        if self._arr is None:
            self._arr = np.array(self.img)
        return self._arr

    @property
    def img(self) -> Image.Image:
        """Image of subtitle."""
        if self._img is None:
            self._img = Image.fromarray(self.arr)
        return self._img

    @img.setter
    def img(self, img: Image.Image) -> None:
        """Set image of subtitle."""
        self._img = img
        self._arr = None
        self._base64 = None

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
    def img_with_white_bg(self):
        """Image with white background."""
        if self._img_on_white_bg is None:
            self._img_on_white_bg = get_img_with_white_bg(self.img)
        return self._img_on_white_bg

    @property
    def text_excluding_whitespace(self) -> str:
        """Text excluding whitespace."""
        return "".join([c for c in self.text if c not in whitespace])
