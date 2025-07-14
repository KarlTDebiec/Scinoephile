# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translate README files using an LLM."""

from __future__ import annotations

from textwrap import dedent

from scinoephile.core.abcs import LLMProvider, LLMQueryer
from scinoephile.openai import OpenAIProvider
from scinoephile.translation.models import (
    ReadmeTranslationAnswer,
    ReadmeTranslationQuery,
)
from scinoephile.translation.testing import ReadmeTranslationTestCase


class ReadmeTranslator(
    LLMQueryer[
        ReadmeTranslationQuery,
        ReadmeTranslationAnswer,
        ReadmeTranslationTestCase,
    ]
):
    """Translate README files using an LLM."""

    def __init__(
        self,
        model: str = "gpt-4o",
        provider: LLMProvider | None = None,
        cache_dir_path: str | None = None,
    ) -> None:
        """Initialize.

        Arguments:
            model: Model to use
            provider: LLM provider to query
            cache_dir_path: Directory in which to cache
        """
        super().__init__(
            model=model,
            cache_dir_path=cache_dir_path,
            provider=provider or OpenAIProvider(),
        )

    @property
    def answer_cls(self) -> type[ReadmeTranslationAnswer]:
        """Answer class."""
        return ReadmeTranslationAnswer

    @property
    def answer_example(self) -> ReadmeTranslationAnswer:
        """Example answer."""
        return ReadmeTranslationAnswer(readme="Translated README")

    @property
    def answer_template(self) -> str:
        """Answer template."""
        return "README:\n{readme}\n"

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return dedent(
            """
                You are a helpful assistant that translates the Scinoephile README.
                Use the English README as the source of truth. When available, use the
                previous translation to preserve style and terminology. Your response
                must be a JSON object with the following structure:
                """
        ).strip()

    @property
    def query_cls(self) -> type[ReadmeTranslationQuery]:
        """Query class."""
        return ReadmeTranslationQuery

    @property
    def query_template(self) -> str:
        """Query template."""
        return (
            "English README:\n{english_readme}\n"
            "Previous translation:\n{chinese_readme}\n"
            "Target language: {language}\n"
        )

    @property
    def test_case_cls(self) -> type[ReadmeTranslationTestCase]:
        """Test case class."""
        return ReadmeTranslationTestCase

    def translate(
        self,
        english_readme: str,
        chinese_readme: str,
        language: str,
    ) -> str:
        """Translate README.

        Arguments:
            english_readme: Current English README
            chinese_readme: Previous README in the target language
            language: Target language, ``"zhongwen"`` or ``"yuewen"``
        Returns:
            Translated README
        """
        query = ReadmeTranslationQuery(
            english_readme=english_readme,
            chinese_readme=chinese_readme,
            language=language,
        )
        answer = self(query)
        return answer.readme
