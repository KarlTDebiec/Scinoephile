#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for transcribing audio using Whisper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import whisper_timestamped as whisper
from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio.models import TranscribedSegment, TranscriptionPayload
from scinoephile.common.file import get_temp_file_path


class WhisperTranscriber(Runnable):
    """Runnable for transcribing audio using Whisper."""

    def __init__(self, model_name: str = "khleeloo/whisper-large-v3-cantonese"):
        """Initialize the transcriber with a Whisper model.

        Arguments:
            model_name: Name of Whisper model to use
        """
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscriptionPayload:
        """Transcribe audio block.

        Arguments:
            input: Transcription payload containing audio block
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            Transcription payload with transcribed segments
        """
        source = input["source"]
        cache_path = Path("transcriber_cache.json")

        if cache_path.exists():
            print("📂 Using cached transcription")
            with cache_path.open("r", encoding="utf-8") as f:
                segments = [TranscribedSegment.model_validate(s) for s in json.load(f)]
            return {"source": source, "segments": segments}

        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            source.audio.export(temp_audio_path, format="wav")
            result = whisper.transcribe(
                self.model,
                str(temp_audio_path),
                language="yue",
            )

        segments = [TranscribedSegment(**s) for s in result["segments"]]

        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(
                [s.model_dump() for s in segments], f, ensure_ascii=False, indent=2
            )
            print("💾 Saved transcription cache")

        return TranscriptionPayload(
            source=source,
            segments=segments,
        )
