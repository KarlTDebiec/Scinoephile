#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 中文 subtitles."""

from __future__ import annotations

import re
from logging import info, warning
from pathlib import Path
from textwrap import dedent

from scinoephile.common.validation import val_output_path
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.testing import (
    get_test_cases_from_file_path,
    test_data_root,
    update_test_cases,
)

from .llm_queryer import ZhongwenProofreadingLLMQueryer
from .test_case import ZhongwenProofreadingTestCase

__all__ = ["ZhongwenProofreader"]


class ZhongwenProofreader:
    """Proofreads 中文 subtitles."""

    def __init__(
        self,
        test_cases: list[ZhongwenProofreadingTestCase] | None = None,
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
            test_cases = self.get_default_test_cases()

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(get_test_cases_from_file_path(test_case_path))
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = ZhongwenProofreadingLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Proofreads 中文 subtitles."""

    def proofread(self, series: Series, stop_at_idx: int | None = None):
        """Proofread 中文 subtitles.

        Arguments:
            series: 中文 subtitles
            stop_at_idx: stop processing at this index
        """
        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.create_test_case_file(self.test_case_path)

        # Proofread subtitles
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        stop_at_idx = stop_at_idx or len(series.blocks)
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = ZhongwenProofreadingTestCase.get_test_case_cls(len(block))
            query_cls = test_case_cls.query_cls
            answer_cls = test_case_cls.answer_cls
            query = query_cls(
                **{
                    f"zimu_{idx + 1}": re.sub(r"\\N", r"\n", subtitle.text).strip()
                    for idx, subtitle in enumerate(block)
                }
            )
            answer = self.llm_queryer(query, answer_cls, test_case_cls)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                if revised := getattr(answer, f"xiugai_{sub_idx + 1}"):
                    subtitle.text = revised
                output_series.append(subtitle)

            info(
                f"Block {block_idx} ({block.start_idx} - {block.end_idx}):\n"
                f"{block.to_series().to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        # Log test cases
        if self.test_case_path is not None:
            update_test_cases(self.test_case_path, "test_cases", self.llm_queryer)

        # Organize and return
        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series

    @classmethod
    def get_default_test_cases(cls):
        """Get default test cases included with package.

        Returns:
            test cases
        """
        try:
            # noinspection PyUnusedImports
            from test.data.kob import kob_zhongwen_proofreading_test_cases
            from test.data.mlamd import mlamd_zhongwen_proofreading_test_cases
            from test.data.mnt import mnt_zhongwen_proofreading_test_cases
            from test.data.t import t_zhongwen_proofreading_test_cases

            return (
                kob_zhongwen_proofreading_test_cases
                + mlamd_zhongwen_proofreading_test_cases
                + mnt_zhongwen_proofreading_test_cases
                + t_zhongwen_proofreading_test_cases
            )
        except ImportError as exc:
            warning(
                f"Default test cases not available for {cls.__name__}, "
                f"encountered Exception:\n{exc}"
            )
            return []

    @staticmethod
    def create_test_case_file(test_case_path: Path):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
        """
        contents = dedent('''
            """中文 proofreading test cases."""

            from __future__ import annotations

            from scinoephile.core.zhongwen.proofreading import ZhongwenProofreadingTestCase

            # noinspection PyArgumentList
            test_cases = []  # test_cases
            """中文 proofreading test cases."""

            __all__ = [
                "test_cases",
            ]''').strip()
        test_case_path.parent.mkdir(parents=True, exist_ok=True)
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")
