#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the Whisper transcriber."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.audio.transcription import (
    DemucsMode,
    VadMode,
    get_segment_split_at_idx,
)
from scinoephile.audio.transcription.quality import get_transcription_quality_issue
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModelSpec,
)
from scinoephile.audio.transcription.whisper.model import WhisperModel
from scinoephile.audio.transcription.whisper.transcriber import WhisperTranscriber
from scinoephile.common import package_root
from scinoephile.common.subprocess import run_command
from scinoephile.core import Language
from scinoephile.core.ml import ModelSpec
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

_CUSTOM_MODEL = replace(
    WHISPER_LARGE_V3_CANTONESE_MODEL, name="custom/model", revision="custom-revision"
)

_CTC_MODEL_SPEC = ModelSpec(name="ctc/test-model", revision="ctc-revision")
"""CTC model specification used by Whisper fallback tests."""


def _get_whisper_transcriber(
    spec: WhisperModelSpec = WHISPER_LARGE_V3_CANTONESE_MODEL,
    language: Language = Language.yue_hant,
    device: str | None = "cpu",
    **kwargs: Any,
) -> WhisperTranscriber:
    """Get a Whisper transcriber with a configured executable model.

    Arguments:
        spec: Whisper model specification
        language: language to transcribe
        device: Torch device passed to the executable model
        **kwargs: additional Whisper transcriber arguments
    Returns:
        configured Whisper transcriber
    """
    return WhisperTranscriber(
        model=WhisperModel(spec, language, device=device), language=language, **kwargs
    )


def test_init_defaults_demucs_and_vad_to_off():
    """Test Whisper defaults Demucs and VAD to off."""
    transcriber = _get_whisper_transcriber()

    assert transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.vad_mode is VadMode.OFF
    assert transcriber.demucs_separator is None
    assert transcriber.model.spec is WHISPER_LARGE_V3_CANTONESE_MODEL
    assert transcriber.language is Language.yue_hant
    assert transcriber.recovery_transcriber is None


@parametrize("language", [Language.yue_hans, Language.yue_hant])
def test_init_derives_whisper_language(language: Language):
    """Test the model derives its Whisper language code.

    Arguments:
        language: language to transcribe
    """
    transcriber = _get_whisper_transcriber(language=language)

    assert transcriber.language is language
    assert transcriber.model.language_code == "yue"


def test_init_rejects_unsupported_language():
    """Test Whisper rejects a language unsupported by its model."""
    with raises(ValueError, match="eng is not supported"):
        _get_whisper_transcriber(language=Language.eng)


def _get_cache_path(transcriber: WhisperTranscriber, audio: AudioSegment) -> Path:
    """Get the cache path for the transcriber's first preprocessing settings.

    Arguments:
        transcriber: Whisper transcriber
        audio: audio whose cache path is requested
    Returns:
        cache path for the first preprocessing settings
    """
    settings = transcriber._get_preprocessing_settings()[0]
    cache_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )
    return cache_path


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
            "runtime": {
                "torch": {"distribution": "torch", "version": "test-version"},
                "transformers": {
                    "distribution": "transformers",
                    "version": "test-version",
                },
            },
            "script_conversion": None,
        },
        language=Language.yue_hant,
        model=SimpleNamespace(spec=spec, device="cpu"),
        return_value=aligned_segments,
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
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )


