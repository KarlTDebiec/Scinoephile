#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract text strings for 中文 proofreading."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.zhongwen.abcs import ZhongwenPrompt

__all__ = ["ZhongwenProofreadingPrompt"]


class ZhongwenProofreadingPrompt(ZhongwenPrompt, ABC):
    """Abstract text strings for 中文 proofreading."""

    # Prompt
    base_system_prompt: ClassVar[str]
    """Base system prompt."""

    # Query descriptions
    zimu_description: ClassVar[str]
    """Description of 'zimu' field."""

    # Answer descriptions
    xiugai_description: ClassVar[str]
    """Description of 'xiugai' field."""

    beizhu_description: ClassVar[str]
    """Description of 'beizhu' field."""

    # Test case validation errors
    zimu_xiugai_equal_error: ClassVar[str]
    """Error message when 'zimu' and 'xiugai' fields are equal."""

    beizhu_missing_error: ClassVar[str]
    """Error message when 'xiugai' field is present but ''beizhu' field is missing."""

    xiugai_missing_error: ClassVar[str]
    """Error message when 'xiugai' field is missing but 'beizhu' field is present."""
