#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for written Cantonese block review."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.dual_block import DualBlockManager

from .prompts import YueVsZhoYueHansBlockReviewPrompt

__all__ = ["YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC"]

YUE_ZHO_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-block-review",
    test_case_table_name="test_cases__yue_zho__block_review",
    manager_cls=DualBlockManager,
    prompt_cls=YueVsZhoYueHansBlockReviewPrompt,
)
"""Operation specification for written Cantonese block review."""
