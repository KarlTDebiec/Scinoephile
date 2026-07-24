#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of forced transcription alignment helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import numpy as np
import pytest

from scinoephile.audio.transcription import forced_alignment
from scinoephile.audio.transcription.forced_alignment import (
    TranscriptionAlignmentError,
    align_mimo_transcription,
)


def test_align_mimo_transcription_converts_whisperx_words(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test WhisperX-aligned words are converted to transcribed segments."""
    fake_whisperx = SimpleNamespace(
        align=_fake_whisperx_align_with_words,
        load_align_model=lambda **_kwargs: ("model", {"language": "zh"}),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_whisperx_module",
        lambda: fake_whisperx,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "hello world",
        duration_seconds=1.25,
        aligner_backend="whisperx",
        aligner_language="zh",
    )

    assert len(segments) == 1
    assert segments[0].id == 0
    assert segments[0].seek == 0
    assert segments[0].start == 0.0
    assert segments[0].end == 1.25
    assert segments[0].text == "hello world"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["hello", " world"]
    assert segments[0].words[0].confidence == 0.8


def test_align_mimo_transcription_runs_whisperx_worker(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test WhisperX alignment can run through an isolated worker process."""
    captured: dict[str, object] = {}

    def fake_run(
        command: list[str],
        *,
        input: str,
        text: bool,
        capture_output: bool,
        check: bool,
        timeout: float | None,
    ) -> subprocess.CompletedProcess[str]:
        """Capture worker invocation and return WhisperX-style alignment JSON."""
        captured["command"] = command
        captured["input"] = input
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=(
                "model log\n"
                '{"segments":[{"start":0.0,"end":1.0,"text":"你好",'
                '"words":[{"word":"你","start":0.0,"end":0.4,"score":0.8},'
                '{"word":"好","start":0.4,"end":1.0,"score":0.9}]}]}\n'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment.subprocess.run",
        fake_run,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "你好",
        duration_seconds=1.0,
        aligner_backend="whisperx",
        aligner_language="zh",
        aligner_model_name="custom/aligner",
        aligner_worker_command=["python", "worker.py"],
        aligner_worker_timeout_seconds=7.5,
    )

    request = json.loads(cast(str, captured["input"]))
    assert captured["command"] == ["python", "worker.py"]
    assert captured["timeout"] == 7.5
    assert request["audio_path"] == "/tmp/audio.wav"
    assert request["backend"] == "whisperx"
    assert request["text"] == "你好"
    assert request["duration_seconds"] == 1.0
    assert request["language"] == "zh"
    assert request["model_name"] == "custom/aligner"
    assert segments[0].text == "你好"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好"]


def test_align_mimo_transcription_preserves_trailing_unaligned_text(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test trailing punctuation omitted by WhisperX remains word-covered.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    fake_whisperx = SimpleNamespace(
        align=lambda **_kwargs: {
            "segments": [
                {
                    "start": 0.0,
                    "end": 1.0,
                    "text": "你好！",
                    "words": [{"word": "你好", "start": 0.0, "end": 1.0, "score": 0.9}],
                }
            ]
        },
        load_align_model=lambda **_kwargs: ("model", {"language": "zh"}),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_whisperx_module",
        lambda: fake_whisperx,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "你好！",
        duration_seconds=1.0,
        aligner_backend="whisperx",
    )

    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你好！"]
    assert "".join(word.text for word in segments[0].words) == segments[0].text


def test_align_mimo_transcription_uses_ctc_backend_by_default(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test default CTC alignment expands token spans like WhisperX."""
    log_probs = np.log(
        np.array(
            [
                [0.85, 0.10, 0.05],
                [0.05, 0.90, 0.05],
                [0.85, 0.10, 0.05],
                [0.05, 0.05, 0.90],
            ]
        )
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_ctc_alignment_inputs",
        lambda **_kwargs: (log_probs, [1, 2], [0, 1], 0),
        raising=False,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "你好",
        duration_seconds=1.0,
    )

    assert len(segments) == 1
    assert segments[0].text == "你好"
    assert segments[0].start == pytest.approx(0.25)
    assert segments[0].end == pytest.approx(1.0)
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好"]
    assert segments[0].words[0].start == pytest.approx(0.25)
    assert segments[0].words[0].end == pytest.approx(0.75)
    assert segments[0].words[1].start == pytest.approx(0.75)
    assert segments[0].words[1].end == pytest.approx(1.0)
    assert 0.0 < segments[0].words[0].confidence <= 1.0


def test_align_mimo_transcription_ctc_preserves_unaligned_punctuation(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC alignment preserves punctuation absent from the aligner vocab."""
    log_probs = np.log(
        np.array(
            [
                [0.85, 0.10, 0.05],
                [0.05, 0.90, 0.05],
                [0.85, 0.10, 0.05],
                [0.85, 0.10, 0.05],
                [0.05, 0.05, 0.90],
                [0.85, 0.10, 0.05],
            ]
        )
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_ctc_alignment_inputs",
        lambda **_kwargs: (log_probs, [1, 2], [0, 1], 0),
        raising=False,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "你好。",
        duration_seconds=1.2,
        aligner_backend="ctc",
    )

    assert segments[0].text == "你好。"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好", "。"]
    assert segments[0].words[2].start == pytest.approx(1.0)
    assert segments[0].words[2].end == pytest.approx(1.2)
    assert segments[0].words[2].confidence == 0.0


def test_ctc_token_ids_use_wildcard_for_unknown_non_space_chars():
    """Test CTC token preparation keeps unknown punctuation like WhisperX."""

    class FakeTokenizer:
        """Fake tokenizer with one known transcript character."""

        unk_token_id = 3
        """Unknown token ID."""

        @staticmethod
        def convert_tokens_to_ids(token: str) -> int:
            """Convert a token to a fake token ID.

            Arguments:
                token: token text
            Returns:
                fake token ID
            """
            if token == "你":
                return 1
            return 3

    processor = SimpleNamespace(tokenizer=FakeTokenizer())

    token_ids, char_indices = forced_alignment._get_ctc_token_ids(
        text="你。",
        processor=processor,
    )

    assert token_ids == [1, -1]
    assert char_indices == [0, 1]


def test_ctc_components_are_cached_by_model_and_device(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC component loading is cached for repeated alignment calls."""

    class FakeAutoProcessor:
        """Fake Hugging Face processor factory."""

        model_names: list[str] = []
        """Model names loaded by the fake factory."""

        @classmethod
        def from_pretrained(cls, model_name: str) -> object:
            """Load a fake processor.

            Arguments:
                model_name: model checkpoint name
            Returns:
                fake processor
            """
            cls.model_names.append(model_name)
            return object()

    class FakeModel:
        """Fake Hugging Face CTC model."""

        def __init__(self):
            """Initialize a fake model."""
            self.devices: list[str] = []
            self.eval_count = 0

        def eval(self):
            """Mark the fake model as evaluated."""
            self.eval_count += 1

        def to(self, device: str) -> FakeModel:
            """Move the fake model to a device.

            Arguments:
                device: device identifier
            Returns:
                fake model
            """
            self.devices.append(device)
            return self

    class FakeAutoModelForCTC:
        """Fake Hugging Face CTC model factory."""

        model_names: list[str] = []
        """Model names loaded by the fake factory."""

        @classmethod
        def from_pretrained(cls, model_name: str) -> FakeModel:
            """Load a fake CTC model.

            Arguments:
                model_name: model checkpoint name
            Returns:
                fake CTC model
            """
            cls.model_names.append(model_name)
            return FakeModel()

    monkeypatch.setattr(
        forced_alignment,
        "_CTC_COMPONENTS_BY_MODEL_AND_DEVICE",
        {},
        raising=False,
    )
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(
            AutoModelForCTC=FakeAutoModelForCTC,
            AutoProcessor=FakeAutoProcessor,
        ),
    )

    first_processor, first_model = forced_alignment._get_ctc_components(
        model_name="model-a",
        device="cpu",
    )
    second_processor, second_model = forced_alignment._get_ctc_components(
        model_name="model-a",
        device="cpu",
    )
    third_processor, third_model = forced_alignment._get_ctc_components(
        model_name="model-a",
        device="mps",
    )

    assert second_processor is first_processor
    assert second_model is first_model
    assert third_processor is not first_processor
    assert third_model is not first_model
    assert FakeAutoProcessor.model_names == ["model-a", "model-a"]
    assert FakeAutoModelForCTC.model_names == ["model-a", "model-a"]


def test_align_mimo_transcription_ctc_rounds_timings_like_whisperx(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC alignment rounds character timings like WhisperX."""
    log_probs = np.log(
        np.array(
            [
                [0.85, 0.10, 0.05],
                [0.05, 0.90, 0.05],
                [0.85, 0.10, 0.05],
                [0.05, 0.05, 0.90],
            ]
        )
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_ctc_alignment_inputs",
        lambda **_kwargs: (log_probs, [1, 2], [0, 1], 0),
        raising=False,
    )

    segments = align_mimo_transcription(
        Path("/tmp/audio.wav"),
        "你好",
        duration_seconds=1.234,
        aligner_backend="ctc",
    )

    assert segments[0].words is not None
    assert segments[0].words[0].start == round(1.234 / 4, 3)
    assert segments[0].words[0].end == round(3 * 1.234 / 4, 3)
    assert segments[0].words[0].confidence == round((0.9 + 0.85) / 2, 3)


def test_align_mimo_transcription_rejects_missing_word_timing(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo alignment fails when any word lacks timing data."""
    fake_whisperx = SimpleNamespace(
        align=lambda **_kwargs: {
            "segments": [
                {
                    "start": 0.0,
                    "end": 1.0,
                    "text": "hello",
                    "words": [{"word": "hello", "start": 0.0}],
                }
            ]
        },
        load_align_model=lambda **_kwargs: ("model", {"language": "zh"}),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_whisperx_module",
        lambda: fake_whisperx,
    )

    with pytest.raises(TranscriptionAlignmentError, match="missing word timings"):
        align_mimo_transcription(
            Path("/tmp/audio.wav"),
            "hello",
            duration_seconds=1.0,
            aligner_backend="whisperx",
        )


def test_align_mimo_transcription_rejects_empty_text():
    """Test empty MiMo text is not sent through forced alignment."""
    with pytest.raises(TranscriptionAlignmentError, match="empty transcript"):
        align_mimo_transcription(
            Path("/tmp/audio.wav"),
            "   ",
            duration_seconds=1.0,
        )


def _fake_whisperx_align_with_words(**kwargs: object) -> dict[str, object]:
    """Get a fake WhisperX alignment result with usable word timings."""
    assert kwargs["transcript"] == [{"start": 0.0, "end": 1.25, "text": "hello world"}]
    assert kwargs["audio"] == "/tmp/audio.wav"
    assert kwargs["device"] == "cpu"
    return {
        "segments": [
            {
                "start": 0.0,
                "end": 1.25,
                "text": "hello world",
                "words": [
                    {"word": "hello", "start": 0.0, "end": 0.55, "score": 0.8},
                    {"word": "world", "start": 0.65, "end": 1.25, "score": 0.9},
                ],
            }
        ]
    }
