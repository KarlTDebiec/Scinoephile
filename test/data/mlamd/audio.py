#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

from scinoephile.audio import (
    AudioSeries,
    get_segment_split_on_whitespace,
    get_series_from_segments,
)
from scinoephile.audio.cantonese import (
    CantoneseAligner,
    CantoneseMerger,
    CantoneseProofer,
    CantoneseShifter,
    CantoneseSplitter,
)
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_segment_hanzi_converted,
)
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.testing import test_data_root
from test.data.mlamd import (
    mlamd_merge_test_cases,
    mlamd_proof_test_cases,
    mlamd_shift_test_cases,
    mlamd_split_test_cases,
)

# for i, tc in enumerate(mlamd_proofread_test_cases):
#     zw = len(remove_punc_and_whitespace(tc.zhongwen))
#     yw = len(remove_punc_and_whitespace(tc.yuewen_proofread))
#     print(
#         f"Test case {i:2d}: {zw:4d} {yw:4d} {float(zw) / yw:6.2f} {tc.zhongwen}\n"
#         f"                               {tc.yuewen_proofread:}"
#     )
# exit()

if __name__ == "__main__":
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(2)

    # 中文
    zhongwen = Series.load(test_output_dir / "zho-Hans" / "zho-Hans.srt")

    # 粤文
    yuewen = AudioSeries.load(test_output_dir / "yue-Hans_audio")
    assert len(zhongwen.blocks) == len(yuewen.blocks)

    # Utilities
    transcriber = WhisperTranscriber(
        "khleeloo/whisper-large-v3-cantonese",
        cache_dir_path=test_data_root / "cache",
    )
    merger = CantoneseMerger(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    proofer = CantoneseProofer(
        examples=[m for m in mlamd_proof_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    shifter = CantoneseShifter(
        examples=[m for m in mlamd_shift_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    splitter = CantoneseSplitter(
        examples=[m for m in mlamd_split_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    aligner = CantoneseAligner(
        merger=merger, proofer=proofer, shifter=shifter, splitter=splitter
    )

    all_series = []
    for i, block in enumerate(yuewen.blocks):
        print(f"Block {i} ({block.start_idx} - {block.end_idx})")
        if i > 2:
            continue

        # Transcribe audio
        segments = transcriber(block.audio)

        # Split segments into more segments
        split_segments = []
        for segment in segments:
            split_segments.extend(get_segment_split_on_whitespace(segment))

        # Simplify segments (optional)
        converted_segments = []
        for segment in split_segments:
            converted_segments.append(get_segment_hanzi_converted(segment, "hk2s"))

        # Merge segments into a series
        yuewen_series = get_series_from_segments(
            converted_segments, offset=block[0].start
        )

        # Sync segments with the corresponding 中文 subtitles
        zhongwen_series = zhongwen.blocks[i].to_series()
        op = aligner.align(zhongwen_series, yuewen_series)
        yuewen_series = op.yuewen

        # Block complete
        print(f"MANDARIN:\n{zhongwen_series.to_simple_string()}")
        print(f"CANTONESE:\n{yuewen_series.to_simple_string()}")
        all_series.append(yuewen_series)

    yuewen_series = get_concatenated_series(all_series)
    print(f"\nConcatenated Series:\n{yuewen_series.to_simple_string()}")
