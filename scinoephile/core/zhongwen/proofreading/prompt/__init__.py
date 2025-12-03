#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 中文 proofreading."""

from __future__ import annotations

from .base import ZhongwenProofreadingPrompt
from .simplified import ZhongwenProofreadingSimplifiedPrompt
from .traditional import ZhongwenProofreadingTraditionalPrompt

__all__ = [
    "ZhongwenProofreadingPrompt",
    "ZhongwenProofreadingSimplifiedPrompt",
    "ZhongwenProofreadingTraditionalPrompt",
]
