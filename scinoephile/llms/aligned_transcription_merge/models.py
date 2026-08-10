#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for aligned transcription merge test cases."""

from __future__ import annotations

import unicodedata
from typing import ClassVar, Self

from pydantic import Field, ValidationInfo, model_validator

from scinoephile.core.llms import Answer, Query, TestCase
from scinoephile.core.llms.models import LLMModel, make_hashable

from .prompt import AlignedTranscriptionMergePrompt
from .validation import get_aligned_transcription_merge_validation

__all__ = [
    "AlignedTranscriptionMergeAnswer",
    "AlignedTranscriptionMergeQuery",
    "AlignedTranscriptionMergeSource",
    "AlignedTranscriptionMergeSubtitle",
    "AlignedTranscriptionMergeTestCase",
]


_BASE_PROMPT = AlignedTranscriptionMergePrompt()

_ALIGNMENT_GAP_CHARACTER = "　"
"""Fullwidth ideographic space used for ordinary alignment gaps."""
_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""
_REFERENCE_BOUNDARY_CHARACTER = "｜"
"""Fullwidth boundary marker excluded from reference-free queries."""
_VAD_SPEECH_CHARACTER = "＊"
"""Fullwidth unattributed-speech marker used in speaker rows."""
_FORBIDDEN_SOURCE_NAMES = frozenset({"guide", "reference"})
"""Reserved names rejected from reference-free ASR inputs."""
_SPEAKER_CHARACTERS = frozenset(
    {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER, _VAD_SPEECH_CHARACTER}
    | {chr(ord("Ａ") + index) for index in range(26)}
)
"""Characters permitted in the speaker annotation row."""
_LANGUAGE_CHARACTERS = frozenset(
    {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER, "粵", "普", "英", "日", "韓", "外"}
    | {chr(ord("Ａ") + index) for index in range(26)}
)
"""Characters permitted in the spoken-language annotation row."""


class AlignedTranscriptionMergeSource(LLMModel):
    """One named ASR row within a complete request alignment."""

    name: str = Field(min_length=1)
    """Stable ASR source name."""
    text: str = Field(min_length=1, max_length=10_000)
    """Column-aligned ASR characters and gaps."""


class AlignedTranscriptionMergeQuery(Query):
    """Reference-free aligned ASR and speaker evidence for one request."""

    prompt: ClassVar[AlignedTranscriptionMergePrompt] = _BASE_PROMPT
    """Text and field aliases for aligned transcription merging."""
    sources: list[AlignedTranscriptionMergeSource] = Field(min_length=2)
    """Named equal-status ASR source rows."""
    speaker: str = Field(min_length=1, max_length=10_000)
    """Column-aligned speaker and voice-activity annotations."""
    language_trace: str | None = Field(
        default=None,
        min_length=1,
        max_length=10_000,
        exclude_if=lambda value: value is None,
    )
    """Column-aligned spoken-language annotations, when available."""
    singing_trace: str | None = Field(
        default=None,
        min_length=1,
        max_length=10_000,
        exclude_if=lambda value: value is None,
    )
    """Column-aligned singing annotations, when available."""
    music_trace: str | None = Field(
        default=None,
        min_length=1,
        max_length=10_000,
        exclude_if=lambda value: value is None,
    )
    """Column-aligned music annotations, when available."""

    @property
    def key(self) -> tuple:
        """Unique key including optional traces omitted from serialization."""
        data = self.model_dump(mode="json")
        data.update(
            {
                "language_trace": self.language_trace,
                "music_trace": self.music_trace,
                "singing_trace": self.singing_trace,
            }
        )
        return tuple(
            make_hashable(data[field]) for field in sorted(type(self).model_fields)
        )

    @model_validator(mode="after")
    def validate_rows(self) -> Self:
        """Ensure the request contains a valid equal-width ASR alignment."""
        names = [source.name.strip() for source in self.sources]
        if any(not name for name in names) or len(set(names)) != len(names):
            raise ValueError(self.prompt.source_name_err)
        if any(name.casefold() in _FORBIDDEN_SOURCE_NAMES for name in names):
            raise ValueError(self.prompt.reference_source_err)
        row_lengths = {
            len(self.speaker),
            *(len(source.text) for source in self.sources),
            *(
                len(annotation)
                for annotation in (
                    self.language_trace,
                    self.singing_trace,
                    self.music_trace,
                )
                if annotation is not None
            ),
        }
        if row_lengths != {len(self.speaker)}:
            raise ValueError(self.prompt.row_length_err)
        annotation_rows = tuple(
            annotation
            for annotation in (
                self.speaker,
                self.language_trace,
                self.singing_trace,
                self.music_trace,
            )
            if annotation is not None
        )
        if any(
            _REFERENCE_BOUNDARY_CHARACTER in row
            for row in (*annotation_rows, *(source.text for source in self.sources))
        ):
            raise ValueError(self.prompt.reference_marker_err)
        if any(character not in _SPEAKER_CHARACTERS for character in self.speaker):
            raise ValueError(self.prompt.speaker_character_err)
        if self.language_trace is not None and any(
            character not in _LANGUAGE_CHARACTERS for character in self.language_trace
        ):
            raise ValueError(self.prompt.language_character_err)
        for annotation, marker in (
            (self.singing_trace, "唱"),
            (self.music_trace, "樂"),
        ):
            if annotation is not None and any(
                character not in {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER, marker}
                for character in annotation
            ):
                raise ValueError(self.prompt.audio_event_character_err)
        if not any(
            character not in {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER}
            for source in self.sources
            for character in source.text
        ):
            raise ValueError(self.prompt.transcript_empty_err)
        return self


