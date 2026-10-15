#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the application-wide cache namespace registry."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription import TranscriptionCache
from scinoephile.audio.transcription.mlx_audio import (
    MlxAudioRecognitionCache,
    MlxAudioRecognitionResult,
)
from scinoephile.core.cache.operations import clear_cache, get_cache_entries
from scinoephile.workflows.cache_registry import CACHE_REGISTRY


def test_cache_registry_matches_owned_layout():
    """Test the registry contains the complete Scinoephile-owned cache layout."""
    assert {namespace.value for namespace in CACHE_REGISTRY} == {
        "audio/classification/event",
        "audio/classification/language",
        "audio/diarization",
        "audio/separation/demucs",
        "audio/transcription/ctc",
        "audio/transcription/mlx_audio",
        "audio/transcription/mlx_audio/recognition",
        "audio/transcription/whisper",
        "audio/vad",
        "dictionaries/cuhk/discovery",
        "dictionaries/cuhk/pages",
        "image/ocr/lens",
        "image/ocr/paddle",
        "image/ocr/tesseract/legacy_data",
        "image/ocr/tesseract/results",
        "lang/zho/subtitles/analysis",
        "llms/<operation>",
        "media/subtitles",
    }


@pytest.mark.parametrize("clear_recognition", [False, True])
def test_mlx_cache_layers_have_independent_entry_boundaries(
    tmp_path: Path, clear_recognition: bool
):
    """Inspect and clear either MLX cache without touching its other layer.

    Arguments:
        tmp_path: temporary cache root path
        clear_recognition: whether to clear recognition instead of aligned output
    """
    audio = AudioSegment.silent(duration=100)
    recognition_path = MlxAudioRecognitionCache(tmp_path).save(
        audio, {}, MlxAudioRecognitionResult(text="你好", generation_tokens=2)
    )
    aligned_path = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_MLX_AUDIO, "mlx-audio", "MLX-Audio"
    ).save(audio, {}, [])
    namespace = AudioCacheNamespace.TRANSCRIPTION_MLX_AUDIO.value
    selected_path = aligned_path
    protected_path = recognition_path
    if clear_recognition:
        namespace = AudioCacheNamespace.TRANSCRIPTION_MLX_AUDIO_RECOGNITION.value
        selected_path = recognition_path
        protected_path = aligned_path

    entries = get_cache_entries(tmp_path, CACHE_REGISTRY, namespace=namespace)

    assert [entry.path for entry in entries] == [selected_path]
    assert len(get_cache_entries(tmp_path, CACHE_REGISTRY)) == 2
    removed = clear_cache(tmp_path, CACHE_REGISTRY, namespace=namespace)
    assert [entry.path for entry in removed] == [selected_path]
    assert not selected_path.exists()
    assert protected_path.is_file()
