#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for OCR operations."""

from __future__ import annotations

from .ocr_cli import OcrCli

__all__ = [
    "OcrCli",
    "OcrPaddleCli",
    "OcrTesseract4Cli",
    "OcrTesseract5Cli",
]


def __getattr__(name: str):
    """Lazily import heavy OCR command implementations."""
    if name == "OcrPaddleCli":
        from .ocr_paddle_cli import OcrPaddleCli  # noqa: PLC0415

        return OcrPaddleCli
    if name == "OcrTesseract4Cli":
        from .ocr_tesseract4_cli import OcrTesseract4Cli  # noqa: PLC0415

        return OcrTesseract4Cli
    if name == "OcrTesseract5Cli":
        from .ocr_tesseract5_cli import OcrTesseract5Cli  # noqa: PLC0415

        return OcrTesseract5Cli
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
