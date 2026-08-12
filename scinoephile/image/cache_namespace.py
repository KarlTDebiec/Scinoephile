#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["ImageCacheNamespace"]


class ImageCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the image package."""

    OCR_LENS = "image/ocr/lens"
    """Google Lens OCR results."""
    OCR_PADDLE = "image/ocr/paddle"
    """PaddleOCR results."""
    OCR_TESSERACT = "image/ocr/tesseract/results"
    """Tesseract OCR results."""
    OCR_TESSERACT_LEGACY_DATA = "image/ocr/tesseract/legacy_data"
    """Legacy-capable Tesseract trained data."""
