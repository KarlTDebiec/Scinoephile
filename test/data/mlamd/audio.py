#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import time
from pathlib import Path

from data.mlamd import mlamd_merge_test_cases

from scinoephile.audio import AudioSeries
from scinoephile.audio.models import TranscriptionPayload
from scinoephile.audio.runnables import (
    CantoneseMergerInner,
    CantoneseMergerOuter,
    HanziConverter,
    SegmentSplitter,
    SeriesCompiler,
    SyncGrouper,
    WhisperTranscriber,
    map_field,
)
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    bluray_root = Path("/Volumes/Backup/Video/Disc")
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    title = Path(__file__).parent.name
    # set_logging_verbosity(2)
    examples = mlamd_merge_test_cases

    # Cantonese
    subtitle_path = test_output_dir / "zho-Hans" / "zho-Hans.srt"
    video_path = bluray_root / "My Life as Mcdull.mkv"
    # yue_hans = AudioSeries.load(subtitle_path, video_path=video_path, audio_track=0)
    # yue_hans.save(test_output_dir / "yue-Hans_audio")
    yue_hans = AudioSeries.load(test_output_dir / "yue-Hans_audio")
    # Runnables
    # Code: Preprocess 广东话 audio for transcription
    # Whisper: Transcribe 广东话 audio to 粤文
    transcriber = WhisperTranscriber(
        "khleeloo/whisper-large-v3-cantonese",
        cache_dir_path="/Users/karldebiec/Code/Scinoephile/test/data/mlamd/output/yue-Hans_audio/cache/",
    )
    # Code: Convert 繁体中文 into 简体中文
    hanzi_converter = map_field("yuewen_segments", HanziConverter("hk2s"))
    # Code: Split transcribed segments into smaller segments
    segment_splitter = map_field("yuewen_segments", SegmentSplitter(), flatten=True)
    # Code: Convert transcriptions to subtitles
    series_compiler = SeriesCompiler()
    # Code: Get sync groups between source 中文 subtitles and transcribed 粤文 subtitles
    sync_grouper = SyncGrouper()
    # LLM: Merge transcribed 粤文 subtitles to match source 中文 subtitles
    cantonese_merger = CantoneseMergerOuter(
        inner=CantoneseMergerInner(
            examples=mlamd_merge_test_cases,
            print_test_case=True,
        ),
    )
    # LLM: Proofread transcribed 粤文 subtitles using source 中文 subtitles

    # Pipeline
    chain = (
        transcriber
        | hanzi_converter
        | segment_splitter
        | series_compiler
        | sync_grouper
        | cantonese_merger
    )
    chain.get_graph().print_ascii()

    for i, block in enumerate(yue_hans.blocks, start=1):
        print(f"\n🧱 Block {i}: {block}")
        print("🔊 Audio:", block.audio)
        start_time = time.perf_counter()
        zhongwen_subs = AudioSeries()
        zhongwen_subs.audio = block.audio
        zhongwen_subs.events = block.events
        payload = TranscriptionPayload(zhongwen_subs=zhongwen_subs)
        timestamped_transcription = chain.invoke(payload)
        elapsed = time.perf_counter() - start_time

        print("📝 Timestamped Whisper Transcription:", timestamped_transcription)
        print(f"⏱️ Transcription time: {elapsed:.2f} seconds")
        # if i == 2:
        #     break
