#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to images."""

from __future__ import annotations

from .bbox_manager import BboxManager
from .char_pair import CharPair
from .image_series import ImageSeries
from .image_subtitle import ImageSubtitle
from .validation_manager import ValidationManager
from .whitespace_manager import WhitespaceManager

__all__ = [
    "BboxManager",
    "CharPair",
    "ImageSeries",
    "ImageSubtitle",
    "ValidationManager",
    "WhitespaceManager",
]
