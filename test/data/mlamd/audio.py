#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import time
from pathlib import Path
from pprint import pprint
from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio import AudioSeries, HanziConverter, Transcriber
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.testing import test_data_root


class SeriesMerger(Runnable):
    def invoke(
        self,
        input: dict,
        config: RunnableConfig | None = None,
        **kwargs: dict[str, Any],
    ) -> AudioSeries:
        block = input["block"]
        segments = input["segments"]
        series = AudioSeries()
        series.audio = block.audio
        series.events = block.events
        print(f"{len(series.events), len(segments)}")
        pprint([event.text for event in series.events])
        pprint([segment.text for segment in segments])
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
    # Code: Preprocess audio for transcription
    # LLM: Transcribe audio to Cantonese
    transcriber = Transcriber("khleeloo/whisper-large-v3-cantonese")
    # Code: Convert simplified Chinese to traditional
    hanzi_converter = HanziConverter("hk2s")
    # Code: Convert transcriptions to subtitles
    series_merger = SeriesMerger()
    #   AudioSubtitle will need to store metadata such as words, timings, and confidence
    # Code: Get sync groups between source subtitles and transcribed subtitles
    #   Several source subtitles expected to map to each transcribed subtitle
    # LLM: Re-split each transcribed subtitle to timings of source subtitles
    #   After this, mapping should be 1:1
    # LLM: Proofread transcribed subtitles using source subtitles

    # Pipeline
    pipeline = transcriber | hanzi_converter | series_merger

    for i, block in enumerate(yue_hans.blocks, start=1):
        print(f"\n🧱 Block {i}: {block}")
        print("🔊 Audio:", block.audio)
        start_time = time.perf_counter()
        timestamped_transcription = pipeline.invoke({"block": block})
        elapsed = time.perf_counter() - start_time

        print("📝 Timestamped Whisper Transcription:", timestamped_transcription)
        print(f"⏱️ Transcription time: {elapsed:.2f} seconds")
        break
