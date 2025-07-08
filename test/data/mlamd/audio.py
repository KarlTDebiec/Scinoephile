#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import time
from logging import error
from pathlib import Path

from scinoephile.audio import AudioSeries
from scinoephile.audio.models import TranscriptionPayload
from scinoephile.audio.runnables import (
    SeriesCompiler,
    WhisperTranscriber,
    map_field,
)
from scinoephile.core import ScinoephileError
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    bluray_root = Path("/Volumes/Backup/Video/Disc")
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    title = Path(__file__).parent.name
    # set_logging_verbosity(2)

    # Cantonese
    subtitle_path = test_output_dir / "zho-Hans" / "zho-Hans.srt"
    video_path = bluray_root / "My Life as Mcdull.mkv"
    # yue_hans = AudioSeries.load(subtitle_path, video_path=video_path, audio_track=0)
    # yue_hans.save(test_output_dir / "yue-Hans_audio")
    yue_hans = AudioSeries.load(test_output_dir / "yue-Hans_audio")
    # Runnables
    # Code: Preprocess 广东话 audio for transcription
    # Whisper: Transcribe 广东话 audio to 粤文
    transcriber = map_field(
        "zhongwen_subs",
        WhisperTranscriber(
            "khleeloo/whisper-large-v3-cantonese",
            cache_dir_path="/Users/karldebiec/Code/Scinoephile/test/data/mlamd/output/yue-Hans_audio/cache/",
        ),
        output_field="yuewen_segments",
    )
    # Code: Convert transcriptions to subtitles
    series_compiler = SeriesCompiler()

    # Pipeline
    chain = transcriber | series_compiler

    for i, block in enumerate(yue_hans.blocks, start=1):
        if i != 3:
            continue
        print(f"\n🧱 Block {i}: {block}")
        print("🔊 Audio:", block.audio)
        start_time = time.perf_counter()
        zhongwen_subs = AudioSeries()
        zhongwen_subs.audio = block.audio
        zhongwen_subs.events = block.events
        payload = TranscriptionPayload(zhongwen_subs=zhongwen_subs)
        try:
            timestamped_transcription = chain.invoke(payload)
        except ScinoephileError as e:
            error(f"Error processing block {i}:\n{e}")
            continue
        elapsed = time.perf_counter() - start_time

        print("📝 Timestamped Whisper Transcription:", timestamped_transcription)
        print(f"⏱️ Transcription time: {elapsed:.2f} seconds")
