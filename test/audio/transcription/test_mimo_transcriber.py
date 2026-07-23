#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of MimoTranscriber."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.transcription.forced_alignment import TranscriptionAlignmentError
from scinoephile.audio.transcription.mimo_transcriber import (
    MIMO_MLX_MODEL_NAME,
    MIMO_MODEL_NAME,
    MimoRuntime,
    MimoRuntimeUnsupportedError,
    MimoTranscriber,
    MimoTranscriptEmptyError,
    MimoTranscriptionError,
    MimoWorkerError,
)


def test_get_cache_path_separates_mimo_configuration():
    """Test MiMo cache paths differ by cache-relevant configuration."""
    audio = Mock(raw_data=b"audio")
    first_transcriber = _get_mimo_transcriber()
    second_transcriber = _get_mimo_transcriber()
    first_transcriber.aligner_model_name = "aligner/one"
    second_transcriber.aligner_model_name = "aligner/two"

    first_cache_path = first_transcriber._get_cache_path(audio)
    second_cache_path = second_transcriber._get_cache_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path.parent == Path("/tmp/mimo")
    assert second_cache_path.parent == Path("/tmp/mimo")
    assert first_cache_path != second_cache_path


def test_get_cache_path_auto_uses_mlx_model_on_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test auto runtime uses the MLX model on Apple Silicon."""
    audio = Mock(raw_data=b"audio")
    transcriber = _get_mimo_transcriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.AUTO,
    )
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
    assert transcriber._get_effective_model_name() == MIMO_MLX_MODEL_NAME


def test_get_cache_path_auto_rejects_non_apple_silicon(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test auto runtime fails clearly when MLX is unavailable."""
    audio = Mock(raw_data=b"audio")
    transcriber = _get_mimo_transcriber(mimo_runtime=MimoRuntime.AUTO)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.system",
        Mock(return_value="Linux"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.platform.machine",
        Mock(return_value="x86_64"),
    )

    with pytest.raises(MimoRuntimeUnsupportedError, match="Apple Silicon MLX"):
        transcriber._get_cache_path(audio)


def test_get_cache_path_separates_aligner_worker_command():
    """Test MiMo cache paths differ by isolated aligner worker command."""
    audio = Mock(raw_data=b"audio")
    first_transcriber = _get_mimo_transcriber()
    second_transcriber = _get_mimo_transcriber()
    first_transcriber.aligner_worker_command = ("python", "worker-one.py")
    second_transcriber.aligner_worker_command = ("python", "worker-two.py")

    first_cache_path = first_transcriber._get_cache_path(audio)
    second_cache_path = second_transcriber._get_cache_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_mimo_generation_options():
    """Test MiMo cache paths differ by generation options."""
    audio = Mock(raw_data=b"audio")
    first_transcriber = _get_mimo_transcriber()
    second_transcriber = _get_mimo_transcriber()
    second_transcriber.language = "auto"
    second_transcriber.max_tokens = 1024

    first_cache_path = first_transcriber._get_cache_path(audio)
    second_cache_path = second_transcriber._get_cache_path(audio)

    assert first_cache_path is not None
    assert second_cache_path is not None
    assert first_cache_path != second_cache_path


def test_init_rejects_non_positive_max_tokens():
    """Test MiMo transcriber rejects unusable generation token limits."""
    with pytest.raises(ValueError, match="MiMo max tokens must be positive"):
        MimoTranscriber(max_tokens=0)


def test_init_rejects_vad_fallback_when_vad_is_disabled():
    """Test MiMo transcriber rejects a contradictory VAD configuration."""
    with pytest.raises(ValueError, match="when VAD is disabled"):
        MimoTranscriber(fallback_without_vad=True)


def test_get_cached_transcription_reads_mimo_payload(tmp_path: Path):
    """Test MiMo cache reads segment payloads from metadata-bearing files."""
    transcriber = MimoTranscriber(
        cache_dir_path=tmp_path,
        mimo_runtime=MimoRuntime.MLX,
    )
    audio = Mock(raw_data=b"audio")
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


def test_parse_worker_stdout_accepts_logging_before_json():
    """Test worker stdout parsing tolerates noisy model logs before JSON."""
    parsed = MimoTranscriber._parse_worker_stdout(
        'loading model\n{"text": "你好", "backend": "mimo", "duration_seconds": 1.2}\n'
    )

    assert parsed["text"] == "你好"
    assert parsed["backend"] == "mimo"