class AlignedTranscriptionMergeSubtitle(LLMModel):
    """One ordered consensus subtitle derived from merged answer text."""

    index: int = Field(ge=1)
    """One-based subtitle index."""
    text: str = Field(min_length=1, max_length=1000)
    """Complete consensus subtitle text."""


class AlignedTranscriptionMergeAnswer(Answer):
    """Merged consensus text containing inline subtitle boundaries."""

    prompt: ClassVar[AlignedTranscriptionMergePrompt] = _BASE_PROMPT
    """Text and field aliases for aligned transcription merging."""
    text: str = Field(max_length=20_000)
    """Consensus transcript with boundaries, or empty when evidence is insufficient."""

    @property
    def subtitles(self) -> list[AlignedTranscriptionMergeSubtitle]:
        """Get consensus subtitles deterministically from the boundary markers."""
        if not self.text:
            return []
        return [
            AlignedTranscriptionMergeSubtitle(index=index, text=text)
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
        if not self.text.endswith(_REFERENCE_BOUNDARY_CHARACTER):
            raise ValueError(self.prompt.answer_text_err)
        subtitle_texts = self.text[:-1].split(_REFERENCE_BOUNDARY_CHARACTER)
        if not subtitle_texts or any(not text.strip() for text in subtitle_texts):
            raise ValueError(self.prompt.answer_text_err)
        annotation_characters = {
            _ALIGNMENT_GAP_CHARACTER,
            _PAUSE_CHARACTER,
            _VAD_SPEECH_CHARACTER,
        }
        if any(annotation_characters.intersection(text) for text in subtitle_texts):
            raise ValueError(self.prompt.answer_text_err)
        return self


class AlignedTranscriptionMergeTestCase(TestCase):
    """Aligned transcription merge query and optional consensus answer."""

    query_cls: ClassVar[type[AlignedTranscriptionMergeQuery]] = (
        AlignedTranscriptionMergeQuery
    )
    """Query model class."""
    answer_cls: ClassVar[type[AlignedTranscriptionMergeAnswer]] = (
        AlignedTranscriptionMergeAnswer
    )
    """Answer model class."""
    prompt: ClassVar[AlignedTranscriptionMergePrompt] = _BASE_PROMPT
    """Text and field aliases for aligned transcription merging."""
    query: AlignedTranscriptionMergeQuery
    """Reference-free aligned ASR evidence."""
    answer: AlignedTranscriptionMergeAnswer | None = None
    """Merged consensus subtitles, if available."""

    @model_validator(mode="after")
    def validate_answer(self, info: ValidationInfo) -> Self:
        """Ensure the answer is sufficiently complete and obeys the length limit.

        Arguments:
            info: Pydantic validation context
        Returns:
            validated test case
        """
        context = info.context
        if self.answer is None or (
            isinstance(context, dict)
            and context.get("skip_output_quality_validation") is True
        ):
            return self
        if any(
            unicodedata.category(character)[0] in {"P", "S"}
            for character in self.answer.transcript
        ):
            raise ValueError(self.prompt.answer_punctuation_err)
        validation = get_aligned_transcription_merge_validation(
            tuple(source.text for source in self.query.sources),
            self.answer.transcript,
            self.prompt.language,
        )
        consensus_coverage = validation.majority_coverage
        if not validation.preserves_required_majority(
            self.prompt.minimum_consensus_coverage
        ):
            raise ValueError(self.prompt.consensus_coverage_err(consensus_coverage))
        overlong_indexes = [
            subtitle.index
            for subtitle in self.answer.subtitles
            if sum(not character.isspace() for character in subtitle.text)
            > self.prompt.max_subtitle_characters
        ]
        if overlong_indexes:
            raise ValueError(self.prompt.subtitle_length_err(overlong_indexes))
        return self

    def get_no_op_answer(self) -> AlignedTranscriptionMergeAnswer:
        """Get an answer selecting the first ASR source.

        Returns:
            first-source text as one subtitle
        """
        text = (
            self.query.sources[0]
            .text.replace(_ALIGNMENT_GAP_CHARACTER, "")
            .replace(_PAUSE_CHARACTER, "")
            .strip()
        )
        if text:
            text += _REFERENCE_BOUNDARY_CHARACTER
        return AlignedTranscriptionMergeAnswer(text=text)
