#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates README from English to Chinese."""

from __future__ import annotations

from scinoephile.core.abcs import LLMQueryer
from scinoephile.translation.models import (
    ReadmeTranslationAnswer,
    ReadmeTranslationQuery,
)
from scinoephile.translation.testing import ReadmeTranslationTestCase


class ReadmeTranslator(
    LLMQueryer[
        ReadmeTranslationQuery, ReadmeTranslationAnswer, ReadmeTranslationTestCase
    ]
):
    """Translates README from English to Chinese."""

    @property
    def answer_cls(self) -> type[ReadmeTranslationAnswer]:
        """Answer class."""
        return ReadmeTranslationAnswer

    @property
    def answer_example(self) -> ReadmeTranslationAnswer:
        """Example answer."""
        return ReadmeTranslationAnswer(
            updated_chinese="Updated Chinese README",
        )

    @property
    def answer_template(self) -> str:
        """Answer template."""
        return "Updated Chinese README:\n{updated_chinese}\n"

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that updates the Chinese version of a README.
        Use the updated English README as the source of truth.
        When appropriate, reference the out-of-date Chinese README to guide style and
        terminology.
        Use traditional Chinese characters.
        Your response must be a JSON object with the following structure:
        """

    @property
    def query_cls(self) -> type[ReadmeTranslationQuery]:
        """Query class."""
        return ReadmeTranslationQuery

    @property
    def query_template(self) -> str:
        """Query template."""
        return (
            "Updated English README:\n{updated_english}\n"
            "Out-of-date Chinese README:\n{outdated_chinese}\n"
            "Chinese language: {language}\n"
        )

    @property
    def test_case_cls(self) -> type[ReadmeTranslationTestCase]:
        """Test case class."""
        return ReadmeTranslationTestCase
