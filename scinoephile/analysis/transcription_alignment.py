#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Versioned artifacts for aligned multi-source transcription evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle

__all__ = [
    "SubtitleTimingSettings",
    "TranscriptionAlignmentArtifact",
    "TranscriptionAlignmentBlock",
    "TranscriptionAlignmentColumn",
    "TranscriptionAlignmentRow",
    "TranscriptionAlignmentSource",
    "TranscriptionAlignmentSubtitle",
]

_GAP_CHARACTER = "　"
_PAUSE_CHARACTER = "・"
_REFERENCE_BOUNDARY_CHARACTER = "｜"
_SPEECH_CHARACTER = "＊"
_SPEAKER_CHARACTERS = frozenset(
    {_GAP_CHARACTER, _PAUSE_CHARACTER, _SPEECH_CHARACTER}
    | {chr(ord("Ａ") + index) for index in range(26)}
)


class SubtitleTimingSettings(BaseModel):
    """Settings that convert speech bounds into nonoverlapping display bounds."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lead_in_seconds: float = Field(default=0.0, ge=0.0)
    """Preferred display time before CTC-estimated speech begins."""
    lead_out_seconds: float = Field(default=0.0, ge=0.0)
    """Preferred display time after CTC-estimated speech ends."""
    minimum_duration_seconds: float = Field(default=0.75, gt=0.0)
    """Preferred minimum subtitle display duration."""


class TranscriptionAlignmentSource(BaseModel):
    """One ASR source participating in every block alignment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    """Stable source name used as the alignment row label."""
    backend: str = Field(min_length=1)
    """Transcription backend implementation name."""
    model: str = Field(min_length=1)
    """Backend-specific model identifier."""


class TranscriptionAlignmentColumn(BaseModel):
    """Overall-time interval represented by one alignment column."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(ge=1)
    """One-based column index within the block."""
    start_ms: int = Field(ge=0)
    """Inclusive column start on the complete source timeline."""
    end_ms: int = Field(ge=0)
    """Exclusive column end on the complete source timeline."""
    kind: Literal["text", "pause"]
    """Whether the column contains lexical evidence or a shared timed pause."""

    @model_validator(mode="after")
    def _validate_timing(self) -> TranscriptionAlignmentColumn:
        """Validate the overall-time interval."""
        if self.end_ms < self.start_ms:
            raise ValueError("Alignment column end must not precede its start.")
        if self.kind == "pause" and self.end_ms == self.start_ms:
            raise ValueError("Alignment pause columns must have positive duration.")
        return self


class TranscriptionAlignmentRow(BaseModel):
    """One equal-width ASR row in a transcription alignment block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    """Stable source name matching an artifact source descriptor."""
    text: str = Field(min_length=1)
    """Aligned characters, fullwidth gaps, and shared pause markers."""


