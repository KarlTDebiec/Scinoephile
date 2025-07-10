#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 merging; may also be used for few-shot prompt."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MergeTestCase:
    """Test case for 粤文 merging; may also be used for few-shot prompt."""

    zhongwen_input: str
    """Input single-line 中文 text."""
    yuewen_input: list[str]
    """Input multi-line 粤文 text."""

    yuewen_output: str
    """Output single-line 粤文 text."""

    include_in_prompt: bool = False
    """Whether to include test case in prompt examples."""
