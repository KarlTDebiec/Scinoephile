#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CTC transcription alignment."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from scinoephile.audio.transcription import (
    CtcAligner,
    TranscriptionAlignmentError,
)


def test_ctc_aligner_expands_token_spans(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC alignment expands token spans."""
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
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio_path, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner(
        Path("/tmp/audio.wav"),
        "你好",
        1.0,
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


def test_ctc_best_path_requires_blank_between_repeated_labels():
    """Test adjacent repeated labels cannot advance on consecutive frames."""
    log_probs = np.log(
        np.array(
            [
                [0.01, 0.99],
                [0.01, 0.99],
            ]
        )
    )

    with pytest.raises(
        TranscriptionAlignmentError,
        match="did not reach all tokens",
    ):
        CtcAligner._get_best_path(log_probs, [1, 1], 0)


def test_ctc_best_path_accepts_blank_between_repeated_labels():
    """Test a blank-separated path can align adjacent repeated labels."""
    log_probs = np.log(
        np.array(
            [
                [0.01, 0.99],
                [0.99, 0.01],
                [0.01, 0.99],
            ]
        )
    )

    path = CtcAligner._get_best_path(log_probs, [1, 1], 0)

    assert [(token_idx, frame_idx) for token_idx, frame_idx, _ in path] == [
        (0, 0),
        (0, 1),
        (1, 2),
    ]


def test_ctc_aligner_preserves_unaligned_punctuation(
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
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio_path, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner.align(
        Path("/tmp/audio.wav"),
        "你好。",
        1.2,
    )

    assert segments[0].text == "你好。"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好", "。"]
    assert segments[0].words[2].start == pytest.approx(1.0)
    assert segments[0].words[2].end == pytest.approx(1.2)
    assert segments[0].words[2].confidence == 0.0


def test_ctc_aligner_preserves_all_unknown_characters(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test a transcript outside the CTC vocabulary receives fallback timings."""
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio_path, _text: (np.empty((1, 1)), [], [], 0),
    )

    segments = aligner.align(
        Path("/tmp/audio.wav"),
        "佢哋嘅",
        1.5,
    )

    assert segments[0].text == "佢哋嘅"
    assert segments[0].start == pytest.approx(0.0)
    assert segments[0].end == pytest.approx(1.5)
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["佢", "哋", "嘅"]
    assert [word.start for word in segments[0].words] == pytest.approx([0.0, 0.5, 1.0])
    assert [word.end for word in segments[0].words] == pytest.approx([0.5, 1.0, 1.5])
    assert all(word.confidence == 0.0 for word in segments[0].words)


@pytest.mark.parametrize(
    ("text", "char_indices", "expected_words"),
    [
        ("你，好", [0, 2], ["你，", "好"]),
        ("你嘅好", [0, 2], ["你嘅", "好"]),
        ("你， 好", [0, 3], ["你，", " 好"]),
    ],
)
def test_ctc_aligner_attaches_internal_unaligned_characters(
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    char_indices: list[int],
    expected_words: list[str],
):
    """Test unsupported internal characters inherit an adjacent word timing."""
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
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio_path, _text: (log_probs, [1, 2], char_indices, 0),
    )

    segments = aligner.align(
        Path("/tmp/audio.wav"),
        text,
        1.0,
    )

    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == expected_words
    assert "".join(word.text for word in segments[0].words) == text
    assert all(
        int(word.end * 1000) > int(word.start * 1000) for word in segments[0].words
    )


def test_ctc_token_ids_normalize_supported_chars_and_skip_unknown_chars():
    """Test CTC token preparation normalizes case and Chinese script."""

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
            return {
                "你": 1,
                "说": 2,
                "A": 4,
            }.get(token, 3)

    aligner = CtcAligner()
    aligner._processor = SimpleNamespace(tokenizer=FakeTokenizer())
    aligner._model = object()

    token_ids, char_indices = aligner._get_token_ids("你說。a嘅")

    assert token_ids == [1, 2, 4]
    assert char_indices == [0, 1, 3]


def test_ctc_components_are_cached_by_model_and_device(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC components are configurable and cached by model and device."""

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

    monkeypatch.setattr(CtcAligner, "_components", {})
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(
            AutoModelForCTC=FakeAutoModelForCTC,
            AutoProcessor=FakeAutoProcessor,
        ),
    )

    first_aligner = CtcAligner("organization/model-a")
    second_aligner = CtcAligner("organization/model-a")
    other_model_aligner = CtcAligner("organization/model-b")
    other_device_aligner = CtcAligner("organization/model-a", "mps")

    assert second_aligner.processor is first_aligner.processor
    assert second_aligner.model is first_aligner.model
    assert other_model_aligner.processor is not first_aligner.processor
    assert other_model_aligner.model is not first_aligner.model
    assert other_device_aligner.processor is not first_aligner.processor
    assert other_device_aligner.model is not first_aligner.model
    assert FakeAutoProcessor.model_names == [
        "organization/model-a",
        "organization/model-b",
        "organization/model-a",
    ]
    assert FakeAutoModelForCTC.model_names == [
        "organization/model-a",
        "organization/model-b",
        "organization/model-a",
    ]


def test_ctc_aligner_rounds_timings(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC alignment rounds character timings."""
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
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio_path, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner.align(
        Path("/tmp/audio.wav"),
        "你好",
        1.234,
    )

    assert segments[0].words is not None
    assert segments[0].words[0].start == round(1.234 / 4, 3)
    assert segments[0].words[0].end == round(3 * 1.234 / 4, 3)
    assert segments[0].words[0].confidence == round((0.9 + 0.85) / 2, 3)


def test_ctc_aligner_rejects_empty_text():
    """Test empty text is not sent through forced alignment."""
    with pytest.raises(TranscriptionAlignmentError, match="empty transcript"):
        CtcAligner().align(
            Path("/tmp/audio.wav"),
            "   ",
            1.0,
        )


@pytest.mark.parametrize(
    "backend_error",
    [OSError("model unavailable"), RuntimeError("backend failed")],
)
def test_ctc_aligner_wraps_backend_errors(
    monkeypatch: pytest.MonkeyPatch,
    backend_error: Exception,
):
    """Test low-level CTC failures are exposed as alignment errors."""
    aligner = CtcAligner()
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        Mock(side_effect=backend_error),
    )

    with pytest.raises(
        TranscriptionAlignmentError,
        match="Unable to run CTC transcription alignment",
    ):
        aligner.align(
            Path("/tmp/audio.wav"),
            "你好",
            1.0,
        )