class TranscriptionAlignmentSubtitle(BaseModel):
    """One merged subtitle with speech and display timing kept separately."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(ge=1)
    """One-based subtitle index in the complete artifact output."""
    text: str = Field(min_length=1)
    """Merged, punctuated subtitle text."""
    speech_start_ms: int = Field(ge=0)
    """Inclusive CTC-estimated speech start on the complete source timeline."""
    speech_end_ms: int = Field(ge=0)
    """Exclusive CTC-estimated speech end on the complete source timeline."""
    start_ms: int = Field(ge=0)
    """Inclusive final SRT display start."""
    end_ms: int = Field(ge=0)
    """Exclusive final SRT display end."""
    speaker: str | None = None
    """Anonymous diarization label assigned to the subtitle, when available."""

    @model_validator(mode="after")
    def _validate_timing(self) -> TranscriptionAlignmentSubtitle:
        """Validate speech and display intervals."""
        if self.speech_end_ms < self.speech_start_ms:
            raise ValueError("Subtitle speech end must not precede its start.")
        if self.end_ms <= self.start_ms:
            raise ValueError("Subtitle display duration must be positive.")
        if self.start_ms > self.speech_start_ms:
            raise ValueError("Subtitle display start must not follow speech start.")
        if self.end_ms < self.speech_end_ms:
            raise ValueError("Subtitle display end must not precede speech end.")
        return self


class TranscriptionAlignmentBlock(BaseModel):
    """One VAD-derived block of aligned ASR, speaker, and merged evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(ge=1)
    """One-based block index in the complete VAD plan."""
    core_start_ms: int = Field(ge=0)
    """Inclusive start of the block-owned source interval."""
    core_end_ms: int = Field(ge=0)
    """Exclusive end of the block-owned source interval."""
    buffered_start_ms: int = Field(ge=0)
    """Inclusive start of the ASR input interval."""
    buffered_end_ms: int = Field(ge=0)
    """Exclusive end of the ASR input interval."""
    columns: tuple[TranscriptionAlignmentColumn, ...]
    """Overall-time alignment column metadata."""
    rows: tuple[TranscriptionAlignmentRow, ...]
    """Source rows in artifact source order."""
    speaker: str
    """Speaker/VAD annotation row aligned with all source rows."""
    merged: str
    """Lexical merged row aligned with all source rows."""
    subtitles: tuple[TranscriptionAlignmentSubtitle, ...]
    """Core-owned merged subtitles produced from this block."""
    source_errors: dict[str, str] = Field(default_factory=dict)
    """Source failures that were tolerated while processing the block."""

    @model_validator(mode="after")
    def _validate_shape(self) -> TranscriptionAlignmentBlock:
        """Validate block ranges, column indexes, and row widths."""
        self._validate_ranges()
        self._validate_rows()
        self._validate_annotations()
        return self

    def _validate_ranges(self) -> None:
        """Validate core, buffer, and column ranges."""
        if self.core_end_ms <= self.core_start_ms:
            raise ValueError("Alignment block core duration must be positive.")
        if self.buffered_end_ms <= self.buffered_start_ms:
            raise ValueError("Alignment block buffered duration must be positive.")
        if (
            self.core_start_ms < self.buffered_start_ms
            or self.core_end_ms > self.buffered_end_ms
        ):
            raise ValueError("Alignment block core must lie within its buffer.")
        if not self.columns:
            raise ValueError("Alignment blocks must contain at least one column.")
        if tuple(column.index for column in self.columns) != tuple(
            range(1, len(self.columns) + 1)
        ):
            raise ValueError("Alignment column indexes must be consecutive.")

    def _validate_rows(self) -> None:
        """Validate aligned row widths, names, and source errors."""
        row_width = len(self.columns)
        if any(len(row.text) != row_width for row in self.rows):
            raise ValueError("Alignment source rows must match the column count.")
        if len(self.speaker) != row_width:
            raise ValueError("Alignment speaker row must match the column count.")
        if len(self.merged) != row_width:
            raise ValueError("Alignment merged row must match the column count.")
        if len({row.name for row in self.rows}) != len(self.rows):
            raise ValueError("Alignment block source row names must be unique.")
        if any(
            not name.strip() or not error.strip()
            for name, error in self.source_errors.items()
        ):
            raise ValueError(
                "Alignment source errors must have nonblank names and text."
            )

    def _validate_annotations(self) -> None:
        """Validate production-only annotations and shared pause columns."""
        if any(character not in _SPEAKER_CHARACTERS for character in self.speaker):
            raise ValueError("Alignment speaker row contains an invalid character.")
        if _REFERENCE_BOUNDARY_CHARACTER in self.merged or any(
            _REFERENCE_BOUNDARY_CHARACTER in row.text for row in self.rows
        ):
            raise ValueError(
                "Production alignment rows must not contain reference boundaries."
            )
        for column_idx, column in enumerate(self.columns):
            if column.kind != "pause":
                continue
            if (
                self.speaker[column_idx] != _PAUSE_CHARACTER
                or self.merged[column_idx] != _PAUSE_CHARACTER
            ):
                raise ValueError(
                    "Alignment pause columns must be shared by annotation rows."
                )
            if any(row.text[column_idx] != _PAUSE_CHARACTER for row in self.rows):
                raise ValueError("Alignment pause columns must be shared by ASR rows.")


