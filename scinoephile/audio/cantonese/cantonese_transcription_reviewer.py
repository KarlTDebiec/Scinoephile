#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

import asyncio
from pathlib import Path

from scinoephile.audio import AudioBlock, AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_segment_split_on_whitespace,
    get_segment_zhongwen_converted,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core import Block, Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.llms import Queryer
from scinoephile.core.zhongwen import OpenCCConfig
from scinoephile.testing import test_data_root

from .alignment import Aligner
from .merging import MergingPrompt, MergingTestCase
from .proofing import ProofingPrompt, ProofingTestCase
from .review import ReviewPrompt, ReviewTestCase
from .shifting import ShiftingPrompt, ShiftingTestCase
from .translation import TranslationPrompt, TranslationTestCase


class CantoneseTranscriptionReviewer:
    """Class for reviewing and refining Cantonese transcriptions."""

    def __init__(
        self,
        test_case_directory_path: Path,
        shifting_test_cases: list[ShiftingTestCase],
        merging_test_cases: list[MergingTestCase],
        proofing_test_cases: list[ProofingTestCase],
        translation_test_cases: list[TranslationTestCase],
        review_test_cases: list[ReviewTestCase],
    ):
        """Initialize.

        Arguments:
            test_case_directory_path: path to directory containing test cases
            shifting_test_cases: shifting test cases
            merging_test_cases: merging test cases
            proofing_test_cases: proofing test cases
            translation_test_cases: translation test cases
            review_test_cases: review test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.transcriber = WhisperTranscriber(
            "khleeloo/whisper-large-v3-cantonese",
            cache_dir_path=test_data_root / "cache",
        )
        shifting_queryer_cls = Queryer.get_queryer_cls(ShiftingPrompt)
        self.shifting_queryer = shifting_queryer_cls(
            prompt_test_cases=[tc for tc in shifting_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in shifting_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        merging_queryer_cls = Queryer.get_queryer_cls(MergingPrompt)
        self.merging_queryer = merging_queryer_cls(
            prompt_test_cases=[tc for tc in merging_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in merging_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        proofing_queryer_cls = Queryer.get_queryer_cls(ProofingPrompt)
        self.proofing_queryer = proofing_queryer_cls(
            prompt_test_cases=[tc for tc in proofing_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in proofing_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        translation_queryer_cls = Queryer.get_queryer_cls(TranslationPrompt)
        self.translation_queryer = translation_queryer_cls(
            prompt_test_cases=[tc for tc in translation_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in translation_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        review_queryer_cls = Queryer.get_queryer_cls(ReviewPrompt)
        self.review_queryer = review_queryer_cls(
            prompt_test_cases=[tc for tc in review_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in review_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        self.aligner = Aligner(
            shifting_queryer=self.shifting_queryer,
            merging_queryer=self.merging_queryer,
            proofing_queryer=self.proofing_queryer,
            translation_queryer=self.translation_queryer,
            review_queryer=self.review_queryer,
        )

    async def process_all_blocks(
        self,
        yuewen: AudioSeries,
        zhongwen: Series,
        stop_at_idx: int | None = None,
    ):
        """Process all blocks of audio, transcribing and aligning them with subtitles.

        Arguments:
            yuewen: Nascent 粤文 subtitles
            zhongwen: Corresponding 中文 subtitles
            stop_at_idx: Stop after processing this block index
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
                f"BLOCK {block_idx} "
                f"({yuewen_block.start_idx} - {yuewen_block.end_idx}):"
            )
            print(f"中文:\n{zhongwen_block.to_series().to_simple_string()}")
            print(f"粤文:\n{yuewen_block_series.to_simple_string()}")
            all_yuewen_block_series[block_idx] = yuewen_block_series

        # Run all blocks
        if not stop_at_idx:
            stop_at_idx = len(yuewen.blocks) - 1
        async with asyncio.TaskGroup() as task_group:
            for block_idx in range(stop_at_idx + 1):
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
        zhongwen_block: Block,
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
        converted_segments = [
            get_segment_zhongwen_converted(segment, OpenCCConfig.hk2s)
            for segment in split_segments
        ]

        # Merge segments into a series
        yuewen_block_series = get_series_from_segments(
            converted_segments, offset=yuewen_block[0].start
        )

        # Sync segments with the corresponding 中文 subtitles
        alignment = await self.aligner.align(
            zhongwen_block.to_series(), yuewen_block_series
        )
        yuewen_block_series = alignment.yuewen

        self.aligner.update_all_test_cases(self.test_case_directory_path)

        return yuewen_block_series
