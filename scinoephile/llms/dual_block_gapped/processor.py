#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes dual block subtitles when the primary series has gaps."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.llms.base import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.pairs import get_block_pairs_by_pause
from scinoephile.multilang.synchronization import get_sync_overlap_matrix
from scinoephile.testing import test_data_root

from .prompt import DualBlockGappedPrompt
from .test_case import DualBlockGappedTestCase

__all__ = ["DualBlockGappedProcessor"]


class DualBlockGappedProcessor:
    """Processes dual block subtitles where the primary series contains gaps."""

    prompt_cls: type[DualBlockGappedPrompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[DualBlockGappedPrompt],
        test_cases: list[DualBlockGappedTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[DualBlockGappedTestCase] | None = None,
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
                    DualBlockGappedTestCase,
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
        primary: Series,
        secondary: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Fill gaps in the primary series using the secondary series as reference.

        Arguments:
            primary: primary subtitles (may contain gaps)
            secondary: secondary subtitles providing reference
            stop_at_idx: stop processing at this block index
        Returns:
            primary subtitles with gaps filled
        """
        block_pairs = get_block_pairs_by_pause(primary, secondary)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (prim_blk, sec_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            if len(sec_blk) == 0:
                raise ScinoephileError("Secondary blocks must contain subtitles.")

            size = len(sec_blk)
            overlap = get_sync_overlap_matrix(prim_blk, sec_blk)
            sync_groups = [([], [sec_idx]) for sec_idx in range(len(sec_blk))]
            for prim_idx in range(len(prim_blk)):
                sg_idx = np.argmax(overlap[prim_idx, :])
                sync_groups[sg_idx][0].append(prim_idx)
            missing = tuple(
                idx for idx, group in enumerate(sync_groups) if not group[0]
            )

            if not missing:
                output_series_to_concatenate[blk_idx] = prim_blk
                continue

            test_case_cls = DualBlockGappedTestCase.get_test_case_cls(
                size, missing, self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            prim_idx = 0
            for sec_idx in range(size):
                if sec_idx not in missing:
                    key_primary = self.prompt_cls.source_one(sec_idx + 1)
                    val_primary = re.sub(r"\\N", "\n", prim_blk[prim_idx].text).strip()
                    query_kwargs[key_primary] = val_primary
                    prim_idx += 1
                key_secondary = self.prompt_cls.source_two(sec_idx + 1)
                val_secondary = re.sub(r"\\N", "\n", sec_blk[sec_idx].text).strip()
                query_kwargs[key_secondary] = val_secondary
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sec_idx in range(size):
                secondary_sub = sec_blk[sec_idx]
                start = secondary_sub.start
                end = secondary_sub.end
                if sec_idx not in missing:
                    key_primary = self.prompt_cls.source_one(sec_idx + 1)
                    primary_text = getattr(test_case.query, key_primary)
                else:
                    key_output = self.prompt_cls.output(sec_idx + 1)
                    primary_text = getattr(test_case.answer, key_output)
                output_series.append(Subtitle(start=start, end=end, text=primary_text))

            info(
                f"Block {blk_idx} ({prim_blk.start_idx} - {prim_blk.end_idx}):\n"
                f"{prim_blk.to_series().to_simple_string()}"
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
