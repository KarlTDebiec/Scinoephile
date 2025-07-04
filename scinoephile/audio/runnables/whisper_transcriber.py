#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for transcribing audio using Whisper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import whisper_timestamped as whisper
from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio import AudioSeries
from scinoephile.audio.models import TranscribedSegment
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import validate_output_directory


class WhisperTranscriber(Runnable):
    """Runnable for transcribing audio using Whisper."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        cache_dir_path: str | None = None,
    ):
        """Initialize the transcriber with a Whisper model.

        Arguments:
            model_name: Name of Whisper model to use
            cache_dir_path: Directory in which to store cache files
        """
        self.model_name = model_name
        self.model = whisper.load_model(model_name)
        self.language = language
        self.cache_dir_path = validate_output_directory(cache_dir_path)

    def invoke(
        self,
        input: AudioSeries,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> list[TranscribedSegment]:
        """Transcribe audio block.

        Arguments:
            input: Transcription payload containing audio block
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            Transcription payload with transcribed segments
        """
        audio = input.audio
        cache_path = self._get_cache_path(audio.raw_data)

        # Load transcription from cache if available
        if cache_path.exists():
            print(f"Loaded transcription from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                yuewen_segments = [
                    TranscribedSegment.model_validate(s) for s in json.load(f)
                ]
            return yuewen_segments

        # Transcribe using Whisper
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            result = whisper.transcribe(
                self.model,
                str(temp_audio_path),
                language=self.language,
            )
        yuewen_segments = [TranscribedSegment(**s) for s in result["segments"]]

        # Save transcription to cache
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(
                [s.model_dump() for s in yuewen_segments],
                f,
                ensure_ascii=False,
                indent=2,
            )
            print(f"Saved transcription to cache: {cache_path}")

        return yuewen_segments

    def _get_cache_path(self, audio_data: bytes) -> Path:
        """Get cache path based on hash of audio data.

        Arguments:
            audio_data: Audio data to hash
        Returns:
            Path to transcription cache file
        """
        sha256 = hashlib.sha256(audio_data).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"
