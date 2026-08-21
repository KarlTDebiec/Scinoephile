#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CTC transcription alignment."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import (
    CtcAligner,
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
)
from scinoephile.audio.transcription.ctc.model import CtcModel
from scinoephile.audio.transcription.ctc.model_spec import CtcModelSpec
from scinoephile.audio.transcription.ctc.path import get_best_path
from scinoephile.audio.transcription.ctc.text import get_transcribed_words
from scinoephile.audio.transcription.ctc.tokenization import get_token_ids
from scinoephile.core import Language, OpenCCConfig
from scinoephile.core.ml import ModelSpec

_CUSTOM_MODEL = ModelSpec(name="organization/model", revision="custom-revision")
"""Custom CTC model specification used by tests."""


def test_ctc_aligner_allows_model_override(monkeypatch: pytest.MonkeyPatch):
    """Test an explicit CTC model does not require a language default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.aligner._DEFAULT_MODEL_SPECS", {}
    )
    aligner = CtcAligner(Language.eng, _CUSTOM_MODEL, "mps")

    assert aligner.language is Language.eng
    assert aligner.model.spec is _CUSTOM_MODEL
    assert aligner.model.device == "mps"


def test_ctc_aligner_groups_english_character_timings_into_words():
    """Test English CTC character timings are grouped into words."""
    text = "HI THERE"
    timed_chars = {
        char_idx: (char_idx / 10, (char_idx + 1) / 10, 0.8)
        for char_idx in range(len(text))
    }

    words = get_transcribed_words(Language.eng, text, timed_chars, len(text) / 10)

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (log_probs, [1, 2], [0, 1], 0),
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
    ("language", "expected_model_spec"),
    [
        (
            Language.eng,
            CtcModelSpec(
                name="facebook/wav2vec2-base-960h",
                revision="22aad52d435eb6dbaf354bdad9b0da84ce7d6156",
                script=None,
            ),
        ),
        (
            Language.yue_hans,
            CtcModelSpec(
                name="ctl/wav2vec2-large-xlsr-cantonese",
                revision="11cb21cb68b4ed15f4c6633494ae6cc90a89bc34",
                script="Hant",
            ),
        ),
        (
            Language.yue_hant,
            CtcModelSpec(
                name="ctl/wav2vec2-large-xlsr-cantonese",
                revision="11cb21cb68b4ed15f4c6633494ae6cc90a89bc34",
                script="Hant",
            ),
        ),
        (
            Language.zho_hans,
            CtcModelSpec(
                name="jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
                revision="99ccb2737be22b8bb50dcfcc39ad4d567fb90cfd",
                script="Hans",
            ),
        ),
        (
            Language.zho_hant,
            CtcModelSpec(
                name="jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
                revision="99ccb2737be22b8bb50dcfcc39ad4d567fb90cfd",
                script="Hans",
            ),
        ),
    ],
)
def test_ctc_aligner_selects_language_default_model(
    language: Language, expected_model_spec: CtcModelSpec
):
    """Test each transcription language selects its default CTC model.

    Arguments:
        language: transcription language
        expected_model_spec: expected default CTC model specification
    """
    aligner = CtcAligner(language)

    assert aligner.language is language
    assert aligner.model.spec == expected_model_spec


def test_ctc_aligner_loads_default_model_at_pinned_revision(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test default CTC assets load from their immutable Hugging Face revision."""
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    runtime_model = Mock()
    runtime_model.to.return_value = runtime_model
    model_factory = Mock(return_value=runtime_model)
    runtime_processor = SimpleNamespace(
        feature_extractor=SimpleNamespace(sampling_rate=16000)
    )
    processor_factory = Mock(return_value=runtime_processor)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.import_transformers",
        Mock(
            return_value=SimpleNamespace(
                AutoModelForCTC=SimpleNamespace(from_pretrained=model_factory),
                AutoProcessor=SimpleNamespace(from_pretrained=processor_factory),
            )
        ),
    )
    aligner = CtcAligner(Language.eng)

    processor = aligner.model.processor

    assert aligner.model.model is runtime_model
    assert aligner.model.model is runtime_model
    assert aligner.model.processor is processor
    expected_revision = "22aad52d435eb6dbaf354bdad9b0da84ce7d6156"
    assert get_snapshot_dir_path.call_args_list == [
        call("facebook/wav2vec2-base-960h", expected_revision),
        call("facebook/wav2vec2-base-960h", expected_revision),
    ]
    model_factory.assert_called_once_with(Path("/cached/model"), local_files_only=True)
    processor_factory.assert_called_once_with(
        Path("/cached/model"), local_files_only=True
    )


