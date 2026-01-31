#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR-related image processing."""

from __future__ import annotations

from .bbox_validator import BboxValidator
from .char_validator import CharValidator

__all__ = [
    "BboxValidator",
    "CharValidator",
]
