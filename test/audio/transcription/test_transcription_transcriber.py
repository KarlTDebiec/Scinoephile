#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared transcription preprocessing and fallback behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription import (
    DemucsMode,
    TranscribedSegment,
    Transcriber,
    TranscriptionCache,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionPreprocessingSettings,
    TranscriptionRecognitionError,
    VadMode,
)
from scinoephile.audio.vad import VoiceActivityError
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.identity import CacheIdentity

_DEMUCS_CACHE_IDENTITY = {
    "model_name": "htdemucs_ft",
    "runtime": {"distribution": "demucs-infer", "version": "test"},
}


def _get_segment(text: str) -> TranscribedSegment:
    """Get a minimal transcribed segment.

    Arguments:
        text: text
    Returns:
        a minimal transcribed segment
    """
    return TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text=text)


class _TestTranscriber(Transcriber):
    """Concrete transcriber exposing shared control flow for testing."""

    cache_namespace = AudioCacheNamespace.TRANSCRIPTION_WHISPER
    backend_name = "test"
    backend_label = "Test"

    def __init__(
        self,
        cache_root_path: Path,
        demucs_mode: DemucsMode,
        vad_mode: VadMode,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: cache root path
            demucs_mode: demucs mode value
            vad_mode: vad mode value
            overwrite_cache: overwrite cache
        """
        self.outcomes: dict[
            TranscriptionPreprocessingSettings,
            list[TranscribedSegment] | TranscriptionError,
        ] = {}
        self.calls: list[tuple[AudioSegment, TranscriptionPreprocessingSettings]] = []
        super().__init__(cache_root_path, demucs_mode, vad_mode, overwrite_cache)

    def _get_transcriber_cache_identity(self, audio: AudioSegment) -> CacheIdentity:
        """Get the test transcriber cache identity.

        Arguments:
            audio: audio
        Returns:
            the test transcriber cache identity
        """
        return {}

    def _transcribe_attempt(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Return or raise the configured outcome for preprocessing settings.

        Arguments:
            audio: audio
            settings: settings
        Returns:
            or raise the configured outcome for preprocessing settings
        Raises:
            Exception: if the operation fails
        """
        self.calls.append((audio, settings))
        outcome = self.outcomes[settings]
        if isinstance(outcome, TranscriptionError):
            raise outcome
        return outcome


class _PerAudioCacheTranscriber(_TestTranscriber):
    """Test transcriber whose cache identity depends on audio duration."""

    def _get_transcriber_cache_identity(self, audio: AudioSegment) -> CacheIdentity:
        """Add the audio duration to the transcriber cache identity.

        Arguments:
            audio: audio
        Returns:
            transcriber cache identity
        """
        cache_identity = dict(super()._get_transcriber_cache_identity(audio))
        cache_identity["audio_duration_ms"] = len(audio)
        return cache_identity


def test_get_preprocessing_settings_orders_preferred_configurations_first(
    tmp_path: Path,
):
    """Test automatic modes try Demucs and VAD before their fallbacks.

    Arguments:
        tmp_path: temporary directory path
    """
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VadMode.AUTO)

    assert transcriber._cache.cache_dir_path == tmp_path / "audio/transcription/whisper"
    assert transcriber.demucs_separator is not None
    assert transcriber.demucs_separator._cache.cache_dir_path == (
        tmp_path / "audio/separation/demucs"
    )
    assert transcriber._get_preprocessing_settings() == (
        TranscriptionPreprocessingSettings(True, True),
        TranscriptionPreprocessingSettings(True, False),
        TranscriptionPreprocessingSettings(False, True),
        TranscriptionPreprocessingSettings(False, False),
    )


def test_get_preprocessing_settings_honors_forced_modes(tmp_path: Path):
    """Test forced modes produce only their requested configuration.

    Arguments:
        tmp_path: temporary directory path
    """
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.ON)

    assert transcriber._get_preprocessing_settings() == (
        TranscriptionPreprocessingSettings(False, True),
    )


def test_per_audio_cache_identity_is_used_for_cache_lifecycle(tmp_path: Path):
    """Test per-audio identity controls cache saves, loads, and removals.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    settings = TranscriptionPreprocessingSettings(False, False)
    segments = [_get_segment("cached")]
    transcriber = _PerAudioCacheTranscriber(tmp_path, DemucsMode.OFF, VadMode.OFF)
    transcriber.outcomes[settings] = segments

    assert transcriber(audio) == segments
    cache_identity = transcriber._get_cache_identity(audio, settings)
    per_audio_cache_path = transcriber._cache.get_path(audio, cache_identity)
    cache_identity.pop("audio_duration_ms")
    generic_cache_path = transcriber._cache.get_path(audio, cache_identity)
    assert per_audio_cache_path.exists()
    assert not generic_cache_path.exists()
    assert transcriber.last_cache_key_sha256 == per_audio_cache_path.stem

    assert transcriber(audio) == segments
    assert transcriber.calls == [(audio, settings)]
    assert transcriber.last_cache_key_sha256 == per_audio_cache_path.stem

    transcriber.remove_cached_transcriptions(audio)
    assert not per_audio_cache_path.exists()
    assert transcriber.get_cached_transcription(audio) is None
    assert transcriber.last_cache_key_sha256 is None


def test_demucs_runtime_separates_transcription_cache_paths(tmp_path: Path):
    """Test Demucs runtime upgrades invalidate dependent transcription output.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    settings = TranscriptionPreprocessingSettings(True, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.ON, VadMode.OFF)
    assert transcriber.demucs_separator is not None
    transcriber.demucs_separator._cache.runtime_identity = {
        "demucs_infer": {"distribution": "demucs-infer", "version": "4.2.2"},
        "torch": {"distribution": "torch", "version": "stable"},
        "torchaudio": {"distribution": "torchaudio", "version": "stable"},
    }
    first_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )
    transcriber.demucs_separator._cache.runtime_identity = {
        "demucs_infer": {"distribution": "demucs-infer", "version": "4.3.0"},
        "torch": {"distribution": "torch", "version": "stable"},
        "torchaudio": {"distribution": "torchaudio", "version": "stable"},
    }
    second_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )

    assert first_path != second_path


