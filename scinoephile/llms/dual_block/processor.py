#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes dual block subtitle matters."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.llms.base import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.synchronization import are_series_one_to_one
from scinoephile.testing import test_data_root

from .prompt import DualBlockPrompt
from .test_case import DualBlockTestCase

__all__ = ["DualBlockProcessor"]


class DualBlockProcessor:
    """Processes two subtitle series blockwise using a dual block prompt."""

    prompt_cls: type[DualBlockPrompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[DualBlockPrompt],
        test_cases: list[DualBlockTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[DualBlockTestCase] | None = None,
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
            test_cases = default_test_cases or []

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(
                load_test_cases_from_json(
                    test_case_path,
                    DualBlockTestCase,
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

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Process paired subtitle series blockwise.

        Arguments:
            source_one: primary subtitles to be revised
            source_two: secondary subtitles providing reference
            stop_at_idx: stop processing at this block index
        Returns:
            processed subtitles based on the primary series
        """
        if not are_series_one_to_one(source_one, source_two):
            raise ScinoephileError(
                "Primary and secondary series must have the same number of subtitles."
            )

        block_pairs = list(zip(source_one.blocks, source_two.blocks))
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (blk_one, blk_two) in enumerate(block_pairs):
            if blk_idx >= stop_at_idx:
                break
            if len(blk_one) != len(blk_two):
                raise ScinoephileError(
                    "Blocks must be aligned with the same number of subtitles."
                )

            test_case_cls = DualBlockTestCase.get_test_case_cls(
                len(blk_one), self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for sub_idx in range(len(blk_one)):
                key_one = self.prompt_cls.source_one(sub_idx + 1)
                query_kwargs[key_one] = re.sub(
                    r"\\N", "\n", blk_one[sub_idx].text
                ).strip()
                key_two = self.prompt_cls.source_two(sub_idx + 1)
                query_kwargs[key_two] = re.sub(
                    r"\\N", "\n", blk_two[sub_idx].text
                ).strip()
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(blk_one):
                output_key = self.prompt_cls.output(sub_idx + 1)
                if output := getattr(test_case.answer, output_key):
                    subtitle.text = output
                output_series.append(subtitle)

            info(
                f"Block {blk_idx} ({blk_one.start_idx} - {blk_one.end_idx}):\n"
                f"{blk_one.to_series().to_simple_string()}"
            )
            output_series_to_concatenate[blk_idx] = output_series

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
