#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of WhisperTranscriber."""

from __future__ import annotations

import builtins
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import MonkeyPatch, importorskip, raises

from scinoephile.audio.transcription import (
    DemucsMode,
    VADMode,
    get_segment_split_at_idx,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.common import package_root
from scinoephile.common.subprocess import run_command
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


def test_init_defaults_preprocessing_to_auto():
    """Test Whisper defaults both preprocessing dimensions to automatic."""
    transcriber = WhisperTranscriber()

    assert transcriber.demucs_mode is DemucsMode.AUTO
    assert transcriber.vad_mode is VADMode.AUTO


def _get_cache_path(
    transcriber: WhisperTranscriber,
    audio: AudioSegment,
) -> Path:
    """Get the cache path for the transcriber's first configured attempt."""
    attempt = transcriber._get_attempts()[0]
    cache_path = transcriber._cache.get_path(
        audio,
        transcriber._get_cache_metadata(attempt),
    )
    assert cache_path is not None
    return cache_path


@parametrize(
    ("field_name", "first_value", "second_value"),
    [
        ("vad_mode", VADMode.ON, VADMode.OFF),
        ("model_name", "model/one", "model/two"),
        ("demucs_mode", DemucsMode.ON, DemucsMode.OFF),
        ("temperature", 0.0, (0.0, 0.2, 0.4)),
        ("condition_on_previous_text", True, False),
    ],
)
def test_get_cache_path_separates_configuration(
    tmp_path: Path,
    field_name: str,
    first_value: object,
    second_value: object,
):
    """Test Whisper cache paths differ by cache-relevant configuration.

    Arguments:
        tmp_path: temporary cache directory path
        field_name: transcriber configuration field under test
        first_value: first transcriber field value
        second_value: second transcriber field value
    """
    audio = AudioSegment(
        data=b"audio",
        sample_width=1,
        frame_rate=8000,
        channels=1,
    )
    first_transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
    )
    second_transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
    )
    setattr(first_transcriber, field_name, first_value)
    setattr(second_transcriber, field_name, second_value)
    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path.parent == tmp_path
    assert second_cache_path.parent == tmp_path
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_audio_formats(tmp_path: Path):
    """Test Whisper cache paths include audio format metadata."""
    raw_data = b"\0\1" * 100
    first_audio = AudioSegment(
        data=raw_data,
        sample_width=2,
        frame_rate=16000,
        channels=1,
    )
    second_audio = AudioSegment(
        data=raw_data,
        sample_width=2,
        frame_rate=8000,
        channels=1,
    )
    transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
    )

    assert _get_cache_path(transcriber, first_audio) != _get_cache_path(
        transcriber,
        second_audio,
    )


def test_get_cache_path_accepts_list_temperature_schedule(tmp_path: Path):
    """Test list and tuple temperature schedules use the same cache key."""
    audio = AudioSegment(
        data=b"audio",
        sample_width=1,
        frame_rate=8000,
        channels=1,
    )
    list_transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
        temperature=[0.0, 0.2, 0.4],
    )
    tuple_transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
        temperature=(0.0, 0.2, 0.4),
    )

    assert _get_cache_path(list_transcriber, audio) == _get_cache_path(
        tuple_transcriber,
        audio,
    )


def test_transcribe_forwards_recovery_decoding_options(monkeypatch: MonkeyPatch):
    """Test Whisper receives configured defensive decoding options."""
    whisper = Mock()
    whisper.transcribe.return_value = {"segments": []}
    temperatures = (0.0, 0.2, 0.4)
    transcriber = WhisperTranscriber(
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        temperature=temperatures,
        condition_on_previous_text=False,
    )
    transcriber._model = Mock()
    monkeypatch.setattr(transcriber, "_get_whisper_module", Mock(return_value=whisper))
    audio = AudioSegment.silent(duration=1000)

    assert transcriber(audio) == []
    whisper.transcribe.assert_called_once()
    assert whisper.transcribe.call_args.kwargs["temperature"] == temperatures
    assert whisper.transcribe.call_args.kwargs["condition_on_previous_text"] is False
    assert whisper.transcribe.call_args.kwargs["sample_len"] == 32


