#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes mono track / block matters."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.llms.base import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.testing import test_data_root

from .prompt import MonoBlockPrompt
from .test_case import MonoBlockTestCase

__all__ = ["MonoBlockProcessor"]


class MonoBlockProcessor:
    """Processes mono track / block matters."""

    prompt_cls: type[MonoBlockPrompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[MonoBlockPrompt],
        test_cases: list[MonoBlockTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[MonoBlockTestCase] | None = None,
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
                    MonoBlockTestCase,
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

    def process(self, series: Series, stop_at_idx: int | None = None) -> Series:
        """Processes mono track / block matters.

        Arguments:
            series: subtitles
            stop_at_idx: stop processing at this index
        Returns:
            processed subtitles
        """
        # Process subtitles
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        stop_at_idx = stop_at_idx or len(series.blocks)
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = MonoBlockTestCase.get_test_case_cls(
                len(block), self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for idx, subtitle in enumerate(block):
                key = self.prompt_cls.input_field(idx + 1)
                query_kwargs[key] = re.sub(r"\\N", "\n", subtitle.text).strip()
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                key = self.prompt_cls.output_field(sub_idx + 1)
                if output_text := getattr(test_case.answer, key):
                    subtitle.text = output_text
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
