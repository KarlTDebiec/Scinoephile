#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional OCR dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "import_chrome_lens_py_lens_api",
    "import_chrome_lens_py_lens_api_error",
    "import_paddleocr_paddle_ocr",
]

if TYPE_CHECKING:
    from chrome_lens_py import LensAPI, LensAPIError
    from paddleocr import PaddleOCR

_OCR_EXTRA_MESSAGE = (
    "OCR support requires optional OCR dependencies. Install scinoephile with the "
    "'ocr' extra, or the 'ocr-cuda' extra for CUDA support."
)


def import_chrome_lens_py_lens_api() -> type[LensAPI]:
    """Import the Google Lens API class on demand.

    Returns:
        Google Lens API class
    """
    try:
        from chrome_lens_py import LensAPI
    except ImportError as exc:
        raise ImportError(_OCR_EXTRA_MESSAGE) from exc
    return LensAPI


def import_chrome_lens_py_lens_api_error() -> type[LensAPIError]:
    """Import the Google Lens API error class on demand.

    Returns:
        Google Lens API error class
    """
    try:
        from chrome_lens_py import LensAPIError
    except ImportError as exc:
        raise ImportError(_OCR_EXTRA_MESSAGE) from exc
    return LensAPIError


def import_paddleocr_paddle_ocr() -> type[PaddleOCR]:
    """Import the PaddleOCR class on demand.

    Returns:
        PaddleOCR class
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise ImportError(_OCR_EXTRA_MESSAGE) from exc
    return PaddleOCR
