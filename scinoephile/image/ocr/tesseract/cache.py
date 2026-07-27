#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Caches Tesseract OCR results."""

from __future__ import annotations

from pathlib import Path

from scinoephile.image.ocr.cache import OcrCache

__all__ = ["TesseractCache"]

_CACHE_VERSION = 1
"""Current Tesseract OCR cache version."""


class TesseractCache(OcrCache[str]):
    """Caches normalized Tesseract OCR text."""

    def __init__(
        self,
        cache_root_path: Path | None = None,
        overwrite: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            overwrite: whether to replace matching cache files
        """
        super().__init__(
            cache_root_path,
            "tesseract",
            "Tesseract OCR",
            _CACHE_VERSION,
            overwrite,
        )

    def _deserialize(self, payload: object) -> str:
        """Deserialize and validate recognized text.

        Arguments:
            payload: decoded JSON payload
        Returns:
            recognized text
        """
        if not isinstance(payload, dict):
            raise ValueError("Tesseract OCR cache must contain an object")
        text = payload.get("text")
        if not isinstance(text, str):
            raise ValueError("Tesseract OCR cache text must be a string")
        return text

    def _serialize(self, result: str) -> object:
        """Serialize recognized text.

        Arguments:
            result: recognized text
        Returns:
            JSON-serializable payload
        """
        return {"text": result}
