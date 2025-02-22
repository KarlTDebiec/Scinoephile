#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np
from PIL import Image

from scinoephile.core import Subtitle
from scinoephile.image.base64 import get_base64_image


class ImageSubtitle(Subtitle):
    """Individual subtitle with image."""

    def __init__(self, data: np.ndarray, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.data = data
        self._base64: str | None = None
        self._img: Image.Image | None = None

    @property
    def base64(self) -> str:
        """Base64 encoding of image."""
        if not hasattr(self, "_base64") or self._base64 is None:
            self._base64 = get_base64_image(self.img)
        return self._base64

    @property
    def img(self) -> Image.Image:
        """Image of subtitle."""
        if not hasattr(self, "_img") or self._img is None:
            self._img = Image.fromarray(self.data)
        return self._img

    @img.setter
    def img(self, img: Image.Image) -> None:
        """Set image of subtitle."""
        self._img = img
        self.data = np.array(img)
        self._base64 = None
