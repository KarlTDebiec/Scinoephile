#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base class for cached audio transcription with preprocessing fallbacks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from scinoephile.audio.separation import DemucsSeparator
from scinoephile.core.cache.cache_namespace import CacheNamespace
from scinoephile.core.exceptions import ScinoephileError

from .cache import TranscriptionCache
from .exceptions import TranscriptionEmptyError, TranscriptionError
from .preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VadMode,
)
from .transcribed_segment import TranscribedSegment

__all__ = ["Transcriber"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)


class Transcriber(ABC):
    """Transcribes audio across configured Demucs and VAD fallbacks."""

    cache_namespace: ClassVar[CacheNamespace]
    """Registered namespace for cached backend output."""

    backend_name: ClassVar[str]
    """Stable backend name stored in cache metadata."""

    backend_label: ClassVar[str]
    """Human-readable backend name used in log messages."""

    def __init__(
        self,
        cache_root_path: Path | None,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VadMode = VadMode.OFF,
        overwrite_cache: bool = False,
        demucs_separator: DemucsSeparator | None = None,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            overwrite_cache: whether to replace matching cache files
            demucs_separator: optional shared Demucs vocal separator
        """
        self.demucs_mode = demucs_mode
        """Demucs preprocessing mode."""

        self.vad_mode = vad_mode
        """Voice activity detection mode."""

        self._cache = TranscriptionCache(
            cache_root_path,
            self.cache_namespace,
            self.backend_name,
            self.backend_label,
            overwrite_cache,
        )
        """Timestamped transcription cache."""

        self.demucs_separator: DemucsSeparator | None = None
        """Demucs vocal separator used by configured preprocessing settings."""
        if self.demucs_mode is not DemucsMode.OFF:
            if demucs_separator is None:
                demucs_separator = DemucsSeparator(
                    cache_root_path=self._cache.cache_root_path,
                    overwrite_cache=overwrite_cache,
                )
            self.demucs_separator = demucs_separator

    def __call__(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            is_usable: optional callback used to reject output and trigger retries
        Returns:
            transcription split into timestamped segments
        """
        return self.transcribe(audio, is_usable=is_usable)

    def get_cached_transcription(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment] | None:
        """Get the first usable cached transcription across configured settings.

        Arguments:
            audio: audio used for cache-key generation
            is_usable: optional callback used to reject cached output
        Returns:
            first usable cached transcription, if present
        """
        segments, _ = self._find_cached_transcription(
            audio, self._get_preprocessing_settings(), is_usable
        )
        return segments

    def remove_cached_transcriptions(self, audio: AudioSegment):
        """Remove cached transcriptions for all configured settings.

        Arguments:
            audio: audio used for cache-key generation
        """
        for settings in self._get_preprocessing_settings():
            self._cache.remove(audio, self._get_cache_metadata(audio, settings))

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe audio across configured preprocessing settings.

        Arguments:
            audio: audio to transcribe
            is_usable: optional callback used to reject output and trigger retries
        Returns:
            first usable transcription, or an empty list when output was rejected
        """
        preprocessing_settings = self._get_preprocessing_settings()

        # Inspect every cache before running expensive preprocessing
        segments, rejected_settings = self._find_cached_transcription(
            audio, preprocessing_settings, is_usable
        )
        if segments is not None:
            return segments

        # Run only configurations that do not already have a rejected cache
        settings_to_run = [
            settings
            for settings in preprocessing_settings
            if settings not in rejected_settings
        ]

        # Run Demucs once if any remaining configuration requires separated audio
        separated_audio = None
        if any(settings.use_demucs for settings in settings_to_run):
            separated_audio = self._get_separated_audio(audio)

        # Run remaining transcription configurations
        return self._run_configurations(
            audio, settings_to_run, rejected_settings, separated_audio, is_usable
        )

    def _find_cached_transcription(
        self,
        audio: AudioSegment,
        preprocessing_settings: Sequence[TranscriptionPreprocessingSettings],
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
    ) -> tuple[
        list[TranscribedSegment] | None, set[TranscriptionPreprocessingSettings]
    ]:
        """Find a usable cache and identify rejected preprocessing settings.

        Arguments:
            audio: audio used for cache-key generation
            preprocessing_settings: preprocessing settings in cache lookup order
            is_usable: optional callback used to reject cached output
        Returns:
            usable cached segments and rejected preprocessing settings
        """
        rejected_settings: set[TranscriptionPreprocessingSettings] = set()
        for settings in preprocessing_settings:
            metadata = self._get_cache_metadata(audio, settings)
            cached_transcription = self._cache.load(audio, metadata)
            if cached_transcription is None:
                continue
            cache_path, segments = cached_transcription
            segments = self._prepare_cached_segments(segments, cache_path, settings)
            if segments and (is_usable is None or is_usable(segments)):
                return segments, rejected_settings
            rejected_settings.add(settings)
        return None, rejected_settings

    def _get_preprocessing_settings(
        self,
    ) -> tuple[TranscriptionPreprocessingSettings, ...]:
        """Get configured preprocessing settings in retry order.

        Returns:
            configured transcription preprocessing settings
        """
        if self.demucs_mode is DemucsMode.ON:
            demucs_values = (True,)
        elif self.demucs_mode is DemucsMode.OFF:
            demucs_values = (False,)
        else:
            demucs_values = (True, False)

        if self.vad_mode is VadMode.ON:
            vad_values = (True,)
        elif self.vad_mode is VadMode.OFF:
            vad_values = (False,)
        else:
            vad_values = (True, False)

        return tuple(
            TranscriptionPreprocessingSettings(use_demucs, use_vad)
            for use_demucs in demucs_values
            for use_vad in vad_values
        )

    @abstractmethod
    def _get_backend_cache_metadata(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> Mapping[str, object]:
        """Get backend-specific cache metadata for one configuration.

        Arguments:
            audio: audio whose properties may affect backend behavior
            settings: preprocessing settings
        Returns:
            backend configuration identifying the output
        """
        raise NotImplementedError()

    def _get_cache_metadata(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> dict[str, object]:
        """Get complete backend and preprocessing cache metadata.

        Arguments:
            audio: audio whose properties may affect backend behavior
            settings: preprocessing settings
        Returns:
            configuration identifying the output
        """
        demucs_model_name = None
        if settings.use_demucs:
            assert self.demucs_separator is not None
            demucs_model_name = self.demucs_separator.model_name
        return {
            **self._get_backend_cache_metadata(audio, settings),
            "demucs_model_name": demucs_model_name,
            "use_demucs": settings.use_demucs,
            "use_vad": settings.use_vad,
        }

    def _get_separated_audio(self, audio: AudioSegment) -> AudioSegment | None:
        """Get Demucs-separated audio for configured preprocessing settings.

        Arguments:
            audio: original audio to separate
        Returns:
            separated audio, or None after an automatic-mode failure
        """
        assert self.demucs_separator is not None
        logger.info(f"Applying Demucs vocal separation before {self.backend_label}")
        try:
            return self.demucs_separator(audio)
        except ScinoephileError as exc:
            if self.demucs_mode is DemucsMode.ON:
                raise
            logger.warning(
                f"Demucs separation failed; retrying {self.backend_label} "
                f"with original audio: {exc}"
            )
            return None

    def _prepare_cached_segments(
        self,
        segments: list[TranscribedSegment],
        cache_path: Path,
        settings: TranscriptionPreprocessingSettings,
    ) -> list[TranscribedSegment]:
        """Prepare cached segments for use.

        Arguments:
            segments: cached transcription segments
            cache_path: path from which the segments were loaded
            settings: preprocessing settings that produced the segments
        Returns:
            prepared cached segments
        """
        return segments

    def _run_configurations(
        self,
        audio: AudioSegment,
        settings_to_run: Sequence[TranscriptionPreprocessingSettings],
        rejected_settings: set[TranscriptionPreprocessingSettings],
        separated_audio: AudioSegment | None,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
    ) -> list[TranscribedSegment]:
        """Run uncached transcription configurations in preprocessing order.

        Arguments:
            audio: original audio to transcribe
            settings_to_run: preprocessing settings to run in retry order
            rejected_settings: settings with unusable cached output
            separated_audio: Demucs-separated audio, if available
            is_usable: optional callback used to reject output and trigger retries
        Returns:
            first usable transcription, or an empty list when output was rejected
        """
        successful_result = bool(rejected_settings)
        last_error: TranscriptionError | None = None
        for settings in settings_to_run:
            transcription_audio = audio
            if settings.use_demucs:
                if separated_audio is None:
                    continue
                transcription_audio = separated_audio

            if self.vad_mode is VadMode.AUTO and not settings.use_vad:
                logger.info(f"Retrying {self.backend_label} without VAD")
            try:
                segments = self._transcribe_attempt(transcription_audio, settings)
            except TranscriptionEmptyError as exc:
                logger.warning(f"{self.backend_label} attempt failed: {exc}")
                self._cache.save(audio, self._get_cache_metadata(audio, settings), [])
                last_error = exc
                continue
            except TranscriptionError as exc:
                logger.warning(f"{self.backend_label} attempt failed: {exc}")
                last_error = exc
                continue
            successful_result = True

            self._cache.save(audio, self._get_cache_metadata(audio, settings), segments)
            if is_usable is None or is_usable(segments):
                return segments

        if not successful_result and last_error is not None:
            raise last_error
        return []

    @abstractmethod
    def _transcribe_attempt(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Run one uncached transcription attempt.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            settings: preprocessing settings
        Returns:
            timestamped transcription segments
        """
        raise NotImplementedError()
