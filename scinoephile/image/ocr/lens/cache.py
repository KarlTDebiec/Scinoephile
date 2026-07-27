#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Caches Google Lens OCR results."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.image.ocr.cache import OcrCache

__all__ = ["LensCache"]

_CACHE_VERSION = 1
"""Current Google Lens OCR cache version."""


class LensCache(OcrCache[list[str]]):
    """Caches normalized Google Lens OCR lines."""

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
            "google-lens",
            "Google Lens OCR",
            _CACHE_VERSION,
            overwrite,
        )

    def _deserialize(self, payload: object) -> list[str]:
        """Deserialize and validate normalized OCR lines.

        Arguments:
            payload: decoded JSON payload
        Returns:
            normalized OCR lines
        """
        if not isinstance(payload, dict):
            raise ValueError("Google Lens OCR cache must contain an object")
        lines = payload.get("lines")
        if not isinstance(lines, list):
            raise ValueError("Google Lens OCR cache must contain a lines list")
        if not all(isinstance(line, str) for line in lines):
            raise ValueError("Google Lens OCR cache lines must be strings")
        return cast(list[str], lines)

    def _serialize(self, result: list[str]) -> object:
        """Serialize normalized OCR lines.

        Arguments:
            result: normalized OCR lines
        Returns:
            JSON-serializable payload
        """
        return {"lines": result}
