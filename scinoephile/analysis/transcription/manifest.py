#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compact provenance for one aligned multi-source transcription run."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    model_validator,
)

from scinoephile.core.language import Language

__all__ = ["ProcessorIdentity", "RunBlock", "RunManifest", "normalize_excluded_blocks"]

_NonBlankString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
"""String normalized by trimming whitespace and rejecting blank values."""
_Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Lowercase hexadecimal SHA-256 digest."""
_StrictPositiveInt = Annotated[int, Field(strict=True, ge=1)]
"""Positive integer that rejects coercion from booleans and other types."""


def normalize_excluded_blocks(
    exclude_blocks: Sequence[object], planned_block_count: int | None = None
) -> tuple[int, ...]:
    """Validate and normalize configured block exclusions.

    Arguments:
        exclude_blocks: one-based block numbers to skip
        planned_block_count: optional number of blocks in the complete plan
    Returns:
        unique excluded block numbers in ascending order
    Raises:
        ValueError: if a block number is not an integer or lies outside the plan
    """
    validated_blocks = []
    for block_number in exclude_blocks:
        if isinstance(block_number, bool) or not isinstance(block_number, int):
            raise ValueError("Excluded transcription blocks must be integers.")
        validated_blocks.append(block_number)
    excluded_blocks = tuple(sorted(set(validated_blocks)))
    if excluded_blocks and excluded_blocks[0] < 1:
        raise ValueError("Excluded transcription blocks must be positive.")
    if (
        planned_block_count is not None
        and excluded_blocks
        and excluded_blocks[-1] > planned_block_count
    ):
        raise ValueError(
            f"Excluded transcription blocks must lie between 1 and "
            f"{planned_block_count}."
        )
    return excluded_blocks


class ProcessorIdentity(BaseModel):
    """Identity of the configured transcription processor."""

    model_config = ConfigDict(allow_inf_nan=False, extra="forbid", frozen=True)

    operation: _NonBlankString
    """Stable LLM operation identifier."""
    prompt_name: _NonBlankString
    """Stable content-addressed prompt name."""
    system_prompt_sha256: _Sha256
    """Digest of the complete system prompt."""
    provider_identity: dict[str, JsonValue] = Field(min_length=1)
    """Configured provider and model identity."""
    no_op: bool
    """Whether deterministic consensus replaced LLM queries."""


class RunBlock(BaseModel):
    """Cache references and outcome for one selected transcription block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(ge=1)
    """One-based block index."""
    status: Literal["transcribed", "empty", "excluded"]
    """Outcome of processing this selected block."""
    reason: _NonBlankString | None = None
    """Human-readable omission reason, when applicable."""
    source_cache_key_sha256s: dict[_NonBlankString, _Sha256] = Field(
        default_factory=dict
    )
    """Selected ASR cache-key digests by source name."""
    query_key_sha256s: tuple[_Sha256, ...] = ()
    """Semantic transcription query-key digests in request order."""


class RunManifest(BaseModel):
    """Compact provenance identifying one multi-source transcription run."""

    model_config = ConfigDict(allow_inf_nan=False, extra="forbid", frozen=True)

    format: Literal["scinoephile-transcription-run"] = "scinoephile-transcription-run"
    """Stable manifest format identifier."""
    version: Literal[3] = 3
    """Manifest schema version."""
    language: Language
    """Transcription output language."""
    audio_sha256: _Sha256
    """SHA-256 digest of decoded source audio bytes."""
    audio_duration_ms: int = Field(gt=0)
    """Complete decoded audio duration."""
    audio_channels: int = Field(gt=0)
    """Number of channels in the decoded source audio."""
    audio_frame_rate: int = Field(gt=0)
    """Frame rate of the decoded source audio."""
    audio_sample_width: int = Field(gt=0)
    """Sample width of the decoded source audio in bytes."""
    block_vad_identity: dict[str, JsonValue] = Field(min_length=1)
    """Block-planning VAD model and postprocessing identity."""
    planned_block_count: int = Field(ge=0)
    """Number of blocks in the complete hard-cut plan."""
    excluded_blocks: tuple[_StrictPositiveInt, ...] = ()
    """One-based block numbers excluded by configuration."""
    blocks: tuple[RunBlock, ...]
    """Selected blocks and their run outcomes."""
    processor: ProcessorIdentity
    """Consensus transcription processor identity."""
    alignment_sha256: _Sha256
    """Digest of the corresponding portable alignment artifact."""

    def save(self, path: Path):
        """Save this run manifest as canonical UTF-8 JSON.

        Arguments:
            path: output JSON path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> RunManifest:
        """Load and validate a run manifest from JSON.

        Arguments:
            path: JSON manifest path
        Returns:
            validated run manifest
        """
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    @model_validator(mode="after")
    def _validate_document(self) -> RunManifest:
        """Validate selected block order and bounds.

        Raises:
            ValueError: if a value is invalid
        """
        if self.excluded_blocks != tuple(sorted(set(self.excluded_blocks))):
            raise ValueError(
                "Excluded transcription block numbers must be unique and ordered."
            )
        if self.excluded_blocks and (
            self.excluded_blocks[0] < 1
            or self.excluded_blocks[-1] > self.planned_block_count
        ):
            raise ValueError("Excluded transcription block exceeds the block plan.")
        indexes = tuple(block.index for block in self.blocks)
        if indexes != tuple(sorted(set(indexes))):
            raise ValueError(
                "Transcription run block indexes must be unique and ordered."
            )
        if indexes and indexes[-1] > self.planned_block_count:
            raise ValueError("Transcription run block index exceeds the block plan.")
        excluded_blocks = set(self.excluded_blocks)
        if any(
            (block.status == "excluded") != (block.index in excluded_blocks)
            for block in self.blocks
        ):
            raise ValueError(
                "Transcription run block statuses must match configured exclusions."
            )
        return self
