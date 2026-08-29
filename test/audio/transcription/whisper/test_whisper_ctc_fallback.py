#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Whisper native decoding with CTC timestamp fallback."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import MonkeyPatch, raises

from scinoephile.audio.transcription import (
    DemucsMode,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionRecognitionError,
    VadMode,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper.model import WhisperModel
from scinoephile.audio.transcription.whisper.model_spec import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModelSpec,
)
from scinoephile.audio.transcription.whisper.transcriber import WhisperTranscriber
from scinoephile.core import Language
from scinoephile.core.ml import ModelSpec
from test.helpers import parametrize

_CUSTOM_MODEL = replace(
    WHISPER_LARGE_V3_CANTONESE_MODEL, name="custom/model", revision="custom-revision"
)
_CTC_MODEL_SPEC = ModelSpec(name="ctc/test-model", revision="ctc-revision")
_SUBTITLE_CREDIT_TEXT = "字幕由 Amara.org 社群提供"
_TIMESTAMP_ALIGNMENT_ERROR = (
    "Inconsistent number of segments: whisper_segments (2) != "
    "timestamped_word_segments (1)"
)


def _get_cache_path(transcriber: WhisperTranscriber, audio: AudioSegment) -> Path:
    """Get the cache path for the transcriber's first preprocessing settings.

    Arguments:
        transcriber: Whisper transcriber
        audio: audio whose cache path is requested
    Returns:
        cache path for the first preprocessing settings
    """
    settings = transcriber._get_preprocessing_settings()[0]
    return transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )


def _get_ctc_aligner(text: str = "你好", spec: ModelSpec = _CTC_MODEL_SPEC) -> Mock:
    """Get a mock CTC aligner with one aligned output segment.

    Arguments:
        text: transcript text retained in aligned output
        spec: CTC model specification
    Returns:
        configured mock aligner
    """
    aligned_segments = [
        TranscribedSegment(
            id=0,
            seek=0,
            start=0.0,
            end=1.0,
            text=text,
            words=[TranscribedWord(text=text, start=0.0, end=1.0, confidence=1.0)],
        )
    ]
    return Mock(
        cache_config_identity={
            "alignment_version": 1,
            "device": "cpu",
            "language": Language.yue_hant.code,
            "model_name": spec.name,
            "model_revision": spec.revision,
            "runtime": {},
            "script_conversion": None,
        },
        language=Language.yue_hant,
        model=SimpleNamespace(spec=spec, device="cpu"),
        return_value=aligned_segments,
    )


def _get_whisper_transcriber(
    spec: WhisperModelSpec = WHISPER_LARGE_V3_CANTONESE_MODEL,
    language: Language = Language.yue_hant,
    device: str | None = "cpu",
    **kwargs: Any,
) -> WhisperTranscriber:
    """Get a Whisper transcriber with a configured executable model.

    Arguments:
        spec: Whisper model specification
        language: transcription language
        device: Torch device used for inference
        **kwargs: additional transcriber configuration
    Returns:
        configured Whisper transcriber
    """
    return WhisperTranscriber(
        model=WhisperModel(spec, language, device=device), language=language, **kwargs
    )


def _patch_whisper_timestamped(
    monkeypatch: MonkeyPatch, transcribe: Callable[..., object]
):
    """Patch Whisper Timestamped with the provided transcribe callable.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        transcribe: replacement transcription callable
    """
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )


