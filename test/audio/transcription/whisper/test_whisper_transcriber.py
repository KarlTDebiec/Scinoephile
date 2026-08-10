#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the Whisper transcriber."""

from __future__ import annotations

import builtins
import json
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.audio.transcription import (
    DemucsMode,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionInferenceError,
    VADMode,
    get_segment_split_at_idx,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper.model import CANTONESE_MODEL, WhisperModel
from scinoephile.audio.transcription.whisper.transcriber import WhisperTranscriber
from scinoephile.common import package_root
from scinoephile.common.subprocess import run_command
from scinoephile.core import Language
from scinoephile.core.dependencies.transcription import import_whisper_timestamped
from test.helpers import parametrize

_OPTIONAL_TRANSCRIPTION_MODULES = (
    "demucs_infer",
    "huggingface_hub",
    "onnxruntime",
    "torch",
    "torchaudio",
    "transformers",
    "whisper_timestamped",
)

_TIMESTAMP_ALIGNMENT_ERROR = (
    "Inconsistent number of segments: whisper_segments (2) != "
    "timestamped_word_segments (1)"
)
"""Known assertion raised when Whisper Timestamped cannot align decoder output."""


def _get_model(model_name: str = "custom/model") -> WhisperModel:
    """Get a Whisper model for tests.

    Arguments:
        model_name: model name or local model path
    Returns:
        configured Whisper model
    """
    return WhisperModel(model_name, dict.fromkeys(Language, "yue"))


_CUSTOM_MODEL = _get_model()


def test_init_defaults_demucs_and_vad_to_off():
    """Test Whisper defaults Demucs and VAD to off."""
    transcriber = WhisperTranscriber()

    assert transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.vad_mode is VADMode.OFF
    assert transcriber.demucs_separator is None
    assert transcriber.model is CANTONESE_MODEL
    assert transcriber.language is Language.yue_hant
    assert transcriber.whisper_language == "yue"


def test_init_rejects_unsupported_language():
    """Test Whisper rejects a language unsupported by its model."""
    with raises(ValueError, match="eng is not supported"):
        WhisperTranscriber(language=Language.eng)


def _get_cache_path(transcriber: WhisperTranscriber, audio: AudioSegment) -> Path:
    """Get the cache path for the transcriber's first preprocessing settings."""
    settings = transcriber._get_preprocessing_settings()[0]
    cache_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_metadata(audio, settings)
    )
    return cache_path


