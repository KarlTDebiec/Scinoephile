#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with image."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np
from PIL import Image

from scinoephile.core import Subtitle


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

    @property
    def img(self) -> Image:
        """Image of subtitle."""
        if not hasattr(self, "_img"):
            self._img = Image.fromarray(self.data)
        return self._img
