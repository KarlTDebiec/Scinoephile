#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for standard Chinese OCR fusion."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager

from .prompts import ZhoHansOcrFusionPrompt

__all__ = ["ZHO_OCR_FUSION_OPERATION_SPEC"]

ZHO_OCR_FUSION_OPERATION_SPEC = OperationSpec(
    operation="zho-ocr-fusion",
    test_case_table_name="test_cases__zho__ocr_fusion",
    manager_cls=OcrFusionManager,
    prompt_cls=ZhoHansOcrFusionPrompt,
)
"""Operation specification for standard Chinese OCR fusion."""
