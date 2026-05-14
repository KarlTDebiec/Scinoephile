#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for OCR operations.

Package hierarchy (modules may import from any above):
* ocr_fuse_cli / ocr_lens_cli / ocr_paddle_cli / ocr_tesseract_cli
  / ocr_validate_cli
* ocr_cli
"""

from __future__ import annotations

from .ocr_cli import OcrCli

__all__ = [
    "OcrCli",
    "OcrFuseCli",
    "OcrLensCli",
    "OcrPaddleCli",
    "OcrTesseractCli",
    "OcrValidateCli",
]


def __getattr__(name: str):
    """Lazily import heavy OCR command implementations."""
    if name == "OcrFuseCli":
        from .ocr_fuse_cli import OcrFuseCli  # noqa: PLC0415

        return OcrFuseCli
    if name == "OcrLensCli":
        from .ocr_lens_cli import OcrLensCli  # noqa: PLC0415

        return OcrLensCli
    if name == "OcrPaddleCli":
        from .ocr_paddle_cli import OcrPaddleCli  # noqa: PLC0415

        return OcrPaddleCli
    if name == "OcrTesseractCli":
        from .ocr_tesseract_cli import OcrTesseractCli  # noqa: PLC0415

        return OcrTesseractCli
    if name == "OcrValidateCli":
        from .ocr_validate_cli import OcrValidateCli  # noqa: PLC0415

        return OcrValidateCli
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