def test_run_worker_passes_runtime_effective_model_and_source_pythonpath(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test worker requests include runtime and import path for external venvs."""
    captured: dict[str, object] = {}

    def fake_run(
        command: Sequence[str],
        *,
        input: str,
        text: bool,
        capture_output: bool,
        check: bool,
        timeout: float | None,
        env: Mapping[str, str],
    ) -> subprocess.CompletedProcess[str]:
        """Capture subprocess invocation and return a minimal worker payload."""
        captured["command"] = command
        captured["input"] = input
        captured["env"] = env
        return subprocess.CompletedProcess(
            command,
            0,
            stdout='{"text": "你好", "backend": "mimo"}\n',
            stderr="",
        )

    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.subprocess.run",
        fake_run,
    )
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
    )

    payload = transcriber._run_worker(tmp_path / "audio.wav")

    request = json.loads(cast(str, captured["input"]))
    assert request["model_name"] == MIMO_MLX_MODEL_NAME
    assert request["runtime"] == "mlx"
    assert payload["text"] == "你好"
    python_paths = cast(Mapping[str, str], captured["env"])["PYTHONPATH"].split(
        os.pathsep
    )
    assert str(Path(__file__).resolve().parents[3]) in python_paths


def test_transcribe_uses_in_process_mimo_when_worker_command_absent(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo transcription runs in-process by default."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
    )
    patched_align = Mock(return_value=expected_segments)

    def fake_transcribe_with_mimo(request: Mapping[str, object]) -> dict[str, object]:
        """Capture in-process MiMo request and return transcript text."""
        captured["request"] = request
        return {"text": "你好", "backend": "mimo"}

    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.subprocess.run",
        Mock(side_effect=AssertionError("subprocess should not be used")),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        fake_transcribe_with_mimo,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    request = cast(Mapping[str, object], captured["request"])
    assert segments == expected_segments
    assert request["model_name"] == MIMO_MLX_MODEL_NAME
    assert request["runtime"] == "mlx"
    assert request["language"] == "yue"


def test_transcribe_passes_mimo_language_and_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo transcription forwards generation options."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
        language="auto",
        max_tokens=1024,
    )

    def fake_transcribe_with_mimo(request: Mapping[str, object]) -> dict[str, object]:
        """Capture in-process MiMo request and return transcript text."""
        captured["request"] = request
        return {"text": "你好", "backend": "mimo"}

    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        fake_transcribe_with_mimo,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        Mock(return_value=expected_segments),
    )

    segments = transcriber.transcribe(audio)

    request = cast(Mapping[str, object], captured["request"])
    assert segments == expected_segments
    assert request["language"] == "auto"
    assert request["max_tokens"] == 1024


def test_transcribe_chunks_audio_and_offsets_segments(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo chunking offsets segments and drops overlap duplicates."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    patched_run_mimo = Mock(
        side_effect=[
            {"text": "one", "backend": "mimo"},
            {"text": "two", "backend": "mimo"},
            {"text": "three", "backend": "mimo"},
        ]
    )
    patched_align = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            [
                _get_timed_segment("duplicate", start=0.1, end=0.3),
                _get_timed_segment("two", start=0.7, end=2.2),
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


def test_transcribe_vad_restores_original_timestamps(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo VAD removes silence and restores original word timings."""
    audio = AudioSegment.silent(duration=6000)
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
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
        mimo_runtime=MimoRuntime.MLX,
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
    expected_segments = [_get_timed_segment("fallback")]
    transcriber = MimoTranscriber(
        model_name=MIMO_MODEL_NAME,
        mimo_runtime=MimoRuntime.MLX,
        use_vad=True,
        fallback_without_vad=True,
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


def test_transcribe_aligns_mimo_text_and_writes_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test MiMo transcription text is aligned, returned, and cached."""
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MimoTranscriber(
        cache_dir_path=tmp_path,
        mimo_runtime=MimoRuntime.MLX,
    )
    monkeypatch.setattr(
        transcriber,
        "_run_mimo",
        lambda _audio_path: {"text": "你好", "backend": "mimo"},
    )
    patched_align = Mock(return_value=expected_segments)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_align.assert_called_once()
    assert patched_align.call_args.kwargs["aligner_worker_command"] is None
    assert patched_align.call_args.kwargs["aligner_worker_timeout_seconds"] is None
    cache_path = transcriber._get_cache_path(audio)
    assert cache_path is not None
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache_payload["backend"] == "mimo"
    assert cache_payload["model_name"] == MIMO_MLX_MODEL_NAME
    assert cache_payload["segments"][0]["text"] == "你好"


def test_transcribe_rejects_low_information_vocalizations(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test isolated vocalizations do not become accepted fallback output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    transcriber = MimoTranscriber(mimo_runtime=MimoRuntime.MLX)
    monkeypatch.setattr(
        transcriber,
        "_run_mimo",
        Mock(return_value={"text": "啊！啊！", "backend": "mimo"}),
    )
    patched_align = Mock()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.align_mimo_transcription",
        patched_align,
    )

    with pytest.raises(MimoTranscriptionError, match="low-information"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_align.assert_not_called()


def test_transcribe_wraps_in_process_mimo_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test in-process MiMo import/runtime errors are user-facing worker errors."""
    audio = AudioSegment.silent(duration=1000)
    transcriber = MimoTranscriber(mimo_runtime=MimoRuntime.MLX)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mimo_transcriber.transcribe_with_mimo",
        Mock(side_effect=ImportError("missing mlx_audio")),
    )

    with pytest.raises(MimoWorkerError, match="Unable to run MiMo in-process"):
        transcriber.transcribe(audio)


@pytest.mark.parametrize(
    "failure",
    [
        MimoTranscriptEmptyError("empty transcript"),
        TranscriptionAlignmentError("alignment failed"),
    ],
)
def test_transcribe_uses_fallback_backend_when_mimo_fails(
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
):
    """Test direct MiMo callers can opt into fallback backend behavior."""
    audio = AudioSegment.silent(duration=1000)
    fallback_segments = [_get_timed_segment("fallback")]
    fallback_backend = Mock(return_value=fallback_segments)
    transcriber = MimoTranscriber(fallback_backend=fallback_backend)
    monkeypatch.setattr(transcriber, "_run_mimo", Mock(side_effect=failure))

    segments = transcriber.transcribe(audio)

    assert segments == fallback_segments
    fallback_backend.assert_called_once_with(audio, cache_audio=audio)


def _get_mimo_transcriber(
    *,
    cache_dir_path: Path = Path("/tmp/mimo"),
    model_name: str = MIMO_MODEL_NAME,
    tokenizer_name: str = "XiaomiMiMo/MiMo-Audio-Tokenizer",
    mimo_runtime: MimoRuntime = MimoRuntime.MLX,
    aligner_backend: str = "whisperx",
    aligner_language: str = "zh",
    aligner_model_name: str | None = None,
    aligner_worker_command: Sequence[str] | None = None,
) -> MimoTranscriber:
    """Get a minimally initialized MiMo transcriber.

    Arguments:
        cache_dir_path: cache directory path
        model_name: MiMo model name
        tokenizer_name: MiMo audio tokenizer name
        mimo_runtime: MiMo runtime implementation
        aligner_backend: timestamp alignment backend
        aligner_language: language code used by timestamp alignment
        aligner_model_name: optional timestamp alignment model name
        aligner_worker_command: optional timestamp aligner worker command
    Returns:
        minimally initialized transcriber
    """
    transcriber = object.__new__(MimoTranscriber)
    transcriber.cache_dir_path = cache_dir_path
    transcriber.model_name = model_name
    transcriber.tokenizer_name = tokenizer_name
    transcriber.mimo_runtime = mimo_runtime
    transcriber.language = "yue"
    transcriber.audio_tag = ""
    transcriber.aligner_backend = aligner_backend
    transcriber.aligner_language = aligner_language
    transcriber.aligner_model_name = aligner_model_name
    transcriber.aligner_worker_command = (
        tuple(aligner_worker_command) if aligner_worker_command is not None else None
    )
    transcriber.aligner_worker_timeout_seconds = None
    transcriber.worker_command = None
    transcriber.worker_timeout_seconds = None
    transcriber.max_tokens = None
    transcriber.chunk_duration_seconds = None
    transcriber.chunk_overlap_seconds = 1.0
    transcriber.use_demucs = False
    transcriber.use_vad = False
    transcriber.fallback_without_vad = False
    transcriber.fallback_backend = None
    return transcriber


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
