#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads English subtitles."""

from __future__ import annotations

import asyncio
import re
from importlib.util import module_from_spec, spec_from_file_location
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.english.proofreading.english_proofreading_llm_queryer import (
    EnglishProofreadingLLMQueryer,
)
from scinoephile.core.english.proofreading.english_proofreading_query import (
    EnglishProofreadingQuery,
)
from scinoephile.core.english.proofreading.english_proofreading_test_case import (
    EnglishProofreadingTestCase,
)
from scinoephile.testing import (
    test_data_root,
    update_test_cases,
)

try:
    # noinspection PyUnusedImports
    from test.data.kob import kob_english_proofreading_test_cases

    # noinspection PyUnusedImports
    from test.data.mlamd import mlamd_english_proofreading_test_cases

    # noinspection PyUnusedImports
    from test.data.mnt import mnt_english_proofreading_test_cases

    # noinspection PyUnusedImports
    from test.data.t import t_english_proofreading_test_cases

    default_test_cases = (
        kob_english_proofreading_test_cases
        + mlamd_english_proofreading_test_cases
        + mnt_english_proofreading_test_cases
        + t_english_proofreading_test_cases
    )
except ImportError:
    default_test_cases = []


class EnglishProofreader:
    """Proofreads English subtitles."""

    def __init__(
        self,
        test_cases: list[EnglishProofreadingTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
    ):
        """Initialize.

        Arguments:
            test_cases: test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
        """
        if test_cases is None:
            test_cases = default_test_cases

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)

            if test_case_path.exists():
                spec = spec_from_file_location("test_cases", test_case_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                for name in getattr(module, "__all__", []):
                    if name.endswith("test_cases"):
                        if value := getattr(module, name, None):
                            test_cases.extend(value)

        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = EnglishProofreadingLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Proofreads English subtitles."""

    def proofread(self, series: Series, stop_at_idx: int | None = None):
        """Proofread English subtitles.

        Arguments:
            series: English subtitles
            stop_at_idx: stop processing at this index
        """
        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.test_case_path.parent.mkdir(parents=True, exist_ok=True)
            self.create_test_case_file(self.test_case_path, len(series.blocks))

        # Proofread subtitles
        all_output_series: list[Series | None] = [None] * len(series.blocks)
        stop_at_idx = stop_at_idx or len(series.blocks)
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query for proofreading
            test_case_cls = EnglishProofreadingTestCase.get_test_case_cls(len(block))
            query_cls = test_case_cls.query_cls
            answer_cls = test_case_cls.answer_cls
            query = self.get_query(block.to_series(), query_cls)
            answer = self.llm_queryer(query, answer_cls, test_case_cls)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                if revised := getattr(answer, f"revised_{sub_idx + 1}"):
                    subtitle.text = revised
                output_series.append(subtitle)

            info(
                f"Block {block_idx} ({block.start_idx} - {block.end_idx}):\n"
                f"{block.to_series().to_simple_string()}"
            )
            all_output_series[block_idx] = output_series
        if self.test_case_path is not None:
            asyncio.run(
                update_test_cases(self.test_case_path, "test_cases", self.llm_queryer)
            )

        # Concatenate and return
        output_series = get_concatenated_series(
            [s for s in all_output_series if s is not None]
        )
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series

    @staticmethod
    def create_test_case_file(test_case_path: Path, n_blocks: int):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
            n_blocks: number of blocks for which to create test cases
        """
        contents = '''"""English proofreading test cases."""

from __future__ import annotations

from scinoephile.core.english.proofreading import EnglishProofreadingTestCase

# noinspection PyArgumentList
test_cases = []  # test_cases
"""English proofreading test cases."""

__all__ = [
    "test_cases",
]'''
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")

    @staticmethod
    def get_query(
        series: Series, query_cls: type[EnglishProofreadingQuery]
    ) -> EnglishProofreadingQuery:
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
