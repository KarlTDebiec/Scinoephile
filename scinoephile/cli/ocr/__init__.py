#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for OCR operations."""

from __future__ import annotations

from .ocr_cli import OcrCli
from .ocr_paddle_cli import OcrPaddleCli

__all__ = [
    "OcrCli",
    "OcrPaddleCli",
]
