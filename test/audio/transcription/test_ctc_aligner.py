#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CTC transcription alignment."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import (
    CtcAligner,
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
)
from scinoephile.core import Language


def test_ctc_aligner_allows_model_override(monkeypatch: pytest.MonkeyPatch):
    """Test an explicit CTC model does not require a language default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc_aligner._DEFAULT_MODEL_NAMES", {}
    )
    aligner = CtcAligner(Language.eng, "organization/model", "mps")

    assert aligner.language is Language.eng
    assert aligner.model_name == "organization/model"
    assert aligner.device == "mps"


def test_ctc_aligner_groups_english_character_timings_into_words():
    """Test English CTC character timings are grouped into words."""
    text = "HI THERE"
    timed_chars = {
        char_idx: (char_idx / 10, (char_idx + 1) / 10, 0.8)
        for char_idx in range(len(text))
    }

    words = CtcAligner(Language.eng)._get_transcribed_words(
        text, timed_chars, len(text) / 10
    )

    assert [word.text for word in words] == ["HI", " THERE"]
    assert "".join(word.text for word in words) == text
    assert [word.start for word in words] == pytest.approx([0.0, 0.2])
    assert [word.end for word in words] == pytest.approx([0.2, 0.8])
    assert [word.confidence for word in words] == pytest.approx([0.8, 0.8])


def test_ctc_aligner_expands_token_spans(monkeypatch: pytest.MonkeyPatch):
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
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1000), "你好")

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


@pytest.mark.parametrize(
    ("language", "expected_model_name"),
    [
        (Language.eng, "facebook/wav2vec2-base-960h"),
        (Language.yue_hans, "ctl/wav2vec2-large-xlsr-cantonese"),
        (Language.yue_hant, "ctl/wav2vec2-large-xlsr-cantonese"),
        (Language.zho_hans, "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"),
        (Language.zho_hant, "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"),
    ],
)
def test_ctc_aligner_selects_language_default_model(
    language: Language, expected_model_name: str
):
    """Test each transcription language selects its default CTC model.

    Arguments:
        language: transcription language
        expected_model_name: expected default CTC model name
    """
    aligner = CtcAligner(language)

    assert aligner.language is language
    assert aligner.model_name == expected_model_name


def test_ctc_audio_samples_use_requested_rate_and_float32():
    """Test CTC audio conversion normalizes channel, rate, and sample format."""
    audio = (
        AudioSegment.silent(duration=100, frame_rate=8000)
        .set_channels(2)
        .set_sample_width(1)
    )

    samples = CtcAligner._get_audio_samples(audio, 12000)

    assert samples.ndim == 1
    assert samples.dtype == np.float32
    assert len(samples) == pytest.approx(1200, abs=1)
    assert np.all(samples == 0.0)


def test_ctc_audio_samples_reject_empty_audio():
    """Test CTC audio conversion rejects empty audio."""
    with pytest.raises(TranscriptionAlignmentError, match="empty audio"):
        CtcAligner._get_audio_samples(AudioSegment.empty(), 16000)


def test_ctc_alignment_uses_processor_sampling_rate(monkeypatch: pytest.MonkeyPatch):
    """Test CTC alignment uses the configured processor's sampling rate."""
    aligner = CtcAligner(Language.yue_hant)
    aligner._processor = SimpleNamespace(
        feature_extractor=SimpleNamespace(sampling_rate=8000)
    )
    aligner._model = object()
    get_audio_samples = Mock(side_effect=RuntimeError("stop after conversion"))
    monkeypatch.setattr(aligner, "_get_audio_samples", get_audio_samples)
    audio = AudioSegment.silent(duration=100)

    with pytest.raises(RuntimeError, match="stop after conversion"):
        aligner._get_alignment_inputs(audio, "你")

    get_audio_samples.assert_called_once_with(audio, 8000)


def test_ctc_best_path_requires_blank_between_repeated_labels():
    """Test adjacent repeated labels cannot advance on consecutive frames."""
    log_probs = np.log(np.array([[0.01, 0.99], [0.01, 0.99]]))

    with pytest.raises(
        TranscriptionAlignmentIncompleteError, match="did not reach all tokens"
    ):
        CtcAligner._get_best_path(log_probs, [1, 1], 0)


def test_ctc_best_path_accepts_blank_between_repeated_labels():
    """Test a blank-separated path can align adjacent repeated labels."""
    log_probs = np.log(np.array([[0.01, 0.99], [0.99, 0.01], [0.01, 0.99]]))

    path = CtcAligner._get_best_path(log_probs, [1, 1], 0)

    assert [(token_idx, frame_idx) for token_idx, frame_idx, _ in path] == [
        (0, 0),
        (0, 1),
        (1, 2),
    ]


