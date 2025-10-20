#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import asyncio

from data.t import (
    t_distribute_test_cases,
    t_merge_test_cases,
    t_proof_test_cases,
    t_review_test_cases,
    t_shift_test_cases,
    t_translate_test_cases,
)

from scinoephile.audio import AudioSeries
from scinoephile.audio.cantonese import CantoneseTranscriptionReviewer
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.testing import test_data_root


async def main():
    input_dir = test_data_root / "t" / "input"
    output_dir = test_data_root / "t" / "output"
    set_logging_verbosity(2)

    # 中文
    zhongwen = Series.load(output_dir / "zho-Hans_clean_flatten.srt")

    # 粤文
    yuewen = AudioSeries.load(output_dir / "yue-Hans_audio")
    assert len(zhongwen.blocks) == len(yuewen.blocks)

    # Utilities
    reviewer = CantoneseTranscriptionReviewer(
        test_case_directory_path=test_data_root / "t",
        distribute_test_cases=t_distribute_test_cases,
        shift_test_cases=t_shift_test_cases,
        merge_test_cases=t_merge_test_cases,
        proof_test_cases=t_proof_test_cases,
        translate_test_cases=t_translate_test_cases,
        review_test_cases=t_review_test_cases,
    )

    # Process all blocks
    yuewen_series = await reviewer.process_all_blocks(yuewen, zhongwen, stop_at_idx=1)

    # Update output file
    # if len(zhongwen.blocks) == len(yuewen.blocks):
    #     outfile_path = output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt"
    #     if outfile_path.exists():
    #         outfile_path.unlink()
    #     yuewen_series.save(outfile_path)
    #     info(f"Saved 粤文 subtitles to {outfile_path}")


if __name__ == "__main__":
    asyncio.run(main())
