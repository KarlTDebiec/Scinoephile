#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for English block review."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.mono_block import MonoBlockManager

from .prompts import EngBlockReviewPrompt

__all__ = ["ENG_BLOCK_REVIEW_OPERATION_SPEC"]

ENG_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="eng-block-review",
    test_case_table_name="test_cases__eng__block_review",
    manager_cls=MonoBlockManager,
    prompt_cls=EngBlockReviewPrompt,
)
"""Operation specification for English block review."""
