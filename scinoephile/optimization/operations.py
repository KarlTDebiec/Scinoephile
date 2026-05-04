#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for optimization workflows."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.lang.eng.block_review.operation import (
    ENG_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.lang.eng.ocr_fusion.operation import ENG_OCR_FUSION_OPERATION_SPEC
from scinoephile.lang.zho.block_review.operation import (
    ZHO_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.lang.zho.ocr_fusion.operation import ZHO_OCR_FUSION_OPERATION_SPEC
from scinoephile.multilang.yue_zho.block_review.operation import (
    YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.line_review.operation import (
    YUE_ZHO_LINE_REVIEW_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.transcription.operation import (
    YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
)
from scinoephile.multilang.yue_zho.translation.operation import (
    YUE_ZHO_TRANSLATION_OPERATION_SPEC,
)

__all__ = [
    "get_operation_spec",
    "operation_names",
    "operation_specs",
]


_OPERATION_SPECS: tuple[OperationSpec, ...] = (
    ENG_BLOCK_REVIEW_OPERATION_SPEC,
    ENG_OCR_FUSION_OPERATION_SPEC,
    ZHO_BLOCK_REVIEW_OPERATION_SPEC,
    ZHO_OCR_FUSION_OPERATION_SPEC,
    YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC,
    YUE_ZHO_LINE_REVIEW_OPERATION_SPEC,
    YUE_ZHO_TRANSLATION_OPERATION_SPEC,
    YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC,
)
"""Operation specs registered for optimization workflows."""

_OPERATIONS: dict[str, OperationSpec] = {
    spec.operation: spec for spec in _OPERATION_SPECS
}
"""Operation specs keyed by operation name."""

operation_specs: tuple[OperationSpec, ...] = tuple(
    sorted(_OPERATION_SPECS, key=lambda spec: spec.operation)
)
"""Known operation specs."""


def get_operation_spec(operation: str) -> OperationSpec:
    """Get operation spec.

    Arguments:
        operation: operation name
    Returns:
        operation spec
    """
    return _OPERATIONS[operation]


operation_names: tuple[str, ...] = tuple(spec.operation for spec in operation_specs)
"""Known operation names."""
