#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR text result."""

from __future__ import annotations

from dataclasses import dataclass

from .bounding_box import PaddleOcrBoundingBox

__all__ = ["PaddleOcrTextResult"]


@dataclass(frozen=True)
class PaddleOcrTextResult:
    """PaddleOCR text detection result."""

    text: str
    """Recognized text."""
    confidence: float
    """Recognition confidence."""
    bounding_box: PaddleOcrBoundingBox
    """Text bounding box."""
