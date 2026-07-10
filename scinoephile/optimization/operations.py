#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for optimization workflows."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.delineation import DELINEATION_OPERATION_SPEC
from scinoephile.llms.gap_translation import GAP_TRANSLATION_OPERATION_SPEC
from scinoephile.llms.guided_review import GUIDED_REVIEW_OPERATION_SPEC
from scinoephile.llms.guided_translation import GUIDED_TRANSLATION_OPERATION_SPEC
from scinoephile.llms.ocr_fusion import OCR_FUSION_OPERATION_SPEC
from scinoephile.llms.pairwise_review import PAIRWISE_REVIEW_OPERATION_SPEC
from scinoephile.llms.punctuation import PUNCTUATION_OPERATION_SPEC
from scinoephile.llms.review import REVIEW_OPERATION_SPEC
from scinoephile.llms.translation import TRANSLATION_OPERATION_SPEC

__all__ = ["OPERATIONS"]


OPERATIONS: dict[str, OperationSpec] = {
    spec.operation: spec
    for spec in sorted(
        (
            DELINEATION_OPERATION_SPEC,
            GAP_TRANSLATION_OPERATION_SPEC,
            GUIDED_REVIEW_OPERATION_SPEC,
            GUIDED_TRANSLATION_OPERATION_SPEC,
            OCR_FUSION_OPERATION_SPEC,
            PAIRWISE_REVIEW_OPERATION_SPEC,
            PUNCTUATION_OPERATION_SPEC,
            REVIEW_OPERATION_SPEC,
            TRANSLATION_OPERATION_SPEC,
        ),
        key=lambda operation_spec: operation_spec.operation,
    )
}
"""Optimization operations keyed by operation name."""
