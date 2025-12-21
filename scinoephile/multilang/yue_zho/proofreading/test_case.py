#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test cases for 粤文 vs. 中文 proofreading."""

from __future__ import annotations

from abc import ABC

from scinoephile.llms.dual_single import DualSingleTestCase

__all__ = ["YueZhoProofreadingTestCase"]


class YueZhoProofreadingTestCase(DualSingleTestCase, ABC):
    """Test cases for 粤文 vs. 中文 proofreading."""

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
