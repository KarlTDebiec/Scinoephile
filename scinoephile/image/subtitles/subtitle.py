#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""

from __future__ import annotations

from dataclasses import fields
from typing import Any, override

import numpy as np
from PIL import Image

from scinoephile.core.subtitles import Subtitle

__all__ = ["ImageSubtitle"]


class ImageSubtitle(Subtitle):
    """Individual subtitle with image."""

    @override
    def __init__(self, img: Image.Image, **kwargs: Any):
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
        self._bboxes: list[tuple[int, int, int, int]] | None = None
        self._img_with_bboxes: Image.Image | None = None

    @property
    def arr(self) -> np.ndarray:
        """Image as numpy array."""
        if self._arr is None:
            self._arr = np.array(self.img)
        return self._arr

    @property
    def bboxes(self) -> list[tuple[int, int, int, int]] | None:
        """Bounding boxes of characters in image."""
        return self._bboxes

    @bboxes.setter
    def bboxes(self, bboxes: list[tuple[int, int, int, int]]):
        """Set bounding boxes of characters in image.

        Arguments:
            bboxes: bounding boxes of characters in image
        """
        self._bboxes = bboxes

    @property
    def img(self) -> Image.Image:
        """Image of subtitle."""
        return self._img

    @img.setter
    def img(self, img: Image.Image):
        """Set image of subtitle.

        Arguments:
            img: Image of subtitle
        """
        self._img = img
        self._arr = None
        self._bboxes = None
        self._img_with_bboxes = None
