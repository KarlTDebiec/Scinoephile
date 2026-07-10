#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to guided review using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import GuidedReviewManager
from .processor import GuidedReviewProcessor
from .prompt import GuidedReviewPrompt

__all__ = [
    "GUIDED_REVIEW_OPERATION_SPEC",
    "GuidedReviewManager",
    "GuidedReviewProcessor",
    "GuidedReviewPrompt",
]

GUIDED_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="guided-review",
    test_case_table_name="test_cases__guided_review",
    manager_cls=GuidedReviewManager,
    prompt_cls=GuidedReviewPrompt,
)
"""Operation specification for guided review."""
