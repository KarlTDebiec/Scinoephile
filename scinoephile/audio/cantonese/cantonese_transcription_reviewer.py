#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

import asyncio
from pathlib import Path

from scinoephile.audio import AudioBlock, AudioSeries, get_series_from_segments
from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.audio.cantonese.alignment.testing import update_all_test_cases
from scinoephile.audio.cantonese.distribution import DistributeTestCase, Distributor
from scinoephile.audio.cantonese.merging import Merger, MergeTestCase
from scinoephile.audio.cantonese.proofing import Proofer, ProofTestCase
from scinoephile.audio.cantonese.review import Reviewer
from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.audio.cantonese.shifting import Shifter, ShiftTestCase
from scinoephile.audio.cantonese.translation import Translator
from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_segment_hanzi_converted,
    get_segment_split_on_whitespace,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.testing import test_data_root


class CantoneseTranscriptionReviewer:
    """Class for reviewing and refining Cantonese transcriptions."""

    def __init__(
        self,
        test_case_directory_path: Path,
        distribute_test_cases: list[DistributeTestCase],
        shift_test_cases: list[ShiftTestCase],
        merge_test_cases: list[MergeTestCase],
        proof_test_cases: list[ProofTestCase],
        translate_test_cases: list[TranslateTestCase],
        review_test_cases: list[ReviewTestCase],
    ):
        """Initialize.

        Arguments:
            test_case_directory_path: path to directory containing test cases
            distribute_test_cases: distribute test cases
            shift_test_cases: shift test cases
            merge_test_cases: merge test cases
            proof_test_cases: proof test cases
            translate_test_cases: translate test cases
            review_test_cases: review test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.transcriber = WhisperTranscriber(
            "khleeloo/whisper-large-v3-cantonese",
            cache_dir_path=test_data_root / "cache",
        )
        self.distributor = Distributor(
            prompt_test_cases=[tc for tc in distribute_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in distribute_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.shifter = Shifter(
            prompt_test_cases=[tc for tc in shift_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in shift_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.merger = Merger(
            prompt_test_cases=[tc for tc in merge_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in merge_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.proofer = Proofer(
            prompt_test_cases=[tc for tc in proof_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in proof_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.translator = Translator(
            prompt_test_cases=[tc for tc in translate_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in translate_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.reviewer = Reviewer(
            prompt_test_cases=[tc for tc in review_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in review_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.aligner = Aligner(
            distributor=self.distributor,
            shifter=self.shifter,
            merger=self.merger,
            proofer=self.proofer,
            translator=self.translator,
            reviewer=self.reviewer,
        )

    async def process_all_blocks(
        self,
        yuewen: AudioSeries,
        zhongwen: AudioSeries,
    ):
        """Process all blocks of audio, transcribing and aligning them with subtitles.

        Arguments:
            yuewen: Nascent 粤文 subtitles
            zhongwen: Corresponding 中文 subtitles
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
                yuewen_block_series = await self.process_block(
                    block_idx, yuewen_block, zhongwen_block
                )
            print(
                f"BLOCK {block_idx} ({yuewen_block.start_idx} - {yuewen_block.end_idx}):"
            )
            print(f"中文:\n{zhongwen_block.to_series().to_simple_string()}")
            print(f"粤文:\n{yuewen_block_series.to_simple_string()}")
            all_yuewen_block_series[block_idx] = yuewen_block_series

        # Run all blocks
        async with asyncio.TaskGroup() as task_group:
            for block_idx in [0, 1]:  # range(len(yuewen.blocks)):
                task_group.create_task(run_block(block_idx))

        # Concatenate and return
        yuewen_series = get_concatenated_series(
            [s for s in all_yuewen_block_series if s is not None]
        )
        print(f"Concatenated Series:\n{yuewen_series.to_simple_string()}")
        return yuewen_series

    async def process_block(
        self,
        idx: int,
        yuewen_block: AudioBlock,
        zhongwen_block: AudioBlock,
    ) -> AudioSeries:
        """Process a single block of audio, transcribing and aligning it with subtitles.

        Arguments:
            idx: Index of block being processed
            yuewen_block: Nascent 粤文 block
            zhongwen_block: Corresponding 中文 block
        """
        # Transcribe audio
        segments = self.transcriber(yuewen_block.audio)

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
        alignment = await self.aligner.align(
            zhongwen_block.to_series(), yuewen_block_series
        )
        yuewen_block_series = alignment.yuewen

        await update_all_test_cases(self.test_case_directory_path, idx, self.aligner)

        return yuewen_block_series