def _get_ctc_aligner(text: str = "你好", model_name: str = "ctc/test-model") -> Mock:
    """Get a mock CTC aligner with one aligned output segment.

    Arguments:
        text: transcript text retained in aligned output
        model_name: CTC model identity
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
        language=Language.yue_hant, model_name=model_name, return_value=aligned_segments
    )


def _patch_whisper_timestamped(
    monkeypatch: MonkeyPatch, transcribe: Callable[..., object]
):
    """Patch Whisper Timestamped with the provided transcribe callable.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        transcribe: replacement Whisper Timestamped transcription callable
    """
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.transcriber."
        "import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )


@parametrize(
    ("field_name", "first_value", "second_value"),
    [
        ("vad_mode", VADMode.ON, VADMode.OFF),
        ("model", _get_model("model/one"), _get_model("model/two")),
        ("demucs_mode", DemucsMode.ON, DemucsMode.OFF),
        ("temperature", 0.0, (0.0, 0.2, 0.4)),
        ("condition_on_previous_text", True, False),
    ],
)
def test_get_cache_path_separates_configuration(
    tmp_path: Path, field_name: str, first_value: object, second_value: object
):
    """Test Whisper cache paths differ by cache-relevant configuration.

    Arguments:
        tmp_path: temporary cache directory path
        field_name: transcriber configuration field under test
        first_value: first transcriber field value
        second_value: second transcriber field value
    """
    audio = AudioSegment(data=b"audio", sample_width=1, frame_rate=8000, channels=1)
    if field_name == "demucs_mode":
        assert isinstance(first_value, DemucsMode)
        assert isinstance(second_value, DemucsMode)
        first_transcriber = WhisperTranscriber(
            cache_root_path=tmp_path, model=_CUSTOM_MODEL, demucs_mode=first_value
        )
        second_transcriber = WhisperTranscriber(
            cache_root_path=tmp_path, model=_CUSTOM_MODEL, demucs_mode=second_value
        )
    else:
        first_transcriber = WhisperTranscriber(
            cache_root_path=tmp_path, model=_CUSTOM_MODEL
        )
        second_transcriber = WhisperTranscriber(
            cache_root_path=tmp_path, model=_CUSTOM_MODEL
        )
        setattr(first_transcriber, field_name, first_value)
        setattr(second_transcriber, field_name, second_value)
    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path.parent == tmp_path / "whisper"
    assert second_cache_path.parent == tmp_path / "whisper"
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_audio_formats(tmp_path: Path):
    """Test Whisper cache paths include audio format metadata."""
    raw_data = b"\0\1" * 100
    first_audio = AudioSegment(
        data=raw_data, sample_width=2, frame_rate=16000, channels=1
    )
    second_audio = AudioSegment(
        data=raw_data, sample_width=2, frame_rate=8000, channels=1
    )
    transcriber = WhisperTranscriber(cache_root_path=tmp_path, model=_CUSTOM_MODEL)

    assert _get_cache_path(transcriber, first_audio) != _get_cache_path(
        transcriber, second_audio
    )


def test_get_cache_path_accepts_list_temperature_schedule(tmp_path: Path):
    """Test list and tuple temperature schedules use the same cache key."""
    audio = AudioSegment(data=b"audio", sample_width=1, frame_rate=8000, channels=1)
    list_transcriber = WhisperTranscriber(
        cache_root_path=tmp_path, model=_CUSTOM_MODEL, temperature=[0.0, 0.2, 0.4]
    )
    tuple_transcriber = WhisperTranscriber(
        cache_root_path=tmp_path, model=_CUSTOM_MODEL, temperature=(0.0, 0.2, 0.4)
    )

    assert _get_cache_path(list_transcriber, audio) == _get_cache_path(
        tuple_transcriber, audio
    )


def test_get_cache_path_includes_ctc_fallback_configuration(tmp_path: Path):
    """Test CTC fallback mode, language, and model contribute to cache identity.

    Arguments:
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    without_fallback = WhisperTranscriber(
        cache_root_path=tmp_path, model=_CUSTOM_MODEL, demucs_mode=DemucsMode.OFF
    )
    first_fallback = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=_get_ctc_aligner(),
    )
    second_model_fallback = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=_get_ctc_aligner(model_name="ctc/other-model"),
    )
    second_language_aligner = _get_ctc_aligner()
    second_language_aligner.language = Language.zho_hant
    second_language_fallback = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=second_language_aligner,
    )

    cache_paths = {
        _get_cache_path(transcriber, audio)
        for transcriber in (
            without_fallback,
            first_fallback,
            second_model_fallback,
            second_language_fallback,
        )
    }

    assert len(cache_paths) == 4
    settings = first_fallback._get_preprocessing_settings()[0]
    metadata = first_fallback._get_cache_metadata(audio, settings)
    assert metadata["timestamp_fallback"] == "ctc"
    assert metadata["timestamp_fallback_language"] == "yue-Hant"
    assert metadata["timestamp_fallback_model_name"] == "ctc/test-model"


