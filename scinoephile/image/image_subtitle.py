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
from scinoephile.image.drawing import (
    get_aligned_image_of_text,
    get_grayscale_image_on_white,
    get_image_diff,
    get_scaled_image,
    get_stacked_image,
)


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
        self._image: Image.Image | None = None
        self._image_diff: Image.Image | None = None
        self._image_from_text: Image.Image | None = None
        self._image_stack: Image.Image | None = None

    @property
    def base64(self) -> str:
        """Base64 encoding of image."""
        if not hasattr(self, "_base64") or self._base64 is None:
            self._base64 = get_base64_image(self.image)
        return self._base64

    @property
    def image(self) -> Image.Image:
        """Image of subtitle."""
        if not hasattr(self, "_image") or self._image is None:
            self._image = Image.fromarray(self.data)
        return self._image

    @image.setter
    def image(self, image: Image.Image) -> None:
        """Set image of subtitle."""
        self._image = image
        self.data = np.array(image)
        self._base64 = None

    @property
    def image_from_text(self) -> Image.Image | None:
        """Image generated from subtitle text, to compare with actual image."""
        if self.text is None:
            return None
        if not hasattr(self, "_image_from_text") or self._image_from_text is None:
            self._image_from_text = get_aligned_image_of_text(
                self.text, get_grayscale_image_on_white(self.image)
            )
        return self._image_from_text

    @property
    def image_diff(self) -> Image.Image | None:
        """Difference between actual and generated image, using pillow."""
        if self.image_from_text is None:
            return None
        if not hasattr(self, "_image_diff") or self._image_diff is None:
            image_l = get_grayscale_image_on_white(self.image)
            image_from_text_scaled = get_scaled_image(image_l, self.image_from_text)
            self._image_diff = get_image_diff(self.image, image_from_text_scaled)
        return self._image_diff

    @property
    def image_stack(self) -> Image.Image | None:
        """Image and image generated from text, vertically stacked."""
        if self.image_from_text is None:
            return None
        if not hasattr(self, "_image_stack") or self._image_stack is None:
            image_l = get_grayscale_image_on_white(self.image)
            image_from_text_scaled = get_scaled_image(image_l, self.image_from_text)
            image_diff = self.image_diff
            self._image_stack = get_stacked_image(
                image_l, image_from_text_scaled, image_diff
            )
        return self._image_stack
