#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for OCR operations.

Package hierarchy (modules may import from any above):
* ocr_fuse_cli / ocr_lens_cli / ocr_paddle_cli / ocr_process_cli
  / ocr_tesseract_cli / ocr_validate_cli
* ocr_cli
"""

from __future__ import annotations

from .ocr_cli import OcrCli
from .ocr_fuse_cli import OcrFuseCli
from .ocr_lens_cli import OcrLensCli
from .ocr_paddle_cli import OcrPaddleCli
from .ocr_process_cli import OcrProcessCli
from .ocr_tesseract_cli import OcrTesseractCli
from .ocr_validate_cli import OcrValidateCli

__all__ = [
    "OcrCli",
    "OcrFuseCli",
    "OcrLensCli",
    "OcrPaddleCli",
    "OcrProcessCli",
    "OcrTesseractCli",
    "OcrValidateCli",
]
