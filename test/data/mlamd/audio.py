#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

import asyncio
from logging import info

from scinoephile.audio import AudioBlock, AudioSeries, get_series_from_segments
from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.audio.cantonese.alignment.testing import update_all_test_cases
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
from scinoephile.core import Series, get_series_with_subs_merged
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


async def process_block(
    idx: int,
    yuewen_block: AudioBlock,
    zhongwen_block: AudioBlock,
    transcriber: WhisperTranscriber,
    aligner: Aligner,
) -> AudioSeries:
    """Process a single block of audio, transcribing and aligning it with subtitles.

    Arguments:
        idx: Index of block being processed
        yuewen_block: Nascent 粤文 block
        zhongwen_block: Corresponding 中文 block
        transcriber: Transcriber of 粤语 audio to 粤语 text
        aligner: Aligner of 粤文 and 中文 subtitles
    """
    # Transcribe audio
    segments = transcriber(yuewen_block.audio)

    # Split segments based on pauses
    split_segments = []
    for segment in segments:
        split_segments.extend(get_segment_split_on_whitespace(segment))

    # Simplify segments (optional)
    converted_segments = []
    for segment in split_segments:
        converted_segments.append(get_segment_hanzi_converted(segment, "hk2s"))

    # Merge segments into a series
    yuewen_block_series = get_series_from_segments(
        converted_segments, offset=yuewen_block[0].start
    )

    # Sync segments with the corresponding 中文 subtitles
    alignment = await aligner.align(zhongwen_block.to_series(), yuewen_block_series)
    yuewen_block_series = alignment.yuewen

    await update_all_test_cases(test_data_root / "mlamd", idx, aligner)

    return yuewen_block_series


async def process_all_blocks(
    yuewen: AudioSeries,
    zhongwen: AudioSeries,
    transcriber: WhisperTranscriber,
    aligner: Aligner,
):
    """Process all blocks of audio, transcribing and aligning them with subtitles.

    Arguments:
        yuewen: Nascent 粤文 subtitles
        zhongwen: Corresponding 中文 subtitles
        transcriber: Transcriber of 粤语 audio to 粤语 text
        aligner: Aligner of 粤文 and 中文 subtitles
    """
    semaphore = asyncio.Semaphore(1)
    all_yuewen_block_series: list | None = [None] * len(yuewen.blocks)

    async def run_block(block_idx: int):
        """Run processing for a single block of audio.

        Arguments:
            block_idx: Index of the block to process
        """
        # if block_idx > 50:
        #     return
        yuewen_block = yuewen.blocks[block_idx]
        zhongwen_block = zhongwen.blocks[block_idx]
        async with semaphore:
            yuewen_block_series = await process_block(
                block_idx,
                yuewen_block,
                zhongwen_block,
                transcriber,
                aligner,
            )
        print(f"BLOCK {block_idx} ({yuewen_block.start_idx} - {yuewen_block.end_idx}):")
        print(f"中文:\n{zhongwen_block.to_series().to_simple_string()}")
        print(f"粤文:\n{yuewen_block_series.to_simple_string()}")
        all_yuewen_block_series[block_idx] = yuewen_block_series

    # Run all blocks
    async with asyncio.TaskGroup() as task_group:
        for block_idx in range(len(yuewen.blocks)):
            task_group.create_task(run_block(block_idx))

    # Concatenate and return
    yuewen_series = get_concatenated_series(
        [s for s in all_yuewen_block_series if s is not None]
    )
    print(f"Concatenated Series:\n{yuewen_series.to_simple_string()}")
    return yuewen_series


async def main():
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(1)

    # 中文
    zhongwen = Series.load(test_output_dir / "zho-Hans" / "zho-Hans.srt")
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
        cache_dir_path=test_data_root / "cache",
    )
    shifter = Shifter(
        prompt_test_cases=[tc for tc in mlamd_shift_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_shift_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    merger = Merger(
        prompt_test_cases=[tc for tc in mlamd_merge_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_merge_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    proofer = Proofer(
        prompt_test_cases=[tc for tc in mlamd_proof_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_proof_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    translator = Translator(
        prompt_test_cases=[tc for tc in mlamd_translate_test_cases if tc.prompt],
        verified_test_cases=[tc for tc in mlamd_translate_test_cases if tc.verified],
        cache_dir_path=test_data_root / "cache",
    )
    reviewer = Reviewer(
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

    # Process all blocks
    yuewen_series = await process_all_blocks(yuewen, zhongwen, transcriber, aligner)

    # Update output file
    if len(zhongwen.blocks) == len(yuewen.blocks):
        outfile_path = test_output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt"
        if outfile_path.exists():
            outfile_path.unlink()
        yuewen_series.save(outfile_path)
        info(f"Saved 粤文 subtitles to {outfile_path}")


if __name__ == "__main__":
    asyncio.run(main())