def test_transcribe_forwards_recovery_decoding_options(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test Whisper receives configured defensive decoding options."""
    caplog.set_level(
        "DEBUG", logger="scinoephile.audio.transcription.whisper.transcriber"
    )
    transcribe = Mock(return_value={"segments": []})
    temperatures = (0.0, 0.2, 0.4)
    transcriber = WhisperTranscriber(
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        temperature=temperatures,
        condition_on_previous_text=False,
    )
    transcriber._loaded_model_instance = Mock()
    _patch_whisper_timestamped(monkeypatch, transcribe)
    audio = AudioSegment.silent(duration=1000)

    assert transcriber(audio) == []
    transcribe.assert_called_once()
    assert transcribe.call_args.kwargs["temperature"] == temperatures
    assert transcribe.call_args.kwargs["condition_on_previous_text"] is False
    assert transcribe.call_args.kwargs["sample_len"] == 32
    budget_record = next(
        record
        for record in caplog.records
        if "Whisper decoding budget per window" in record.message
    )
    assert budget_record.levelname == "DEBUG"
    assert not any("Whisper reached its" in record.message for record in caplog.records)


def test_transcribe_timestamped_success_does_not_use_ctc(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test successful Whisper Timestamped output bypasses native and CTC fallback.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ctc_aligner = _get_ctc_aligner()
    timestamped_transcribe = Mock(return_value={"segments": []})
    model = Mock()
    model.decode = Mock()
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber._loaded_model_instance = model
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
    decode = Mock()
    model = Mock()
    model.decode = decode

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

    def transcribe_natively(*_args: object, **_kwargs: object) -> dict[str, object]:
        """Return native text after confirming the decode method was restored."""
        assert model.decode is decode
        return {"text": transcript_text, "segments": native_segments}

    model.transcribe = Mock(side_effect=transcribe_natively)
    timestamped_transcribe = Mock(
        side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR)
    )
    temperatures = (0.0, 0.2, 0.4)
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        language=Language.yue_hant,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        temperature=temperatures,
        condition_on_previous_text=False,
        ctc_aligner=ctc_aligner,
    )
    transcriber._loaded_model_instance = model
    _patch_whisper_timestamped(monkeypatch, timestamped_transcribe)

    segments = transcriber(audio)

    assert len(segments) == 1
    assert segments[0].text == transcript_text
    assert segments[0].avg_logprob == -0.75
    assert segments[0].compression_ratio == 2.8
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
    assert model.decode is decode
    assert _get_cache_path(transcriber, audio).is_file()


def test_transcribe_timestamp_assertion_without_ctc_remains_error(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test Whisper timestamping assertions retain existing no-aligner behavior.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    decode = Mock()
    model = Mock()
    model.decode = decode
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._loaded_model_instance = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    with raises(
        TranscriptionInferenceError, match="Whisper inference failed with an assertion"
    ):
        transcriber(AudioSegment.silent(duration=1000))

    model.transcribe.assert_not_called()
    assert model.decode is decode


def test_transcribe_unrelated_assertion_does_not_use_ctc(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test only the known Whisper Timestamped alignment assertion triggers CTC.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ctc_aligner = _get_ctc_aligner()
    model = Mock()
    model.decode = Mock()
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber._loaded_model_instance = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError("unexpected assertion"))
    )

    with raises(TranscriptionInferenceError, match="unexpected assertion"):
        transcriber(AudioSegment.silent(duration=1000))

    model.transcribe.assert_not_called()
    ctc_aligner.assert_not_called()


@parametrize(
    ("native_output", "error_type", "message"),
    [
        (None, TranscriptionInferenceError, "malformed output"),
        ({}, TranscriptionInferenceError, "missing transcript text"),
        ({"text": None}, TranscriptionInferenceError, "missing transcript text"),
        ({"text": "   "}, TranscriptionEmptyError, "empty transcript"),
        ({"text": "你好"}, TranscriptionInferenceError, "malformed segments"),
        (
            {"text": "你好", "segments": [{"text": "你好"}]},
            TranscriptionInferenceError,
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
    """Test malformed and empty native Whisper fallback output is rejected.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
        native_output: output returned by native Whisper
        error_type: expected transcription exception type
        message: expected exception message fragment
    """
    ctc_aligner = _get_ctc_aligner()
    model = Mock()
    model.decode = Mock()
    model.transcribe.return_value = native_output
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber._loaded_model_instance = model
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
    model.decode = Mock()
    native_error = RuntimeError("decoder failed")
    model.transcribe.side_effect = native_error
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        ctc_aligner=ctc_aligner,
    )
    transcriber._loaded_model_instance = model
    _patch_whisper_timestamped(
        monkeypatch, Mock(side_effect=AssertionError(_TIMESTAMP_ALIGNMENT_ERROR))
    )

    with raises(
        TranscriptionInferenceError, match="Unable to run native Whisper fallback"
    ) as exc_info:
        transcriber(AudioSegment.silent(duration=1000))

    assert exc_info.value.__cause__ is native_error
    ctc_aligner.assert_not_called()


def test_transcribe_logs_when_decoding_window_reaches_token_limit(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Log exhausted decoder state even when Whisper discards the unfinished tail."""
    caplog.set_level(
        "INFO", logger="scinoephile.audio.transcription.whisper.transcriber"
    )
    decode = Mock(
        side_effect=[
            SimpleNamespace(tokens=list(range(32))),
            SimpleNamespace(tokens=list(range(32))),
            SimpleNamespace(tokens=list(range(31))),
        ]
    )

    def transcribe(model: Mock, *_args: object, **_kwargs: object) -> object:
        """Decode two windows and discard the exhausted tail from returned segments."""
        first_window = object()
        model.decode(first_window, object())
        model.decode(first_window, object())
        model.decode(object(), object())
        return {
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 0.5,
                    "text": "",
                    "tokens": list(range(8)),
                }
            ]
        }

    model = Mock()
    model.decode = decode
    transcriber = WhisperTranscriber(
        model=_CUSTOM_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    transcriber._loaded_model_instance = model
    _patch_whisper_timestamped(monkeypatch, Mock(side_effect=transcribe))
    audio = AudioSegment.silent(duration=1000)

    transcriber(audio)

    assert model.decode is decode
    limit_record = next(
        record
        for record in caplog.records
        if "Whisper reached its 32-token decoding limit" in record.message
    )
    assert limit_record.levelname == "INFO"
    assert "affected windows: 1" in limit_record.message


@parametrize(
    ("duration_ms", "expected"),
    [(100, 32), (1000, 32), (6530, 105), (14000, 224), (30000, 224)],
)
def test_get_sample_len_bounds_decode_by_audio_duration(
    duration_ms: int, expected: int
):
    """Bound the decode token budget while leaving room for dense speech.

    Arguments:
        duration_ms: source audio duration in milliseconds
        expected: expected Whisper token budget
    """
    audio = AudioSegment.silent(duration=duration_ms)

    assert WhisperTranscriber._get_sample_len(audio) == expected


def test_model_is_shared_across_decoding_configurations(monkeypatch: MonkeyPatch):
    """Reuse one loaded model across fallback transcription configurations."""
    loaded_model = Mock()
    whisper_timestamped = Mock()
    whisper_timestamped.load_model.return_value = loaded_model
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.transcriber."
        "import_whisper_timestamped",
        Mock(return_value=whisper_timestamped),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.transcriber.get_torch_device",
        Mock(return_value="cpu"),
    )
    WhisperTranscriber._models.clear()
    vad_transcriber = WhisperTranscriber(
        model=_CUSTOM_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.ON
    )
    no_vad_transcriber = WhisperTranscriber(
        model=_CUSTOM_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )

    try:
        assert vad_transcriber._loaded_model is loaded_model
        assert no_vad_transcriber._loaded_model is loaded_model
        whisper_timestamped.load_model.assert_called_once()
    finally:
        WhisperTranscriber._models.clear()


