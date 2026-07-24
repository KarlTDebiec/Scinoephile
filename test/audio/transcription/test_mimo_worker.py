#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the MiMo worker entrypoint."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import mimo_worker


@pytest.fixture(autouse=True)
def clear_mimo_worker_model_cache(monkeypatch: pytest.MonkeyPatch):
    """Clear the in-process MiMo model cache between tests."""
    monkeypatch.setattr(mimo_worker, "_MLX_MODEL_BY_REFERENCE", {})


def test_transcribe_with_mimo_mlx_loads_model_and_maps_yue_language(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test the MLX runtime loads MiMo and maps Cantonese metadata to Chinese."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_result = SimpleNamespace(
        text="今日天气好好。",
        segments=[{"text": "今日天气好好。", "start": 0.0, "end": 1.0}],
        language="zh",
        total_time=0.5,
        prompt_tokens=10,
        generation_tokens=6,
        total_tokens=16,
    )
    fake_model = Mock()
    fake_model.generate.return_value = fake_result
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_worker, "_get_mlx_load", Mock(return_value=fake_load))

    payload = mimo_worker.transcribe_with_mimo(
        {
            "audio_path": str(audio_path),
            "model_name": "/models/MiMo-V2.5-ASR-MLX",
            "language": "yue",
            "runtime": "mlx",
        }
    )

    fake_load.assert_called_once_with(Path("/models/MiMo-V2.5-ASR-MLX"))
    fake_model.generate.assert_called_once_with(str(audio_path), language="zh")
    assert payload["runtime"] == "mlx"
    assert payload["text"] == "今日天气好好。"
    assert payload["segments"] == fake_result.segments
    assert payload["language"] == "zh"
    assert payload["duration_seconds"] == pytest.approx(1.0)
    assert payload["elapsed_seconds"] == pytest.approx(0.5)
    assert payload["prompt_tokens"] == 10
    assert payload["generation_tokens"] == 6
    assert payload["total_tokens"] == 16


def test_transcribe_with_mimo_mlx_passes_auto_language_and_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test the MLX runtime forwards auto language and max token settings."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_result = SimpleNamespace(
        text="今日天气好好。",
        segments=[{"text": "今日天气好好。", "start": 0.0, "end": 1.0}],
        language=None,
    )
    fake_model = Mock()
    fake_model.generate.return_value = fake_result
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_worker, "_get_mlx_load", Mock(return_value=fake_load))

    mimo_worker.transcribe_with_mimo(
        {
            "audio_path": str(audio_path),
            "model_name": "/models/MiMo-V2.5-ASR-MLX",
            "language": "auto",
            "max_tokens": 1024,
            "runtime": "mlx",
        }
    )

    fake_model.generate.assert_called_once_with(
        str(audio_path),
        language=None,
        max_tokens=1024,
    )


def test_transcribe_with_mimo_mlx_reuses_loaded_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test repeated in-process MLX transcription reuses the loaded MiMo model."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    fake_result = SimpleNamespace(
        text="今日天气好好。",
        segments=[],
        language="zh",
    )
    fake_model = Mock()
    fake_model.generate.return_value = fake_result
    fake_load = Mock(return_value=fake_model)
    monkeypatch.setattr(mimo_worker, "_get_mlx_load", Mock(return_value=fake_load))
    request = {
        "audio_path": str(audio_path),
        "model_name": "/models/MiMo-V2.5-ASR-MLX",
        "runtime": "mlx",
    }

    first_payload = mimo_worker.transcribe_with_mimo(request)
    second_payload = mimo_worker.transcribe_with_mimo(request)

    fake_load.assert_called_once_with(Path("/models/MiMo-V2.5-ASR-MLX"))
    assert fake_model.generate.call_count == 2
    assert first_payload["text"] == "今日天气好好。"
    assert second_payload["text"] == "今日天气好好。"


def test_transcribe_with_mimo_auto_prefers_mlx_on_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test auto runtime selects MLX on Apple Silicon."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    patched_transcribe_with_mlx = Mock(return_value={"runtime": "mlx"})
    monkeypatch.setattr(mimo_worker.platform, "system", Mock(return_value="Darwin"))
    monkeypatch.setattr(mimo_worker.platform, "machine", Mock(return_value="arm64"))
    monkeypatch.setattr(
        mimo_worker,
        "_transcribe_with_mlx",
        patched_transcribe_with_mlx,
    )

    payload = mimo_worker.transcribe_with_mimo(
        {
            "audio_path": str(audio_path),
            "model_name": "/models/MiMo-V2.5-ASR-MLX",
            "runtime": "auto",
        }
    )

    assert payload == {"runtime": "mlx"}
    patched_transcribe_with_mlx.assert_called_once()


def test_transcribe_with_mimo_auto_rejects_non_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test auto runtime fails clearly when MLX is unavailable."""
    audio_path = tmp_path / "audio.wav"
    AudioSegment.silent(duration=1000).export(audio_path, format="wav")
    monkeypatch.setattr(mimo_worker.platform, "system", Mock(return_value="Linux"))
    monkeypatch.setattr(mimo_worker.platform, "machine", Mock(return_value="x86_64"))

    with pytest.raises(ValueError, match="Apple Silicon MLX"):
        mimo_worker.transcribe_with_mimo(
            {
                "audio_path": str(audio_path),
                "model_name": "/models/MiMo-V2.5-ASR-MLX",
                "runtime": "auto",
            }
        )
