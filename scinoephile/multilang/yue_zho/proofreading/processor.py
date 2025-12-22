#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes 粤文 vs. 中文 proofreading."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common.validation import val_output_path
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.llms.base import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.pairs import get_block_pairs_by_pause
from scinoephile.multilang.synchronization import get_sync_overlap_matrix
from scinoephile.testing import test_data_root

from .prompts import YueZhoHansProofreadingPrompt
from .test_case import YueZhoProofreadingTestCase

__all__ = ["YueZhoProofreadingProcessor"]


class YueZhoProofreadingProcessor:
    """Processes 粤文 vs. 中文 proofreading."""

    prompt_cls: type[YueZhoHansProofreadingPrompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[YueZhoHansProofreadingPrompt],
        test_cases: list[YueZhoProofreadingTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[YueZhoProofreadingTestCase] | None = None,
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
                    YueZhoProofreadingTestCase,
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
        """Proofread 粤文 against 中文 with tolerant alignment.

        Arguments:
            source_one: 粤文 subtitles (may omit some 中文 lines)
            source_two: 中文 reference subtitles
            stop_at_idx: stop processing at this block index
        Returns:
            Proofread 粤文 subtitles
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            overlap = get_sync_overlap_matrix(one_blk, two_blk)
            output_block = Series()

            sync_grps = [([], [two_idx]) for two_idx in range(len(two_blk))]
            for one_idx in range(len(one_blk)):
                two_idx = np.argmax(overlap[one_idx, :])
                sync_grps[two_idx][0].append(one_idx)

            # Query LLM
            test_case_cls = YueZhoProofreadingTestCase.get_test_case_cls(
                self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            for one_grp, two_grp in sync_grps:
                if not one_grp:
                    continue
                one_idx = one_grp[0]
                two_idx = two_grp[0]
                one_sub = one_blk[one_idx]
                two_sub = two_blk[two_idx]
                one_val = re.sub(r"\\N", "\n", one_sub.text).strip()
                two_val = re.sub(r"\\N", "\n", two_sub.text).strip()
                if one_val == two_val:
                    output_block.append(
                        Subtitle(start=one_sub.start, end=one_sub.end, text=one_val)
                    )
                    continue
                query_kwargs = {
                    self.prompt_cls.src_1: one_val,
                    self.prompt_cls.src_2: two_val,
                }
                query = query_cls(**query_kwargs)
                test_case = test_case_cls(query=query)
                test_case: YueZhoProofreadingTestCase = self.queryer(test_case)

                output = getattr(test_case.answer, self.prompt_cls.output)
                if output == "\ufffd":
                    continue
                output_block.append(
                    Subtitle(start=one_sub.start, end=one_sub.end, text=output)
                )

            info(f"Block {blk_idx}:\n{one_blk.to_simple_string()}")
            output_series_to_concatenate[blk_idx] = output_block

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