def test_transcribe_timestamped_success_does_not_use_ctc(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test successful Whisper Timestamped output bypasses native CTC fallback.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ctc_aligner = _get_ctc_aligner()
    timestamped_transcribe = Mock(return_value={"segments": []})
    model = Mock()
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(monkeypatch, timestamped_transcribe)

    assert transcriber(AudioSegment.silent(duration=1000)) == []
    timestamped_transcribe.assert_called_once()
    model.transcribe.assert_not_called()
    ctc_aligner.assert_not_called()


def test_transcribe_falls_back_to_native_text_with_ctc_alignment(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test failed Whisper timestamping falls back to native text plus CTC.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcript_text = " 你好 "
    ctc_aligner = _get_ctc_aligner(transcript_text)
    model = Mock()
    native_segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 0.4,
            "text": " 你",
            "avg_logprob": -0.25,
            "compression_ratio": 0.8,
            "no_speech_prob": 0.1,
        },
        {
            "id": 1,
            "seek": 0,
            "start": 0.4,
            "end": 1.0,
            "text": "好 ",
            "avg_logprob": -0.75,
            "compression_ratio": 2.8,
            "no_speech_prob": 0.6,
        },
    ]
    model.transcribe.return_value = {
        "text": transcript_text,
        "segments": native_segments,
    }
    timestamped_transcribe = Mock(
        side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR)
    )
    temperatures = (0.0, 0.2, 0.4)
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        language=Language.yue_hant,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        temperature=temperatures,
        condition_on_previous_text=False,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(monkeypatch, timestamped_transcribe)

    segments = transcriber(audio)

    assert len(segments) == 1
    assert segments[0].text == transcript_text
    assert segments[0].avg_logprob == -0.75
    assert segments[0].compression_ratio == 0.5
    assert segments[0].no_speech_prob == 0.6
    timestamped_transcribe.assert_called_once()
    model.transcribe.assert_called_once()
    assert model.transcribe.call_args.kwargs == {
        "language": "yue",
        "temperature": temperatures,
        "condition_on_previous_text": False,
        "sample_len": 32,
        "word_timestamps": False,
        "verbose": False,
    }
    ctc_aligner.assert_called_once_with(audio, transcript_text)
    assert _get_cache_path(transcriber, audio).is_file()


def test_transcribe_discards_ctc_aligned_terminal_credit(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test CTC-aligned fallback output receives Whisper normalization.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcript_text = _SUBTITLE_CREDIT_TEXT
    ctc_aligner = _get_ctc_aligner(transcript_text)
    model = Mock()
    model.transcribe.return_value = {
        "text": transcript_text,
        "segments": [
            {
                "id": 0,
                "seek": 0,
                "start": 0.0,
                "end": 1.0,
                "text": transcript_text,
                "no_speech_prob": 0.824,
            }
        ],
    }
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    assert transcriber(audio) == []


def test_transcribe_timestamp_assertion_without_ctc_remains_error(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test timestamping assertions retain existing no-aligner behavior.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    model = Mock()
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    with raises(
        TranscriptionRecognitionError,
        match="Whisper inference failed with an assertion",
    ):
        transcriber(AudioSegment.silent(duration=1000))

    model.transcribe.assert_not_called()


def test_transcribe_unrelated_assertion_does_not_use_ctc(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test only the known timestamping assertion triggers CTC fallback.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ctc_aligner = _get_ctc_aligner()
    model = Mock()
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError("unexpected assertion"))
    )

    with raises(TranscriptionRecognitionError, match="unexpected assertion"):
        transcriber(AudioSegment.silent(duration=1000))

    model.transcribe.assert_not_called()
    ctc_aligner.assert_not_called()


@parametrize(
    ("native_output", "error_type", "message"),
    [
        (None, TranscriptionRecognitionError, "malformed output"),
        ({}, TranscriptionRecognitionError, "missing transcript text"),
        ({"text": None}, TranscriptionRecognitionError, "missing transcript text"),
        ({"text": "   "}, TranscriptionEmptyError, "empty transcript"),
        ({"text": "你好"}, TranscriptionRecognitionError, "malformed segments"),
        (
            {"text": "你好", "segments": [{"text": "你好"}]},
            TranscriptionRecognitionError,
            "malformed segments",
        ),
    ],
)
def test_transcribe_rejects_invalid_native_fallback_output(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    native_output: object,
    error_type: type[TranscriptionError],
    message: str,
):
    """Test malformed and empty native fallback output is rejected.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
        native_output: simulated native Whisper output
        error_type: expected transcription exception type
        message: expected exception message fragment
    """
    ctc_aligner = _get_ctc_aligner()
    model = Mock()
    model.transcribe.return_value = native_output
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    with raises(error_type, match=message):
        transcriber(AudioSegment.silent(duration=1000))

    ctc_aligner.assert_not_called()


def test_transcribe_wraps_native_fallback_failure(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test native Whisper decoding failures become transcription errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ctc_aligner = _get_ctc_aligner()
    model = Mock()
    native_error = RuntimeError("decoder failed")
    model.transcribe.side_effect = native_error
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber.model.model = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    with raises(
        TranscriptionRecognitionError, match="Unable to run native Whisper fallback"
    ) as exc_info:
        transcriber(AudioSegment.silent(duration=1000))

    assert exc_info.value.__cause__ is native_error
    ctc_aligner.assert_not_called()
