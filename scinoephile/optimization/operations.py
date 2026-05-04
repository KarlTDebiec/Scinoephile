#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for optimization workflows."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.lang.eng.block_review import (
    ENG_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.lang.eng.ocr_fusion import ENG_OCR_FUSION_OPERATION_SPEC
from scinoephile.lang.zho.block_review import (
    ZHO_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.lang.zho.ocr_fusion import ZHO_OCR_FUSION_OPERATION_SPEC
from scinoephile.multilang.yue_zho.block_review import (
    YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.line_review import (
    YUE_ZHO_LINE_REVIEW_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.transcription import (
    YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.translation import (
    YUE_ZHO_TRANSLATION_OPERATION_SPEC,
)

__all__ = ["OPERATIONS"]


OPERATIONS: dict[str, OperationSpec] = {
    spec.operation: spec
    for spec in sorted(
        (
            ENG_BLOCK_REVIEW_OPERATION_SPEC,
            ENG_OCR_FUSION_OPERATION_SPEC,
            ZHO_BLOCK_REVIEW_OPERATION_SPEC,
            ZHO_OCR_FUSION_OPERATION_SPEC,
            YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC,
            YUE_ZHO_LINE_REVIEW_OPERATION_SPEC,
            YUE_ZHO_TRANSLATION_OPERATION_SPEC,
            YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
            YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
        ),
        key=lambda operation_spec: operation_spec.operation,
    )
}
"""Optimization operations keyed by operation name."""