def test_ctc_aligner_aligns_word_delimiter():
    """Test a tokenizer word delimiter participates in the CTC path."""

    class FakeTokenizer:
        """Fake tokenizer with a word delimiter token."""

        unk_token_id = 4
        """Unknown token ID."""

        word_delimiter_token_id = 2
        """Word delimiter token ID."""

        @staticmethod
        def convert_tokens_to_ids(token: str) -> int:
            """Convert a token to a fake token ID.

            Arguments:
                token: token text
            Returns:
                fake token ID
            """
            return {"你": 1, "好": 3}.get(token, 4)

    log_probs = np.log(
        np.array(
            [
                [0.004999, 0.990, 0.004, 0.001, 0.000001],
                [0.0001, 0.0001, 0.998799, 0.0010, 0.000001],
                [0.004999, 0.001, 0.004, 0.990, 0.000001],
            ]
        )
    )
    aligner = CtcAligner(Language.yue_hant)
    aligner._processor = SimpleNamespace(tokenizer=FakeTokenizer())
    aligner._model = object()

    token_ids, char_indices = aligner._get_token_ids("你 好")
    path = aligner._get_best_path(log_probs, token_ids, 0)

    assert token_ids == [1, 2, 3]
    assert char_indices == [0, 1, 2]
    assert [(token_idx, frame_idx) for token_idx, frame_idx, _ in path] == [
        (0, 0),
        (1, 1),
        (2, 2),
    ]


