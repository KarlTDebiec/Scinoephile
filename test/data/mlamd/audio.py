#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import whisper_timestamped as whisper
from langchain_core.runnables import Runnable, RunnableConfig
from opencc import OpenCC
from pydantic import BaseModel, Field

from scinoephile.audio import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.testing import test_data_root


class TimestampedWord(BaseModel):
    """Single word within a transcribed segment."""

    text: str = Field(..., description="Word's transcription.")
    start: float = Field(..., description="Start time of word in seconds.")
    end: float = Field(..., description="End time of word in seconds.")
    confidence: float = Field(..., description="Confidence of transcription.")


class TimestampedSegment(BaseModel):
    """Transcribed segment."""

    id: int = Field(..., description="Segment ID, usually sequential.")
    seek: int = Field(..., description="Audio seek offset where segment starts.")
    start: float = Field(..., description="Start time of segment in seconds.")
    end: float = Field(..., description="End time of the segment in seconds.")
    text: str = Field(..., description="Full transcription of segment.")
    tokens: list[int] | None = Field(None, description="Token IDs for segment.")
    temperature: float | None = Field(None, description="Sampling temperature.")
    avg_logprob: float | None = Field(None, description="Average log-probability.")
    compression_ratio: float | None = Field(None, description="Compression ratio.")
    no_speech_prob: float | None = Field(None, description="Probability of no speech.")
    words: list[TimestampedWord] | None = Field(None, description="Words in segments.")


class Transcriber(Runnable):
    def __init__(self, model_name: str = "khleeloo/whisper-large-v3-cantonese"):
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

    def invoke(
        self, input: Any, config: RunnableConfig | None = None, **kwargs
    ) -> list[dict]:
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            input.audio.export(temp_audio_path, format="wav")
            result = whisper.transcribe(
                self.model,
                str(temp_audio_path),
                language="yue",
            )
        return [TimestampedSegment(**s) for s in result["segments"]]


class HanziConverter(Runnable):
    def __init__(self, config: str = "s2hk"):
        self.config = config
        self.converter = OpenCC(config)

    def invoke(
        self,
        input: list[TimestampedSegment],
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> list[TimestampedSegment]:
        for segment in input:
            segment.text = self.converter.convert(segment.text)
            if segment.words:
                for word in segment.words:
                    word.text = self.converter.convert(word.text)
            print(f"{len(segment.text)}, {len(segment.words)} words in segment")
            print(f"|{segment.text}|{''.join([w.text for w in segment.words])}|")
        return input


if __name__ == "__main__":
    bluray_root = Path("/Volumes/Backup/Video/Disc")
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    title = Path(__file__).parent.name
    set_logging_verbosity(2)

    # Cantonese
    subtitle_path = test_output_dir / "zho-Hans" / "zho-Hans.srt"
    video_path = bluray_root / "My Life as Mcdull.mkv"
    # yue_hans = AudioSeries.load(subtitle_path, video_path=video_path, audio_track=0)
    # yue_hans.save(test_output_dir / "yue-Hans_audio")
    yue_hans = AudioSeries.load(test_output_dir / "yue-Hans_audio")

    # Runnables
    transcriber = Transcriber("khleeloo/whisper-large-v3-cantonese")
    hanzi_converter = HanziConverter("s2hk")

    # Pipeline
    pipeline = transcriber | hanzi_converter

    for i, block in enumerate(yue_hans.blocks, start=1):
        print(f"\n🧱 Block {i}: {block}")
        print("🔊 Audio:", block.audio)
        start_time = time.perf_counter()
        timestamped_transcription = pipeline.invoke(block)
        elapsed = time.perf_counter() - start_time

        print("📝 Timestamped Whisper Transcription:", timestamped_transcription)
        print(f"⏱️ Transcription time: {elapsed:.2f} seconds")
        break
