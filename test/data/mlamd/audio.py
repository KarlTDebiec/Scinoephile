#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import asyncio
from logging import info

from scinoephile.audio import AudioSeries
from scinoephile.audio.cantonese import CantoneseTranscriptionReviewer
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series, get_series_with_subs_merged
from scinoephile.testing import test_data_root
from test.data.mlamd import (
    mlamd_distribute_test_cases,
    mlamd_merge_test_cases,
    mlamd_proof_test_cases,
    mlamd_review_test_cases,
    mlamd_shift_test_cases,
    mlamd_translate_test_cases,
)


async def main():
    input_dir = test_data_root / "mlamd" / "input"
    output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(2)

    # 中文
    zhongwen = Series.load(output_dir / "zho-Hans" / "zho-Hans.srt")
    if (
        zhongwen.events[539].text == "不知道为什么"
        and zhongwen.events[540].text == "「珊你个头」却特别刺耳"
    ):
        info(
            "Merging 中文 subtitles 539 and 540, which comprise one sentence whose "
            "structure is reversed in the 粤文."
        )
        zhongwen = get_series_with_subs_merged(zhongwen, 539)

    # 粤文
    yuewen = AudioSeries.load(output_dir / "yue-Hans_audio")
    assert len(zhongwen.blocks) == len(yuewen.blocks)

    # Utilities
    reviewer = CantoneseTranscriptionReviewer(
        test_case_directory_path=output_dir,
        distribute_test_cases=mlamd_distribute_test_cases,
        shift_test_cases=mlamd_shift_test_cases,
        merge_test_cases=mlamd_merge_test_cases,
        proof_test_cases=mlamd_proof_test_cases,
        translate_test_cases=mlamd_translate_test_cases,
        review_test_cases=mlamd_review_test_cases,
    )

    # Process all blocks
    yuewen_series = await reviewer.process_all_blocks(yuewen, zhongwen)

    # Update output file
    if len(zhongwen.blocks) == len(yuewen.blocks):
        outfile_path = output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt"
        if outfile_path.exists():
            outfile_path.unlink()
        yuewen_series.save(outfile_path)
        info(f"Saved 粤文 subtitles to {outfile_path}")


if __name__ == "__main__":
    asyncio.run(main())
