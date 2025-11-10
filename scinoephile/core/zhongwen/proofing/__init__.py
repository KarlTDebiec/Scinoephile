#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofing."""

from scinoephile.core.zhongwen.proofing.zhongwen_proof_llm_queryer import (
    ZhongwenProofLLMQueryer,
)
from scinoephile.core.zhongwen.proofing.zhongwen_proofer import ZhongwenProofer

__all__ = [
    "ZhongwenProofLLMQueryer",
    "ZhongwenProofer",
]
