#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for written Cantonese line review."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import YueZhoLineReviewManager
from .prompts import YueVsZhoYueHansLineReviewPrompt

__all__ = ["YUE_ZHO_LINE_REVIEW_OPERATION_SPEC"]

YUE_ZHO_LINE_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-line-review",
    test_case_table_name="test_cases__yue_zho__line_review",
    manager_cls=YueZhoLineReviewManager,
    prompt_cls=YueVsZhoYueHansLineReviewPrompt,
)
"""Operation specification for written Cantonese line review."""
