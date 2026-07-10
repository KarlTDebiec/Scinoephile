#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to OCR fusion.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import OcrFusionManager
from .processor import OcrFusionProcessor
from .prompt import OcrFusionPrompt

__all__ = [
    "OCR_FUSION_OPERATION_SPEC",
    "OcrFusionManager",
    "OcrFusionProcessor",
    "OcrFusionPrompt",
]

OCR_FUSION_OPERATION_SPEC = OperationSpec(
    operation="ocr-fusion",
    manager_cls=OcrFusionManager,
    prompt_cls=OcrFusionPrompt,
)
"""Operation specification for monolingual OCR fusion."""
