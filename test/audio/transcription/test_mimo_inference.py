#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of direct MiMo inference."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import mimo_inference


@pytest.fixture(autouse=True)
def clear_mimo_model_cache(monkeypatch: pytest.MonkeyPatch):
    """Clear the in-process MiMo model cache between tests."""
    monkeypatch.setattr(mimo_inference, "_MLX_MODEL_BY_REFERENCE", {})


def test_transcribe_with_mimo_loads_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test direct inference loads MiMo and returns typed output."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_model = Mock()
    fake_model.generate.return_value = SimpleNamespace(text="今日天气好好。")
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_inference, "_get_mlx_load", Mock(return_value=fake_load))

    result = mimo_inference.transcribe_with_mimo(
        audio_path,
        model_name="/models/MiMo-V2.5-ASR-MLX",
        language="zh",
    )

    fake_load.assert_called_once_with(Path("/models/MiMo-V2.5-ASR-MLX"))
    fake_model.generate.assert_called_once_with(str(audio_path), language="zh")
    assert result.text == "今日天气好好。"
    assert result.duration_seconds == pytest.approx(1.0)


def test_transcribe_with_mimo_passes_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test direct inference forwards the maximum token setting."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_model = Mock()
    fake_model.generate.return_value = {"text": "今日天气好好。"}
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_inference, "_get_mlx_load", Mock(return_value=fake_load))

    mimo_inference.transcribe_with_mimo(
        audio_path,
        model_name="model",
        language="en",
        max_tokens=1024,
    )

    fake_model.generate.assert_called_once_with(
        str(audio_path),
        language="en",
        max_tokens=1024,
    )


def test_transcribe_with_mimo_reuses_loaded_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test repeated direct inference reuses the loaded MiMo model."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_model = Mock()
    fake_model.generate.return_value = SimpleNamespace(text="今日天气好好。")
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_inference, "_get_mlx_load", Mock(return_value=fake_load))

    for _ in range(2):
        mimo_inference.transcribe_with_mimo(
            audio_path,
            model_name="model",
            language="zh",
        )

    fake_load.assert_called_once_with("model")
    assert fake_model.generate.call_count == 2


def test_transcribe_with_mimo_rejects_missing_text(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test malformed inference output is rejected at the runtime boundary."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_model = Mock()
    fake_model.generate.return_value = SimpleNamespace()
    monkeypatch.setattr(
        mimo_inference,
        "_get_mlx_load",
        Mock(return_value=Mock(return_value=fake_model)),
    )

    with pytest.raises(ValueError, match="missing transcript text"):
        mimo_inference.transcribe_with_mimo(
            audio_path,
            model_name="model",
            language="zh",
        )
