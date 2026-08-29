#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for compact transcription run manifests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentSource,
)
from scinoephile.analysis.transcription.manifest import (
    ProcessorIdentity,
    RunBlock,
    RunManifest,
)
from scinoephile.core import Language


def test_alignment_sha256_is_stable():
    """Semantically identical alignment artifacts should have the same digest."""
    artifact = AlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=1_000,
        sources=(
            AlignmentSource(name="whisper", backend="whisper", model="large-v3"),
            AlignmentSource(name="qwen", backend="mlx-audio", model="qwen3-asr"),
        ),
        blocks=(),
    )

    digest = artifact.sha256

    assert len(digest) == 64
    assert (
        digest
        == AlignmentArtifact.model_validate(artifact.model_dump(mode="json")).sha256
    )
    assert digest != artifact.model_copy(update={"audio_duration_ms": 2_000}).sha256


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_processor_identity_rejects_nonfinite_provider_values(value: float):
    """Processor identities should reject values that JSON cannot preserve.

    Arguments:
        value: nonfinite provider value
    """
    digest = "a" * 64

    with pytest.raises(ValidationError):
        ProcessorIdentity(
            operation="transcription",
            prompt_name="test",
            system_prompt_sha256=digest,
            provider_identity={"temperature": value},
            no_op=False,
        )


@pytest.mark.parametrize(
    ("indexes", "planned_block_count"), [((1, 1), 2), ((2, 1), 2), ((3,), 2)]
)
def test_run_manifest_rejects_invalid_block_indexes(
    indexes: tuple[int, ...], planned_block_count: int
):
    """Run manifests should reject duplicate, unordered, or out-of-plan blocks.

    Arguments:
        indexes: invalid block indexes
        planned_block_count: number of planned blocks
    """
    digest = "a" * 64

    with pytest.raises(ValidationError):
        RunManifest(
            language=Language.yue_hant,
            audio_sha256=digest,
            audio_duration_ms=1_000,
            audio_channels=1,
            audio_frame_rate=16_000,
            audio_sample_width=2,
            block_vad_identity={"implementation": "pyannote"},
            planned_block_count=planned_block_count,
            blocks=tuple(
                RunBlock(index=index, status="transcribed") for index in indexes
            ),
            processor=ProcessorIdentity(
                operation="transcription",
                prompt_name="test",
                system_prompt_sha256=digest,
                provider_identity={"implementation": "test"},
                no_op=False,
            ),
            alignment_sha256=digest,
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_run_manifest_rejects_nonfinite_vad_values(value: float):
    """Run manifests should reject VAD identities that JSON cannot preserve.

    Arguments:
        value: nonfinite VAD value
    """
    digest = "a" * 64

    with pytest.raises(ValidationError):
        RunManifest(
            language=Language.yue_hant,
            audio_sha256=digest,
            audio_duration_ms=1_000,
            audio_channels=1,
            audio_frame_rate=16_000,
            audio_sample_width=2,
            block_vad_identity={"threshold": value},
            planned_block_count=0,
            blocks=(),
            processor=ProcessorIdentity(
                operation="transcription",
                prompt_name="test",
                system_prompt_sha256=digest,
                provider_identity={"implementation": "test"},
                no_op=False,
            ),
            alignment_sha256=digest,
        )


def test_run_manifest_round_trip(tmp_path: Path):
    """A compact manifest should retain run provenance.

    Arguments:
        tmp_path: temporary directory
    """
    digest = "a" * 64
    manifest = RunManifest(
        language=Language.yue_hant,
        audio_sha256=digest,
        audio_duration_ms=1_000,
        audio_channels=1,
        audio_frame_rate=16_000,
        audio_sample_width=2,
        block_vad_identity={"implementation": "pyannote"},
        planned_block_count=2,
        blocks=(
            RunBlock(
                index=1,
                status="transcribed",
                source_cache_key_sha256s={"whisper": digest},
                query_key_sha256s=(digest,),
            ),
        ),
        processor=ProcessorIdentity(
            operation="transcription",
            prompt_name="test",
            system_prompt_sha256=digest,
            provider_identity={"implementation": "test", "model": "test"},
            no_op=False,
        ),
        alignment_sha256=digest,
    )
    manifest_path = tmp_path / "run_manifest.json"

    manifest.save(manifest_path)

    assert RunManifest.load(manifest_path) == manifest
