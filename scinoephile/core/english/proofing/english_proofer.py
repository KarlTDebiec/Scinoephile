#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads English subtitles."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from scinoephile.common.validation import val_input_dir_path
from scinoephile.core import Block, Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.english.proofing import EnglishProofLLMQueryer
from scinoephile.core.english.proofing.abcs import (
    EnglishProofAnswer,
    EnglishProofQuery,
    EnglishProofTestCase,
)
from scinoephile.testing import test_data_root, update_dynamic_test_cases


class EnglishProofer:
    """Proofreads English subtitles."""

    def __init__(
        self,
        proof_test_cases: list[EnglishProofTestCase],
        test_case_directory_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            proof_test_cases: proof test cases
            test_case_directory_path: path to directory containing test cases
        """
        self.proofer = EnglishProofLLMQueryer(
            prompt_test_cases=[tc for tc in proof_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in proof_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        """Proofreads English subtitles."""

        if test_case_directory_path is not None:
            test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.test_case_directory_path = test_case_directory_path
        """Path to directory containing test cases."""

    async def process_all_blocks(
        self,
        series: Series,
        stop_at_idx: int | None = None,
    ):
        """Process all blocks.

        Arguments:
            series: English subtitles
            stop_at_idx: stop processing at this index
        """
        semaphore = asyncio.Semaphore(1)
        all_block_series: list | None = [None] * len(series.blocks)

        async def run_block(block_idx: int):
            """Run processing for a single block.

            Arguments:
                block_idx: index of the block to process
            """
            block = series.blocks[block_idx]
            async with semaphore:
                block_series = await self.process_block(block_idx, block)
            print(f"BLOCK {block_idx} ({block.start_idx} - {block.end_idx}):")
            print(f"English:\n{block.to_series().to_simple_string()}")
            all_block_series[block_idx] = block_series

        # Run all blocks
        if stop_at_idx is None:
            stop_at_idx = len(series.blocks) - 1
        async with asyncio.TaskGroup() as task_group:
            for idx in range(stop_at_idx + 1):
                task_group.create_task(run_block(idx))

        # Concatenate and return
        proofread_series = get_concatenated_series(
            [s for s in all_block_series if s is not None]
        )
        print(f"Concatenated Series:\n{proofread_series.to_simple_string()}")
        return proofread_series

    async def process_block(
        self,
        block_idx: int,
        block: Block,
    ) -> Series:
        """Process a single block.

        Arguments:
            block_idx: index of block being processed
            block: block to process
        Returns:
            Series
        """
        query_cls, answer_cls, test_case_cls = self.get_models(len(block))

        # Query for proofreading
        query = self.get_query(block, query_cls)
        answer = await self.proofer.call(query, answer_cls, test_case_cls)

        nascent_series = Series()
        for sub_idx, subtitle in enumerate(block):
            if revised := getattr(answer, f"revised_{sub_idx + 1}"):
                subtitle.text = revised
            nascent_series.append(subtitle)

        if self.test_case_directory_path is not None:
            await update_dynamic_test_cases(
                self.test_case_directory_path / "proofing.py",
                f"proof_test_case_block_{block_idx}",
                self.proofer,
            )

        return nascent_series

    @staticmethod
    def get_models(
        size: int,
    ) -> tuple[
        type[EnglishProofQuery], type[EnglishProofAnswer], type[EnglishProofTestCase]
    ]:
        """Get proofreading query, answer and test case for a series of a given size.

        Arguments:
            size: length of series
        Returns
            EnglishProofQuery, EnglishProofAnswer, and EnglishProofTestCase classes
        """
        query_cls = EnglishProofQuery.get_query_cls(size)
        answer_cls = EnglishProofAnswer.get_answer_cls(size)
        test_case_cls = EnglishProofTestCase.get_test_case_cls(
            size, query_cls, answer_cls
        )
        return query_cls, answer_cls, test_case_cls

    @staticmethod
    def get_query(
        series: Series, query_cls: type[EnglishProofQuery]
    ) -> EnglishProofQuery:
        """Get the query for a given series.

        Arguments:
            series: subtitles
            query_cls: query class
        Returns:
            instance of query_cls for series
        """
        kwargs = {}
        for idx, subtitle in enumerate(series.events, 1):
            kwargs[f"subtitle_{idx}"] = re.sub(r"\\N", r"\n", subtitle.text).strip()

        return query_cls(**kwargs)
