#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文 vs. 中文 proofreading test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.dual_single import DualSingleQuery, DualSingleTestCase

from .answer import YueZhoProofreadingAnswer
from .prompts import YueZhoHansProofreadingPrompt

__all__ = ["YueZhoProofreadingTestCase"]


class YueZhoProofreadingTestCase(DualSingleTestCase, ABC):
    """ABC for 粤文 vs. 中文 proofreading test cases."""

    answer_cls: ClassVar[type[YueZhoProofreadingAnswer]] = YueZhoProofreadingAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualSingleQuery]] = DualSingleQuery
    """Query class for this test case."""
    prompt_cls: ClassVar[type[YueZhoHansProofreadingPrompt]]
    """Text for LLM correspondence."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        min_difficulty = super(DualSingleTestCase, self).get_min_difficulty()
        if self.answer is None:
            return min_difficulty

        yuewen = getattr(self.query, self.prompt_cls.src_1, None)
        yuewen_proofread = getattr(self.answer, self.prompt_cls.output, None)
        if yuewen != yuewen_proofread:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty
