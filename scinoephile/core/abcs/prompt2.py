#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for corresponding with an LLM."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

__all__ = ["Prompt2"]


class Prompt2(ABC):
    """Text strings to be used for corresponding with an LLM."""

    # Prompt
    base_system_prompt: ClassVar[str]
    """Base system prompt."""

    schema_intro: ClassVar[str]
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str]
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str]
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str]
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str]
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str]
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str]
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str]
    """Text following test case validation errors."""

    # Test case field descriptions
    difficulty_description: ClassVar[str] = (
        "Difficulty level of the test case, used for filtering."
    )
    """Description of 'difficulty' field."""

    prompt_description: ClassVar[str] = (
        "Whether to include test case in prompt examples."
    )
    """Description of 'prompt' field."""

    verified_description: ClassVar[str] = (
        "Whether to include test case in the verified answers cache."
    )
    """Description of 'verified' field."""
