#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the executable Whisper model."""

from __future__ import annotations

import builtins
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

from pydub import AudioSegment
from pytest import MonkeyPatch, raises

from scinoephile.audio.transcription import DemucsMode, VadMode
from scinoephile.audio.transcription.whisper.model import WhisperModel
from scinoephile.audio.transcription.whisper.model_spec import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
)
from scinoephile.audio.transcription.whisper.transcriber import WhisperTranscriber
from scinoephile.core import DependencyError, Language
from scinoephile.core.dependencies.transcription import import_whisper_timestamped
from test.helpers import parametrize

_CUSTOM_MODEL = replace(
    WHISPER_LARGE_V3_CANTONESE_MODEL, name="custom/model", revision="custom-revision"
)


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

    model = WhisperModel(_CUSTOM_MODEL, Language.yue_hant)

    assert model.get_sample_len(audio) == expected


def test_model_selects_available_device_lazily(monkeypatch: MonkeyPatch):
    """Select the available Torch device only when first needed.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    get_torch_device = Mock(return_value="mps")
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.get_torch_device",
        get_torch_device,
    )

    model = WhisperModel(_CUSTOM_MODEL, Language.yue_hant)

    get_torch_device.assert_not_called()
    assert model.device == "mps"
    assert model.device == "mps"
    get_torch_device.assert_called_once_with()


def test_model_honors_explicit_device(monkeypatch: MonkeyPatch):
    """Honor an explicit Torch device without running auto-selection.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    get_torch_device = Mock(return_value="mps")
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.get_torch_device",
        get_torch_device,
    )

    model = WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu")

    assert model.device == "cpu"
    get_torch_device.assert_not_called()


def test_model_is_shared_across_decoding_configurations(monkeypatch: MonkeyPatch):
    """Share one executable model across transcription configurations.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    loaded_model = Mock()
    whisper_timestamped = Mock()
    whisper_timestamped.load_model.return_value = loaded_model
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=whisper_timestamped),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.get_torch_device",
        Mock(return_value="cpu"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model."
        "get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/snapshot")),
    )
    model = WhisperModel(_CUSTOM_MODEL, Language.yue_hant)
    vad_transcriber = WhisperTranscriber(
        model, Language.yue_hant, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.ON
    )
    no_vad_transcriber = WhisperTranscriber(
        model, Language.yue_hant, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.OFF
    )

    assert vad_transcriber.model is model
    assert no_vad_transcriber.model is model
    assert vad_transcriber.model.model is loaded_model
    assert no_vad_transcriber.model.model is loaded_model
    whisper_timestamped.load_model.assert_called_once()


def test_default_model_loads_from_pinned_snapshot(monkeypatch: MonkeyPatch):
    """Resolve the default model's immutable revision before Whisper loading.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    loaded_model = Mock()
    whisper_timestamped = SimpleNamespace(load_model=Mock(return_value=loaded_model))
    get_snapshot_dir_path = Mock(return_value=Path("/cached/snapshot"))
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.get_torch_device",
        Mock(return_value="cpu"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=whisper_timestamped),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model."
        "get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    model = WhisperModel(WHISPER_LARGE_V3_CANTONESE_MODEL, Language.yue_hant)

    assert model.model is loaded_model
    get_snapshot_dir_path.assert_called_once_with(
        WHISPER_LARGE_V3_CANTONESE_MODEL.name, WHISPER_LARGE_V3_CANTONESE_MODEL.revision
    )
    whisper_timestamped.load_model.assert_called_once_with(
        "/cached/snapshot", device="cpu"
    )


def test_model_retries_with_complete_snapshot_after_missing_cached_file(
    monkeypatch: MonkeyPatch,
):
    """Retry model loading with a complete snapshot after a missing cached file.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    loaded_model = Mock()
    load_model = Mock(side_effect=[FileNotFoundError, loaded_model])
    whisper_timestamped = SimpleNamespace(load_model=load_model)
    snapshot_download = Mock(return_value="/downloaded/snapshot")
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=whisper_timestamped),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_huggingface_hub",
        Mock(return_value=SimpleNamespace(snapshot_download=snapshot_download)),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model."
        "get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/snapshot")),
    )
    model = WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu")

    assert model.model is loaded_model
    assert load_model.call_args_list == [
        call("/cached/snapshot", device="cpu"),
        call("/downloaded/snapshot", device="cpu"),
    ]
    snapshot_download.assert_called_once_with(
        repo_id=_CUSTOM_MODEL.name, revision=_CUSTOM_MODEL.revision
    )


def test_whisper_module_requires_transcription_extra(monkeypatch: MonkeyPatch):
    """Test Whisper import errors mention the transcription extra.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    original_import = builtins.__import__

    def import_without_whisper(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Import modules while simulating an unavailable Whisper dependency.

        Arguments:
            name: module name
            globals: calling module globals
            locals: calling module locals
            fromlist: requested names imported from the module
            level: relative import level
        Returns:
            imported module or object

        Raises:
            ImportError: if Whisper Timestamped is requested
        """
        if name == "whisper_timestamped":
            raise ImportError("blocked optional dependency")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_whisper)

    with raises(DependencyError, match="'transcription' extra"):
        import_whisper_timestamped()