def test_ctc_aligner_resolves_custom_model_snapshot(monkeypatch: pytest.MonkeyPatch):
    """Test a custom Hugging Face asset resolves to a local snapshot before loading.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    aligner = CtcAligner(Language.eng, _CUSTOM_MODEL)
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    processor = SimpleNamespace(feature_extractor=SimpleNamespace(sampling_rate=16000))
    processor_factory = Mock(return_value=processor)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.import_transformers",
        Mock(
            return_value=SimpleNamespace(
                AutoProcessor=SimpleNamespace(from_pretrained=processor_factory)
            )
        ),
    )

    assert aligner.model.processor is processor
    get_snapshot_dir_path.assert_called_once_with(
        "organization/model", "custom-revision"
    )
    processor_factory.assert_called_once_with(
        Path("/cached/model"), local_files_only=True
    )


@pytest.mark.parametrize("sampling_rate", [None, 0, -1, "16000"])
def test_ctc_model_rejects_invalid_processor_sampling_rate(
    sampling_rate: object, monkeypatch: pytest.MonkeyPatch
):
    """Test processor loading rejects an invalid sampling rate.

    Arguments:
        sampling_rate: invalid processor sampling rate
        monkeypatch: pytest monkeypatch fixture
    """
    processor_factory = Mock(
        return_value=SimpleNamespace(
            feature_extractor=SimpleNamespace(sampling_rate=sampling_rate)
        )
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/model")),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.import_transformers",
        Mock(
            return_value=SimpleNamespace(
                AutoProcessor=SimpleNamespace(from_pretrained=processor_factory)
            )
        ),
    )

    with pytest.raises(TranscriptionAlignmentError, match="valid sampling rate"):
        _ = CtcModel(_CUSTOM_MODEL, "cpu").processor


def test_ctc_aligner_persistently_caches_alignment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test repeated CTC alignment loads timestamped output from disk.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
    """
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
    audio = AudioSegment.silent(duration=1000)
    first_aligner = CtcAligner(Language.yue_hant, cache_root_path=tmp_path)
    get_alignment_inputs = Mock(return_value=(log_probs, [1, 2], [0, 1], 0))
    monkeypatch.setattr(CtcModel, "__call__", get_alignment_inputs)

    first_segments = first_aligner(audio, "你好")
    second_aligner = CtcAligner(Language.yue_hant, cache_root_path=tmp_path)
    second_segments = second_aligner(audio, "你好")

    assert second_segments == first_segments
    assert get_alignment_inputs.call_count == 1
    assert len(list((tmp_path / "audio" / "transcription" / "ctc").glob("*.json"))) == 1


def test_ctc_model_uses_processor_sampling_rate(monkeypatch: pytest.MonkeyPatch):
    """Test CTC inference prepares audio at the processor's sampling rate."""
    model = CtcModel(_CUSTOM_MODEL, "cpu")
    processor = Mock(side_effect=RuntimeError("stop after conversion"))
    processor.feature_extractor = SimpleNamespace(sampling_rate=8000)
    monkeypatch.setitem(model.__dict__, "processor", processor)
    to_mono_int16 = Mock(return_value=np.array([0, 16384], dtype=np.int16))
    monkeypatch.setattr(
        "scinoephile.audio.transcription.ctc.model.to_mono_int16", to_mono_int16
    )
    audio = AudioSegment.silent(duration=100)

    with pytest.raises(RuntimeError, match="stop after conversion"):
        model(audio, "你")

    to_mono_int16.assert_called_once_with(audio, 8000)
    samples = processor.call_args.args[0]
    assert samples.dtype == np.float32
    assert samples == pytest.approx([0.0, 0.5])


def test_ctc_model_rejects_empty_audio(monkeypatch: pytest.MonkeyPatch):
    """Test CTC inference rejects empty audio."""
    model = CtcModel(_CUSTOM_MODEL, "cpu")
    processor = Mock()
    processor.feature_extractor = SimpleNamespace(sampling_rate=16000)
    monkeypatch.setitem(model.__dict__, "processor", processor)

    with pytest.raises(TranscriptionAlignmentError, match="empty audio"):
        model(AudioSegment.empty(), "text")


def test_ctc_best_path_requires_blank_between_repeated_labels():
    """Test adjacent repeated labels cannot advance on consecutive frames."""
    log_probs = np.log(np.array([[0.01, 0.99], [0.01, 0.99]]))

    with pytest.raises(
        TranscriptionAlignmentIncompleteError, match="did not reach all tokens"
    ):
        get_best_path(log_probs, [1, 1], 0)


def test_ctc_best_path_accepts_blank_between_repeated_labels():
    """Test a blank-separated path can align adjacent repeated labels."""
    log_probs = np.log(np.array([[0.01, 0.99], [0.99, 0.01], [0.01, 0.99]]))

    path = get_best_path(log_probs, [1, 1], 0)

    assert [(token_idx, frame_idx) for token_idx, frame_idx, _ in path] == [
        (0, 0),
        (0, 1),
        (1, 2),
    ]