@parametrize(
    ("duration_ms", "expected"),
    [
        (100, 32),
        (1000, 32),
        (6530, 105),
        (14000, 224),
        (30000, 224),
    ],
)
def test_get_sample_len_bounds_decode_by_audio_duration(
    duration_ms: int,
    expected: int,
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
    whisper = Mock()
    loaded_model = Mock()
    whisper.load_model.return_value = loaded_model
    monkeypatch.setattr(
        WhisperTranscriber,
        "_get_whisper_module",
        Mock(return_value=whisper),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper_transcriber.get_torch_device",
        Mock(return_value="cpu"),
    )
    WhisperTranscriber._models.clear()
    vad_transcriber = WhisperTranscriber(
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.ON,
    )
    no_vad_transcriber = WhisperTranscriber(
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )

    try:
        assert vad_transcriber.model is loaded_model
        assert no_vad_transcriber.model is loaded_model
        whisper.load_model.assert_called_once()
    finally:
        WhisperTranscriber._models.clear()


def test_transcribe_overwrites_matching_cache(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test cache overwrite removes the matching file before transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._model = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("cached", encoding="utf-8")
    whisper = Mock()

    def transcribe(*_args: object, **_kwargs: object) -> dict[str, list[object]]:
        """Return empty output after confirming the old cache was removed."""
        assert not cache_path.exists()
        return {"segments": []}

    whisper.transcribe.side_effect = transcribe
    monkeypatch.setattr(
        transcriber,
        "_get_whisper_module",
        Mock(return_value=whisper),
    )

    assert transcriber(audio, overwrite_cache=True) == []
    assert json.loads(cache_path.read_text(encoding="utf-8"))["segments"] == []
    whisper.transcribe.assert_called_once()


def test_transcribe_recovers_from_malformed_cache(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test malformed cached output is replaced by a fresh transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._model = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    whisper = Mock()
    whisper.transcribe.return_value = {"segments": []}
    monkeypatch.setattr(
        transcriber,
        "_get_whisper_module",
        Mock(return_value=whisper),
    )

    assert transcriber.transcribe(audio) == []
    assert json.loads(cache_path.read_text(encoding="utf-8"))["segments"] == []
    whisper.transcribe.assert_called_once()


def test_transcribe_preserves_cache_when_atomic_write_fails(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test failed cache serialization does not corrupt an existing cache file.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = WhisperTranscriber(
        cache_dir_path=tmp_path,
        model_name="custom/model",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
    )
    transcriber._model = Mock()
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("existing cache", encoding="utf-8")
    whisper = Mock()
    whisper.transcribe.return_value = {"segments": []}
    monkeypatch.setattr(
        transcriber,
        "_get_whisper_module",
        Mock(return_value=whisper),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.cache.json.dump",
        Mock(side_effect=RuntimeError("write failed")),
    )

    with raises(RuntimeError, match="write failed"):
        transcriber.transcribe(audio)

    assert cache_path.read_text(encoding="utf-8") == "existing cache"


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
    model_name: str,
    expected: bool,
):
    """Test HuggingFace retry is skipped for local filesystem paths."""
    importorskip("huggingface_hub")
    transcriber = WhisperTranscriber(model_name=model_name)

    assert transcriber._model_name_is_huggingface_repo_id() is expected


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
        [sys.executable, "-c", script],
        cwd_path=package_root.parent,
        env=env,
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
        WhisperTranscriber._get_whisper_module()


def test_normalize_transcription_segments_coalesces_malformed_duplicate_pair():
    """Test malformed empty-text and duplicate-text segments are coalesced."""
    transcriber = WhisperTranscriber(model_name="custom/model")

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
                TranscribedWord(
                    text="先生",
                    start=156.85,
                    end=157.19,
                    confidence=0.99,
                ),
                TranscribedWord(
                    text="你就",
                    start=157.19,
                    end=158.31,
                    confidence=0.686,
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
        segments,
        source="cache",
        cache_path=Path("/tmp/whisper.json"),
        use_vad=True,
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
