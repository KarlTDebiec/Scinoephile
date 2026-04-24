#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of WhisperTranscriber."""

from __future__ import annotations

from pathlib import Path

from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber


def test_get_cache_path_separates_vad_modes_with_shared_cache_dir():
    """Test Whisper cache paths differ by VAD mode within one cache directory."""
    vad_on_transcriber = object.__new__(WhisperTranscriber)
    vad_on_transcriber.cache_dir_path = Path("/tmp/whisper")
    vad_on_transcriber.model_name = "custom/model"
    vad_on_transcriber.language = "yue"
    vad_on_transcriber.use_vad = True

    vad_off_transcriber = object.__new__(WhisperTranscriber)
    vad_off_transcriber.cache_dir_path = Path("/tmp/whisper")
    vad_off_transcriber.model_name = "custom/model"
    vad_off_transcriber.language = "yue"
    vad_off_transcriber.use_vad = False

    vad_on_cache_path = vad_on_transcriber._get_cache_path(b"audio")
    vad_off_cache_path = vad_off_transcriber._get_cache_path(b"audio")

    assert vad_on_cache_path is not None
    assert vad_off_cache_path is not None
    assert vad_on_cache_path.parent == Path("/tmp/whisper")
    assert vad_off_cache_path.parent == Path("/tmp/whisper")
    assert vad_on_cache_path != vad_off_cache_path


def test_get_cache_path_separates_models():
    """Test Whisper cache paths differ for different model names."""
    transcriber_one = object.__new__(WhisperTranscriber)
    transcriber_one.cache_dir_path = Path("/tmp/whisper")
    transcriber_one.model_name = "model/one"
    transcriber_one.language = "yue"
    transcriber_one.use_vad = True

    transcriber_two = object.__new__(WhisperTranscriber)
    transcriber_two.cache_dir_path = Path("/tmp/whisper")
    transcriber_two.model_name = "model/two"
    transcriber_two.language = "yue"
    transcriber_two.use_vad = True

    cache_path_one = transcriber_one._get_cache_path(b"audio")
    cache_path_two = transcriber_two._get_cache_path(b"audio")

    assert cache_path_one is not None
    assert cache_path_two is not None
    assert cache_path_one != cache_path_two
