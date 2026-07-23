#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to OCR fusion.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import OcrFusionManager
from .models import OcrFusionAnswer, OcrFusionQuery, OcrFusionTestCase
from .processor import OcrFusionProcessor
from .prompt import OcrFusionPrompt

__all__ = [
    "OcrFusionAnswer",
    "OcrFusionManager",
    "OcrFusionProcessor",
    "OcrFusionPrompt",
    "OcrFusionQuery",
    "OcrFusionTestCase",
]
