#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for test-case persistence sync."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Manager, Prompt
from scinoephile.lang.eng.block_review import EngBlockReviewPrompt
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.zho.block_review import ZhoHansBlockReviewPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHansOcrFusionPrompt
from scinoephile.llms.dual_block import DualBlockManager
from scinoephile.llms.dual_block_gapped import DualBlockGappedManager
from scinoephile.llms.dual_pair import DualPairManager
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager
from scinoephile.multilang.yue_zho.block_review import (
    YueVsZhoYueHansBlockReviewPrompt,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueVsZhoYueHansLineReviewPrompt,
    YueZhoLineReviewManager,
)
from scinoephile.multilang.yue_zho.transcription import (
    YueVsZhoYueHansDeliniationPrompt,
    YueVsZhoYueHansPunctuationPrompt,
    YueZhoPunctuationManager,
)
from scinoephile.multilang.yue_zho.translation import (
    YueVsZhoYueHansTranslationPrompt,
)

__all__ = [
    "OperationSpec",
    "get_operation_spec",
    "operation_names",
]


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """Specification for syncing a family of test-case JSONs."""

    operation: str
    """Operation name exposed through the CLI."""
    table_name: str
    """SQLite table name used to persist cases for this operation."""
    manager_cls: type[Manager]
    """Manager class used to load and validate cases for this operation."""
    prompt_cls: type[Prompt]
    """Prompt class used to load and validate cases for this operation."""


_OPERATION_SPECS: tuple[OperationSpec, ...] = (
    OperationSpec(
        operation="eng-block-review",
        table_name="test_cases__eng__block_review",
        manager_cls=MonoBlockManager,
        prompt_cls=EngBlockReviewPrompt,
    ),
    OperationSpec(
        operation="eng-ocr-fusion",
        table_name="test_cases__eng__ocr_fusion",
        manager_cls=OcrFusionManager,
        prompt_cls=EngOcrFusionPrompt,
    ),
    OperationSpec(
        operation="zho-block-review",
        table_name="test_cases__zho__block_review",
        manager_cls=MonoBlockManager,
        prompt_cls=ZhoHansBlockReviewPrompt,
    ),
    OperationSpec(
        operation="zho-ocr-fusion",
        table_name="test_cases__zho__ocr_fusion",
        manager_cls=OcrFusionManager,
        prompt_cls=ZhoHansOcrFusionPrompt,
    ),
    OperationSpec(
        operation="yue-zho-block-review",
        table_name="test_cases__yue_zho__block_review",
        manager_cls=DualBlockManager,
        prompt_cls=YueVsZhoYueHansBlockReviewPrompt,
    ),
    OperationSpec(
        operation="yue-zho-line-review",
        table_name="test_cases__yue_zho__line_review",
        manager_cls=YueZhoLineReviewManager,
        prompt_cls=YueVsZhoYueHansLineReviewPrompt,
    ),
    OperationSpec(
        operation="yue-zho-translation",
        table_name="test_cases__yue_zho__translation",
        manager_cls=DualBlockGappedManager,
        prompt_cls=YueVsZhoYueHansTranslationPrompt,
    ),
    OperationSpec(
        operation="yue-zho-transcription-deliniation",
        table_name="test_cases__yue_zho__transcription_deliniation",
        manager_cls=DualPairManager,
        prompt_cls=YueVsZhoYueHansDeliniationPrompt,
    ),
    OperationSpec(
        operation="yue-zho-transcription-punctuation",
        table_name="test_cases__yue_zho__transcription_punctuation",
        manager_cls=YueZhoPunctuationManager,
        prompt_cls=YueVsZhoYueHansPunctuationPrompt,
    ),
)
"""Operation specs for test case synchronization."""

_OPERATIONS: dict[str, OperationSpec] = {
    spec.operation: spec for spec in _OPERATION_SPECS
}
"""Operation specs keyed by operation name."""


def get_operation_spec(operation: str) -> OperationSpec:
    """Get operation spec.

    Arguments:
        operation: operation name
    Returns:
        operation spec
    """
    return _OPERATIONS[operation]


operation_names: tuple[str, ...] = tuple(sorted(_OPERATIONS))
"""Known operation names."""
