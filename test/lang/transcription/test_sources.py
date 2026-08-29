#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the multi-source transcription registry."""

from __future__ import annotations

from unittest.mock import patch

from pytest import raises

from scinoephile.audio.transcription import VadMode
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
)
from scinoephile.audio.transcription.whisper.model import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.transcription.sources import (
    TranscriptionSourceSpec,
    get_transcription_sources,
)


def test_default_cantonese_sources_use_configured_models_without_internal_vad():
    """Test default Cantonese sources use typed models without internal VAD."""
    with (
        patch("scinoephile.lang.transcription.sources.WhisperTranscriber") as whisper,
        patch("scinoephile.lang.transcription.sources.MlxAudioTranscriber") as mlx,
    ):
        whisper.backend_name = "whisper"
        mlx.backend_name = "mlx-audio"
        transcribers, descriptors = get_transcription_sources(Language.yue_hant)

    assert tuple(transcribers) == (
        "whisper",
        "mimo",
        "qwen",
        "sensevoice",
        "firered",
        "glm",
    )
    assert tuple(source.name for source in descriptors) == tuple(transcribers)
    assert tuple(source.backend for source in descriptors) == (
        "whisper",
        "mlx-audio",
        "mlx-audio",
        "mlx-audio",
        "mlx-audio",
        "mlx-audio",
    )
    assert tuple(source.model for source in descriptors) == (
        WHISPER_LARGE_V3_CANTONESE_MODEL.model_name,
        MIMO_MODEL.name,
        QWEN3_ASR_MODEL.name,
        SENSEVOICE_MODEL.name,
        FIRERED_ASR2_MODEL.name,
        GLM_ASR_MODEL.name,
    )
    assert whisper.call_args.kwargs["model"] is WHISPER_LARGE_V3_CANTONESE_MODEL
    assert whisper.call_args.kwargs["language"] is Language.yue_hant
    assert whisper.call_args.kwargs["vad_mode"] is VadMode.OFF
    assert whisper.call_args.kwargs["recover_decoding"]
    assert [call.kwargs["model"].spec for call in mlx.call_args_list] == [
        MIMO_MODEL,
        QWEN3_ASR_MODEL,
        SENSEVOICE_MODEL,
        FIRERED_ASR2_MODEL,
        GLM_ASR_MODEL,
    ]
    assert all(
        call.kwargs["ctc_aligner"].language is Language.yue_hant
        for call in mlx.call_args_list
    )
    assert all(call.kwargs["vad_mode"] is VadMode.OFF for call in mlx.call_args_list)
    assert all(
        call.kwargs["chunk_duration_seconds"] == 30.0 for call in mlx.call_args_list
    )


def test_source_spec_normalizes_name():
    """Test source specifications normalize surrounding name whitespace."""
    source = TranscriptionSourceSpec(
        name=" whisper ", model=WHISPER_LARGE_V3_CANTONESE_MODEL
    )

    assert source.name == "whisper"


def test_source_validation_rejects_invalid_registries():
    """Test source construction rejects unsupported and ambiguous registries."""
    source = TranscriptionSourceSpec(
        name="whisper", model=WHISPER_LARGE_V3_CANTONESE_MODEL
    )
    with raises(ScinoephileError, match="does not support eng"):
        get_transcription_sources(Language.eng)
    with raises(ScinoephileError, match="does not support eng"):
        get_transcription_sources(
            Language.eng,
            source_specs=[
                source,
                TranscriptionSourceSpec(
                    name="whisper-2", model=WHISPER_LARGE_V3_CANTONESE_MODEL
                ),
            ],
        )
    with raises(ValueError, match="at least two"):
        get_transcription_sources(Language.yue_hant, source_specs=[source])
    with raises(ValueError, match="unique"):
        get_transcription_sources(Language.yue_hant, source_specs=[source, source])
