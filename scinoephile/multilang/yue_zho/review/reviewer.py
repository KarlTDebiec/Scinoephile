#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreader for subtitles."""

from __future__ import annotations

import re
from collections.abc import Sequence
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.llms import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwiseTestCase
from scinoephile.testing import test_data_root

from .prompts import YueHansReviewPrompt

__all__ = ["YueVsZhoReviewer"]

from ...synchronization import are_series_one_to_one


class YueVsZhoReviewer:
    """Reviews 粤文 subtitles vs. 中文."""

    prompt_cls: type[YueHansReviewPrompt]
    """text for LLM correspondence"""

    def __init__(
        self,
        prompt_cls: type[YueHansReviewPrompt] = YueHansReviewPrompt,
        test_cases: list[ManyToManyBlockwiseTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: Sequence[ManyToManyBlockwiseTestCase] | None = None,
    ):
        """Initialize.

        Arguments:
            prompt_cls: text for LLM correspondence
            test_cases: test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
            default_test_cases: default test cases
        """
        self.prompt_cls = prompt_cls

        if test_cases is None:
            if default_test_cases is not None:
                test_cases = default_test_cases
            else:
                test_cases = []

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(
                load_test_cases_from_json(
                    test_case_path,
                    ManyToManyBlockwiseTestCase,
                    prompt_cls=self.prompt_cls,
                ),
            )
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        queryer_cls = Queryer.get_queryer_cls(self.prompt_cls)
        self.queryer = queryer_cls(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """LLM queryer."""

    def review(
        self, yuewen: Series, zhongwen: Series, stop_at_idx: int | None = None
    ) -> Series:
        """Review 粤文 subtitles vs. 中文.

        Arguments:
            yuewen: 粤文 subtitles
            zhongwen: 中文 subtitles
            stop_at_idx: stop processing at this block index
        Returns:
            reviewed 粤文 subtitles
        """
        if not are_series_one_to_one(yuewen, zhongwen):
            raise ScinoephileError(
                "粤文 and 中文 sources must have the same number of subtitles."
                f" Got {len(yuewen)} 粤文 subtitles and {len(zhongwen)} 中文 subtitles."
            )

        # Review subtitles
        output_series_to_concatenate: list[Series | None] = [None] * len(yuewen.blocks)
        stop_at_idx = stop_at_idx or len(yuewen.blocks)
        for blk_idx, (yw_blk, zw_blk) in enumerate(zip(yuewen.blocks, zhongwen.blocks)):
            if blk_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = ManyToManyBlockwiseTestCase.get_test_case_cls(
                len(yw_blk), self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for sub_idx in range(len(yw_blk)):
                yw_key = self.prompt_cls.source_one(sub_idx + 1)
                yw_val = re.sub(r"\\N", "\n", yw_blk[sub_idx].text).strip()
                query_kwargs[yw_key] = yw_val
                zw_key = self.prompt_cls.source_two(sub_idx + 1)
                zw_val = re.sub(r"\\N", "\n", zw_blk[sub_idx].text).strip()
                query_kwargs[zw_key] = zw_val
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, yw_sub in enumerate(yw_blk):
                output_key = self.prompt_cls.output(sub_idx + 1)
                if output := getattr(test_case.answer, output_key):
                    yw_sub.text = output
                output_series.append(yw_sub)

            info(
                f"Block {blk_idx} ({yw_blk.start_idx} - {yw_blk.end_idx}):\n"
                f"{yw_blk.to_series().to_simple_string()}"
            )
            output_series_to_concatenate[blk_idx] = output_series

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
