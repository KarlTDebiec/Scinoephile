#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for transcription test cases."""

from __future__ import annotations

import unicodedata
from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase
from scinoephile.core.llms.models import LLMModel

from .prompt import TranscriptionPrompt
from .validation import get_transcription_validation

__all__ = [
    "TranscriptionAnswer",
    "TranscriptionQuery",
    "TranscriptionSource",
    "TranscriptionSubtitle",
    "TranscriptionTestCase",
]


_BASE_PROMPT = TranscriptionPrompt()

_SPEAKER_CHARACTERS = frozenset(
    {"　", "・", "＊"} | {chr(ord("Ａ") + index) for index in range(26)}
)
"""Characters permitted in the speaker annotation row."""
_LANGUAGE_CHARACTERS = frozenset(
    {"　", "・", "粵", "普", "英", "日", "韓", "外"}
    | {chr(ord("Ａ") + index) for index in range(26)}
)
"""Characters permitted in the spoken-language annotation row."""


class TranscriptionSource(LLMModel):
    """One named ASR row within a complete request alignment."""

    name: str = Field(min_length=1)
    """Stable ASR source name."""
    text: str = Field(min_length=1, max_length=10_000)
    """Column-aligned ASR characters and gaps."""


class TranscriptionQuery(Query):
    """Reference-free aligned ASR and speaker evidence for one request."""

    prompt: ClassVar[TranscriptionPrompt] = _BASE_PROMPT
    """Text and field aliases for transcription."""
    sources: list[TranscriptionSource] = Field(min_length=1)
    """One or more named equal-status ASR source rows."""
    speaker: str = Field(min_length=1, max_length=10_000)
    """Column-aligned speaker and voice-activity annotations."""
    language: str | None = Field(default=None, min_length=1, max_length=10_000)
    """Column-aligned spoken-language annotations, when available."""
    singing: str | None = Field(default=None, min_length=1, max_length=10_000)
    """Column-aligned singing annotations, when available."""
    music: str | None = Field(default=None, min_length=1, max_length=10_000)
    """Column-aligned music annotations, when available."""

    @model_validator(mode="after")
    def validate_rows(self) -> Self:
        """Ensure the request contains a valid equal-width ASR alignment."""
        # Source names identify independent ASR inputs, not reference guides
        names = [source.name.strip() for source in self.sources]
        if any(not name for name in names) or len(set(names)) != len(names):
            raise ValueError(self.prompt.source_name_err)
        if any(name.casefold() in {"guide", "reference"} for name in names):
            raise ValueError(self.prompt.reference_source_err)

        # Every row shares one alignment-column grid without subtitle boundaries
        rows = (
            self.speaker,
            *(source.text for source in self.sources),
            *(
                annotation
                for annotation in (self.language, self.singing, self.music)
                if annotation is not None
            ),
        )
        if len({len(row) for row in rows}) != 1:
            raise ValueError(self.prompt.row_length_err)
        if any("｜" in row for row in rows):
            raise ValueError(self.prompt.reference_marker_err)

        # Validate the compact alphabets used by annotation rows
        if any(character not in _SPEAKER_CHARACTERS for character in self.speaker):
            raise ValueError(self.prompt.speaker_character_err)
        if self.language is not None and any(
            character not in _LANGUAGE_CHARACTERS for character in self.language
        ):
            raise ValueError(self.prompt.language_character_err)
        for annotation, marker in ((self.singing, "唱"), (self.music, "樂")):
            if annotation is not None and any(
                character not in {"　", "・", marker} for character in annotation
            ):
                raise ValueError(self.prompt.audio_event_character_err)

        # At least one ASR source must contain text beyond gaps and pauses
        if not any(
            character not in {"　", "・"}
            for source in self.sources
            for character in source.text
        ):
            raise ValueError(self.prompt.transcript_empty_err)
        return self


class TranscriptionSubtitle(LLMModel):
    """One ordered consensus subtitle derived from answer text."""

    index: int = Field(ge=1)
    """One-based subtitle index."""
    text: str = Field(min_length=1, max_length=1000)
    """Complete consensus subtitle text."""


class TranscriptionAnswer(Answer):
    """Consensus text containing inline subtitle boundaries."""

    max_subtitle_characters: ClassVar[int] = 20
    """Maximum nonwhitespace characters permitted in one subtitle."""
    prompt: ClassVar[TranscriptionPrompt] = _BASE_PROMPT
    """Text and field aliases for transcription."""
    text: str = Field(max_length=20_000)
    """Consensus transcript with boundaries, or empty when evidence is insufficient."""

    @property
    def subtitles(self) -> list[TranscriptionSubtitle]:
        """Get consensus subtitles deterministically from the boundary markers."""
        if not self.text:
            return []
        return [
            TranscriptionSubtitle(index=index, text=text)
            for index, text in enumerate(self.text[:-1].split("｜"), start=1)
        ]

    @property
    def transcript(self) -> str:
        """Get the complete consensus transcript."""
        return "".join(subtitle.text for subtitle in self.subtitles)

    @model_validator(mode="after")
    def validate_text(self) -> Self:
        """Ensure boundary markers form nonblank, annotation-free subtitles."""
        if not self.text:
            return self

        # Every subtitle must contain text and end with a boundary
        if not self.text.endswith("｜"):
            raise ValueError(self.prompt.answer_text_err)
        subtitle_texts = self.text[:-1].split("｜")
        if any(not text.strip() for text in subtitle_texts):
            raise ValueError(self.prompt.answer_text_err)

        # Display subtitles contain neither alignment annotations nor punctuation
        if any({"　", "・", "＊"}.intersection(text) for text in subtitle_texts):
            raise ValueError(self.prompt.answer_text_err)
        if any(
            unicodedata.category(character)[0] in {"P", "S"}
            for character in self.transcript
        ):
            raise ValueError(self.prompt.answer_punctuation_err)

        # Enforce the display-length limit per subtitle
        overlong_indexes = [
            subtitle.index
            for subtitle in self.subtitles
            if sum(not character.isspace() for character in subtitle.text)
            > self.max_subtitle_characters
        ]
        if overlong_indexes:
            raise ValueError(
                self.prompt.subtitle_length_err(
                    overlong_indexes, self.max_subtitle_characters
                )
            )
        return self


class TranscriptionTestCase(TestCase):
    """Transcription query and optional consensus answer."""

    minimum_consensus_coverage: ClassVar[float] = 0.9
    """Minimum sequence-aligned preservation of strict-majority ASR evidence."""
    query_cls: ClassVar[type[TranscriptionQuery]] = TranscriptionQuery
    """Query model class."""
    answer_cls: ClassVar[type[TranscriptionAnswer]] = TranscriptionAnswer
    """Answer model class."""
    prompt: ClassVar[TranscriptionPrompt] = _BASE_PROMPT
    """Text and field aliases for transcription."""
    query: TranscriptionQuery
    """Reference-free aligned ASR evidence."""
    answer: TranscriptionAnswer | None = None
    """Consensus subtitles, if available."""

    @model_validator(mode="after")
    def validate_consensus_coverage(self) -> Self:
        """Ensure the answer preserves sufficient consensus from the ASR sources.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        validation = get_transcription_validation(
            tuple(source.text for source in self.query.sources),
            self.answer.transcript,
            self.prompt.language,
        )
        if not validation.preserves_required_majority(self.minimum_consensus_coverage):
            raise ValueError(
                self.prompt.consensus_coverage_err(
                    validation.majority_coverage, self.minimum_consensus_coverage
                )
            )
        return self
