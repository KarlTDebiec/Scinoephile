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
    "PromptLocalizationKwargs",
]


class PromptLocalizationKwargs(TypedDict):
    """Shared localization fields accepted by all prompt types."""

    schema_intro: str
    """Text preceding schema description."""
    few_shot_intro: str
    """Text preceding few-shot examples."""
    few_shot_query_intro: str
    """Text preceding each few-shot example query."""
    few_shot_answer_intro: str
    """Text preceding each few-shot expected answer."""
    answer_invalid_pre: str
    """Text preceding answer validation errors."""
    answer_invalid_post: str
    """Text following answer validation errors."""
    difficulty_description: str
    """Description of 'difficulty' field."""
    few_shot_description: str
    """Description of 'few_shot' field."""
    verified_description: str
    """Description of 'verified' field."""
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
    schema_intro: str = ""
    """Text preceding schema description."""
    few_shot_intro: str = ""
    """Text preceding few-shot examples."""
    few_shot_query_intro: str = ""
    """Text preceding each few-shot example query."""
    few_shot_answer_intro: str = ""
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: str = ""
    """Text preceding answer validation errors."""
    answer_invalid_post: str = ""
    """Text following answer validation errors."""

    # Test case field descriptions
    difficulty_description: str = (
        "Difficulty level of the test case, used for filtering."
    )
    """Description of 'difficulty' field."""
    few_shot_description: str = "Whether to include test case in few-shot examples."
    """Description of 'few_shot' field."""
    verified_description: str = (
        "Whether to include test case in the verified answers cache."
    )
    """Description of 'verified' field."""

    # Test case validation errors
    test_case_invalid_pre: str = ""
    """Text preceding test case validation errors."""
    test_case_invalid_post: str = ""
    """Text following test case validation errors."""

    @property
    def localization_kwargs(self) -> PromptLocalizationKwargs:
        """Get shared localization fields as prompt-construction keywords."""
        return {
            "schema_intro": self.schema_intro,
            "few_shot_intro": self.few_shot_intro,
            "few_shot_query_intro": self.few_shot_query_intro,
            "few_shot_answer_intro": self.few_shot_answer_intro,
            "answer_invalid_pre": self.answer_invalid_pre,
            "answer_invalid_post": self.answer_invalid_post,
            "difficulty_description": self.difficulty_description,
            "few_shot_description": self.few_shot_description,
            "verified_description": self.verified_description,
            "test_case_invalid_pre": self.test_case_invalid_pre,
            "test_case_invalid_post": self.test_case_invalid_post,
        }

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
                "language": self.language.tag,
                "type": type(self).__name__,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = hashlib.sha256(payload_json.encode()).hexdigest()[:12]
        language_name = self.language.tag.replace("-", "_")
        return f"{type(self).__name__}_{language_name}_{digest}"

    def transformed(
        self,
        language: Language,
        transform: Callable[[str], str],
    ) -> Self:
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
