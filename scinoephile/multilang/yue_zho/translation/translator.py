#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 subtitles against 中文."""

from __future__ import annotations

from collections.abc import Sequence
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import Series
from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.llms import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwiseTestCase
from scinoephile.multilang.pairs import get_block_pairs_by_pause
from scinoephile.testing import test_data_root

from .prompts import YueHansTranslationPrompt

__all__ = ["YueVsZhoTranslator"]


class YueVsZhoTranslator:
    """Translates 粤文 subtitles against 中文."""

    prompt_cls: type[YueHansTranslationPrompt]
    """text for LLM correspondence"""

    def __init__(
        self,
        prompt_cls: type[YueHansTranslationPrompt] = YueHansTranslationPrompt,
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
            test_cases = list(default_test_cases or [])

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

    def translate(
        self,
        yuewen: Series,
        zhongwen: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Translate 粤文 subtitles against 中文.

        Arguments:
            yuewen: 粤文 subtitles
            zhongwen: 中文 subtitles
            stop_at_idx: stop processing at this block index
        Returns:
            translated 粤文 subtitles
        """
        # Translate subtitles
        block_pairs = get_block_pairs_by_pause(yuewen, zhongwen)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (yw_blk, zw_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = ManyToManyBlockwiseTestCase.get_test_case_cls(
                size, self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for zw_idx in range(1, size + 1):
                yue_text = self._get_yue_text(yw_blk, zw_to_yw.get(zw_idx, []))
                zhong_text = self._normalize_text(zw_blk[zw_idx].text)
                query_kwargs[self.prompt_cls.source_one(zw_idx + 1)] = yue_text
                query_kwargs[self.prompt_cls.source_two(zw_idx + 1)] = zhong_text
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()

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
