#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using Whisper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import whisper_timestamped as whisper
from pydub import AudioSegment

from scinoephile.audio.models import TranscribedSegment
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import validate_output_directory


class WhisperTranscriber:
    """Transcribes audio using Whisper."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        cache_dir_path: str | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: Name of Whisper model to use
            language: Language code for transcription
            cache_dir_path: Directory in which to cache
        """
        self.model_name = model_name
        self.model = whisper.load_model(model_name)
        self.language = language
        self.cache_dir_path = validate_output_directory(cache_dir_path)

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: Audio to transcribe
        Returns:
            Transcription, split into segments
        """
        return self.transcribe(audio)

    def transcribe(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: Audio to transcribe
        Returns:
            Transcription, split into segments
        """
        cache_path = self._get_cache_path(audio.raw_data)

        # Load transcription from cache if available
        if cache_path.exists():
            print(f"Loaded transcription from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                segments = [TranscribedSegment.model_validate(s) for s in json.load(f)]
            return segments

        # Transcribe using Whisper
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            result = whisper.transcribe(
                self.model, str(temp_audio_path), language=self.language
            )
        segments = [TranscribedSegment(**s) for s in result["segments"]]

        # Save transcription to cache
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(
                [s.model_dump() for s in segments], f, ensure_ascii=False, indent=2
            )
            print(f"Saved transcription to cache: {cache_path}")

        return segments

    def _get_cache_path(self, audio_data: bytes) -> Path:
        """Get cache path based on hash of audio data.

        Arguments:
            audio_data: Audio data to hash
        Returns:
            Path to transcription cache file
        """
        sha256 = hashlib.sha256(audio_data).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"
