#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR support for image subtitles."""

from __future__ import annotations

from .tesseract_ocr_recognizer import (
    Tesseract4OcrRecognizer,
    Tesseract5OcrRecognizer,
    TesseractOcrRecognizer,
)

__all__ = [
    "Tesseract4OcrRecognizer",
    "Tesseract5OcrRecognizer",
    "TesseractOcrRecognizer",
]
