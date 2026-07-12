#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for punctuation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import (
    Answer,
    Manager,
    PromptModelField,
    Query,
    TestCase,
)

from .models import PunctuationAnswer, PunctuationQuery, PunctuationTestCase
from .prompt import PunctuationPrompt

__all__ = ["PunctuationManager"]


class PunctuationManager(Manager):
    """Factories for punctuation LLM classes."""

    operation: ClassVar[str] = "punctuation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PunctuationPrompt] = PunctuationTestCase.prompt
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = PunctuationTestCase
    """Static test-case model defining punctuation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        return cls.create_prompt_model(
            PunctuationAnswer,
            prompt,
            {
                "output": PromptModelField(
                    alias=prompt.output,
                    description=prompt.output_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        return cls.create_prompt_model(
            PunctuationQuery,
            prompt,
            {
                "subtitles": PromptModelField(
                    alias=prompt.src_1,
                    description=prompt.src_1_desc,
                ),
                "guide": PromptModelField(
                    alias=prompt.src_2,
                    description=prompt.src_2_desc,
                ),
            },
        )
