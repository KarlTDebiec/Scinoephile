#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for multi-source review test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.llms.models import LLMModel

from .prompt import MultiReviewPrompt

__all__ = [
    "MultiReviewAnswer",
    "MultiReviewQuery",
    "MultiReviewSource",
    "MultiReviewSubtitle",
    "MultiReviewTestCase",
]


_BASE_PROMPT = MultiReviewPrompt()


class MultiReviewSubtitle(TestCaseSubtitle):
    """Guide-indexed subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class MultiReviewSource(LLMModel):
    """Named sparse subtitle source."""

    name: str = Field(min_length=1)
    """Stable source name."""
    subtitles: list[MultiReviewSubtitle]
    """Sparse subtitles indexed by guide position."""


class MultiReviewQuery(Query):
    """Equal-status subtitle sources and a complete guide for one passage."""

    prompt: ClassVar[MultiReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    sources: list[MultiReviewSource] = Field(min_length=2)
    """Named equal-status subtitle sources."""
    guides: list[MultiReviewSubtitle] = Field(min_length=1)
    """Complete guide subtitles in index order."""

    @model_validator(mode="after")
    def validate_guide_indices(self) -> Self:
        """Ensure guide indexes are consecutive, ordered, and begin at one."""
        indexes = [guide.index for guide in self.guides]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        return self

    @model_validator(mode="after")
    def validate_source_count(self) -> Self:
        """Ensure at least two subtitle sources are present."""
        if len(self.sources) < 2:
            raise ValueError(self.prompt.source_count_err)
        return self

    @model_validator(mode="after")
    def validate_source_indices(self) -> Self:
        """Ensure source indexes are ordered, unique, and present in the guide."""
        guide_indexes = {guide.index for guide in self.guides}
        for source in self.sources:
            indexes = [subtitle.index for subtitle in source.subtitles]
            if indexes != sorted(set(indexes)):
                raise ValueError(self.prompt.source_indices_err)
            if not set(indexes) <= guide_indexes:
                raise ValueError(self.prompt.source_index_missing_err)
        return self

    @model_validator(mode="after")
    def validate_source_names(self) -> Self:
        """Ensure source names are nonblank and unique."""
        names = [source.name for source in self.sources]
        stripped_names = [name.strip() for name in names]
        if any(not name for name in stripped_names) or len(set(stripped_names)) != len(
            names
        ):
            raise ValueError(self.prompt.source_name_err)
        return self


class MultiReviewAnswer(Answer):
    """Complete reviewed outputs corresponding to guide subtitles."""

    prompt: ClassVar[MultiReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    outputs: list[MultiReviewSubtitle] = Field(min_length=1)
    """Reviewed outputs in guide-index order."""

    @model_validator(mode="after")
    def validate_output_indices(self) -> Self:
        """Ensure output indexes are consecutive, ordered, and begin at one."""
        indexes = [output.index for output in self.outputs]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.output_indices_err)
        return self


class MultiReviewTestCase(TestCase):
    """Multi-review query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[MultiReviewQuery]] = MultiReviewQuery
    """Query model class."""
    answer_cls: ClassVar[type[MultiReviewAnswer]] = MultiReviewAnswer
    """Answer model class."""
    prompt: ClassVar[MultiReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: MultiReviewQuery
    """Equal-status subtitle sources and complete guide."""
    answer: MultiReviewAnswer | None = None
    """Complete reviewed outputs, if available."""

    def get_no_op_answer(self) -> MultiReviewAnswer:
        """Get an answer selecting the first available source at each index.

        Returns:
            guide-indexed outputs without synthesized text
        """
        source_text_by_index = [
            {subtitle.index: subtitle.text for subtitle in source.subtitles}
            for source in self.query.sources
        ]
        outputs: list[MultiReviewSubtitle] = []
        for guide in self.query.guides:
            text = ""
            for source in source_text_by_index:
                if guide.index in source:
                    text = source[guide.index]
                    break
            outputs.append(MultiReviewSubtitle(index=guide.index, text=text))
        return MultiReviewAnswer(outputs=outputs)

    @model_validator(mode="after")
    def validate_output_correspondence(self) -> Self:
        """Ensure outputs match guides and unsupported positions remain blank."""
        if self.answer is None:
            return self

        guide_indexes = [guide.index for guide in self.query.guides]
        output_indexes = [output.index for output in self.answer.outputs]
        if output_indexes != guide_indexes:
            raise ValueError(self.prompt.output_correspondence_err)

        supported_indexes = {
            subtitle.index
            for source in self.query.sources
            for subtitle in source.subtitles
        }
        for output in self.answer.outputs:
            if output.index not in supported_indexes and output.text:
                raise ValueError(self.prompt.unsupported_output_err(output.index))
        return self
