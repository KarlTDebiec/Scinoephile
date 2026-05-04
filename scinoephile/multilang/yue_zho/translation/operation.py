#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for written Cantonese translation."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.dual_block_gapped import DualBlockGappedManager

from .prompts import YueVsZhoYueHansTranslationPrompt

__all__ = ["YUE_ZHO_TRANSLATION_OPERATION_SPEC"]

YUE_ZHO_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-translation",
    test_case_table_name="test_cases__yue_zho__translation",
    manager_cls=DualBlockGappedManager,
    prompt_cls=YueVsZhoYueHansTranslationPrompt,
)
"""Operation specification for written Cantonese translation."""
