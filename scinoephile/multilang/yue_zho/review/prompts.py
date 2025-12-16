#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文 review against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwisePrompt
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
]


class YueHansReviewPrompt(ManyToManyBlockwisePrompt, YueHansPrompt):
    """LLM correspondence text for 简体粤文 review against 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = ""
    """Base system prompt."""


class YueHantReviewPrompt:
    """LLM correspondence text for 繁体粤文 review against 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to covert characters from 简体中文 present in parent class."""
