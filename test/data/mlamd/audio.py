#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import time
from pathlib import Path

from scinoephile.audio import AudioSeries, Transcriber
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.hanzi import HanziConverter
from scinoephile.testing import test_data_root

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
    hanzi_converter = HanziConverter("s2hk")
    # Code: Convert transcriptions to subtitles
    #   AudioSubtitle will need to store metadata such as words, timings, and confidence
    # Code: Get sync groups between source subtitles and transcribed subtitles
    #   Several source subtitles may map to each transcribed subtitle
    # LLM:

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
