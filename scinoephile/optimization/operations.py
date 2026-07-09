#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for optimization workflows."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.lang.ocr_fusion import OCR_FUSION_OPERATION_SPEC
from scinoephile.lang.review import REVIEW_OPERATION_SPEC
from scinoephile.multilang.review.guided import GUIDED_REVIEW_OPERATION_SPEC
from scinoephile.multilang.review.pairwise import PAIRWISE_REVIEW_OPERATION_SPEC
from scinoephile.multilang.translation.gap import GAP_TRANSLATION_OPERATION_SPEC
from scinoephile.multilang.translation.guided import GUIDED_TRANSLATION_OPERATION_SPEC
from scinoephile.multilang.translation.standard import TRANSLATION_OPERATION_SPEC
from scinoephile.multilang.yue_zho.transcription import (
    YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
)

__all__ = ["OPERATIONS"]


OPERATIONS: dict[str, OperationSpec] = {
    spec.operation: spec
    for spec in sorted(
        (
            GAP_TRANSLATION_OPERATION_SPEC,
            GUIDED_REVIEW_OPERATION_SPEC,
            GUIDED_TRANSLATION_OPERATION_SPEC,
            OCR_FUSION_OPERATION_SPEC,
            PAIRWISE_REVIEW_OPERATION_SPEC,
            REVIEW_OPERATION_SPEC,
            TRANSLATION_OPERATION_SPEC,
            YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
            YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
        ),
        key=lambda operation_spec: operation_spec.operation,
    )
}
"""Optimization operations keyed by operation name."""
