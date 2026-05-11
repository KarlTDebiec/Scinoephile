#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes dual n to m transforms."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core.llms import Processor
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series

from .manager import DualNToMManager
from .prompt import DualNToMPrompt

__all__ = ["DualNToMProcessor"]


logger = getLogger(__name__)


class DualNToMProcessor(Processor):
    """Processes dual input blocks where outputs follow source one cardinality."""

    prompt_cls: type[DualNToMPrompt]
    """Text for LLM correspondence."""

    manager_cls = DualNToMManager
    """Manager class used to construct test case models."""

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Process paired subtitle blocks with output cardinality from source one.

        Arguments:
            source_one: primary subtitles that determine output timing and count
            source_two: secondary subtitles providing reference text
            stop_at_idx: stop processing at this block index
        Returns:
            generated subtitles using source-one timing
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        if stop_at_idx is None:
            stop_at_idx = len(block_pairs)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs):
            if blk_idx >= stop_at_idx:
                break
            if not one_blk:
                output_series_to_concatenate[blk_idx] = Series()
                continue

            test_case_cls = DualNToMManager.get_test_case_cls(
                source_one_size=len(one_blk),
                source_two_size=len(two_blk),
                prompt_cls=self.prompt_cls,
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for sub_idx, sub in enumerate(one_blk.events, 1):
                key = self.prompt_cls.src_1(sub_idx)
                query_kwargs[key] = sub.text_with_newline.strip()
            for sub_idx, sub in enumerate(two_blk.events, 1):
                key = self.prompt_cls.src_2(sub_idx)
                query_kwargs[key] = sub.text_with_newline.strip()

            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, sub in enumerate(one_blk.events, 1):
                output_key = self.prompt_cls.output(sub_idx)
                output = getattr(test_case.answer, output_key)
                output_series.append(
                    Subtitle(start=sub.start, end=sub.end, text=output)
                )

            logger.info(f"Block {blk_idx}:\n{output_series.to_simple_string()}")
            output_series_to_concatenate[blk_idx] = output_series

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        output_series_blocks = [
            series for series in output_series_to_concatenate if series is not None
        ]
        if output_series_blocks:
            output_series = get_concatenated_series(output_series_blocks)
        else:
            output_series = Series()
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
