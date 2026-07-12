#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for English."""

from __future__ import annotations

from typing import Final

from scinoephile.core.llms import PromptLocalizationFields

__all__ = ["ENG_PROMPT_FIELDS"]


ENG_PROMPT_FIELDS: Final[PromptLocalizationFields] = {
    "few_shot_intro": "Here are some examples of queries and expected answers:",
    "few_shot_query_intro": "Example query:",
    "few_shot_answer_intro": "Expected answer:",
    "answer_invalid_pre": (
        "Your previous response was not valid JSON or did not match the expected "
        "schema. Error details:"
    ),
    "answer_invalid_post": (
        "Please try again and respond only with a valid JSON object matching the "
        "schema."
    ),
    "test_case_invalid_pre": (
        "Your previous response was valid JSON compliant with the answer schema, but "
        "not valid for this specific query. Error details:"
    ),
    "test_case_invalid_post": "Please revise your response accordingly.",
}
"""Shared English LLM correspondence fields."""
