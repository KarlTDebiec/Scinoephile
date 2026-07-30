#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for block-level delineation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle

from .prompt import BlockDelineationPrompt

__all__ = [
    "BlockDelineationAnswer",
    "BlockDelineationQuery",
    "BlockDelineationSubtitle",
    "BlockDelineationTestCase",
]


_BASE_PROMPT = BlockDelineationPrompt()


class BlockDelineationSubtitle(TestCaseSubtitle):
    """Indexed block subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class BlockDelineationQuery(Query):
    """Complete guides and timing-based initial targets for one query window."""

    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    guides: list[BlockDelineationSubtitle] = Field(min_length=1)
    """Complete guide subtitles in index order."""
    targets: list[BlockDelineationSubtitle] = Field(min_length=1)
    """Complete initial target assignment in guide-index order."""
    first_owned_index: int | None = Field(default=None, ge=1)
    """First local target index whose following boundary this window owns."""
    last_owned_index: int | None = Field(default=None, ge=1)
    """Last local target index whose following boundary this window owns."""

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


class BlockDelineationAnswer(Answer):
    """Sparse target replacements for one query window."""

    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    changes: list[BlockDelineationSubtitle] = Field(default_factory=list)
    """Only target subtitles whose text must change."""

    @model_validator(mode="after")
    def validate_change_indices(self) -> Self:
        """Ensure sparse change indexes are ordered and unique."""
        indexes = [change.index for change in self.changes]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.change_indices_err)
        return self


class BlockDelineationTestCase(TestCase):
    """Block-delineation query and optional sparse answer."""

    query_cls: ClassVar[type[BlockDelineationQuery]] = BlockDelineationQuery
    """Query model class."""
    answer_cls: ClassVar[type[BlockDelineationAnswer]] = BlockDelineationAnswer
    """Answer model class."""
    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    query: BlockDelineationQuery
    """Complete guide and initial target block."""
    answer: BlockDelineationAnswer | None = None
    """Sparse delineation changes, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether boundaries change.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is not None and self.answer.changes:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    def get_no_op_answer(self) -> BlockDelineationAnswer:
        """Get a sparse answer that preserves the initial assignment.

        Returns:
            empty sparse-change answer
        """
        return BlockDelineationAnswer()

    @model_validator(mode="after")
    def validate_reconstructed_block(self) -> Self:
        """Ensure sparse changes preserve all target characters in order."""
        if self.answer is None:
            return self

        target_text_by_index = {
            target.index: target.text for target in self.query.targets
        }
        change_indexes = {change.index for change in self.answer.changes}
        if not change_indexes <= set(target_text_by_index):
            raise ValueError(self.prompt.change_index_missing_err)

        output_text_by_index = dict(target_text_by_index)
        output_text_by_index.update(
            {change.index: change.text for change in self.answer.changes}
        )
        expected = "".join(target_text_by_index.values())
        received = "".join(output_text_by_index.values())
        if expected != received:
            mismatch_offset = next(
                (
                    offset
                    for offset, (expected_char, received_char) in enumerate(
                        zip(expected, received, strict=False)
                    )
                    if expected_char != received_char
                ),
                min(len(expected), len(received)),
            )
            cumulative_length = 0
            mismatch_index = len(output_text_by_index)
            for index, text in output_text_by_index.items():
                cumulative_length += len(text)
                if mismatch_offset < cumulative_length:
                    mismatch_index = index
                    break
            raise ValueError(
                self.prompt.target_chars_changed_err(mismatch_index, expected, received)
            )
        return self
