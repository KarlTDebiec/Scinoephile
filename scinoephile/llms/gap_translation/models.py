#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for gap-translation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle

from .prompt import GapTranslationPrompt

__all__ = [
    "GapTranslationAnswer",
    "GapTranslationQuery",
    "GapTranslationSubtitle",
    "GapTranslationTestCase",
]


_BASE_PROMPT = GapTranslationPrompt()


class GapTranslationSubtitle(TestCaseSubtitle):
    """Indexed subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class GapTranslationQuery(Query):
    """Sparse targets and complete guides for gap translation."""

    prompt: ClassVar[GapTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    targets: list[GapTranslationSubtitle]
    """Existing target subtitles indexed by guide position."""
    guides: list[GapTranslationSubtitle] = Field(min_length=1)
    """Complete guide subtitles in index order."""

    @model_validator(mode="after")
    def validate_guide_indices(self) -> Self:
        """Ensure guide indexes are consecutive, ordered, and begin at one."""
        indexes = [guide.index for guide in self.guides]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        return self

    @model_validator(mode="after")
    def validate_target_indices(self) -> Self:
        """Ensure target indexes are ordered, unique, in range, and have a gap."""
        target_indexes = [target.index for target in self.targets]
        if target_indexes != sorted(set(target_indexes)):
            raise ValueError(self.prompt.target_indices_err)

        guide_indexes = {guide.index for guide in self.guides}
        if not set(target_indexes) <= guide_indexes:
            raise ValueError(self.prompt.target_index_missing_err)
        if set(target_indexes) == guide_indexes:
            raise ValueError(self.prompt.target_gap_missing_err)
        return self


class GapTranslationAnswer(Answer):
    """Translations for every missing target index."""

    prompt: ClassVar[GapTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    outputs: list[GapTranslationSubtitle]
    """Translated subtitles in ascending target-index order."""

    @model_validator(mode="after")
    def validate_output_indices(self) -> Self:
        """Ensure output indexes are unique and in ascending order."""
        indexes = [output.index for output in self.outputs]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.output_indices_err)
        return self


class GapTranslationTestCase(TestCase):
    """Gap-translation query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[GapTranslationQuery]] = GapTranslationQuery
    """Query model class."""
    answer_cls: ClassVar[type[GapTranslationAnswer]] = GapTranslationAnswer
    """Answer model class."""
    prompt: ClassVar[GapTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: GapTranslationQuery
    """Sparse targets and complete guides."""
    answer: GapTranslationAnswer | None = None
    """Translations for target gaps, if available."""

    @model_validator(mode="after")
    def validate_output_correspondence(self) -> Self:
        """Ensure outputs exactly fill the guide indexes absent from targets.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        target_indexes = {target.index for target in self.query.targets}
        expected_output_indexes = [
            guide.index
            for guide in self.query.guides
            if guide.index not in target_indexes
        ]
        output_indexes = [output.index for output in self.answer.outputs]
        if output_indexes != expected_output_indexes:
            raise ValueError(self.prompt.output_indices_mismatch_err)
        return self
