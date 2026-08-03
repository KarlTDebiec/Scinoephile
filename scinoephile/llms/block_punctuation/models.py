#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for block-level punctuation test cases."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, Self

from pydantic import Field, ValidationInfo, field_validator, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.llms.models import LLMModel
from scinoephile.core.text import (
    FULL_PUNC_CHARS,
    HALF_PUNC_CHARS,
    RE_HANZI,
    WHITESPACE_CHARS,
    remove_punc_and_whitespace,
)

from .prompt import BlockPunctuationPrompt, PositionalBlockPunctuationPrompt

__all__ = [
    "BlockPunctuationAnswer",
    "BlockPunctuationQuery",
    "BlockPunctuationSubtitle",
    "BlockPunctuationTestCase",
    "PositionalBlockPunctuationAnswer",
    "PositionalBlockPunctuationChange",
    "PositionalBlockPunctuationEdit",
    "PositionalBlockPunctuationTestCase",
    "PositionalBlockPunctuationTarget",
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


class PositionalBlockPunctuationEdit(LLMModel):
    """Punctuation inserted at one position on an immutable target string."""

    prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationPrompt()
    )
    """Text and field aliases for positional punctuation."""
    position: int = Field(ge=0)
    """Zero-based insertion position on the target string."""
    punctuation: str = Field(min_length=1)
    """Punctuation and whitespace inserted at that position."""

    @field_validator("punctuation")
    @classmethod
    def validate_punctuation(cls, value: str) -> str:
        """Ensure an insertion contains no lexical characters."""
        allowed = FULL_PUNC_CHARS | HALF_PUNC_CHARS | WHITESPACE_CHARS
        if any(character not in allowed for character in value):
            raise ValueError(cls.prompt.edit_punctuation_invalid_err)
        return value


class PositionalBlockPunctuationTarget(BlockPunctuationSubtitle):
    """Immutable punctuation target with an explicit character count."""

    prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationPrompt()
    )
    """Text and field aliases for positional punctuation."""
    character_count: int = Field(ge=0)
    """Exact Unicode-character count of the target text."""

    @model_validator(mode="before")
    @classmethod
    def populate_character_count(cls, value: object) -> object:
        """Populate deterministic character-count metadata when omitted."""
        if not isinstance(value, Mapping):
            return value
        character_count_keys = {"character_count", cls.prompt.character_count}
        if any(key in value for key in character_count_keys):
            return value
        text = value.get(cls.prompt.text, value.get("text"))
        if not isinstance(text, str):
            return value
        updated_value = dict(value)
        updated_value[cls.prompt.character_count] = len(text)
        return updated_value

    @model_validator(mode="after")
    def validate_character_count(self) -> Self:
        """Ensure the supplied count exactly describes the target text."""
        if self.character_count != len(self.text):
            raise ValueError(self.prompt.character_count_err)
        return self


class PositionalBlockPunctuationChange(LLMModel):
    """Sparse punctuation insertions for one target subtitle."""

    prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationPrompt()
    )
    """Text and field aliases for positional punctuation."""
    index: int = Field(ge=1)
    """One-based target index."""
    edits: list[PositionalBlockPunctuationEdit] = Field(min_length=1)
    """Ordered punctuation insertion operations."""

    @model_validator(mode="after")
    def validate_edit_positions(self) -> Self:
        """Ensure insertion positions are ordered and unique."""
        positions = [edit.position for edit in self.edits]
        if positions != sorted(set(positions)):
            raise ValueError(self.prompt.edit_positions_err)
        return self


class PositionalBlockPunctuationAnswer(BlockPunctuationAnswer):
    """Sparse positional punctuation insertions for one query window."""

    prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationPrompt()
    )
    """Text and field aliases for positional punctuation."""
    changes: list[PositionalBlockPunctuationChange] = Field(default_factory=list)
    """Only target subtitles requiring punctuation insertions."""


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
        return self.answer_cls()

    def get_output_texts(self) -> list[str]:
        """Overlay sparse full-text punctuation replacements.

        Returns:
            complete punctuated target text by index
        """
        output = [target.text for target in self.query.targets]
        if self.answer is not None:
            for change in self.answer.changes:
                output[change.index - 1] = change.text
        return output

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

        output_by_index = dict(enumerate(self.get_output_texts(), 1))
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


class PositionalBlockPunctuationTestCase(BlockPunctuationTestCase):
    """Block-punctuation query using sparse positional insertions."""

    answer_cls: ClassVar[type[PositionalBlockPunctuationAnswer]] = (
        PositionalBlockPunctuationAnswer
    )
    """Answer model class."""
    prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationPrompt()
    )
    """Text and field aliases for positional punctuation."""
    answer: PositionalBlockPunctuationAnswer | None = None
    """Sparse positional punctuation insertions, if available."""

    @model_validator(mode="after")
    def validate_changed_subtitles(self) -> Self:
        """Keep owned changes and validate insertion positions against targets."""
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
            target_length = len(target_text_by_index[change.index])
            for edit in change.edits:
                if edit.position > target_length:
                    raise ValueError(
                        self.prompt.edit_position_invalid_err_tpl.format(
                            index=change.index,
                            position=edit.position,
                            length=target_length,
                        )
                    )
        return self

    def get_no_op_answer(self) -> PositionalBlockPunctuationAnswer:
        """Get an empty positional-insertion answer."""
        return self.answer_cls()

    def get_output_texts(self) -> list[str]:
        """Apply sparse punctuation insertions without rewriting target text."""
        output = [target.text for target in self.query.targets]
        if self.answer is None:
            return output
        for change in self.answer.changes:
            target = output[change.index - 1]
            insertion_by_position = {
                edit.position: edit.punctuation for edit in change.edits
            }
            pieces: list[str] = []
            for position, character in enumerate(target):
                pieces.append(insertion_by_position.get(position, ""))
                pieces.append(character)
            pieces.append(insertion_by_position.get(len(target), ""))
            output[change.index - 1] = "".join(pieces)
        return output
