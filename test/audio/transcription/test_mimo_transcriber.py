#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of MimoTranscriber."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.transcription.mimo_inference import MimoInferenceResult
from scinoephile.audio.transcription.mimo_transcriber import (
    MimoInferenceError,
    MimoTranscriber,
    MimoTranscriptEmptyError,
    MimoTranscriptionError,
)
from scinoephile.core import Language

MIMO_MODEL_NAME = "mlx-community/MiMo-V2.5-ASR-MLX"


@pytest.fixture(autouse=True)
def use_apple_silicon_platform(monkeypatch: pytest.MonkeyPatch):
    """Run MiMo transcriber tests as though on the supported platform."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.system",
        Mock(return_value="Darwin"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.machine",
        Mock(return_value="arm64"),
    )


def test_get_cache_path_separates_mimo_configuration():
    """Test MiMo cache paths differ by cache-relevant configuration."""
    audio = _get_cache_audio()
    first_transcriber = _get_mimo_transcriber()
    second_transcriber = _get_mimo_transcriber()
    first_transcriber.model_name = "mimo/one"
    second_transcriber.model_name = "mimo/two"

    first_cache_path = first_transcriber._get_cache_path(audio)
    second_cache_path = second_transcriber._get_cache_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path.parent == Path("/tmp/mimo")
    assert second_cache_path.parent == Path("/tmp/mimo")
    assert first_cache_path != second_cache_path


def test_get_cache_path_uses_mlx_runtime_on_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test cache metadata identifies the fixed MLX runtime."""
    audio = _get_cache_audio()
    transcriber = _get_mimo_transcriber(model_name=MIMO_MODEL_NAME)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.system",
        Mock(return_value="Darwin"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.machine",
        Mock(return_value="arm64"),
    )

    cache_path = transcriber._get_cache_path(audio)

    assert cache_path is not None
    assert transcriber._get_cache_metadata()["runtime"] == "mlx"