def test_transcribe_overwrites_matching_cache(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test cache overwrite removes the matching file before transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        overwrite_cache=True,
    )
    transcriber._loaded_model_instance = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("cached", encoding="utf-8")

    def transcribe(*_args: object, **_kwargs: object) -> dict[str, list[object]]:
        """Return empty output after confirming the old cache was removed."""
        assert not cache_path.exists()
        return {"segments": []}

    transcribe_mock = Mock(side_effect=transcribe)
    _patch_whisper_timestamped(monkeypatch, transcribe_mock)

    assert transcriber(audio) == []
    assert json.loads(cache_path.read_text(encoding="utf-8"))["segments"] == []
    transcribe_mock.assert_called_once()


def test_transcribe_recovers_from_malformed_cache(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test malformed cached output is replaced by a fresh transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._loaded_model_instance = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    transcribe = Mock(return_value={"segments": []})
    _patch_whisper_timestamped(monkeypatch, transcribe)

    assert transcriber.transcribe(audio) == []
    assert json.loads(cache_path.read_text(encoding="utf-8"))["segments"] == []
    transcribe.assert_called_once()


def test_transcribe_discards_invalid_cache_when_atomic_write_fails(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Test an invalid cache remains discarded when serialization fails.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_root_path=tmp_path,
        model=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._loaded_model_instance = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("existing cache", encoding="utf-8")
    transcribe = Mock(return_value={"segments": []})
    _patch_whisper_timestamped(monkeypatch, transcribe)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.cache.json.dump",
        Mock(side_effect=RuntimeError("write failed")),
    )

    with raises(RuntimeError, match="write failed"):
        transcriber.transcribe(audio)

    assert not cache_path.exists()


@parametrize(
    ("model_name", "expected"),
    [
        ("khleeloo/whisper-large-v3-cantonese", True),
        ("models/whisper.pt", False),
        ("models/whisper", False),
        ("/opt/models/whisper", False),
        ("large-v3", False),
    ],
)
def test_model_name_is_huggingface_repo_id_rejects_local_paths(
    monkeypatch: MonkeyPatch, model_name: str, expected: bool
):
    """Test HuggingFace retry is skipped for local filesystem paths.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model_name: model name to test
        expected: whether model name is a Hugging Face repository ID
    """

    def validate_repo_id(_: str):
        """Accept the repository ID."""

    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.transcriber."
        "import_huggingface_hub_utils",
        lambda: SimpleNamespace(
            HFValidationError=ValueError, validate_repo_id=validate_repo_id
        ),
    )
    transcriber = WhisperTranscriber(model=_get_model(model_name))

    assert transcriber._model_name_is_huggingface_repo_id() is expected


