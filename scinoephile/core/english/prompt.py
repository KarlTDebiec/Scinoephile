#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for corresponding with an LLM in English."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["EnglishPrompt"]


class EnglishPrompt(Prompt, ABC):
    """Text strings to be used for corresponding with an LLM in English."""

    # Prompt
    schema_intro: ClassVar[str] = (
        "Your response must be a JSON object with the following structure:"
    )
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = (
        "Here are some examples of queries and expected answers:"
    )
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "Example query:"
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "Expected answer:"
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "Your previous response was not valid JSON or did "
        "not match the expected schema. Error details:"
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "Please try again and respond only with a valid "
        "JSON object matching the schema."
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "Your previous response was valid JSON compliant with "
        "the answer schema, but not valid for this specific query. Error details:"
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "Please revise your response accordingly."
    """Text following test case validation errors."""
