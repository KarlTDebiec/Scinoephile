#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Versioned artifacts for aligned multi-source transcription evidence."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from scinoephile.core.language import Language
from scinoephile.core.subtitles import Series, Subtitle

__all__ = [
    "AlignmentArtifact",
    "AlignmentBlock",
    "AlignmentColumn",
    "AlignmentRow",
    "AlignmentSource",
    "AlignmentSubtitle",
    "TimingSettings",
    "TimingSource",
]

_NonBlankString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
"""String normalized by trimming whitespace and rejecting blank values."""
_SpeakerSymbol = Annotated[str, StringConstraints(pattern=r"^[Ａ-Ｚ]$")]
"""Anonymous fullwidth Latin speaker symbol."""

TimingSource = Literal["ctc-request", "ctc-unconsumed-block", "source"]
"""Origin of one final subtitle's speech timing."""


class TimingSettings(BaseModel):
    """Settings that convert speech bounds into nonoverlapping display bounds."""

    model_config = ConfigDict(allow_inf_nan=False, extra="forbid", frozen=True)

    lead_in_seconds: float = Field(default=0.25, ge=0.0)
    """Preferred display time before CTC-estimated speech begins."""
    lead_out_seconds: float = Field(default=0.5, ge=0.0)
    """Preferred display time after CTC-estimated speech ends."""
    minimum_duration_seconds: float = Field(default=0.75, gt=0.0)
    """Preferred minimum subtitle display duration."""


class AlignmentSource(BaseModel):
    """One ASR source participating in every block alignment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: _NonBlankString
    """Stable source name used as the alignment row label."""
    backend: _NonBlankString
    """Transcription backend implementation name."""
    model: _NonBlankString
    """Backend-specific model identifier."""


class AlignmentColumn(BaseModel):
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
    def _validate_timing(self) -> AlignmentColumn:
        """Validate the overall-time interval.

        Raises:
            ValueError: if a value is invalid
        """
        if self.end_ms < self.start_ms:
            raise ValueError("Alignment column end must not precede its start.")
        if self.kind == "pause" and self.end_ms == self.start_ms:
            raise ValueError("Alignment pause columns must have positive duration.")
        return self


class AlignmentRow(BaseModel):
    """One equal-width ASR row in a transcription alignment block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: _NonBlankString
    """Stable source name matching an artifact source descriptor."""
    text: str = Field(min_length=1)
    """Aligned characters, fullwidth gaps, and shared pause markers."""


class AlignmentSubtitle(BaseModel):
    """One merged subtitle with speech and display timing kept separately."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(ge=1)
    """One-based subtitle index in the complete artifact output."""
    text: str = Field(min_length=1)
    """Merged subtitle text."""
    speech_start_ms: int = Field(ge=0)
    """Inclusive CTC-estimated speech start on the complete source timeline."""
    speech_end_ms: int = Field(ge=0)
    """Exclusive CTC-estimated speech end on the complete source timeline."""
    timing_source: TimingSource
    """Origin of the speech interval."""
    start_ms: int = Field(ge=0)
    """Inclusive final SRT display start."""
    end_ms: int = Field(ge=0)
    """Exclusive final SRT display end."""
    speaker: _SpeakerSymbol | None = None
    """Anonymous speaker symbol matching the block's speaker row, when available."""

    @model_validator(mode="after")
    def _validate_timing(self) -> AlignmentSubtitle:
        """Validate speech and display intervals.

        Raises:
            ValueError: if a value is invalid
        """
        if self.speech_end_ms <= self.speech_start_ms:
            raise ValueError("Subtitle speech duration must be positive.")
        if self.end_ms <= self.start_ms:
            raise ValueError("Subtitle display duration must be positive.")
        if self.start_ms > self.speech_start_ms:
            raise ValueError("Subtitle display start must not follow speech start.")
        if self.end_ms < self.speech_end_ms:
            raise ValueError("Subtitle display end must not precede speech end.")
        return self