def test_ctc_aligner_attaches_trailing_unaligned_punctuation(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test trailing punctuation inherits the final aligned word timing."""
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
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner.align(AudioSegment.silent(duration=1200), "你好。")

    assert segments[0].text == "你好。"
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "好。"]
    assert segments[0].end == pytest.approx(1.0)
    assert segments[0].words[1].start == pytest.approx(0.8)
    assert segments[0].words[1].end == pytest.approx(1.0)
    assert segments[0].words[1].confidence == pytest.approx(0.9)


def test_ctc_aligner_times_trailing_unsupported_speech(monkeypatch: pytest.MonkeyPatch):
    """Test trailing unsupported speech retains fallback timing."""
    log_probs = np.log(
        np.array([[0.85, 0.15], [0.05, 0.95], [0.85, 0.15], [0.85, 0.15]])
    )
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner, "_get_alignment_inputs", lambda _audio, _text: (log_probs, [1], [0], 0)
    )

    segments = aligner.align(AudioSegment.silent(duration=1000), "你嘅")

    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == ["你", "嘅"]
    assert segments[0].words[0].end == pytest.approx(0.5)
    assert segments[0].words[1].start == pytest.approx(0.5)
    assert segments[0].words[1].end == pytest.approx(1.0)
    assert segments[0].words[1].confidence == 0.0
    assert segments[0].end == pytest.approx(1.0)


def test_ctc_aligner_preserves_boundary_whitespace(monkeypatch: pytest.MonkeyPatch):
    """Test CTC alignment preserves whitespace around the transcript."""
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
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (log_probs, [1, 2], [1, 2], 0),
    )

    segments = aligner.align(AudioSegment.silent(duration=1000), " 你好 ")

    assert segments[0].text == " 你好 "
    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == [" 你", "好 "]
    assert "".join(word.text for word in segments[0].words) == " 你好 "
    assert segments[0].start == pytest.approx(0.25)
    assert segments[0].end == pytest.approx(1.0)


def test_ctc_aligner_preserves_all_unknown_characters(monkeypatch: pytest.MonkeyPatch):
    """Test a transcript outside the CTC vocabulary receives fallback timings."""
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (np.empty((1, 1)), [], [], 0),
    )

    segments = aligner.align(AudioSegment.silent(duration=1500), "佢哋嘅")

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
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (log_probs, [1, 2], char_indices, 0),
    )

    segments = aligner.align(AudioSegment.silent(duration=1000), text)

    assert segments[0].words is not None
    assert [word.text for word in segments[0].words] == expected_words
    assert "".join(word.text for word in segments[0].words) == text
    assert all(
        int(word.end * 1000) > int(word.start * 1000) for word in segments[0].words
    )


def test_ctc_token_ids_normalize_case_and_skip_unknown_chars():
    """Test CTC token preparation normalizes case and skips unknown text."""

    class FakeTokenizer:
        """Fake tokenizer with one known transcript character."""

        unk_token_id = 3
        """Unknown token ID."""

        word_delimiter_token_id = 5
        """Word delimiter token ID."""

        @staticmethod
        def convert_tokens_to_ids(token: str) -> int:
            """Convert a token to a fake token ID.

            Arguments:
                token: token text
            Returns:
                fake token ID
            """
            return {"你": 1, "說": 2, "A": 4}.get(token, 3)

    aligner = CtcAligner(Language.yue_hant)
    aligner._processor = SimpleNamespace(tokenizer=FakeTokenizer())
    aligner._model = object()

    token_ids, char_indices = aligner._get_token_ids(" 你 說。a嘅 ")

    assert token_ids == [1, 5, 2, 4]
    assert char_indices == [1, 2, 3, 5]


@pytest.mark.parametrize(
    ("language", "text", "recognized_token", "expected_token_ids"),
    [
        (Language.yue_hans, "说", "說", [2]),
        (Language.zho_hant, "說", "说", [2]),
        (Language.yue_hant, "說", "说", []),
        (Language.zho_hans, "说", "說", []),
    ],
)
def test_ctc_token_ids_use_default_model_script_conversion(
    language: Language, text: str, recognized_token: str, expected_token_ids: list[int]
):
    """Test token lookup converts only toward the default model's script.

    Arguments:
        language: transcription language
        text: transcript text
        recognized_token: token recognized by the fake tokenizer
        expected_token_ids: expected recognized token IDs
    """

    class FakeTokenizer:
        """Fake tokenizer recognizing one character."""

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
            if token == recognized_token:
                return 2
            return 3

    aligner = CtcAligner(language)
    aligner._processor = SimpleNamespace(tokenizer=FakeTokenizer())

    token_ids, char_indices = aligner._get_token_ids(text)

    assert token_ids == expected_token_ids
    assert char_indices == list(range(len(expected_token_ids)))


def test_ctc_token_ids_do_not_convert_script_for_model_override():
    """Test custom CTC models do not receive inferred script conversion."""

    class FakeTokenizer:
        """Fake tokenizer recognizing one traditional character."""

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
            if token == "說":
                return 2
            return 3

    aligner = CtcAligner(Language.yue_hans, "organization/model")
    aligner._processor = SimpleNamespace(tokenizer=FakeTokenizer())

    token_ids, char_indices = aligner._get_token_ids("说")

    assert token_ids == []
    assert char_indices == []


def test_ctc_models_and_processors_are_cached_independently(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test CTC models and processors use their appropriate cache keys."""

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

    monkeypatch.setattr(CtcAligner, "_models", {})
    monkeypatch.setattr(CtcAligner, "_processors", {})
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(
            AutoModelForCTC=FakeAutoModelForCTC, AutoProcessor=FakeAutoProcessor
        ),
    )

    first_aligner = CtcAligner(Language.eng, "organization/model-a")
    second_aligner = CtcAligner(Language.eng, "organization/model-a")
    other_model_aligner = CtcAligner(Language.eng, "organization/model-b")
    other_device_aligner = CtcAligner(Language.eng, "organization/model-a", "mps")

    assert second_aligner.processor is first_aligner.processor
    assert second_aligner.model is first_aligner.model
    assert other_model_aligner.processor is not first_aligner.processor
    assert other_model_aligner.model is not first_aligner.model
    assert other_device_aligner.processor is first_aligner.processor
    assert other_device_aligner.model is not first_aligner.model
    assert FakeAutoProcessor.model_names == [
        "organization/model-a",
        "organization/model-b",
    ]
    assert FakeAutoModelForCTC.model_names == [
        "organization/model-a",
        "organization/model-b",
        "organization/model-a",
    ]


def test_ctc_aligner_rounds_timings(monkeypatch: pytest.MonkeyPatch):
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
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner,
        "_get_alignment_inputs",
        lambda _audio, _text: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner.align(AudioSegment.silent(duration=1234), "你好")

    assert segments[0].words is not None
    assert segments[0].words[0].start == round(1.234 / 4, 3)
    assert segments[0].words[0].end == round(3 * 1.234 / 4, 3)
    assert segments[0].words[0].confidence == round((0.9 + 0.85) / 2, 3)


def test_ctc_aligner_rejects_empty_text():
    """Test empty text is not sent through forced alignment."""
    with pytest.raises(TranscriptionAlignmentError, match="empty transcript"):
        CtcAligner(Language.yue_hant).align(AudioSegment.empty(), "   ")


@pytest.mark.parametrize(
    "backend_error", [OSError("model unavailable"), RuntimeError("backend failed")]
)
def test_ctc_aligner_wraps_backend_errors(
    monkeypatch: pytest.MonkeyPatch, backend_error: Exception
):
    """Test low-level CTC failures are exposed as alignment errors."""
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(
        aligner, "_get_alignment_inputs", Mock(side_effect=backend_error)
    )

    with pytest.raises(
        TranscriptionAlignmentError, match="Unable to run CTC transcription alignment"
    ):
        aligner.align(AudioSegment.silent(duration=1000), "你好")
