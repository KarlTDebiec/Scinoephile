#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for compact transcription run manifests."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis.transcription_run import (
    TranscriptionRunBlock,
    TranscriptionRunManifest,
    TranscriptionRunMerger,
)
from scinoephile.core import Language


def test_run_manifest_round_trip(tmp_path: Path):
    """A compact manifest should retain only run and cache identities."""
    digest = "a" * 64
    manifest = TranscriptionRunManifest(
        language=Language.yue_hant,
        audio_sha256=digest,
        audio_duration_ms=1_000,
        block_vad={"implementation": "pyannote"},
        planned_block_count=2,
        blocks=(
            TranscriptionRunBlock(
                index=1,
                status="transcribed",
                source_cache_keys={"whisper": digest},
                merge_query_keys=(digest,),
            ),
        ),
        merger=TranscriptionRunMerger(
            operation="aligned-transcription-merge",
            prompt_name="test",
            system_prompt_sha256=digest,
            provider={"implementation": "test", "model": "test"},
        ),
        alignment_sha256=digest,
    )
    manifest_path = tmp_path / "run_manifest.json"

    manifest.save(manifest_path)

    assert TranscriptionRunManifest.load(manifest_path) == manifest