def test_get_cache_path_rejects_non_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo fails clearly when MLX is unavailable."""
    audio = _get_cache_audio()
    transcriber = _get_mimo_transcriber()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.system",
        Mock(return_value="Linux"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.machine",
        Mock(return_value="x86_64"),
    )

    with pytest.raises(MimoTranscriptionError, match="Apple Silicon MLX"):
        transcriber._get_cache_path(audio)


def test_get_cache_path_separates_mimo_generation_options():
    """Test MiMo cache paths differ by generation options."""
    audio = _get_cache_audio()
    first_transcriber = _get_mimo_transcriber()
    second_transcriber = _get_mimo_transcriber()
    second_transcriber.max_tokens = 1024

    first_cache_path = first_transcriber._get_cache_path(audio)
    second_cache_path = second_transcriber._get_cache_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_audio_formats():
    """Test MiMo cache paths include audio format metadata."""
    raw_data = b"\0\1" * 100
    audio_segments = [
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=8000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=2),
        AudioSegment(data=raw_data, sample_width=1, frame_rate=16000, channels=1),
    ]
    transcriber = _get_mimo_transcriber()

    cache_paths = {
        transcriber._get_cache_path(audio_segment) for audio_segment in audio_segments
    }

    assert len(cache_paths) == len(audio_segments)


@pytest.mark.parametrize(
    ("language", "mimo_language_code"),
    [
        (Language.eng, "en"),
        (Language.yue_hans, "zh"),
        (Language.yue_hant, "zh"),
        (Language.zho_hans, "zh"),
        (Language.zho_hant, "zh"),
    ],
)
def test_init_derives_mimo_language_codes(
    language: Language,
    mimo_language_code: str,
):
    """Test the MiMo language code is derived from Language."""
    transcriber = MimoTranscriber(language=language)

    assert transcriber.mimo_language_code == mimo_language_code


def test_init_rejects_non_positive_max_tokens():
    """Test MiMo transcriber rejects unusable generation token limits."""
    with pytest.raises(ValueError, match="MiMo max tokens must be positive"):
        MimoTranscriber(max_tokens=0)


def test_init_rejects_retry_without_vad_when_vad_is_disabled():
    """Test MiMo transcriber rejects a contradictory VAD configuration."""
    with pytest.raises(ValueError, match="when VAD is disabled"):
        MimoTranscriber(retry_without_vad=True)


def test_init_rejects_retry_without_demucs_when_demucs_is_disabled():
    """Test MiMo transcriber rejects a contradictory Demucs configuration."""
    with pytest.raises(ValueError, match="when Demucs is disabled"):
        MimoTranscriber(retry_without_demucs=True)


def test_get_cached_transcription_reads_mimo_payload(tmp_path: Path):
    """Test MiMo cache reads segment payloads from metadata-bearing files."""
    transcriber = MimoTranscriber(cache_dir_path=tmp_path)
    audio = _get_cache_audio()
    cache_path = transcriber._get_cache_path(audio)
    assert cache_path is not None
    cache_path.write_text(
        json.dumps(
            {
                "backend": "mimo",
                "segments": [
                    {
                        "id": 0,
                        "seek": 0,
                        "start": 0.0,
                        "end": 1.0,
                        "text": "你好",
                        "words": [
                            {
                                "text": "你",
                                "start": 0.0,
                                "end": 0.5,
                                "confidence": 0.9,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    segments = transcriber.get_cached_transcription(audio)

    assert segments is not None
    assert segments[0].text == "你好"
    assert segments[0].words is not None
    assert segments[0].words[0].text == "你"


def test_transcribe_uses_direct_mimo_inference(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo transcription uses direct typed inference."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(model_name=MIMO_MODEL_NAME)
    patched_align = Mock(return_value=expected_segments)

    def fake_transcribe_with_mimo(
        audio_path: Path,
        *,
        model_name: str,
        language: str,
        max_tokens: int | None,
    ) -> MimoInferenceResult:
        """Capture direct MiMo arguments and return transcript text."""
        captured.update(
            audio_path=audio_path,
            model_name=model_name,
            language=language,
            max_tokens=max_tokens,
        )
        return MimoInferenceResult(text="你好", duration_seconds=1.0)

    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        fake_transcribe_with_mimo,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert captured["model_name"] == MIMO_MODEL_NAME
    assert captured["language"] == "zh"
    assert captured["max_tokens"] is None
    assert isinstance(captured["audio_path"], Path)


def test_transcribe_derives_mimo_language_and_passes_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo transcription derives language codes and forwards max tokens."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        language=Language.eng,
        max_tokens=1024,
    )
    patched_align = Mock(return_value=expected_segments)

    def fake_transcribe_with_mimo(
        _audio_path: Path,
        *,
        model_name: str,
        language: str,
        max_tokens: int | None,
    ) -> MimoInferenceResult:
        """Capture direct MiMo arguments and return transcript text."""
        captured.update(
            model_name=model_name,
            language=language,
            max_tokens=max_tokens,
        )
        return MimoInferenceResult(text="你好", duration_seconds=1.0)

    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        fake_transcribe_with_mimo,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert captured["model_name"] == MIMO_MODEL_NAME
    assert captured["language"] == "en"
    assert captured["max_tokens"] == 1024


def test_transcribe_chunks_audio_and_offsets_segments(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo chunking offsets segments and drops overlap duplicates."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    patched_run_mimo = Mock(
        side_effect=[
            MimoInferenceResult(text="one", duration_seconds=2.5),
            MimoInferenceResult(text="two", duration_seconds=3.0),
            MimoInferenceResult(text="three", duration_seconds=1.0),
        ]
    )
    patched_align = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            [
                TranscribedSegment(
                    id=0,
                    seek=0,
                    start=0.1,
                    end=2.2,
                    text="duplicatetwo",
                    words=[
                        TranscribedWord(
                            text="duplicate",
                            start=0.1,
                            end=0.3,
                            confidence=0.9,
                        ),
                        TranscribedWord(
                            text="two",
                            start=0.7,
                            end=2.2,
                            confidence=0.9,
                        ),
                    ],
                )
            ],
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_run_mimo", patched_run_mimo)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    assert patched_run_mimo.call_count == 3
    assert patched_align.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.id for segment in segments] == [0, 1, 2]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 2.2, 4.1])
    assert [segment.end for segment in segments] == pytest.approx([0.9, 3.7, 4.5])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(2.2)
    assert segments[1].words[0].end == pytest.approx(3.7)


def test_transcribe_chunks_audio_skips_empty_windows(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test an empty MiMo chunk does not discard speech from other chunks."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MimoTranscriber(
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            MimoTranscriptEmptyError("MiMo returned empty transcript."),
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_audio_window", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert patched_transcribe.call_count == 3
    assert [segment.text for segment in segments] == ["one", "three"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 4.1])


def test_transcribe_chunks_audio_rejects_all_empty_windows(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test chunked MiMo transcription remains empty when every chunk is empty."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MimoTranscriber(
        chunk_duration_seconds=2.0,
    )
    monkeypatch.setattr(
        transcriber,
        "_transcribe_audio_window",
        Mock(side_effect=MimoTranscriptEmptyError("MiMo returned empty transcript.")),
    )

    with pytest.raises(MimoTranscriptEmptyError, match="across audio chunks"):
        transcriber.transcribe(audio)


def test_transcribe_vad_restores_original_timestamps(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo VAD removes silence and restores original word timings."""
    audio = AudioSegment.silent(duration=6000)
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        use_vad=True,
    )
    monkeypatch.setattr(
        transcriber,
        "_get_vad_speech_intervals",
        Mock(return_value=[(1000, 2000), (4000, 5500)]),
    )
    patched_transcribe = Mock(
        return_value=[
            _get_timed_segment("one", start=0.1, end=0.9),
            _get_timed_segment("two", start=1.2, end=2.2),
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    segments = transcriber.transcribe(audio)

    speech_audio = patched_transcribe.call_args.args[0]
    assert len(speech_audio) == 2500
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([1.1, 4.2])
    assert [segment.end for segment in segments] == pytest.approx([1.9, 5.2])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(4.2)
    assert segments[1].words[0].end == pytest.approx(5.2)


def test_transcribe_vad_rejects_audio_without_detected_speech(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo VAD does not invoke MiMo when no speech is detected."""
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        use_vad=True,
    )
    monkeypatch.setattr(
        transcriber,
        "_get_vad_speech_intervals",
        Mock(return_value=[]),
    )
    patched_transcribe = Mock()
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    with pytest.raises(MimoTranscriptEmptyError, match="VAD found no speech"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_transcribe.assert_not_called()


def test_transcribe_vad_auto_retries_unfiltered_audio(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test automatic MiMo VAD retries unfiltered audio after VAD failure."""
    expected_segments = [_get_timed_segment("retry")]
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        use_vad=True,
        retry_without_vad=True,
    )
    monkeypatch.setattr(
        transcriber,
        "_get_vad_speech_intervals",
        Mock(return_value=[]),
    )
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)
    audio = AudioSegment.silent(duration=1000)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(audio)


def test_transcribe_retries_without_vad_after_unusable_output(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test rejected VAD output triggers the configured non-VAD retry."""
    rejected_segments = [_get_timed_segment("rejected")]
    expected_segments = [_get_timed_segment("accepted")]
    transcriber = MimoTranscriber(use_vad=True, retry_without_vad=True)
    patched_transcribe = Mock(
        side_effect=[rejected_segments, expected_segments],
    )
    monkeypatch.setattr(transcriber, "_transcribe_uncached", patched_transcribe)

    segments = transcriber.transcribe(
        AudioSegment.silent(duration=1000),
        is_usable=lambda candidate: candidate == expected_segments,
        use_cache=False,
    )

    assert segments == expected_segments
    assert [call.kwargs["use_vad"] for call in patched_transcribe.call_args_list] == [
        True,
        False,
    ]


def test_transcribe_retries_original_audio_after_unusable_demucs_output(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test rejected Demucs output triggers the configured original-audio retry."""
    rejected_segments = [_get_timed_segment("rejected")]
    expected_segments = [_get_timed_segment("accepted")]
    transcriber = MimoTranscriber(
        use_demucs=True,
        retry_without_demucs=True,
    )
    original_audio = AudioSegment.silent(duration=1000)
    separated_audio = AudioSegment.silent(duration=900)
    transcriber.demucs_separator = Mock(return_value=separated_audio)
    patched_transcribe = Mock(
        side_effect=[rejected_segments, expected_segments],
    )
    monkeypatch.setattr(transcriber, "_transcribe_uncached", patched_transcribe)

    segments = transcriber.transcribe(
        original_audio,
        is_usable=lambda candidate: candidate == expected_segments,
        use_cache=False,
    )

    assert segments == expected_segments
    assert [call.args[0] for call in patched_transcribe.call_args_list] == [
        separated_audio,
        original_audio,
    ]


def test_transcribe_aligns_mimo_text_and_writes_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test MiMo transcription text is aligned, returned, and cached."""
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(cache_dir_path=tmp_path)
    monkeypatch.setattr(
        transcriber,
        "_run_mimo",
        lambda _audio_path: MimoInferenceResult(text="你好", duration_seconds=1.0),
    )
    patched_align = Mock(return_value=expected_segments)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_align.assert_called_once()
    assert patched_align.call_args.kwargs["duration_seconds"] == 1.0
    cache_path = transcriber._get_cache_path(audio)
    assert cache_path is not None
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache_payload["backend"] == "mimo"
    assert cache_payload["model_name"] == MIMO_MODEL_NAME
    assert cache_payload["segments"][0]["text"] == "你好"


def test_transcribe_rejects_low_information_vocalizations(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test isolated vocalizations do not become accepted transcription output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    transcriber = MimoTranscriber()
    monkeypatch.setattr(
        transcriber,
        "_run_mimo",
        Mock(return_value=MimoInferenceResult(text="啊！啊！", duration_seconds=1.0)),
    )
    patched_align = Mock()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    with pytest.raises(MimoTranscriptionError, match="low-information"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_align.assert_not_called()


def test_transcribe_wraps_mimo_inference_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo import/runtime errors are exposed as inference errors."""
    audio = AudioSegment.silent(duration=1000)
    transcriber = MimoTranscriber()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        Mock(side_effect=ImportError("missing mlx_audio")),
    )

    with pytest.raises(MimoInferenceError, match="Unable to run MiMo inference"):
        transcriber.transcribe(audio)


def _get_mimo_transcriber(
    *,
    cache_dir_path: Path = Path("/tmp/mimo"),
    model_name: str = MIMO_MODEL_NAME,
) -> MimoTranscriber:
    """Get a minimally initialized MiMo transcriber.

    Arguments:
        cache_dir_path: cache directory path
        model_name: MiMo model name
    Returns:
        minimally initialized transcriber
    """
    transcriber = object.__new__(MimoTranscriber)
    transcriber.cache_dir_path = cache_dir_path
    transcriber.model_name = model_name
    transcriber.language = Language.yue_hant
    transcriber.mimo_language_code = "zh"
    transcriber.max_tokens = None
    transcriber.chunk_duration_seconds = None
    transcriber.chunk_overlap_seconds = 1.0
    transcriber.use_demucs = False
    transcriber.use_vad = False
    transcriber.retry_without_demucs = False
    transcriber.retry_without_vad = False
    transcriber.demucs_separator = None
    return transcriber


def _get_cache_audio() -> AudioSegment:
    """Get a small audio segment suitable for MiMo cache tests.

    Returns:
        audio segment with concrete format metadata
    """
    return AudioSegment(
        data=b"\0\1" * 100,
        sample_width=2,
        frame_rate=16000,
        channels=1,
    )


def _get_timed_segment(
    text: str,
    *,
    start: float = 0.0,
    end: float = 1.0,
) -> TranscribedSegment:
    """Get a segment with word timing data.

    Arguments:
        text: segment text
        start: start time in seconds
        end: end time in seconds
    Returns:
        segment with one timed word
    """
    return TranscribedSegment(
        id=0,
        seek=0,
        start=start,
        end=end,
        text=text,
        words=[TranscribedWord(text=text, start=start, end=end, confidence=0.9)],
    )