def test_model_name_is_huggingface_repo_id_rejects_validation_errors(
    monkeypatch: MonkeyPatch,
):
    """Test invalid Hugging Face repository IDs are rejected.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """

    def validate_repo_id(_: str):
        """Raise the validation error produced by Hugging Face Hub."""
        raise ValueError("invalid repository ID")

    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.transcriber."
        "import_huggingface_hub_utils",
        lambda: SimpleNamespace(
            HFValidationError=ValueError, validate_repo_id=validate_repo_id
        ),
    )
    transcriber = WhisperTranscriber(model=_get_model("invalid/repository/id"))

    assert not transcriber._model_name_is_huggingface_repo_id()


def test_transcription_imports_without_optional_runtime_dependencies():
    """Test importing transcription APIs does not require runtime extras."""
    script = dedent(
        f"""
        import importlib.abc
        import sys

        blocked_roots = {set(_OPTIONAL_TRANSCRIPTION_MODULES)!r}

        class Blocker(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path, target=None):
                if fullname.split(".", 1)[0] in blocked_roots:
                    raise ImportError(f"blocked optional dependency: {{fullname}}")
                return None

        sys.meta_path.insert(0, Blocker())

        from scinoephile.audio.transcription import (
            DemucsSeparator,
            TranscribedSegment,
            WhisperTranscriber,
            get_segment_split_at_idx,
        )
        from scinoephile.cli.transcribe_cli import TranscribeCli

        WhisperTranscriber()
        assert DemucsSeparator.__name__ == "DemucsSeparator"
        assert TranscribedSegment.__name__ == "TranscribedSegment"
        assert get_segment_split_at_idx.__name__ == "get_segment_split_at_idx"
        assert TranscribeCli.name() == "transcribe"
        """
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(package_root.parent), env.get("PYTHONPATH", "")]
    )
    exitcode, _, _ = run_command(
        [sys.executable, "-c", script], cwd_path=package_root.parent, env=env
    )

    assert exitcode == 0


def test_whisper_module_requires_transcription_extra(monkeypatch: MonkeyPatch):
    """Test Whisper import errors mention the transcription extra."""
    original_import = builtins.__import__

    def import_without_whisper(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        if name == "whisper_timestamped":
            raise ImportError("blocked optional dependency")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_whisper)

    with raises(ImportError, match="'transcription' extra"):
        import_whisper_timestamped()


def test_normalize_transcription_segments_coalesces_malformed_duplicate_pair():
    """Test malformed empty-text and duplicate-text segments are coalesced."""
    transcriber = WhisperTranscriber(model=_CUSTOM_MODEL)

    segments = [
        TranscribedSegment(
            id=8,
            seek=11520,
            start=156.4,
            end=159.97,
            text="",
            tokens=[],
            temperature=0.0,
            avg_logprob=-1.45,
            compression_ratio=0.0,
            no_speech_prob=1.11e-6,
            words=[
                TranscribedWord(text="照", start=156.4, end=156.85, confidence=0.385),
                TranscribedWord(text="先生", start=156.85, end=157.19, confidence=0.99),
                TranscribedWord(
                    text="你就", start=157.19, end=158.31, confidence=0.686
                ),
            ],
        ),
        TranscribedSegment(
            id=9,
            seek=14520,
            start=156.4,
            end=161.29,
            text="照先生你就",
            tokens=[1, 2, 3],
            temperature=0.0,
            avg_logprob=-0.44,
            compression_ratio=0.76,
            no_speech_prob=1.53e-6,
            words=None,
        ),
    ]

    normalized_segments = transcriber._normalize_transcription_segments(
        segments, source="cache", cache_path=Path("/tmp/whisper.json"), use_vad=True
    )

    assert len(normalized_segments) == 1
    assert normalized_segments[0].id == 9
    assert normalized_segments[0].start == 156.4
    assert normalized_segments[0].end == 161.29
    assert normalized_segments[0].text == "照先生你就"
    assert normalized_segments[0].words is not None
    assert [word.text for word in normalized_segments[0].words] == [
        "照",
        "先生",
        "你就",
    ]


def test_get_segment_split_at_idx_includes_segment_details_in_error():
    """Test split error includes identifying segment details."""
    segment = TranscribedSegment(
        id=9,
        seek=14520,
        start=156.4,
        end=161.29,
        text="照先生你就展示畀朕睇下係",
        words=None,
    )

    with raises(ValueError) as exc_info:
        get_segment_split_at_idx(segment, 3)

    assert str(exc_info.value) == (
        "Cannot split segment without word timing data: "
        "id=9 start=156.4 end=161.29 text='照先生你就展示畀朕睇下係' text_len=12."
    )
