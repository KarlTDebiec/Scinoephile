#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using Whisper."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from typing import TYPE_CHECKING, Any
from warnings import catch_warnings, filterwarnings

import whisper_timestamped as whisper

from scinoephile.audio.transcription.backend import get_backend
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import val_output_dir_path

if TYPE_CHECKING:
    from pathlib import Path

    with catch_warnings():
        filterwarnings("ignore", category=SyntaxWarning)
        filterwarnings("ignore", category=RuntimeWarning)
        from pydub import AudioSegment

logger = getLogger(__name__)


class WhisperTranscriber:
    """Transcribes audio using Whisper."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        cache_dir_path: Path | None = None,
        use_demucs: bool = False,
        use_vad: bool = True,
    ):
        """Initialize.

        Arguments:
            model_name: name of Whisper model to use
            language: language code for transcription
            cache_dir_path: directory in which to cache
            use_demucs: whether Demucs preprocessing was applied
            use_vad: whether to enable Whisper VAD
        """
        self.model_name = model_name
        self._model: Any | None = None
        self.language = language
        self.use_demucs = use_demucs
        self.use_vad = use_vad
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into segments
        """
        return self.transcribe(audio, cache_audio=cache_audio)

    @property
    def model(self) -> Any:
        """Get the cached Whisper model, loading it if needed.

        Returns:
            loaded Whisper model
        """
        if self._model is None:
            self._model = whisper.load_model(self.model_name, device=get_backend())
        return self._model

    def get_cached_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
        Returns:
            cached transcription, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None

        logger.info(f"Loaded from cache: {cache_path}")
        with cache_path.open("r", encoding="utf-8") as file:
            segments = [TranscribedSegment.model_validate(s) for s in json.load(file)]
        cache_path.touch()
        return segments

    def transcribe(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into segments
        """
        cache_audio = cache_audio or audio
        if (segments := self.get_cached_transcription(cache_audio)) is not None:
            return segments

        # Transcribe using Whisper
        cache_path = self._get_cache_path(cache_audio)
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            result = whisper.transcribe(
                self.model,
                str(temp_audio_path),
                language=self.language,
                vad=self.use_vad,
            )
        segments = [TranscribedSegment(**s) for s in result["segments"]]

        # Update cache
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(
                    [s.model_dump() for s in segments], f, ensure_ascii=False, indent=2
                )
                logger.info(f"Saved transcription to cache: {cache_path}")

        return segments

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        audio_sha256 = hashlib.sha256(audio.raw_data).hexdigest()
        cache_key = (
            f"{audio_sha256}_{self.model_name}_{self.language}_"
            f"demucs-{'on' if self.use_demucs else 'off'}_"
            f"vad-{'on' if self.use_vad else 'off'}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"
