#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for block-level punctuation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.text import remove_punc_and_whitespace

from .prompt import BlockPunctuationPrompt

__all__ = [
    "BlockPunctuationAnswer",
    "BlockPunctuationQuery",
    "BlockPunctuationSubtitle",
    "BlockPunctuationTestCase",
]


_BASE_PROMPT = BlockPunctuationPrompt()


class BlockPunctuationSubtitle(TestCaseSubtitle):
    """Indexed block subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class BlockPunctuationQuery(Query):
    """Complete guides and delineated targets for one query window."""

    prompt: ClassVar[BlockPunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level punctuation."""
    guides: list[BlockPunctuationSubtitle] = Field(min_length=1)
    """Complete guide subtitles in index order."""
    targets: list[BlockPunctuationSubtitle] = Field(min_length=1)
    """Complete delineated target subtitles in guide-index order."""
    first_owned_index: int | None = Field(default=None, ge=1)
    """First local target index owned by this query window."""
    last_owned_index: int | None = Field(default=None, ge=1)
    """Last local target index owned by this query window."""

    @property
    def owned_index_range(self) -> range:
        """Get the inclusive local target-index range owned by this query."""
        first_index = self.first_owned_index or 1
        last_index = self.last_owned_index or len(self.targets)
        return range(first_index, last_index + 1)

    @model_validator(mode="after")
    def validate_indices(self) -> Self:
        """Ensure guide and target indexes correspond exactly."""
        guide_indexes = [guide.index for guide in self.guides]
        if guide_indexes != list(range(1, len(guide_indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        target_indexes = [target.index for target in self.targets]
        if target_indexes != guide_indexes:
            raise ValueError(self.prompt.target_indices_err)
        if (self.first_owned_index is None) != (self.last_owned_index is None):
            raise ValueError(self.prompt.owned_indices_err)
        if self.first_owned_index is not None and (
            self.last_owned_index is None
            or self.first_owned_index > self.last_owned_index
            or self.last_owned_index > len(guide_indexes)
        ):
            raise ValueError(self.prompt.owned_indices_err)
        return self


class BlockPunctuationAnswer(Answer):
    """Sparse punctuation replacements for one query window."""

    prompt: ClassVar[BlockPunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level punctuation."""
    changes: list[BlockPunctuationSubtitle] = Field(default_factory=list)
    """Only target subtitles whose punctuation must change."""

    @model_validator(mode="after")
    def validate_change_indices(self) -> Self:
        """Ensure sparse change indexes are ordered and unique."""
        indexes = [change.index for change in self.changes]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.change_indices_err)
        return self


class BlockPunctuationTestCase(TestCase):
    """Block-punctuation query and optional sparse answer."""

    query_cls: ClassVar[type[BlockPunctuationQuery]] = BlockPunctuationQuery
    """Query model class."""
    answer_cls: ClassVar[type[BlockPunctuationAnswer]] = BlockPunctuationAnswer
    """Answer model class."""
    prompt: ClassVar[BlockPunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level punctuation."""
    query: BlockPunctuationQuery
    """Complete guide and delineated target block."""
    answer: BlockPunctuationAnswer | None = None
    """Sparse punctuation changes, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether punctuation changes.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is not None and self.answer.changes:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    def get_no_op_answer(self) -> BlockPunctuationAnswer:
        """Get a sparse answer that preserves delineated target text.

        Returns:
            empty sparse-change answer
        """
        return BlockPunctuationAnswer()

    @model_validator(mode="after")
    def validate_changed_subtitles(self) -> Self:
        """Ensure each sparse change modifies only punctuation and whitespace."""
        if self.answer is None:
            return self

        target_text_by_index = {
            target.index: target.text for target in self.query.targets
        }
        change_indexes = {change.index for change in self.answer.changes}
        if not change_indexes <= set(target_text_by_index):
            raise ValueError(self.prompt.change_index_missing_err)
        if not change_indexes <= set(self.query.owned_index_range):
            raise ValueError(self.prompt.change_index_not_owned_err)

        for change in self.answer.changes:
            expected = remove_punc_and_whitespace(target_text_by_index[change.index])
            received = remove_punc_and_whitespace(change.text)
            if expected != received:
                raise ValueError(
                    self.prompt.target_chars_changed_err(
                        change.index, expected, received
                    )
                )
        return self
