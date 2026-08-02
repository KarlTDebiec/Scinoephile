#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for block-level punctuation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, ValidationInfo, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.text import (
    FULL_PUNC_CHARS,
    HALF_PUNC_CHARS,
    RE_HANZI,
    WHITESPACE_CHARS,
    remove_punc_and_whitespace,
)

from .prompt import BlockPunctuationPrompt

__all__ = [
    "BlockPunctuationAnswer",
    "BlockPunctuationQuery",
    "BlockPunctuationSubtitle",
    "BlockPunctuationTestCase",
]


_BASE_PROMPT = BlockPunctuationPrompt()

_LEADING_CLOSING_PUNCTUATION = set(",.!?;:，。！？；：、")
"""Sentence punctuation that must not begin an owned target."""
_HALF_WIDTH_SENTENCE_PUNCTUATION = set(",.!?;:")
"""Half-width sentence punctuation rejected in Hanzi target text."""
_TRAILING_CLOSING_PUNCTUATION = set("'\"')]}>'’”）］｝〉》」』】〕〗〙〛")
"""Closing punctuation allowed after a terminal question mark."""
_STRONG_CANTONESE_INTERROGATIVE_CUES = (
    "係咪",
    "有冇",
    "點解",
    "乜嘢",
    "做咩",
    "邊個",
    "邊度",
    "喺邊",
    "去邊",
    "幾時",
    "幾多",
    "點樣",
)
"""Lexical Cantonese cues that strongly indicate an interrogative."""
_STRONG_CANTONESE_INTERROGATIVE_ENDINGS = ("咩", "嗎", "吗")
"""Sentence-final Cantonese or Chinese interrogative particles."""


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
        owned_indexes = set(self.query.owned_index_range)
        self.answer.changes = [
            change
            for change in self.answer.changes
            if change.index in target_text_by_index and change.index in owned_indexes
        ]
        for change in self.answer.changes:
            expected = remove_punc_and_whitespace(target_text_by_index[change.index])
            received = remove_punc_and_whitespace(change.text)
            if expected != received and len(expected) == len(received):
                source_characters = iter(expected)
                punctuation = FULL_PUNC_CHARS | HALF_PUNC_CHARS | WHITESPACE_CHARS
                change.text = "".join(
                    character
                    if character.isspace() or character in punctuation
                    else next(source_characters)
                    for character in change.text
                )
                received = remove_punc_and_whitespace(change.text)
            if expected != received:
                raise ValueError(
                    self.prompt.target_chars_changed_err(
                        change.index, expected, received
                    )
                )
        return self

    @model_validator(mode="after")
    def validate_output_quality(self, info: ValidationInfo) -> Self:
        """Reject obvious punctuation-layout defects in final owned targets.

        Arguments:
            info: Pydantic validation context
        Returns:
            validated test case
        """
        context = info.context
        if (
            self.answer is None
            or not self.prompt.validate_output_quality
            or (
                isinstance(context, dict)
                and context.get("skip_output_quality_validation") is True
            )
        ):
            return self

        output_by_index = {target.index: target.text for target in self.query.targets}
        output_by_index.update(
            {change.index: change.text for change in self.answer.changes}
        )
        leading_closing_indexes: list[int] = []
        punctuation_only_indexes: list[int] = []
        half_width_by_index: dict[int, str] = {}
        interrogative_indexes: list[int] = []
        guide_by_index = {guide.index: guide.text for guide in self.query.guides}
        for index in self.query.owned_index_range:
            text = output_by_index[index]
            stripped = text.strip()
            if text and not remove_punc_and_whitespace(text):
                punctuation_only_indexes.append(index)
                continue
            if stripped and stripped[0] in _LEADING_CLOSING_PUNCTUATION:
                leading_closing_indexes.append(index)
            if RE_HANZI.search(text):
                half_width_characters = sorted(
                    {
                        character
                        for character_index, character in enumerate(text)
                        if character in _HALF_WIDTH_SENTENCE_PUNCTUATION
                        and RE_HANZI.search(
                            text[:character_index].rstrip()[-1:]
                            + text[character_index + 1 :].lstrip()[:1]
                        )
                    }
                )
                if half_width_characters:
                    half_width_by_index[index] = "".join(half_width_characters)
            target_characters = remove_punc_and_whitespace(
                self.query.targets[index - 1].text
            )
            has_strong_interrogative_cue = any(
                cue in target_characters for cue in _STRONG_CANTONESE_INTERROGATIVE_CUES
            ) or target_characters.endswith(_STRONG_CANTONESE_INTERROGATIVE_ENDINGS)
            if (
                target_characters
                and has_strong_interrogative_cue
                and self._ends_with_question_mark(guide_by_index[index])
                and not any(question_mark in text for question_mark in "?？")
            ):
                interrogative_indexes.append(index)

        errors: list[str] = []
        if leading_closing_indexes:
            indexes = ", ".join(map(str, leading_closing_indexes))
            errors.append(
                self.prompt.leading_closing_punctuation_err_tpl.format(indexes=indexes)
            )
        if punctuation_only_indexes:
            indexes = ", ".join(map(str, punctuation_only_indexes))
            errors.append(
                self.prompt.punctuation_only_target_err_tpl.format(indexes=indexes)
            )
        if half_width_by_index:
            indexes = ", ".join(map(str, half_width_by_index))
            characters = ", ".join(
                f"{index}: {characters!r}"
                for index, characters in half_width_by_index.items()
            )
            errors.append(
                self.prompt.half_width_sentence_punctuation_err_tpl.format(
                    indexes=indexes, characters=characters
                )
            )
        if interrogative_indexes:
            indexes = ", ".join(map(str, interrogative_indexes))
            errors.append(
                self.prompt.interrogative_target_err_tpl.format(indexes=indexes)
            )
        if errors:
            raise ValueError("\n".join(errors))
        return self

    @staticmethod
    def _ends_with_question_mark(text: str) -> bool:
        """Check for a question mark in the final sentence-punctuation cluster.

        Arguments:
            text: subtitle text
        Returns:
            whether the final sentence mark is a question mark
        """
        stripped = text.rstrip()
        while stripped and stripped[-1] in _TRAILING_CLOSING_PUNCTUATION:
            stripped = stripped[:-1].rstrip()
        terminal_marks = ""
        while stripped and stripped[-1] in "!?！？":
            terminal_marks += stripped[-1]
            stripped = stripped[:-1]
        return "?" in terminal_marks or "？" in terminal_marks
