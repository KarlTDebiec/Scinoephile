#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared transcription preprocessing and fallback behavior."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.transcription import (
    DemucsMode,
    TranscribedSegment,
    Transcriber,
    TranscriptionAttempt,
    TranscriptionError,
    TranscriptionInferenceError,
    VADMode,
)
from scinoephile.core import ScinoephileError


def _get_segment(text: str) -> TranscribedSegment:
    """Get a minimal transcribed segment."""
    return TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text=text)


class _TestTranscriber(Transcriber):
    """Concrete transcriber exposing shared control flow for testing."""

    backend_name = "test"
    backend_label = "Test"

    def __init__(
        self,
        cache_dir_path: Path,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
    ):
        """Initialize."""
        self.outcomes: dict[
            TranscriptionAttempt,
            list[TranscribedSegment] | TranscriptionError,
        ] = {}
        self.calls: list[tuple[AudioSegment, TranscriptionAttempt]] = []
        super().__init__(
            cache_dir_path,
            cache_dir_path / "demucs",
            demucs_mode,
            vad_mode,
        )

    def _get_backend_cache_metadata(
        self,
        attempt: TranscriptionAttempt,
    ) -> Mapping[str, object]:
        """Get test backend cache metadata."""
        return {}

    def _transcribe_attempt(
        self,
        audio: AudioSegment,
        attempt: TranscriptionAttempt,
    ) -> list[TranscribedSegment]:
        """Return or raise the configured outcome for an attempt."""
        self.calls.append((audio, attempt))
        outcome = self.outcomes[attempt]
        if isinstance(outcome, TranscriptionError):
            raise outcome
        return outcome


def test_get_attempts_orders_preferred_configurations_first(tmp_path: Path):
    """Test automatic modes try Demucs and VAD before their fallbacks."""
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VADMode.AUTO)

    assert transcriber._get_attempts() == (
        TranscriptionAttempt(True, True),
        TranscriptionAttempt(True, False),
        TranscriptionAttempt(False, True),
        TranscriptionAttempt(False, False),
    )


def test_get_attempts_honors_forced_modes(tmp_path: Path):
    """Test forced modes produce only their requested configuration."""
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VADMode.ON)

    assert transcriber._get_attempts() == (TranscriptionAttempt(False, True),)


def test_fallback_cache_is_checked_before_demucs(tmp_path: Path):
    """Test a usable fallback cache avoids expensive Demucs preprocessing."""
    audio = AudioSegment.silent(duration=100)
    segments = [_get_segment("cached")]
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VADMode.OFF)
    transcriber._cache.save(
        audio,
        transcriber._get_cache_metadata(TranscriptionAttempt(False, False)),
        segments,
    )
    transcriber.demucs_separator = Mock(model_name="htdemucs_ft")

    assert transcriber(audio) == segments
    transcriber.demucs_separator.assert_not_called()
    assert transcriber.calls == []


def test_overwrite_removes_all_attempt_caches_before_transcribing(tmp_path: Path):
    """Test cache overwrite clears every fallback variant before inference."""
    audio = AudioSegment.silent(duration=100)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VADMode.AUTO)
    attempts = transcriber._get_attempts()
    cache_paths = []
    for attempt in attempts:
        cache_path = transcriber._cache.save(
            audio,
            transcriber._get_cache_metadata(attempt),
            [_get_segment("old")],
        )
        assert cache_path is not None
        cache_paths.append(cache_path)
        transcriber.outcomes[attempt] = [_get_segment("new")]
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        return_value=audio,
    )

    assert transcriber(audio, overwrite_cache=True) == [_get_segment("new")]
    assert cache_paths[0].exists()
    assert not any(cache_path.exists() for cache_path in cache_paths[1:])
    transcriber.demucs_separator.assert_called_once_with(
        audio,
        overwrite_cache=True,
    )


def test_auto_demucs_failure_uses_original_audio(tmp_path: Path):
    """Test automatic Demucs failure falls back to the original audio."""
    audio = AudioSegment.silent(duration=100)
    attempt = TranscriptionAttempt(False, False)
    segments = [_get_segment("fallback")]
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VADMode.OFF)
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        side_effect=ScinoephileError("failed"),
    )
    transcriber.outcomes[attempt] = segments

    assert transcriber(audio) == segments
    assert transcriber.calls == [(audio, attempt)]


def test_forced_demucs_failure_propagates(tmp_path: Path):
    """Test forced Demucs failure does not silently use original audio."""
    audio = AudioSegment.silent(duration=100)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.ON, VADMode.OFF)
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        side_effect=ScinoephileError("failed"),
    )

    with raises(ScinoephileError, match="failed"):
        transcriber(audio)


def test_unusable_vad_result_retries_without_vad(tmp_path: Path):
    """Test rejected VAD output triggers the configured non-VAD attempt."""
    audio = AudioSegment.silent(duration=100)
    vad_attempt = TranscriptionAttempt(False, True)
    no_vad_attempt = TranscriptionAttempt(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VADMode.AUTO)
    transcriber.outcomes[vad_attempt] = [_get_segment("bad")]
    transcriber.outcomes[no_vad_attempt] = [_get_segment("good")]

    segments = transcriber(
        audio,
        is_usable=lambda value: value[0].text == "good",
    )

    assert segments == [_get_segment("good")]
    assert [attempt for _, attempt in transcriber.calls] == [
        vad_attempt,
        no_vad_attempt,
    ]


def test_rejected_cached_attempt_is_not_repeated(tmp_path: Path):
    """Test rejected cached output advances directly to the next attempt."""
    audio = AudioSegment.silent(duration=100)
    vad_attempt = TranscriptionAttempt(False, True)
    no_vad_attempt = TranscriptionAttempt(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VADMode.AUTO)
    transcriber._cache.save(
        audio,
        transcriber._get_cache_metadata(vad_attempt),
        [_get_segment("bad")],
    )
    transcriber.outcomes[no_vad_attempt] = [_get_segment("good")]

    segments = transcriber(
        audio,
        is_usable=lambda value: value[0].text == "good",
    )

    assert segments == [_get_segment("good")]
    assert transcriber.calls == [(audio, no_vad_attempt)]


def test_unusable_success_takes_precedence_over_other_attempt_error(tmp_path: Path):
    """Test one rejected result prevents an unrelated retry error from escaping."""
    audio = AudioSegment.silent(duration=100)
    vad_attempt = TranscriptionAttempt(False, True)
    no_vad_attempt = TranscriptionAttempt(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VADMode.AUTO)
    transcriber.outcomes[vad_attempt] = [_get_segment("bad")]
    transcriber.outcomes[no_vad_attempt] = TranscriptionInferenceError("failed")

    assert transcriber(audio, is_usable=lambda _segments: False) == []


def test_last_error_propagates_when_every_attempt_fails(tmp_path: Path):
    """Test the last backend error propagates when no attempt succeeds."""
    audio = AudioSegment.silent(duration=100)
    vad_attempt = TranscriptionAttempt(False, True)
    no_vad_attempt = TranscriptionAttempt(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VADMode.AUTO)
    transcriber.outcomes[vad_attempt] = TranscriptionInferenceError("first")
    transcriber.outcomes[no_vad_attempt] = TranscriptionInferenceError("last")

    with raises(TranscriptionInferenceError, match="last"):
        transcriber(audio)