def test_fallback_cache_is_checked_before_demucs(tmp_path: Path):
    """Test a usable fallback cache avoids expensive Demucs preprocessing.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    segments = [_get_segment("cached")]
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VadMode.OFF)
    transcriber._cache.save(
        audio,
        transcriber._get_cache_identity(
            audio, TranscriptionPreprocessingSettings(False, False)
        ),
        segments,
    )
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft", cache_identity=_DEMUCS_CACHE_IDENTITY
    )

    assert transcriber(audio) == segments
    transcriber.demucs_separator.assert_not_called()
    assert transcriber.calls == []


def test_overwrite_removes_all_configuration_caches_before_transcribing(tmp_path: Path):
    """Test cache overwrite clears every fallback variant before inference.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    transcriber = _TestTranscriber(
        tmp_path, DemucsMode.AUTO, VadMode.AUTO, overwrite_cache=True
    )
    assert transcriber.demucs_separator is not None
    demucs_cache_identity = transcriber.demucs_separator.cache_identity
    preprocessing_settings = transcriber._get_preprocessing_settings()
    stale_cache = TranscriptionCache(
        tmp_path, AudioCacheNamespace.TRANSCRIPTION_WHISPER, "test", "Test"
    )
    cache_paths = []
    for settings in preprocessing_settings:
        cache_path = stale_cache.save(
            audio,
            transcriber._get_cache_identity(audio, settings),
            [_get_segment("old")],
        )
        cache_paths.append(cache_path)
        transcriber.outcomes[settings] = [_get_segment("new")]
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        cache_identity=demucs_cache_identity,
        return_value=audio,
    )

    assert transcriber(audio) == [_get_segment("new")]
    assert cache_paths[0].exists()
    assert not any(cache_path.exists() for cache_path in cache_paths[1:])
    transcriber.demucs_separator.assert_called_once_with(audio)


def test_auto_demucs_failure_uses_original_audio(tmp_path: Path):
    """Test automatic Demucs failure falls back to the original audio.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    settings = TranscriptionPreprocessingSettings(False, False)
    segments = [_get_segment("fallback")]
    transcriber = _TestTranscriber(tmp_path, DemucsMode.AUTO, VadMode.OFF)
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        cache_identity=_DEMUCS_CACHE_IDENTITY,
        side_effect=ScinoephileError("failed"),
    )
    transcriber.outcomes[settings] = segments

    assert transcriber(audio) == segments
    assert transcriber.calls == [(audio, settings)]


def test_forced_demucs_failure_propagates(tmp_path: Path):
    """Test forced Demucs failure does not silently use original audio.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.ON, VadMode.OFF)
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        cache_identity=_DEMUCS_CACHE_IDENTITY,
        side_effect=ScinoephileError("failed"),
    )

    with raises(ScinoephileError, match="failed"):
        transcriber(audio)


def test_unusable_vad_result_retries_without_vad(tmp_path: Path):
    """Test rejected VAD output triggers the non-VAD configuration.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber.outcomes[vad_settings] = [_get_segment("bad")]
    transcriber.outcomes[no_vad_settings] = [_get_segment("good")]

    segments = transcriber(audio, is_usable=lambda value: value[0].text == "good")

    assert segments == [_get_segment("good")]
    assert [settings for _, settings in transcriber.calls] == [
        vad_settings,
        no_vad_settings,
    ]


def test_rejected_cached_configuration_is_not_repeated(tmp_path: Path):
    """Test rejected cached output advances to the next configuration.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber._cache.save(
        audio,
        transcriber._get_cache_identity(audio, vad_settings),
        [_get_segment("bad")],
    )
    transcriber.outcomes[no_vad_settings] = [_get_segment("good")]

    segments = transcriber(audio, is_usable=lambda value: value[0].text == "good")

    assert segments == [_get_segment("good")]
    assert transcriber.calls == [(audio, no_vad_settings)]