@parametrize(
    ("field_name", "first_value", "second_value"),
    [
        ("vad_mode", VadMode.ON, VadMode.OFF),
        (
            "spec",
            replace(_CUSTOM_MODEL, name="model/one"),
            replace(_CUSTOM_MODEL, name="model/two"),
        ),
        (
            "spec",
            replace(_CUSTOM_MODEL, revision="revision-one"),
            replace(_CUSTOM_MODEL, revision="revision-two"),
        ),
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
    if field_name == "spec":
        assert isinstance(first_value, WhisperModelSpec)
        assert isinstance(second_value, WhisperModelSpec)
        first_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=first_value
        )
        second_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=second_value
        )
    elif field_name == "demucs_mode":
        assert isinstance(first_value, DemucsMode)
        assert isinstance(second_value, DemucsMode)
        first_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=_CUSTOM_MODEL, demucs_mode=first_value
        )
        second_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=_CUSTOM_MODEL, demucs_mode=second_value
        )
    else:
        first_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=_CUSTOM_MODEL
        )
        second_transcriber = _get_whisper_transcriber(
            cache_root_path=tmp_path, spec=_CUSTOM_MODEL
        )
        setattr(first_transcriber, field_name, first_value)
        setattr(second_transcriber, field_name, second_value)
    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path.parent == tmp_path / "audio/transcription/whisper"
    assert second_cache_path.parent == tmp_path / "audio/transcription/whisper"
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_devices(tmp_path: Path):
    """Test Whisper cache paths differ by inference device.

    Arguments:
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment(data=b"audio", sample_width=1, frame_rate=8000, channels=1)
    cpu_transcriber = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
    )
    mps_transcriber = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="mps"),
        Language.yue_hant,
        cache_root_path=tmp_path,
    )

    assert _get_cache_path(cpu_transcriber, audio) != _get_cache_path(
        mps_transcriber, audio
    )


def test_get_cache_path_separates_audio_formats(tmp_path: Path):
    """Test Whisper cache paths include audio format identity.

    Arguments:
        tmp_path: temporary cache directory path
    """
    raw_data = b"\0\1" * 100
    first_audio = AudioSegment(
        data=raw_data, sample_width=2, frame_rate=16000, channels=1
    )
    second_audio = AudioSegment(
        data=raw_data, sample_width=2, frame_rate=8000, channels=1
    )
    transcriber = _get_whisper_transcriber(cache_root_path=tmp_path, spec=_CUSTOM_MODEL)

    assert _get_cache_path(transcriber, first_audio) != _get_cache_path(
        transcriber, second_audio
    )


def test_get_cache_path_accepts_list_temperature_schedule(tmp_path: Path):
    """Test list and tuple temperature schedules use the same cache key.

    Arguments:
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment(data=b"audio", sample_width=1, frame_rate=8000, channels=1)
    list_transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path, spec=_CUSTOM_MODEL, temperature=[0.0, 0.2, 0.4]
    )
    tuple_transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path, spec=_CUSTOM_MODEL, temperature=(0.0, 0.2, 0.4)
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
    without_fallback = _get_whisper_transcriber(
        cache_root_path=tmp_path, spec=_CUSTOM_MODEL, demucs_mode=DemucsMode.OFF
    )
    first_fallback = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=_get_ctc_aligner(),
    )
    second_model_fallback = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=_get_ctc_aligner(
            spec=ModelSpec(name="ctc/other-model", revision="ctc-other-revision")
        ),
    )
    second_revision_fallback = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=_get_ctc_aligner(
            spec=ModelSpec(name="ctc/test-model", revision="revision-two")
        ),
    )
    second_language_aligner = _get_ctc_aligner()
    second_language_aligner.language = Language.zho_hant
    second_language_aligner.cache_config_identity = {
        **second_language_aligner.cache_config_identity,
        "language": Language.zho_hant.code,
    }
    second_language_fallback = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        ctc_aligner=second_language_aligner,
    )

    cache_paths = {
        _get_cache_path(transcriber, audio)
        for transcriber in (
            without_fallback,
            first_fallback,
            second_model_fallback,
            second_revision_fallback,
            second_language_fallback,
        )
    }

    assert len(cache_paths) == 5
    settings = first_fallback._get_preprocessing_settings()[0]
    cache_identity = first_fallback._get_cache_identity(audio, settings)
    fallback_identity = cast(Mapping[str, object], cache_identity["timestamp_fallback"])
    assert first_fallback.ctc_aligner is not None
    assert fallback_identity == first_fallback.ctc_aligner.cache_config_identity
    assert fallback_identity["alignment_version"] == 1
    assert fallback_identity["device"] == "cpu"
    assert fallback_identity["language"] == "yue-Hant"
    assert fallback_identity["model_name"] == "ctc/test-model"
    assert fallback_identity["model_revision"] == "ctc-revision"
    runtime_identity = cast(Mapping[str, Mapping[str, str]], cache_identity["runtime"])
    assert runtime_identity["openai_whisper"]["distribution"] == ("openai-whisper")
    assert runtime_identity["torch"]["distribution"] == "torch"
    assert runtime_identity["whisper_timestamped"]["distribution"] == (
        "whisper-timestamped"
    )


