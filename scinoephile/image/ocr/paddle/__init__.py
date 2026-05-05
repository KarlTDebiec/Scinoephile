#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles."""

from __future__ import annotations

from .engine import PaddleOcrRecognizer, PaddleOcrRecognizerProtocol
from .preprocessing import preprocess_paddle_ocr_image
from .result import (
    PaddleOcrBoundingBox,
    PaddleOcrPoint,
    PaddleOcrTextResult,
    format_paddle_ocr_text,
    group_paddle_ocr_text_results,
)
from .series import ocr_image_series_with_paddle

__all__ = [
    "PaddleOcrBoundingBox",
    "PaddleOcrPoint",
    "PaddleOcrRecognizer",
    "PaddleOcrRecognizerProtocol",
    "PaddleOcrTextResult",
    "format_paddle_ocr_text",
    "group_paddle_ocr_text_results",
    "ocr_image_series_with_paddle",
    "preprocess_paddle_ocr_image",
]