def test_rejected_cached_final_configuration_is_not_repeated(tmp_path: Path):
    """Test rejected final cache output prevents repeated transcription.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    audio = AudioSegment.silent(duration=100)
    settings = TranscriptionPreprocessingSettings(True, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.ON, VadMode.OFF)
    transcriber.demucs_separator = Mock(
        model_name="htdemucs_ft",
        cache_identity=_DEMUCS_CACHE_IDENTITY,
        return_value=audio,
    )
    transcriber._cache.save(
        audio, transcriber._get_cache_identity(audio, settings), [_get_segment("bad")]
    )
    transcriber.outcomes[settings] = [_get_segment("good")]

    segments = transcriber(audio, is_usable=lambda value: value[0].text == "good")

    assert segments == []
    transcriber.demucs_separator.assert_not_called()
    assert transcriber.calls == []


def test_empty_failures_are_cached(tmp_path: Path):
    """Test completed attempts without usable speech are not repeated.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber.outcomes[vad_settings] = TranscriptionEmptyError("no VAD speech")
    transcriber.outcomes[no_vad_settings] = TranscriptionEmptyError("empty transcript")

    with raises(TranscriptionEmptyError, match="empty transcript"):
        transcriber(audio, is_usable=bool)

    expected_calls = [(audio, vad_settings), (audio, no_vad_settings)]
    assert transcriber.calls == expected_calls
    assert transcriber(audio) == []
    assert transcriber.calls == expected_calls


def test_cached_empty_attempt_does_not_shadow_cached_fallback(tmp_path: Path):
    """Test an empty preferred cache advances to a successful fallback.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    expected_segments = [_get_segment("fallback")]
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber._cache.save(
        audio, transcriber._get_cache_identity(audio, vad_settings), []
    )
    transcriber._cache.save(
        audio,
        transcriber._get_cache_identity(audio, no_vad_settings),
        expected_segments,
    )

    assert transcriber(audio) == expected_segments
    assert transcriber.calls == []


def test_rejected_cached_configuration_takes_precedence_over_other_error(
    tmp_path: Path,
):
    """Test a rejected cache prevents an unrelated retry error from escaping.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber._cache.save(
        audio,
        transcriber._get_cache_identity(audio, vad_settings),
        [_get_segment("bad")],
    )
    transcriber.outcomes[no_vad_settings] = TranscriptionRecognitionError("failed")

    assert transcriber(audio, is_usable=lambda _segments: False) == []
    assert transcriber.calls == [(audio, no_vad_settings)]


def test_unusable_success_takes_precedence_over_other_configuration_error(
    tmp_path: Path,
):
    """Test one rejected result prevents an unrelated retry error from escaping.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber.outcomes[vad_settings] = [_get_segment("bad")]
    transcriber.outcomes[no_vad_settings] = TranscriptionRecognitionError("failed")

    assert transcriber(audio, is_usable=lambda _segments: False) == []
    assert transcriber.last_cache_key_sha256 is None


def test_last_error_propagates_when_every_configuration_fails(tmp_path: Path):
    """Test the last backend error propagates when no configuration succeeds.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    vad_settings = TranscriptionPreprocessingSettings(False, True)
    no_vad_settings = TranscriptionPreprocessingSettings(False, False)
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.AUTO)
    transcriber.outcomes[vad_settings] = TranscriptionRecognitionError("first")
    transcriber.outcomes[no_vad_settings] = TranscriptionRecognitionError("last")

    with raises(TranscriptionRecognitionError, match="last"):
        transcriber(audio)

    for settings in (vad_settings, no_vad_settings):
        cache_path = transcriber._cache.get_path(
            audio, transcriber._get_cache_identity(audio, settings)
        )
        assert not cache_path.exists()


def test_voice_activity_trace_save_reuses_lookup_identity(tmp_path: Path):
    """Save a newly inferred trace under the identity used for its lookup.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    trace = Mock()
    detector = Mock()
    detector.trace_cache_identity = {"runtime": "test"}
    detector.get_trace.return_value = trace
    cache = Mock()
    cache.load.return_value = None
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.ON)
    transcriber.vad_detector = detector
    transcriber._voice_activity_cache = cache

    assert transcriber._get_voice_activity_trace(audio) is trace
    cache.load.assert_called_once_with(audio, {"runtime": "test"})
    cache.save.assert_called_once_with(audio, {"runtime": "test"}, trace)


def test_voice_activity_error_is_translated_at_transcription_boundary(tmp_path: Path):
    """Translate reusable VAD failures into transcription-domain failures.

    Arguments:
        tmp_path: temporary directory path
    """
    audio = AudioSegment.silent(duration=100)
    voice_activity_error = VoiceActivityError("VAD failed")
    detector = Mock()
    detector.trace_cache_identity = {"runtime": "test"}
    detector.get_trace.side_effect = voice_activity_error
    cache = Mock()
    cache.load.return_value = None
    transcriber = _TestTranscriber(tmp_path, DemucsMode.OFF, VadMode.ON)
    transcriber.vad_detector = detector
    transcriber._voice_activity_cache = cache

    with raises(TranscriptionRecognitionError, match="VAD failed") as exc_info:
        transcriber._get_voice_activity_trace(audio)

    assert exc_info.value.__cause__ is voice_activity_error
