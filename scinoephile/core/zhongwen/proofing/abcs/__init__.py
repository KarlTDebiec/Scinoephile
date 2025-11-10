#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes related to 中文 proofing."""

from __future__ import annotations

from scinoephile.core.zhongwen.proofing.abcs.zhongwen_proof_answer import (
    ZhongwenProofAnswer,
)
from scinoephile.core.zhongwen.proofing.abcs.zhongwen_proof_query import (
    ZhongwenProofQuery,
)
from scinoephile.core.zhongwen.proofing.abcs.zhongwen_proof_test_case import (
    ZhongwenProofTestCase,
)

__all__ = [
    "ZhongwenProofAnswer",
    "ZhongwenProofQuery",
    "ZhongwenProofTestCase",
]