def test_ctc_token_ids_include_word_delimiter():
    """Test token IDs include a tokenizer word delimiter."""

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
    token_ids, char_indices = get_token_ids("你 好", FakeTokenizer())
    path = get_best_path(log_probs, token_ids, 0)

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1200), "你好。")

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (log_probs, [1], [0], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1000), "你嘅")

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (log_probs, [1, 2], [1, 2], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1000), " 你好 ")

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (np.empty((1, 1)), [], [], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1500), "佢哋嘅")

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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (
            log_probs,
            [1, 2],
            char_indices,
            0,
        ),
    )

    segments = aligner(AudioSegment.silent(duration=1000), text)

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

    token_ids, char_indices = get_token_ids(" 你 說。a嘅 ", FakeTokenizer())

    assert token_ids == [1, 5, 2, 4]
    assert char_indices == [1, 2, 3, 5]


@pytest.mark.parametrize(
    (
        "language",
        "text",
        "model_text",
        "recognized_token",
        "expected_config",
        "expected_token_ids",
    ),
    [
        (Language.yue_hans, "说", "說", "說", OpenCCConfig.s2t, [2]),
        (Language.zho_hant, "說", "说", "说", OpenCCConfig.t2s, [2]),
        (Language.yue_hant, "說", None, "说", None, []),
        (Language.zho_hans, "说", None, "說", None, []),
    ],
)
def test_ctc_token_ids_use_default_model_script_conversion(
    language: Language,
    text: str,
    model_text: str | None,
    recognized_token: str,
    expected_config: OpenCCConfig | None,
    expected_token_ids: list[int],
):
    """Test token lookup converts only toward the default model's script.

    Arguments:
        language: transcription language
        text: transcript text
        model_text: transcript converted to the model tokenizer's script
        recognized_token: token recognized by the fake tokenizer
        expected_config: expected script conversion configuration
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
    token_ids, char_indices = get_token_ids(text, FakeTokenizer(), model_text)

    assert aligner._script_conversion_config is expected_config
    assert token_ids == expected_token_ids
    assert char_indices == list(range(len(expected_token_ids)))


@pytest.mark.parametrize(
    ("language", "text", "expected_model_text"),
    [(Language.yue_hans, "说", "說"), (Language.zho_hant, "說", "说")],
)
def test_ctc_aligner_passes_model_script_text_to_model(
    monkeypatch: pytest.MonkeyPatch,
    language: Language,
    text: str,
    expected_model_text: str,
):
    """Test the aligner converts target text before model token lookup.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        language: transcription language
        text: transcription text
        expected_model_text: text expected by the model tokenizer
    """
    audio = AudioSegment.silent(duration=1000)
    aligner = CtcAligner(language)
    model_call = Mock(return_value=(np.empty((1, 1)), [], [], 0))
    monkeypatch.setattr(CtcModel, "__call__", model_call)
    monkeypatch.setattr(aligner.cache, "load", Mock(return_value=None))
    monkeypatch.setattr(aligner.cache, "save", Mock())

    aligner(audio, text)

    model_call.assert_called_once_with(audio, text, expected_model_text)


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

    aligner = CtcAligner(Language.yue_hans, _CUSTOM_MODEL)
    token_ids, char_indices = get_token_ids("说", FakeTokenizer())

    assert aligner._script_conversion_config is None
    assert token_ids == []
    assert char_indices == []


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
        CtcModel,
        "__call__",
        lambda _self, _audio, _text, _model_text=None: (log_probs, [1, 2], [0, 1], 0),
    )

    segments = aligner(AudioSegment.silent(duration=1234), "你好")

    assert segments[0].words is not None
    assert segments[0].words[0].start == round(1.234 / 4, 3)
    assert segments[0].words[0].end == round(3 * 1.234 / 4, 3)
    assert segments[0].words[0].confidence == round((0.9 + 0.85) / 2, 3)


def test_ctc_aligner_rejects_empty_text():
    """Test empty text is not sent through forced alignment."""
    with pytest.raises(TranscriptionAlignmentError, match="empty transcript"):
        CtcAligner(Language.yue_hant)(AudioSegment.empty(), "   ")


@pytest.mark.parametrize(
    "backend_error", [OSError("model unavailable"), RuntimeError("backend failed")]
)
def test_ctc_aligner_wraps_backend_errors(
    monkeypatch: pytest.MonkeyPatch, backend_error: Exception
):
    """Test low-level CTC failures are exposed as alignment errors."""
    aligner = CtcAligner(Language.yue_hant)
    monkeypatch.setattr(CtcModel, "__call__", Mock(side_effect=backend_error))

    with pytest.raises(
        TranscriptionAlignmentError, match="Unable to run CTC transcription alignment"
    ):
        aligner(AudioSegment.silent(duration=1000), "你好")
