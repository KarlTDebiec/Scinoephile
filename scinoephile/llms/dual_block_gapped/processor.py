#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes dual block / subtitle block (gapped) matters."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common.validation import val_output_path
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.core.testing import test_data_root
from scinoephile.llms.base import (
    Queryer,
    TestCase,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.pairs import get_block_pairs_by_pause
from scinoephile.multilang.synchronization import get_sync_overlap_matrix

from .manager import DualBlockGappedManager
from .prompt import DualBlockGappedPrompt

__all__ = ["DualBlockGappedProcessor"]


class DualBlockGappedProcessor:
    """Processes dual block / subtitle block (gapped) matters."""

    prompt_cls: type[DualBlockGappedPrompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[DualBlockGappedPrompt],
        test_cases: list[TestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[TestCase] | None = None,
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
                    DualBlockGappedManager,
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
        """Fill gaps in the primary series using the secondary series as reference.

        Arguments:
            source_one: primary subtitles (may contain gaps)
            source_two: secondary subtitles providing reference
            stop_at_idx: stop processing at this block index
        Returns:
            primary subtitles with gaps filled
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            # Determine TestCase configuration
            size = len(two_blk)
            overlap = get_sync_overlap_matrix(one_blk, two_blk)
            sync_grps = [([], [two_idx]) for two_idx in range(len(two_blk))]
            for one_idx in range(len(one_blk)):
                two_idx = np.argmax(overlap[one_idx, :])
                sync_grps[two_idx][0].append(one_idx)
            gaps = tuple(idx for idx, group in enumerate(sync_grps) if not group[0])
            if not gaps:
                output_series_to_concatenate[blk_idx] = one_blk
                continue

            # Query LLM
            test_case_cls = DualBlockGappedManager.get_test_case_cls(
                size, gaps, self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            one_idx = 0
            for two_idx in range(size):
                if two_idx not in gaps:
                    one_key = self.prompt_cls.src_1(two_idx + 1)
                    one_val = re.sub(r"\\N", "\n", one_blk[one_idx].text).strip()
                    query_kwargs[one_key] = one_val
                    one_idx += 1
                two_key = self.prompt_cls.src_2(two_idx + 1)
                two_val = re.sub(r"\\N", "\n", two_blk[two_idx].text).strip()
                query_kwargs[two_key] = two_val
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for two_idx in range(size):
                two_sub = two_blk[two_idx]
                start = two_sub.start
                end = two_sub.end
                if two_idx not in gaps:
                    one_key = self.prompt_cls.src_1(two_idx + 1)
                    output = getattr(test_case.query, one_key)
                else:
                    one_key = self.prompt_cls.output(two_idx + 1)
                    output = getattr(test_case.answer, one_key)
                output_series.append(Subtitle(start=start, end=end, text=output))

            info(f"Block {blk_idx}:\n{one_blk.to_simple_string()}")
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
