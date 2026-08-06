#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the future-extensible transcription source registry."""

from __future__ import annotations

from unittest.mock import patch

from scinoephile.audio.transcription import VADMode
from scinoephile.audio.transcription.mlx_audio.backend import (
    FIRERED_ASR2_MODEL_NAME,
    GLM_ASR_MODEL_NAME,
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
    SENSEVOICE_MODEL_NAME,
)
from scinoephile.core import Language
from scinoephile.lang.transcription.sources import get_transcription_sources


def test_default_cantonese_registry_builds_all_six_sources_without_internal_vad():
    """The production registry should construct every equal-status ASR source."""
    with (
        patch("scinoephile.lang.transcription.sources.WhisperTranscriber") as whisper,
        patch("scinoephile.lang.transcription.sources.MlxAudioTranscriber") as mlx,
    ):
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
    assert whisper.call_args.kwargs["vad_mode"] is VADMode.OFF
    assert [call.kwargs["model_name"] for call in mlx.call_args_list] == [
        MIMO_MODEL_NAME,
        QWEN3_ASR_MODEL_NAME,
        SENSEVOICE_MODEL_NAME,
        FIRERED_ASR2_MODEL_NAME,
        GLM_ASR_MODEL_NAME,
    ]
    assert all(call.kwargs["vad_mode"] is VADMode.OFF for call in mlx.call_args_list)
    assert [call.kwargs["token_limit_guard"] for call in mlx.call_args_list] == [
        True,
        False,
        False,
        False,
        False,
    ]
