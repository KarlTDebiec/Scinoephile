#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

from scinoephile.audio import AudioSeries
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_hanzi_converted_segment,
    get_series_from_segments,
    get_split_segment,
)
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"

    # Cantonese
    yue_hans = AudioSeries.load(test_output_dir / "yue-Hans_audio")

    transcriber = WhisperTranscriber(
        "khleeloo/whisper-large-v3-cantonese",
        cache_dir_path=test_output_dir / "yue-Hans_audio" / "cache",
    )

    all_series = []
    for i, block in enumerate(yue_hans.blocks, start=1):
        print(f"\nBlock {i}: {block}")
        segments = transcriber(block.audio)
        split_segments = []
        for segment in segments:
            split_segments.extend(get_split_segment(segment))
        converted_segments = []
        for segment in segments:
            converted_segments.append(get_hanzi_converted_segment(segment, "hk2s"))
        series = get_series_from_segments(split_segments, offset=block.events[0].start)
        all_series.append(series)

        print("Transcription:", segments)
        print(f"Series:\n{series.to_simple_string()}")
    series = get_concatenated_series(all_series)
    print(f"\nConcatenated Series:\n{series.to_simple_string()}")
