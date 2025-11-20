#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads Zhongwen subtitles."""

from __future__ import annotations

import asyncio
import re
from importlib.util import module_from_spec, spec_from_file_location
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import Block, Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.zhongwen.proofing.abcs import (
    ZhongwenProofQuery,
    ZhongwenProofTestCase,
)
from scinoephile.core.zhongwen.proofing.zhongwen_proof_llm_queryer import (
    ZhongwenProofLLMQueryer,
)
from scinoephile.testing import test_data_root, update_dynamic_test_cases


class ZhongwenProofer:
    """Proofreads Zhongwen subtitles."""

    def __init__(
        self,
        proof_test_cases: list[ZhongwenProofTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
    ):
        """Initialize.

        Arguments:
            proof_test_cases: proof test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
        """
        if proof_test_cases is None:
            proof_test_cases = []
            # try:
            #     from test.data.kob import kob_zhongwen_proof_test_cases
            #     from test.data.mlamd import mlamd_zhongwen_proof_test_cases
            #     from test.data.t import t_zhongwen_proof_test_cases
            #
            #     proof_test_cases = (
            #         kob_zhongwen_proof_test_cases
            #         + mlamd_zhongwen_proof_test_cases
            #         + t_zhongwen_proof_test_cases
            #     )
            # except ImportError:
            #     pass

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)

            if test_case_path.exists():
                spec = spec_from_file_location("test_cases", test_case_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                for name in getattr(module, "__all__", []):
                    if name.endswith("zhongwen_proof_test_cases"):
                        if value := getattr(module, name, None):
                            proof_test_cases.extend(value)

        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = ZhongwenProofLLMQueryer(
            prompt_test_cases=[tc for tc in proof_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in proof_test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Proofreads Zhongwen subtitles."""

    async def process_all_blocks(self, series: Series, stop_at_idx: int | None = None):
        """Process all blocks.

        Arguments:
            series: 中文 subtitles
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
            info(f"BLOCK {block_idx} ({block.start_idx} - {block.end_idx}):")
            info(f"Zhongwen:\n{block.to_series().to_simple_string()}")
            all_block_series[block_idx] = block_series

        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.test_case_path.parent.mkdir(parents=True, exist_ok=True)
            self.create_test_case_file(self.test_case_path, len(series.blocks))

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
        info(f"Concatenated Series:\n{proofread_series.to_simple_string()}")
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
        test_case_cls = ZhongwenProofTestCase.get_test_case_cls(len(block))
        query_cls = test_case_cls.query_cls
        answer_cls = test_case_cls.answer_cls

        # Query for proofreading
        query = self.get_query(block, query_cls)
        answer = await self.llm_queryer.call(query, answer_cls, test_case_cls)

        nascent_series = Series()
        for sub_idx, subtitle in enumerate(block):
            if revised := getattr(answer, f"xiugai_{sub_idx + 1}"):
                subtitle.text = revised
            nascent_series.append(subtitle)

        if self.test_case_path is not None:
            await update_dynamic_test_cases(
                self.test_case_path,
                f"test_case_block_{block_idx}",
                self.llm_queryer,
            )

        return nascent_series

    @staticmethod
    def create_test_case_file(test_case_path: Path, n_blocks: int):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
            n_blocks: number of blocks for which to create test cases
        """
        header = '''"""Zhongwen proof test cases."""

from __future__ import annotations

from scinoephile.core.zhongwen.proofing.abcs import ZhongwenProofTestCase'''

        blocks = "\n".join(
            f"# noinspection PyArgumentList\n"
            f"test_case_block_{i} = None  # test_case_block_{i}"
            for i in range(n_blocks)
        )

        footer = '''
zhongwen_proof_test_cases: list[ZhongwenProofTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""中文 proof test cases."""

__all__ = [
    "zhongwen_proof_test_cases",
    ]'''

        contents = f"{header}\n\n{blocks}\n\n{footer}\n"
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")

    @staticmethod
    def get_query(
        series: Series, query_cls: type[ZhongwenProofQuery]
    ) -> ZhongwenProofQuery:
        """Get the query for a given series.

        Arguments:
            series: subtitles
            query_cls: query class
        Returns:
            instance of query_cls for series
        """
        kwargs = {}
        for idx, subtitle in enumerate(series.events, 1):
            kwargs[f"zimu_{idx}"] = re.sub(r"\\N", r"\n", subtitle.text).strip()

        return query_cls(**kwargs)
