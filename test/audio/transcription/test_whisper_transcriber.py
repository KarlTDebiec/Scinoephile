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
    vad_on_transcriber.use_demucs = False
    vad_on_transcriber.use_vad = True

    vad_off_transcriber = object.__new__(WhisperTranscriber)
    vad_off_transcriber.cache_dir_path = Path("/tmp/whisper")
    vad_off_transcriber.model_name = "custom/model"
    vad_off_transcriber.language = "yue"
    vad_off_transcriber.use_demucs = False
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
    transcriber_one.use_demucs = False
    transcriber_one.use_vad = True

    transcriber_two = object.__new__(WhisperTranscriber)
    transcriber_two.cache_dir_path = Path("/tmp/whisper")
    transcriber_two.model_name = "model/two"
    transcriber_two.language = "yue"
    transcriber_two.use_demucs = False
    transcriber_two.use_vad = True

    cache_path_one = transcriber_one._get_cache_path(b"audio")
    cache_path_two = transcriber_two._get_cache_path(b"audio")

    assert cache_path_one is not None
    assert cache_path_two is not None
    assert cache_path_one != cache_path_two


def test_get_cache_path_can_use_original_audio_with_processed_input():
    """Test cache path can be derived from original audio bytes."""
    transcriber = object.__new__(WhisperTranscriber)
    transcriber.cache_dir_path = Path("/tmp/whisper")
    transcriber.model_name = "custom/model"
    transcriber.language = "yue"
    transcriber.use_demucs = False
    transcriber.use_vad = True

    original_cache_path = transcriber._get_cache_path(b"original-audio")
    processed_cache_path = transcriber._get_cache_path(b"processed-audio")

    assert original_cache_path is not None
    assert processed_cache_path is not None
    assert original_cache_path != processed_cache_path


def test_get_cache_path_separates_demucs_modes():
    """Test Whisper cache paths differ for Demucs-on and Demucs-off runs."""
    demucs_on_transcriber = object.__new__(WhisperTranscriber)
    demucs_on_transcriber.cache_dir_path = Path("/tmp/whisper")
    demucs_on_transcriber.model_name = "custom/model"
    demucs_on_transcriber.language = "yue"
    demucs_on_transcriber.use_demucs = True
    demucs_on_transcriber.use_vad = True

    demucs_off_transcriber = object.__new__(WhisperTranscriber)
    demucs_off_transcriber.cache_dir_path = Path("/tmp/whisper")
    demucs_off_transcriber.model_name = "custom/model"
    demucs_off_transcriber.language = "yue"
    demucs_off_transcriber.use_demucs = False
    demucs_off_transcriber.use_vad = True

    demucs_on_cache_path = demucs_on_transcriber._get_cache_path(b"audio")
    demucs_off_cache_path = demucs_off_transcriber._get_cache_path(b"audio")

    assert demucs_on_cache_path is not None
    assert demucs_off_cache_path is not None
    assert demucs_on_cache_path != demucs_off_cache_path
