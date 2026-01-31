#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""

from __future__ import annotations

from dataclasses import fields
from typing import Unpack, override

import numpy as np
from PIL import Image

from scinoephile.core.subtitles import Subtitle, SubtitleKwargs
from scinoephile.image.bbox import Bbox

__all__ = ["ImageSubtitle"]


class ImageSubtitle(Subtitle):
    """Individual subtitle with image."""

    @override
    def __init__(
        self,
        img: Image.Image,
        bboxes: list[Bbox] | None = None,
        **kwargs: Unpack[SubtitleKwargs],
    ):
        """Initialize.

        Arguments:
            img: Image of subtitle
            bboxes: bounding boxes for characters in img
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.img = img
        self.arr = np.array(self.img)
        self.bboxes = bboxes

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
        self.arr = np.array(self.img)
        self.bboxes = None
