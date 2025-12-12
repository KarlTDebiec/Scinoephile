#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads English subtitles."""

from __future__ import annotations

import re
from logging import info, warning
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.llms import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.testing import test_data_root

from .prompt import EnglishProofreadingPrompt
from .test_case import EnglishProofreadingTestCase

__all__ = ["EnglishProofreader"]


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
            test_cases = self.get_default_test_cases()

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(
                load_test_cases_from_json(
                    test_case_path,
                    EnglishProofreadingTestCase,
                    prompt_cls=EnglishProofreadingPrompt,
                ),
            )
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        queryer_cls = Queryer.get_queryer_cls(EnglishProofreadingPrompt)
        self.queryer = queryer_cls(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """LLM queryer."""

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
            test_case_cls = EnglishProofreadingTestCase.get_test_case_cls(len(block))
            query_cls = test_case_cls.query_cls
            prompt_cls = query_cls.prompt_cls
            query_attrs: dict[str, str] = {}
            for idx, subtitle in enumerate(block):
                key = prompt_cls.subtitle_field(idx + 1)
                query_attrs[key] = re.sub(r"\\N", "\n", subtitle.text).strip()
            query = query_cls(**query_attrs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                key = prompt_cls.revised_field(sub_idx + 1)
                if revised := getattr(test_case.answer, key):
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
                self.test_case_path, self.queryer.encountered_test_cases.values()
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
        try:
            # noinspection PyUnusedImports
            from test.data.kob import get_kob_eng_proofreading_test_cases

            # noinspection PyUnusedImports
            from test.data.mlamd import get_mlamd_eng_proofreading_test_cases

            # noinspection PyUnusedImports
            from test.data.mnt import get_mnt_eng_proofreading_test_cases

            # noinspection PyUnusedImports
            from test.data.t import get_t_eng_proofreading_test_cases

            return (
                get_kob_eng_proofreading_test_cases()
                + get_mlamd_eng_proofreading_test_cases()
                + get_mnt_eng_proofreading_test_cases()
                + get_t_eng_proofreading_test_cases()
            )
        except ImportError as exc:
            warning(
                f"Default test cases not available for {cls.__name__}, "
                f"encountered Exception:\n{exc}"
            )
        return []
