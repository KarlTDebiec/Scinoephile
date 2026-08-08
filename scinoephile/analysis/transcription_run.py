#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compact provenance for one aligned multi-source transcription run."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from scinoephile.core import Language

from .transcription_alignment import TranscriptionAlignmentArtifact

__all__ = [
    "TranscriptionRunBlock",
    "TranscriptionRunManifest",
    "TranscriptionRunMerger",
    "get_transcription_alignment_sha256",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
type _Sha256 = Annotated[str, Field(pattern=_SHA256_PATTERN)]


def get_transcription_alignment_sha256(artifact: TranscriptionAlignmentArtifact) -> str:
    """Get a stable digest of a portable alignment artifact.

    Arguments:
        artifact: portable alignment artifact
    Returns:
        SHA-256 digest of canonical semantic JSON
    """
    payload = json.dumps(
        artifact.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return sha256(payload.encode("utf-8")).hexdigest()


class TranscriptionRunBlock(BaseModel):
    """Cache identities and outcome for one selected VAD block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(gt=0)
    """One-based VAD block index."""
    status: Literal["transcribed", "empty", "no-core-text"]
    """Outcome of processing this selected block."""
    reason: str | None = None
    """Human-readable omission reason, when applicable."""
    source_cache_keys: dict[str, _Sha256] = Field(default_factory=dict)
    """Selected ASR cache-key digests by source name."""
    merge_query_keys: tuple[_Sha256, ...] = ()
    """Semantic merger query-key digests in request order."""


class TranscriptionRunMerger(BaseModel):
    """Identity of the configured consensus merger."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: str = Field(min_length=1)
    """Stable LLM operation identifier."""
    prompt_name: str = Field(min_length=1)
    """Human-readable prompt version name."""
    system_prompt_sha256: _Sha256
    """Digest of the complete system prompt."""
    additional_context_sha256: _Sha256 | None = None
    """Digest of production context supplied to the merger."""
    provider: dict[str, JsonValue]
    """Provider and model cache identity."""


class TranscriptionRunManifest(BaseModel):
    """Compact identities needed to distinguish and reproduce one run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["scinoephile-transcription-run"] = "scinoephile-transcription-run"
    """Stable manifest format identifier."""
    version: Literal[1] = 1
    """Manifest schema version."""
    language: Language
    """Transcription output language."""
    audio_sha256: _Sha256
    """SHA-256 digest of decoded source audio bytes."""
    audio_duration_ms: int = Field(gt=0)
    """Complete decoded audio duration."""
    block_vad: dict[str, JsonValue]
    """Block-planning VAD cache identity."""
    planned_block_count: int = Field(ge=0)
    """Number of blocks in the complete VAD plan."""
    blocks: tuple[TranscriptionRunBlock, ...]
    """Selected blocks and their run outcomes."""
    merger: TranscriptionRunMerger
    """Consensus merger identity."""
    alignment_sha256: _Sha256
    """Digest of the corresponding portable alignment artifact."""

    @model_validator(mode="after")
    def _validate_document(self) -> TranscriptionRunManifest:
        """Validate selected block order and bounds."""
        indexes = tuple(block.index for block in self.blocks)
        if indexes != tuple(sorted(set(indexes))):
            raise ValueError(
                "Transcription run block indexes must be unique and ordered."
            )
        if indexes and indexes[-1] > self.planned_block_count:
            raise ValueError("Transcription run block index exceeds the VAD plan.")
        return self

    @classmethod
    def load(cls, path: Path) -> TranscriptionRunManifest:
        """Load and validate a run manifest from JSON.

        Arguments:
            path: JSON manifest path
        Returns:
            validated run manifest
        """
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, path: Path):
        """Save this run manifest as canonical UTF-8 JSON.

        Arguments:
            path: output JSON path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")