class AlignmentBlock(BaseModel):
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
    columns: tuple[AlignmentColumn, ...]
    """Overall-time alignment column metadata."""
    rows: tuple[AlignmentRow, ...]
    """Source rows in artifact source order."""
    speaker: str
    """Speaker/VAD annotation row aligned with all source rows."""
    language_trace: str | None = None
    """Spoken-language annotation row aligned with all source rows."""
    language_legend: dict[str, str] = Field(default_factory=dict)
    """Language-row display characters mapped to FireRed language labels."""
    singing_trace: str | None = None
    """Independent FireRed singing annotation row, when available."""
    music_trace: str | None = None
    """Independent FireRed music annotation row, when available."""
    merged: str
    """Lexical merged row aligned with all source rows."""
    subtitles: tuple[AlignmentSubtitle, ...]
    """Core-owned merged subtitles produced from this block."""
    source_errors: dict[str, str] = Field(default_factory=dict)
    """Source failures that were tolerated while processing the block."""

    def _validate_annotation_characters(self) -> None:
        """Validate speaker, language, singing, and music row characters.

        Raises:
            ValueError: if a value is invalid
        """
        if any(
            character not in {"　", "・", "＊"} and not "Ａ" <= character <= "Ｚ"
            for character in self.speaker
        ):
            raise ValueError("Alignment speaker row contains an invalid character.")
        if any(
            len(symbol) != 1 or symbol in {"　", "・"} or not label.strip()
            for symbol, label in self.language_legend.items()
        ):
            raise ValueError(
                "Alignment language legend must map nonreserved characters to labels."
            )
        if self.language_trace is None and self.language_legend:
            raise ValueError("Alignment language legend requires a language row.")
        if self.language_trace is not None and any(
            character not in {"　", "・"} and character not in self.language_legend
            for character in self.language_trace
        ):
            raise ValueError("Alignment language row contains an unknown character.")
        for name, annotation, marker in (
            ("singing", self.singing_trace, "唱"),
            ("music", self.music_trace, "樂"),
        ):
            if annotation is not None and any(
                character not in {"　", "・", marker} for character in annotation
            ):
                raise ValueError(f"Alignment {name} row contains an invalid character.")

    def _validate_annotations(self) -> None:
        """Validate production-only annotations and shared pause columns.

        Raises:
            ValueError: if a value is invalid
        """
        self._validate_annotation_characters()
        if "｜" in self.merged or any("｜" in row.text for row in self.rows):
            raise ValueError(
                "Production alignment rows must not contain reference boundaries."
            )
        self._validate_pause_columns()

    def _validate_pause_columns(self) -> None:
        """Validate that timed pauses are shared by every present row.

        Raises:
            ValueError: if a value is invalid
        """
        for column_idx, column in enumerate(self.columns):
            characters = [
                self.speaker[column_idx],
                self.merged[column_idx],
                *(row.text[column_idx] for row in self.rows),
                *(
                    annotation[column_idx]
                    for annotation in (
                        self.language_trace,
                        self.singing_trace,
                        self.music_trace,
                    )
                    if annotation is not None
                ),
            ]
            if column.kind == "pause" and any(
                character != "・" for character in characters
            ):
                raise ValueError("Alignment pause columns must be shared by every row.")
            if column.kind != "pause" and "・" in characters:
                raise ValueError("Alignment pause markers require a pause column.")

    def _validate_ranges(self) -> None:
        """Validate core, buffer, and column ranges.

        Raises:
            ValueError: if a value is invalid
        """
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
        if any(
            column.start_ms < self.buffered_start_ms
            or column.end_ms > self.buffered_end_ms
            for column in self.columns
        ):
            raise ValueError("Alignment columns must lie within the block buffer.")

    def _validate_rows(self) -> None:
        """Validate aligned row widths, names, and source errors.

        Raises:
            ValueError: if a value is invalid
        """
        row_width = len(self.columns)
        if any(len(row.text) != row_width for row in self.rows):
            raise ValueError("Alignment source rows must match the column count.")
        if len(self.speaker) != row_width:
            raise ValueError("Alignment speaker row must match the column count.")
        for name, annotation in (
            ("language", self.language_trace),
            ("singing", self.singing_trace),
            ("music", self.music_trace),
        ):
            if annotation is not None and len(annotation) != row_width:
                raise ValueError(f"Alignment {name} row must match the column count.")
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

    @model_validator(mode="after")
    def _validate_shape(self) -> AlignmentBlock:
        """Validate block ranges, column indexes, and row widths."""
        self._validate_ranges()
        self._validate_rows()
        self._validate_annotations()
        return self


class AlignmentArtifact(BaseModel):
    """Portable versioned record of a multi-source transcription run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["scinoephile-transcription-alignment"] = (
        "scinoephile-transcription-alignment"
    )
    """Stable artifact format identifier."""
    version: Literal[4] = 4
    """Artifact schema version."""
    language: Language
    """Language of the ASR rows and merged subtitles."""
    audio_duration_ms: int = Field(gt=0)
    """Duration of the complete source audio, including unprocessed regions."""
    pause_unit_ms: int = Field(default=250, gt=0)
    """Nominal duration represented by one shared pause column."""
    request_pause_columns: int = Field(default=4, gt=0)
    """Consecutive pause columns that divide independent merge requests."""
    timing: TimingSettings = Field(default_factory=TimingSettings)
    """Reference-free policy used to convert speech timing to display timing."""
    sources: tuple[AlignmentSource, ...]
    """ASR sources in stable alignment row order."""
    blocks: tuple[AlignmentBlock, ...]
    """Processed VAD blocks in source order."""

    @property
    def sha256(self) -> str:
        """Stable digest of the artifact's canonical semantic JSON."""
        payload = json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(payload.encode("utf-8")).hexdigest()

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

    @classmethod
    def load(cls, path: Path) -> AlignmentArtifact:
        """Load and validate an alignment artifact.

        Arguments:
            path: JSON artifact path
        Returns:
            validated alignment artifact
        """
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def _validate_block(
        self,
        block: AlignmentBlock,
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
        Raises:
            ValueError: if a value is invalid
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

    def _validate_sources(self) -> tuple[str, ...]:
        """Validate and return the stable source-name order.

        Returns:
            stable source names in row order

        Raises:
            ValueError: if a value is invalid
        """
        if len(self.sources) < 2:
            raise ValueError("Transcription alignments require at least two sources.")
        source_names = tuple(source.name for source in self.sources)
        if len(set(source_names)) != len(source_names):
            raise ValueError("Transcription alignment source names must be unique.")
        return source_names

    def _validate_subtitles(
        self,
        block: AlignmentBlock,
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

        Raises:
            ValueError: if a value is invalid
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

    @model_validator(mode="after")
    def _validate_document(self) -> AlignmentArtifact:
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