def test_transcribe_forwards_recovery_decoding_options(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test Whisper receives configured defensive decoding options.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        caplog: pytest log-capture fixture
    """
    caplog.set_level(
        "DEBUG", logger="scinoephile.audio.transcription.whisper.transcriber"
    )
    transcribe = Mock(return_value={"segments": []})
    temperatures = (0.0, 0.2, 0.4)
    transcriber = _get_whisper_transcriber(
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        temperature=temperatures,
        condition_on_previous_text=False,
    )
    transcriber.model.model = Mock()
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


def test_transcribe_overwrites_matching_cache(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test cache overwrite removes the matching file before transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        overwrite_cache=True,
    )
    transcriber.model.model = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("cached", encoding="utf-8")

    def transcribe(*_args: object, **_kwargs: object) -> dict[str, list[object]]:
        """Return empty output after confirming the old cache was removed.

        Arguments:
            *_args: ignored positional arguments
            **_kwargs: ignored keyword arguments
        Returns:
            empty Whisper output
        """
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
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    transcriber.model.model = Mock()
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
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    transcriber.model.model = Mock()
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

        from scinoephile.audio.separation import DemucsSeparator
        from scinoephile.audio.transcription import (
            TranscribedSegment,
            get_segment_split_at_idx,
        )
        from scinoephile.audio.transcription.whisper import (
            WHISPER_LARGE_V3_CANTONESE_MODEL,
            WhisperModel,
            WhisperTranscriber,
        )
        from scinoephile.cli.transcribe_cli import TranscribeCli
        from scinoephile.core import Language

        WhisperTranscriber(
            WhisperModel(WHISPER_LARGE_V3_CANTONESE_MODEL, Language.yue_hant),
            Language.yue_hant,
        )
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


def test_transcribe_recovers_after_repetitive_cached_output(tmp_path: Path):
    """Test temperature fallback recovers an unusable deterministic cache.

    Arguments:
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = _get_whisper_transcriber(
        cache_root_path=tmp_path,
        spec=_CUSTOM_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        recover_decoding=True,
    )
    recovery_transcriber = transcriber.recovery_transcriber
    assert recovery_transcriber is not None
    settings = transcriber._get_preprocessing_settings()[0]
    repeated_segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=1.0,
        text="呀" * 100,
        compression_ratio=37.0,
        words=[TranscribedWord(text="呀" * 100, start=0.0, end=1.0, confidence=1.0)],
    )
    transcriber._cache.save(
        audio, transcriber._get_cache_identity(audio, settings), [repeated_segment]
    )
    recovered_segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=1.0,
        text="救命呀",
        compression_ratio=0.5,
        words=[TranscribedWord(text="救命呀", start=0.0, end=1.0, confidence=1.0)],
    )
    recovery_path = recovery_transcriber._cache.save(
        audio,
        recovery_transcriber._get_cache_identity(audio, settings),
        [recovered_segment],
    )

    segments = transcriber(
        audio,
        is_usable=lambda candidate: get_transcription_quality_issue(candidate) is None,
    )

    assert segments == [recovered_segment]
    assert transcriber.last_cache_key_sha256 == recovery_path.stem


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
