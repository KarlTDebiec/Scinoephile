#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Immutable text and field configuration for LLM correspondence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, fields, replace
from typing import Self, TypedDict

from scinoephile.core.language import Language

__all__ = [
    "Prompt",
    "PromptLocalizationFields",
]


class PromptLocalizationFields(TypedDict):
    """Shared localization fields accepted by all prompt types."""

    few_shot_intro: str
    """Text preceding few-shot examples."""
    few_shot_query_intro: str
    """Text preceding each few-shot example query."""
    few_shot_answer_intro: str
    """Text preceding each few-shot expected answer."""
    answer_invalid_pre: str
    """Text introducing an invalid-answer retry."""
    answer_invalid_post: str
    """Text concluding an invalid-answer retry."""
    test_case_invalid_pre: str
    """Text preceding test case validation errors."""
    test_case_invalid_post: str
    """Text following test case validation errors."""


@dataclass(frozen=True, slots=True, kw_only=True)
class Prompt:
    """Immutable text and field configuration for LLM correspondence."""

    language: Language = Language.eng
    """Language in which the prompt corresponds with the LLM."""

    # Prompt
    base_system_prompt: str = ""
    """Base system prompt."""
    few_shot_intro: str = ""
    """Text preceding few-shot examples."""
    few_shot_query_intro: str = ""
    """Text preceding each few-shot example query."""
    few_shot_answer_intro: str = ""
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: str = ""
    """Text introducing an invalid-answer retry."""
    answer_invalid_post: str = ""
    """Text concluding an invalid-answer retry."""

    # Test case validation errors
    test_case_invalid_pre: str = ""
    """Text preceding test case validation errors."""
    test_case_invalid_post: str = ""
    """Text following test case validation errors."""

    @property
    def name(self) -> str:
        """Stable content-addressed name used for generated model classes."""
        prompt_fields = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "language"
        }
        payload_json = json.dumps(
            {
                "fields": prompt_fields,
                "language": self.language.code,
                "type": type(self).__name__,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = hashlib.sha256(payload_json.encode()).hexdigest()[:12]
        language_name = self.language.code.replace("-", "_")
        return f"{type(self).__name__}_{language_name}_{digest}"

    def transformed(self, language: Language, transform: Callable[[str], str]) -> Self:
        """Build a prompt with all string fields transformed.

        Arguments:
            language: language of the transformed prompt
            transform: string transformation to apply
        Returns:
            transformed prompt
        """
        transformed_fields = {
            field.name: transform(value)
            for field in fields(self)
            if field.name != "language"
            and isinstance(value := getattr(self, field.name), str)
        }
        return replace(self, language=language, **transformed_fields)
