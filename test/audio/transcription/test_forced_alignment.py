#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of forced transcription alignment helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from scinoephile.audio.transcription import forced_alignment
from scinoephile.audio.transcription.forced_alignment import (
    TranscriptionAlignmentError,
    align_transcription,
)


def test_align_transcription_uses_ctc_backend_by_default(
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
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_ctc_alignment_inputs",
        lambda **_kwargs: (log_probs, [1, 2], [0, 1], 0),
        raising=False,
    )

    segments = align_transcription(
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


def test_align_transcription_ctc_preserves_unaligned_punctuation(
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

    segments = align_transcription(
        Path("/tmp/audio.wav"),
        "你好。",
        duration_seconds=1.2,
    )

    assert segments[0].text == "你好。"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好", "。"]
    assert segments[0].words[2].start == pytest.approx(1.0)
    assert segments[0].words[2].end == pytest.approx(1.2)
    assert segments[0].words[2].confidence == 0.0


def test_ctc_token_ids_use_wildcard_for_unknown_non_space_chars():
    """Test CTC token preparation keeps unknown punctuation."""

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


def test_ctc_components_are_cached_by_device(
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
        "_CTC_COMPONENTS_BY_DEVICE",
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

    first_processor, first_model = forced_alignment._get_ctc_components(device="cpu")
    second_processor, second_model = forced_alignment._get_ctc_components(device="cpu")
    third_processor, third_model = forced_alignment._get_ctc_components(device="mps")

    assert second_processor is first_processor
    assert second_model is first_model
    assert third_processor is not first_processor
    assert third_model is not first_model
    assert FakeAutoProcessor.model_names == [
        forced_alignment.CTC_MODEL_NAME,
        forced_alignment.CTC_MODEL_NAME,
    ]
    assert FakeAutoModelForCTC.model_names == [
        forced_alignment.CTC_MODEL_NAME,
        forced_alignment.CTC_MODEL_NAME,
    ]


def test_align_transcription_ctc_rounds_timings(
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
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment._get_ctc_alignment_inputs",
        lambda **_kwargs: (log_probs, [1, 2], [0, 1], 0),
        raising=False,
    )

    segments = align_transcription(
        Path("/tmp/audio.wav"),
        "你好",
        duration_seconds=1.234,
    )

    assert segments[0].words is not None
    assert segments[0].words[0].start == round(1.234 / 4, 3)
    assert segments[0].words[0].end == round(3 * 1.234 / 4, 3)
    assert segments[0].words[0].confidence == round((0.9 + 0.85) / 2, 3)


def test_align_transcription_rejects_empty_text():
    """Test empty text is not sent through forced alignment."""
    with pytest.raises(TranscriptionAlignmentError, match="empty transcript"):
        align_transcription(
            Path("/tmp/audio.wav"),
            "   ",
            duration_seconds=1.0,
        )
