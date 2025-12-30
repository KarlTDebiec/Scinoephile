#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING, Any, cast, override

import numpy as np
from PIL import Image

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Subtitle
from scinoephile.image.drawing import get_img_with_bboxes, get_img_with_white_bg

if TYPE_CHECKING:
    from .series import ImageSeries

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
        self._img_with_white_bg: Image.Image | None = None

    @property
    def bbox_widths(self) -> list[int]:
        """Widths of bounding boxes of characters in image."""
        assert self._bboxes is not None
        return [
            self._bboxes[i][2] - self._bboxes[i][0] for i in range(len(self._bboxes))
        ]

    @property
    def bbox_heights(self) -> list[int]:
        """Heights of bounding boxes of characters in image."""
        assert self._bboxes is not None
        return [
            self._bboxes[i][3] - self._bboxes[i][1] for i in range(len(self._bboxes))
        ]

    @property
    def bbox_gaps(self) -> list[int]:
        """Gaps between bounding boxes of characters in image."""
        assert self._bboxes is not None
        return [
            self._bboxes[i + 1][0] - self._bboxes[i][2]
            for i in range(len(self._bboxes) - 1)
        ]

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
    def img(self, img: Image.Image):
        """Set image of subtitle.

        Arguments:
            img: Image of subtitle
        """
        self._img = img
        self._arr = None
        self._bboxes = None
        self._img_with_bboxes = None
        self._img_with_white_bg = None

    @classmethod
    def from_sup(
        cls,
        start_seconds: float,
        end_seconds: float,
        image: np.ndarray,
        *,
        series: ImageSeries | None = None,
    ) -> ImageSubtitle:
        """Create subtitle from SUP timing and image data.

        Arguments:
            start_seconds: start time in seconds
            end_seconds: end time in seconds
            image: image array (RGBA)
            series: parent series
        Returns:
            ImageSubtitle instance
        """
        img = Image.fromarray(image, "RGBA")
        return cls(
            start=int(round(start_seconds * 1000)),
            end=int(round(end_seconds * 1000)),
            img=img,
            series=series,
        )

    @property
    def img_with_bboxes(self) -> Image.Image:
        """Image with bounding boxes."""
        if self._img_with_bboxes is None:
            if self.bboxes is None:
                raise ScinoephileError("Bboxes are not set for this subtitle.")
            self._img_with_bboxes = get_img_with_bboxes(
                self.img_with_white_bg,
                cast(list[tuple[int, ...]], self.bboxes),
            )
        return self._img_with_bboxes

    @property
    def img_with_white_bg(self) -> Image.Image:
        """Image with white background."""
        if self._img_with_white_bg is None:
            self._img_with_white_bg = get_img_with_white_bg(self.img)
        return self._img_with_white_bg
