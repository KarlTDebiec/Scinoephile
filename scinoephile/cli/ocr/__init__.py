#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for OCR operations."""

from __future__ import annotations

from .ocr_cli import OcrCli

__all__ = [
    "OcrCli",
    "OcrLensCli",
    "OcrPaddleCli",
]


def __getattr__(name: str):
    """Lazily import heavy OCR command implementations."""
    if name == "OcrLensCli":
        from .ocr_lens_cli import OcrLensCli  # noqa: PLC0415

        return OcrLensCli
    if name == "OcrPaddleCli":
        from .ocr_paddle_cli import OcrPaddleCli  # noqa: PLC0415

        return OcrPaddleCli
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
