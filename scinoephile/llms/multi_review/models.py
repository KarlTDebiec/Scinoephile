#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for multi-source review test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.llms.models import LLMModel
from scinoephile.core.text import remove_punc_and_whitespace

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

        if not self.prompt.boundary_aware:
            supported_indexes = {
                subtitle.index
                for source in self.query.sources
                for subtitle in source.subtitles
            }
            for output in self.answer.outputs:
                if output.index not in supported_indexes and output.text:
                    raise ValueError(self.prompt.unsupported_output_err(output.index))
            return self

        source_text_by_index = [
            {
                subtitle.index: remove_punc_and_whitespace(subtitle.text)
                for subtitle in source.subtitles
            }
            for source in self.query.sources
        ]
        for output in self.answer.outputs:
            output_text = remove_punc_and_whitespace(output.text)
            if output_text and not self._has_local_source_support(
                source_text_by_index, output.index, output_text
            ):
                raise ValueError(self.prompt.unsupported_output_err(output.index))

        conflict = self._get_conflicting_boundary_duplication()
        if conflict is not None:
            one_idx, two_idx, fragment = conflict
            raise ValueError(
                self.prompt.conflicting_boundary_duplication_err(
                    one_idx, two_idx, fragment
                )
            )
        return self

    def _get_conflicting_boundary_duplication(self) -> tuple[int, int, str] | None:
        """Get output duplication caused by conflicting source boundaries.

        Returns:
            first index, second index, and duplicated normalized fragment, or None
        """
        assert self.answer is not None
        source_text_by_index = [
            {
                subtitle.index: remove_punc_and_whitespace(subtitle.text)
                for subtitle in source.subtitles
            }
            for source in self.query.sources
        ]
        guide_text_by_index = {
            guide.index: remove_punc_and_whitespace(guide.text)
            for guide in self.query.guides
        }
        normalized_outputs = [
            remove_punc_and_whitespace(output.text) for output in self.answer.outputs
        ]
        for one, two, one_text, two_text in zip(
            self.answer.outputs[:-1],
            self.answer.outputs[1:],
            normalized_outputs[:-1],
            normalized_outputs[1:],
            strict=True,
        ):
            if not one_text or not two_text:
                continue
            if len(one_text) <= len(two_text):
                fragment = one_text
            else:
                fragment = two_text
            if (
                len(fragment) < self.prompt.minimum_duplicate_fragment_characters
                or fragment not in one_text
                or fragment not in two_text
            ):
                continue

            one_guide = guide_text_by_index[one.index]
            two_guide = guide_text_by_index[two.index]
            if one_guide == two_guide:
                continue

            source_pairs = [
                (source_text.get(one.index, ""), source_text.get(two.index, ""))
                for source_text in source_text_by_index
            ]
            if any(
                fragment in source_one and fragment in source_two
                for source_one, source_two in source_pairs
            ):
                continue
            supports_one_only = any(
                fragment in source_one and fragment not in source_two
                for source_one, source_two in source_pairs
            )
            supports_two_only = any(
                fragment not in source_one and fragment in source_two
                for source_one, source_two in source_pairs
            )
            if supports_one_only and supports_two_only:
                return one.index, two.index, fragment
        return None

    @staticmethod
    def _has_local_source_support(
        source_text_by_index: list[dict[int, str]], index: int, text: str
    ) -> bool:
        """Whether an output text has support at its index or a direct neighbor.

        Arguments:
            source_text_by_index: normalized source texts keyed by subtitle index
            index: one-based output subtitle index
            text: normalized output text
        Returns:
            whether a nearby source shares a one- or two-character fragment
        """
        nearby_source_texts = [
            source_texts.get(nearby_index, "")
            for source_texts in source_text_by_index
            for nearby_index in range(index - 1, index + 2)
        ]
        if len(text) == 1:
            return any(nearby_source_texts)

        fragment_length = min(2, len(text))
        fragments = {
            text[start : start + fragment_length]
            for start in range(len(text) - fragment_length + 1)
        }
        return any(
            fragment in source_text
            for source_text in nearby_source_texts
            for fragment in fragments
        )
