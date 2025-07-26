#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

from scinoephile.audio import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.audio.cantonese.distribution import Distributor
from scinoephile.audio.cantonese.merging import Merger
from scinoephile.audio.cantonese.proofing import Proofer
from scinoephile.audio.cantonese.shifting import Shifter
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_segment_hanzi_converted,
    get_segment_split_on_whitespace,
)
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.testing import test_data_root
from test.data.mlamd import (
    mlamd_distribute_test_cases,
    mlamd_merge_test_cases,
    mlamd_proof_test_cases,
    mlamd_shift_test_cases,
)


def replace_test_cases_in_file(file_path: Path, list_name: str, new_cases_str: str):
    pattern = re.compile(rf"({list_name}\s*=\s*)\[(.*?)\]", re.DOTALL)
    contents = file_path.read_text(encoding="utf-8")
    new_contents = pattern.sub(rf"\1{new_cases_str}", contents)
    file_path.write_text(new_contents, encoding="utf-8")
    info(f"Replaced test cases {list_name} in {file_path.name}.")


if __name__ == "__main__":
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(1)

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
    distributor = Distributor(
        examples=[m for m in mlamd_distribute_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    shifter = Shifter(
        examples=[m for m in mlamd_shift_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    merger = Merger(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    proofer = Proofer(
        examples=[m for m in mlamd_proof_test_cases if m.include_in_prompt],
        print_test_case=True,
        cache_dir_path=test_data_root / "cache",
    )
    aligner = Aligner(
        merger=merger, proofer=proofer, shifter=shifter, distributor=distributor
    )

    all_series = []
    for i, block in enumerate(yuewen.blocks):
        print(f"Block {i} ({block.start_idx} - {block.end_idx})")
        if i != 0:
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

        # Test files
        distribution_file = test_data_root / "mlamd" / "distribution.py"
        shifting_file = test_data_root / "mlamd" / "shifting.py"
        merging_file = test_data_root / "mlamd" / "merging.py"
        proofing_file = test_data_root / "mlamd" / "proofing.py"

        # Names of test case lists
        distribution_test_cases = f"distribute_test_cases_block_{i}"
        shifting_test_cases = f"shift_test_cases_block_{i}"
        merging_test_cases = f"merge_test_cases_block_{i}"
        proofing_test_cases = f"proof_test_cases_block_{i}"

        # TODO: Replace test case lists in the test files
        replace_test_cases_in_file(
            distribution_file, distribution_test_cases, distributor.test_case_log_str
        )
        replace_test_cases_in_file(
            shifting_file, shifting_test_cases, shifter.test_case_log_str
        )
        replace_test_cases_in_file(
            merging_file, merging_test_cases, merger.test_case_log_str
        )
        replace_test_cases_in_file(
            proofing_file, proofing_test_cases, proofer.test_case_log_str
        )
        # Reset logs
        distributor.clear_test_case_log()
        shifter.clear_test_case_log()
        merger.clear_test_case_log()
        proofer.clear_test_case_log()

    yuewen_series = get_concatenated_series(all_series)
    print(f"\nConcatenated Series:\n{yuewen_series.to_simple_string()}")
