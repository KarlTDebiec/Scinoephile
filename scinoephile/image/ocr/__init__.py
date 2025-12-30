#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR-related image processing."""

from __future__ import annotations

from .bbox_manager import BboxManager
from .char_pair import CharPair
from .whitespace_manager import WhitespaceManager

__all__ = [
    "BboxManager",
    "CharPair",
    "WhitespaceManager",
]
