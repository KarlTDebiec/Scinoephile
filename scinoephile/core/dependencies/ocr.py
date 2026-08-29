#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional OCR dependencies."""

from __future__ import annotations

from types import ModuleType

from scinoephile.core.exceptions import DependencyError

__all__ = ["import_chrome_lens_py", "import_paddleocr"]

_OCR_EXTRA_MESSAGE = (
    "OCR support requires optional OCR dependencies. Install scinoephile with the "
    "'ocr' extra, or the 'ocr-cuda' extra for CUDA support."
)


def import_chrome_lens_py() -> ModuleType:
    """Import chrome-lens-py on demand.

    Returns:
        chrome-lens-py module
    Raises:
        DependencyError: if OCR dependencies are unavailable
    """
    try:
        import chrome_lens_py
    except ImportError as exc:
        raise DependencyError(_OCR_EXTRA_MESSAGE) from exc
    return chrome_lens_py


def import_paddleocr() -> ModuleType:
    """Import PaddleOCR on demand.

    Returns:
        PaddleOCR module
    Raises:
        DependencyError: if OCR dependencies are unavailable
    """
    try:
        import paddleocr
    except ImportError as exc:
        raise DependencyError(_OCR_EXTRA_MESSAGE) from exc
    return paddleocr
