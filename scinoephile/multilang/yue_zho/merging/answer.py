#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文/中文 transcription merging answers."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.dual_multi_single import DualMultiSingleAnswer

from .prompt import YueZhoHansMergingPrompt

__all__ = ["YueZhoMergingAnswer"]


class YueZhoMergingAnswer(DualMultiSingleAnswer, ABC):
    """ABC for 粤文/中文 transcription merging answers."""

    prompt_cls: ClassVar[type[YueZhoHansMergingPrompt]]
    """Text for LLM correspondence."""
