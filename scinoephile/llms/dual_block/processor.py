#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes dual track / subtitle block matters."""

from __future__ import annotations

from logging import info

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.llms.base import Processor, save_test_cases_to_json

from .manager import DualBlockManager
from .prompt import DualBlockPrompt

__all__ = ["DualBlockProcessor"]


class DualBlockProcessor(Processor):
    """Processes dual track / subtitle block matters."""

    prompt_cls: type[DualBlockPrompt]
    """Text for LLM correspondence."""

    manager_cls = DualBlockManager
    """Manager class used to construct test case models."""

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Process paired subtitle series blockwise.

        Arguments:
            source_one: primary subtitles to be processed
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

        # Track indices for logging
        current_idx = 0
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs):
            if blk_idx >= stop_at_idx:
                break
            if len(one_blk) != len(two_blk):
                raise ScinoephileError(
                    "Blocks must be aligned with the same number of subtitles."
                )

            # Determine TestCase configuration
            size = len(one_blk)

            # Query LLM
            test_case_cls = DualBlockManager.get_test_case_cls(size, self.prompt_cls)
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for sub_idx in range(size):
                one_key = self.prompt_cls.src_1(sub_idx + 1)
                one_val = one_blk[sub_idx].text_with_newline.strip()
                query_kwargs[one_key] = one_val
                two_key = self.prompt_cls.src_2(sub_idx + 1)
                two_val = two_blk[sub_idx].text_with_newline.strip()
                query_kwargs[two_key] = two_val
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, sub in enumerate(one_blk):
                output_key = self.prompt_cls.output(sub_idx + 1)
                if output := getattr(test_case.answer, output_key):
                    sub.text = output
                output_series.append(sub)

            start_idx = current_idx
            end_idx = current_idx + len(one_blk)
            current_idx = end_idx
            info(
                f"Block {blk_idx} ({start_idx} - {end_idx}):\n"
                f"{one_blk.to_simple_string()}"
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
