#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base class for cached audio transcription with preprocessing fallbacks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path

from .attempt import DemucsMode, TranscriptionAttempt, VADMode
from .cache import TranscriptionCache
from .demucs_separator import DemucsSeparator
from .exceptions import TranscriptionError
from .transcribed_segment import TranscribedSegment

__all__ = ["Transcriber"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)


class Transcriber(ABC):
    """Transcribes audio across configured Demucs and VAD fallbacks."""

    backend_name: ClassVar[str]
    """Stable backend name stored in cache metadata."""

    backend_label: ClassVar[str]
    """Human-readable backend name used in log messages."""

    def __init__(
        self,
        cache_dir_path: Path | None,
        demucs_cache_dir_path: Path | None = None,
        demucs_mode: DemucsMode = DemucsMode.AUTO,
        vad_mode: VADMode = VADMode.AUTO,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache transcriptions
            demucs_cache_dir_path: directory in which to cache Demucs output
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
        """
        self.demucs_mode = demucs_mode
        """Demucs preprocessing mode."""

        self.vad_mode = vad_mode
        """Voice activity detection mode."""

        self.demucs_separator: DemucsSeparator | None = None
        """Demucs vocal separator used by configured attempts."""
        if self.demucs_mode is not DemucsMode.OFF:
            if demucs_cache_dir_path is None:
                demucs_cache_dir_path = get_runtime_cache_dir_path("demucs")
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=demucs_cache_dir_path
            )

        self._cache = TranscriptionCache(
            cache_dir_path,
            self.backend_name,
            self.backend_label,
        )
        """Timestamped transcription cache."""

    def __call__(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
        use_cache: bool = True,
        overwrite_cache: bool = False,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            is_usable: optional callback used to reject output and trigger retries
            use_cache: whether to return a cached transcription when available
            overwrite_cache: whether to replace matching cache files
        Returns:
            transcription split into timestamped segments
        """
        return self.transcribe(
            audio,
            is_usable=is_usable,
            use_cache=use_cache,
            overwrite_cache=overwrite_cache,
        )

    @property
    def cache_dir_path(self) -> Path | None:
        """Get the transcription cache directory path."""
        return self._cache.cache_dir_path

    def get_cached_transcription(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment] | None:
        """Get the first usable cached transcription across configured attempts.

        Arguments:
            audio: audio used for cache-key generation
            is_usable: optional callback used to reject cached output
        Returns:
            first usable cached transcription, if present
        """
        segments, _ = self._find_cached_transcription(
            audio,
            self._get_attempts(),
            is_usable,
        )
        return segments

    def remove_cached_transcriptions(self, audio: AudioSegment):
        """Remove cached transcriptions for all configured attempts.

        Arguments:
            audio: audio used for cache-key generation
        """
        for attempt in self._get_attempts():
            self._cache.remove(
                audio,
                self._get_cache_metadata(attempt),
            )

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
        use_cache: bool = True,
        overwrite_cache: bool = False,
    ) -> list[TranscribedSegment]:
        """Transcribe audio across configured preprocessing attempts.

        Arguments:
            audio: audio to transcribe
            is_usable: optional callback used to reject output and trigger retries
            use_cache: whether to return a cached transcription when available
            overwrite_cache: whether to replace matching cache files
        Returns:
            first usable transcription, or an empty list when output was rejected
        """
        attempts = self._get_attempts()

        # Inspect every cache before running expensive preprocessing
        rejected_attempts: set[TranscriptionAttempt] = set()
        if overwrite_cache:
            self.remove_cached_transcriptions(audio)
        elif use_cache:
            segments, rejected_attempts = self._find_cached_transcription(
                audio,
                attempts,
                is_usable,
            )
            if segments is not None:
                return segments

        # Run Demucs once if any remaining attempt requires separated audio
        separated_audio = None
        if any(
            attempt.use_demucs and attempt not in rejected_attempts
            for attempt in attempts
        ):
            separated_audio = self._get_separated_audio(
                audio,
                overwrite_cache,
            )

        # Run remaining transcription attempts
        return self._run_attempts(
            audio,
            attempts,
            rejected_attempts,
            separated_audio,
            is_usable,
        )

    def _find_cached_transcription(
        self,
        audio: AudioSegment,
        attempts: Sequence[TranscriptionAttempt],
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
    ) -> tuple[list[TranscribedSegment] | None, set[TranscriptionAttempt]]:
        """Find a usable cache and identify rejected attempts.

        Arguments:
            audio: audio used for cache-key generation
            attempts: preprocessing attempts in retry order
            is_usable: optional callback used to reject cached output
        Returns:
            usable cached segments and rejected attempts
        """
        rejected_attempts: set[TranscriptionAttempt] = set()
        for attempt in attempts:
            metadata = self._get_cache_metadata(attempt)
            try:
                cached_transcription = self._cache.load(audio, metadata)
            except TranscriptionError as exc:
                logger.warning(
                    f"Unable to read {self.backend_label} transcription cache: {exc}"
                )
                continue
            if cached_transcription is None:
                continue
            cache_path, segments = cached_transcription
            segments = self._prepare_cached_segments(
                segments,
                cache_path,
                attempt,
            )
            if is_usable is None or is_usable(segments):
                return segments, rejected_attempts
            rejected_attempts.add(attempt)
        return None, rejected_attempts

    def _get_attempts(self) -> tuple[TranscriptionAttempt, ...]:
        """Get configured preprocessing attempts in retry order.

        Returns:
            configured transcription attempts
        """
        if self.demucs_mode is DemucsMode.ON:
            demucs_values = (True,)
        elif self.demucs_mode is DemucsMode.OFF:
            demucs_values = (False,)
        else:
            demucs_values = (True, False)

        if self.vad_mode is VADMode.ON:
            vad_values = (True,)
        elif self.vad_mode is VADMode.OFF:
            vad_values = (False,)
        else:
            vad_values = (True, False)

        return tuple(
            TranscriptionAttempt(use_demucs, use_vad)
            for use_demucs in demucs_values
            for use_vad in vad_values
        )

    @abstractmethod
    def _get_backend_cache_metadata(
        self,
        attempt: TranscriptionAttempt,
    ) -> Mapping[str, object]:
        """Get backend-specific cache metadata for one attempt.

        Arguments:
            attempt: preprocessing attempt
        Returns:
            backend configuration identifying the output
        """
        raise NotImplementedError()

    def _get_cache_metadata(
        self,
        attempt: TranscriptionAttempt,
    ) -> dict[str, object]:
        """Get complete backend and preprocessing cache metadata.

        Arguments:
            attempt: preprocessing attempt
        Returns:
            configuration identifying the output
        """
        demucs_model_name = None
        if attempt.use_demucs:
            assert self.demucs_separator is not None
            demucs_model_name = self.demucs_separator.model_name
        return {
            **self._get_backend_cache_metadata(attempt),
            "demucs_model_name": demucs_model_name,
            "use_demucs": attempt.use_demucs,
            "use_vad": attempt.use_vad,
        }

    def _get_separated_audio(
        self,
        audio: AudioSegment,
        overwrite_cache: bool,
    ) -> AudioSegment | None:
        """Get Demucs-separated audio for configured attempts.

        Arguments:
            audio: original audio to separate
            overwrite_cache: whether to replace matching Demucs cache files
        Returns:
            separated audio, or None after an automatic-mode failure
        """
        assert self.demucs_separator is not None
        logger.info(f"Applying Demucs vocal separation before {self.backend_label}")
        try:
            return self.demucs_separator(
                audio,
                overwrite_cache=overwrite_cache,
            )
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
        attempt: TranscriptionAttempt,
    ) -> list[TranscribedSegment]:
        """Prepare cached segments for use.

        Arguments:
            segments: cached transcription segments
            cache_path: path from which the segments were loaded
            attempt: preprocessing attempt that produced the segments
        Returns:
            prepared cached segments
        """
        return segments

    def _run_attempts(
        self,
        audio: AudioSegment,
        attempts: Sequence[TranscriptionAttempt],
        rejected_attempts: set[TranscriptionAttempt],
        separated_audio: AudioSegment | None,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
    ) -> list[TranscribedSegment]:
        """Run uncached transcription attempts in preprocessing order.

        Arguments:
            audio: original audio to transcribe
            attempts: preprocessing attempts in retry order
            rejected_attempts: attempts with unusable cached output
            separated_audio: Demucs-separated audio, if available
            is_usable: optional callback used to reject output and trigger retries
        Returns:
            first usable transcription, or an empty list when output was rejected
        """
        successful_attempt = False
        last_error: TranscriptionError | None = None
        for attempt in attempts:
            if attempt in rejected_attempts:
                continue

            transcription_audio = audio
            if attempt.use_demucs:
                if separated_audio is None:
                    continue
                transcription_audio = separated_audio

            if self.vad_mode is VADMode.AUTO and not attempt.use_vad:
                logger.info(f"Retrying {self.backend_label} without VAD")
            try:
                segments = self._transcribe_attempt(
                    transcription_audio,
                    attempt,
                )
            except TranscriptionError as exc:
                logger.warning(f"{self.backend_label} attempt failed: {exc}")
                last_error = exc
                continue
            successful_attempt = True

            self._cache.save(
                audio,
                self._get_cache_metadata(attempt),
                segments,
            )
            if is_usable is None or is_usable(segments):
                return segments

        if not successful_attempt and last_error is not None:
            raise last_error
        return []

    @abstractmethod
    def _transcribe_attempt(
        self,
        audio: AudioSegment,
        attempt: TranscriptionAttempt,
    ) -> list[TranscribedSegment]:
        """Run one uncached transcription attempt.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            attempt: preprocessing attempt
        Returns:
            timestamped transcription segments
        """
        raise NotImplementedError()
