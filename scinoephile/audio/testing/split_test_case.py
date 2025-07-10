#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 splitting; may also be used for few-shot prompt."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SplitTestCase:
    """Test case for 粤文 splitting; may also be used for few-shot prompt."""

    zhongwen_one_input: str
    """Input 中文 candidate one text."""
    yuewen_one_input: str
    """Input 粤文 text already assigned to 中文 candidate one."""
    zhongwen_two_input: str
    """Input 中文 candidate two text."""
    yuewen_two_input: str
    """Input 粤文 text already assigned to 中文 candidate two."""
    yuewen_input: str
    """Input 粤文 text."""

    yuewen_one_output: str
    """Output 粤文 text assigned to 中文 candidate one."""
    yuewen_two_output: str
    """Output 粤文 text assigned to 中文 candidate two."""

    include_in_prompt: bool = False
    """Whether to include test case in prompt examples."""
