#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Hard-coded operation registry for test-case persistence sync."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Manager, Prompt
from scinoephile.lang.eng.block_review.prompts import EngBlockReviewPrompt
from scinoephile.lang.eng.ocr_fusion.prompts import EngOcrFusionPrompt
from scinoephile.lang.zho.block_review.prompts import ZhoHansBlockReviewPrompt
from scinoephile.lang.zho.ocr_fusion.prompts import ZhoHansOcrFusionPrompt
from scinoephile.llms.dual_block import DualBlockManager
from scinoephile.llms.dual_block_gapped import DualBlockGappedManager
from scinoephile.llms.dual_pair import DualPairManager
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager
from scinoephile.multilang.yue_zho.block_review.prompts import (
    YueVsZhoYueHansBlockReviewPrompt,
)
from scinoephile.multilang.yue_zho.line_review.manager import YueZhoLineReviewManager
from scinoephile.multilang.yue_zho.line_review.prompts import (
    YueVsZhoYueHansLineReviewPrompt,
)
from scinoephile.multilang.yue_zho.transcription.deliniation.prompt import (
    YueVsZhoYueHansDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoPunctuationManager,
)
from scinoephile.multilang.yue_zho.transcription.punctuation.prompt import (
    YueVsZhoYueHansPunctuationPrompt,
)
from scinoephile.multilang.yue_zho.translation.prompts import (
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
    table_name: str
    manager_cls: type[Manager]
    prompt_cls: type[Prompt]


_OPERATIONS: dict[str, OperationSpec] = {
    "eng-block-review": OperationSpec(
        operation="eng-block-review",
        table_name="test_cases__eng__block_review",
        manager_cls=MonoBlockManager,
        prompt_cls=EngBlockReviewPrompt,
    ),
    "eng-ocr-fusion": OperationSpec(
        operation="eng-ocr-fusion",
        table_name="test_cases__eng__ocr_fusion",
        manager_cls=OcrFusionManager,
        prompt_cls=EngOcrFusionPrompt,
    ),
    "zho-block-review": OperationSpec(
        operation="zho-block-review",
        table_name="test_cases__zho__block_review",
        manager_cls=MonoBlockManager,
        prompt_cls=ZhoHansBlockReviewPrompt,
    ),
    "zho-ocr-fusion": OperationSpec(
        operation="zho-ocr-fusion",
        table_name="test_cases__zho__ocr_fusion",
        manager_cls=OcrFusionManager,
        prompt_cls=ZhoHansOcrFusionPrompt,
    ),
    "yue-zho-block-review": OperationSpec(
        operation="yue-zho-block-review",
        table_name="test_cases__yue_zho__block_review",
        manager_cls=DualBlockManager,
        prompt_cls=YueVsZhoYueHansBlockReviewPrompt,
    ),
    "yue-zho-line-review": OperationSpec(
        operation="yue-zho-line-review",
        table_name="test_cases__yue_zho__line_review",
        manager_cls=YueZhoLineReviewManager,
        prompt_cls=YueVsZhoYueHansLineReviewPrompt,
    ),
    "yue-zho-translation": OperationSpec(
        operation="yue-zho-translation",
        table_name="test_cases__yue_zho__translation",
        manager_cls=DualBlockGappedManager,
        prompt_cls=YueVsZhoYueHansTranslationPrompt,
    ),
    "yue-zho-transcription-deliniation": OperationSpec(
        operation="yue-zho-transcription-deliniation",
        table_name="test_cases__yue_zho__transcription_deliniation",
        manager_cls=DualPairManager,
        prompt_cls=YueVsZhoYueHansDeliniationPrompt,
    ),
    "yue-zho-transcription-punctuation": OperationSpec(
        operation="yue-zho-transcription-punctuation",
        table_name="test_cases__yue_zho__transcription_punctuation",
        manager_cls=YueZhoPunctuationManager,
        prompt_cls=YueVsZhoYueHansPunctuationPrompt,
    ),
}


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
