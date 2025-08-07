#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

from scinoephile.audio import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.audio.cantonese.alignment.testing import (
    update_dynamic_test_cases,
    update_test_cases,
)
from scinoephile.audio.cantonese.distribution import Distributor
from scinoephile.audio.cantonese.merging import Merger
from scinoephile.audio.cantonese.proofing import Proofer
from scinoephile.audio.cantonese.review import Reviewer
from scinoephile.audio.cantonese.shifting import Shifter
from scinoephile.audio.cantonese.translation import Translator
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
    mlamd_review_test_cases,
    mlamd_shift_test_cases,
    mlamd_translate_test_cases,
)

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
        prompt_test_cases=[tc for tc in mlamd_distribute_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_distribute_test_cases if tc.verified],
        print_test_case=False,
        cache_dir_path=test_data_root / "cache",
    )
    shifter = Shifter(
        prompt_test_cases=[tc for tc in mlamd_shift_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_shift_test_cases if tc.verified],
        print_test_case=False,
        cache_dir_path=test_data_root / "cache",
    )
    merger = Merger(
        prompt_test_cases=[tc for tc in mlamd_merge_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_merge_test_cases if tc.verified],
        print_test_case=False,
        cache_dir_path=test_data_root / "cache",
    )
    proofer = Proofer(
        prompt_test_cases=[tc for tc in mlamd_proof_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_proof_test_cases if tc.verified],
        print_test_case=False,
        cache_dir_path=test_data_root / "cache",
    )
    translator = Translator(
        print_test_case=True,
        prompt_test_cases=[tc for tc in mlamd_translate_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_translate_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    reviewer = Reviewer(
        print_test_case=True,
        prompt_test_cases=[tc for tc in mlamd_review_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_review_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    aligner = Aligner(
        distributor=distributor,
        shifter=shifter,
        merger=merger,
        proofer=proofer,
        translator=translator,
        reviewer=reviewer,
    )

    all_series = []
    update = True
    for i, block in enumerate(yuewen.blocks):
        print(f"Block {i} ({block.start_idx} - {block.end_idx})")

        if i > 31:
            continue
        update = True

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

        # Replace test case lists in files
        if update:
            update_test_cases(
                test_data_root / "mlamd" / "distribution.py",
                f"distribute_test_cases_block_{i}",
                distributor,
            )
            update_test_cases(
                test_data_root / "mlamd" / "shifting.py",
                f"shift_test_cases_block_{i}",
                shifter,
            )
            update_test_cases(
                test_data_root / "mlamd" / "merging.py",
                f"merge_test_cases_block_{i}",
                merger,
            )
            update_test_cases(
                test_data_root / "mlamd" / "proofing.py",
                f"proof_test_cases_block_{i}",
                proofer,
            )
            if translator.encountered_test_cases:
                update_dynamic_test_cases(
                    test_data_root / "mlamd" / "translation.py",
                    f"translate_test_case_block_{i}",
                    translator,
                )
            update_dynamic_test_cases(
                test_data_root / "mlamd" / "review.py",
                f"review_test_case_block_{i}",
                reviewer,
            )

    yuewen_series = get_concatenated_series(all_series)
    print(f"\nConcatenated Series:\n{yuewen_series.to_simple_string()}")
