#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for standard Chinese block review."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.mono_block import MonoBlockManager

from .prompts import ZhoHansBlockReviewPrompt

__all__ = ["ZHO_BLOCK_REVIEW_OPERATION_SPEC"]

ZHO_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="zho-block-review",
    test_case_table_name="test_cases__zho__block_review",
    manager_cls=MonoBlockManager,
    prompt_cls=ZhoHansBlockReviewPrompt,
)
"""Operation specification for standard Chinese block review."""
