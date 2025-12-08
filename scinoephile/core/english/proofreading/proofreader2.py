#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads English subtitles."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.llms import (
    Queryer2,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.testing import test_data_root

from .prompt2 import EnglishProofreadingPrompt2
from .test_case2 import EnglishProofreadingTestCase2

__all__ = ["EnglishProofreader2"]


class EnglishProofreader2:
    """Proofreads English subtitles."""

    def __init__(
        self,
        test_cases: list[EnglishProofreadingTestCase2] | None = None,
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
            test_cases.extend(load_test_cases_from_json(test_case_path))
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        queryer_cls = Queryer2.get_queryer_cls(EnglishProofreadingPrompt2)
        self.llm_queryer = queryer_cls(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """LLM queryer for proofreading."""

    def proofread(self, series: Series, stop_at_idx: int | None = None) -> Series:
        """Proofread English subtitles.

        Arguments:
            series: English subtitles
            stop_at_idx: stop processing at this index
        Returns:
            proofread English subtitles
        """
        # Proofread subtitles
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        stop_at_idx = stop_at_idx or len(series.blocks)
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = EnglishProofreadingTestCase2.get_test_case_cls(len(block))
            query_cls = test_case_cls.query_cls
            query = query_cls(
                **{
                    f"subtitle_{idx + 1}": re.sub(r"\\N", r"\n", subtitle.text).strip()
                    for idx, subtitle in enumerate(block)
                }
            )
            test_case = test_case_cls(query=query)
            test_case = self.llm_queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                if revised := getattr(test_case.answer, f"revised_{sub_idx + 1}"):
                    subtitle.text = revised
                output_series.append(subtitle)

            info(
                f"Block {block_idx} ({block.start_idx} - {block.end_idx}):\n"
                f"{block.to_series().to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        # Log test cases
        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, test_case.answer.encountered_test_cases
            )

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
        #     try:
        #         # noinspection PyUnusedImports
        #         from test.data.kob import kob_english_proofreading_test_cases
        #         from test.data.mlamd import mlamd_english_proofreading_test_cases
        #         from test.data.mnt import mnt_english_proofreading_test_cases
        #         from test.data.t import t_english_proofreading_test_cases
        #
        #         return (
        #             kob_english_proofreading_test_cases
        #             + mlamd_english_proofreading_test_cases
        #             + mnt_english_proofreading_test_cases
        #             + t_english_proofreading_test_cases
        #         )
        #     except ImportError as exc:
        #         warning(
        #             f"Default test cases not available for {cls.__name__}, "
        #             f"encountered Exception:\n{exc}"
        #         )
        #         return []
        return []

    # @staticmethod
    # def create_test_case_file(test_case_path: Path):
    #     """Create a test case file.
    #
    #     Arguments:
    #         test_case_path: path to file to create
    #     """
    #     contents = dedent('''
    #         """English proofreading test cases."""
    #
    #         from __future__ import annotations
    #
    #         from scinoephile.core.english.proofreading import EnglishProofreadingTestCase
    #
    #         # noinspection PyArgumentList
    #         test_cases = []  # test_cases
    #         """English proofreading test cases."""
    #
    #         __all__ = [
    #             "test_cases",
    #         ]''').strip()
    #     test_case_path.parent.mkdir(parents=True, exist_ok=True)
    #     test_case_path.write_text(contents, encoding="utf-8")
    #     info(f"Created test case file at {test_case_path}.")