class TranscriptionAlignmentArtifact(BaseModel):
    """Portable versioned record of a multi-source transcription run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["scinoephile-transcription-alignment"] = (
        "scinoephile-transcription-alignment"
    )
    """Stable artifact format identifier."""
    version: Literal[1] = 1
    """Artifact schema version."""
    language: Language
    """Language of the ASR rows and merged subtitles."""
    audio_duration_ms: int = Field(gt=0)
    """Duration of the complete source audio, including unprocessed regions."""
    gap_character: Literal["　"] = "　"
    """Fullwidth character used for ordinary alignment gaps."""
    pause_character: Literal["・"] = "・"
    """Fullwidth character used for shared timed pauses."""
    speech_character: Literal["＊"] = "＊"
    """Fullwidth character used for unattributed detected speech."""
    pause_unit_ms: int = Field(default=250, gt=0)
    """Nominal duration represented by one shared pause column."""
    request_pause_columns: int = Field(default=4, gt=0)
    """Consecutive pause columns that divide independent merge requests."""
    timing: SubtitleTimingSettings = Field(default_factory=SubtitleTimingSettings)
    """Reference-free policy used to convert speech timing to display timing."""
    sources: tuple[TranscriptionAlignmentSource, ...]
    """ASR sources in stable alignment row order."""
    blocks: tuple[TranscriptionAlignmentBlock, ...]
    """Processed VAD blocks in source order."""

    @model_validator(mode="after")
    def _validate_document(self) -> TranscriptionAlignmentArtifact:
        """Validate source identity and ordered block contents."""
        source_names = self._validate_sources()
        previous_block_index = 0
        previous_core_end_ms = -1
        subtitle_state = (0, -1, -1)
        for block in self.blocks:
            self._validate_block(
                block, source_names, previous_block_index, previous_core_end_ms
            )
            subtitle_state = self._validate_subtitles(block, *subtitle_state)
            previous_block_index = block.index
            previous_core_end_ms = block.core_end_ms
        return self

    def _validate_sources(self) -> tuple[str, ...]:
        """Validate and return the stable source-name order."""
        if len(self.sources) < 2:
            raise ValueError("Transcription alignments require at least two sources.")
        source_names = tuple(source.name for source in self.sources)
        if len(set(source_names)) != len(source_names):
            raise ValueError("Transcription alignment source names must be unique.")
        return source_names

    def _validate_block(
        self,
        block: TranscriptionAlignmentBlock,
        source_names: tuple[str, ...],
        previous_block_index: int,
        previous_core_end_ms: int,
    ) -> None:
        """Validate one block's source identity and position in the artifact.

        Arguments:
            block: block to validate
            source_names: expected source names in stable order
            previous_block_index: preceding processed VAD block index
            previous_core_end_ms: preceding processed block core end
        """
        if block.buffered_end_ms > self.audio_duration_ms:
            raise ValueError("Alignment block exceeds the source audio duration.")
        if block.index <= previous_block_index:
            raise ValueError("Alignment block indexes must be increasing.")
        if block.core_start_ms < previous_core_end_ms:
            raise ValueError("Alignment block cores must not overlap.")
        block_source_names = tuple(row.name for row in block.rows)
        if block_source_names != tuple(
            name for name in source_names if name in block_source_names
        ):
            raise ValueError("Alignment block rows must follow artifact source order.")
        if not set(block_source_names).issubset(source_names):
            raise ValueError("Alignment block contains an unknown source row.")
        failed_source_names = set(block.source_errors)
        if not failed_source_names.issubset(source_names):
            raise ValueError("Alignment block contains an unknown source error.")
        if set(source_names) - set(block_source_names) != failed_source_names:
            raise ValueError(
                "Every absent alignment source must have one source error."
            )

    def _validate_subtitles(
        self,
        block: TranscriptionAlignmentBlock,
        previous_subtitle_index: int,
        previous_speech_end_ms: int,
        previous_display_end_ms: int,
    ) -> tuple[int, int, int]:
        """Validate one block's subtitles and return updated ordering state.

        Arguments:
            block: block whose subtitles to validate
            previous_subtitle_index: preceding global subtitle index
            previous_speech_end_ms: preceding CTC speech end
            previous_display_end_ms: preceding SRT display end
        Returns:
            updated subtitle index, speech end, and display end
        """
        for subtitle in block.subtitles:
            if subtitle.index != previous_subtitle_index + 1:
                raise ValueError(
                    "Alignment subtitle indexes must be globally consecutive."
                )
            if (
                subtitle.speech_start_ms < block.core_start_ms
                or subtitle.speech_end_ms > block.core_end_ms
            ):
                raise ValueError(
                    "Alignment subtitle speech must lie within its block core."
                )
            if subtitle.end_ms > self.audio_duration_ms:
                raise ValueError("Alignment subtitle exceeds the source audio.")
            if subtitle.speech_start_ms < previous_speech_end_ms:
                raise ValueError("Alignment subtitle speech must not overlap.")
            if subtitle.start_ms < previous_display_end_ms:
                raise ValueError("Alignment subtitle display timing must not overlap.")
            previous_subtitle_index = subtitle.index
            previous_speech_end_ms = subtitle.speech_end_ms
            previous_display_end_ms = subtitle.end_ms
        return (
            previous_subtitle_index,
            previous_speech_end_ms,
            previous_display_end_ms,
        )

    @classmethod
    def load(cls, path: Path) -> TranscriptionAlignmentArtifact:
        """Load and validate an alignment artifact.

        Arguments:
            path: JSON artifact path
        Returns:
            validated alignment artifact
        """
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def get_series(self) -> Series:
        """Get the artifact's merged subtitles as a subtitle series.

        Returns:
            merged subtitle series using final display timings
        """
        return Series(
            events=[
                Subtitle(
                    start=subtitle.start_ms,
                    end=subtitle.end_ms,
                    text=subtitle.text,
                    name=subtitle.speaker or "",
                )
                for block in self.blocks
                for subtitle in block.subtitles
            ]
        )

    def save(self, path: Path):
        """Save the artifact as canonical UTF-8 JSON.

        Arguments:
            path: output JSON path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")
