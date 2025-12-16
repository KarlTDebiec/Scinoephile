#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed subtitles from two sources."""

from __future__ import annotations

from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.llms import (
    Queryer,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.synchronization import are_series_one_to_one
from scinoephile.testing import test_data_root

from .prompt import FusionPrompt
from .test_case import FusionTestCase

__all__ = ["Fuser"]


class Fuser:
    """Fuses OCRed subtitles from two sources."""

    def __init__(
        self,
        prompt_cls: type[FusionPrompt],
        test_cases: list[FusionTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        default_test_cases: list[FusionTestCase] | None = None,
    ):
        """Initialize.

        Arguments:
            prompt_cls: prompt class
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
                    FusionTestCase,
                    prompt_cls=self.prompt_cls,
                )
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

    def fuse(
        self, source_one: Series, source_two: Series, stop_at_idx: int | None = None
    ) -> Series:
        """Fuse OCRed subtitles from two sources.

        Arguments:
            source_one: subtitles from OCR source one
            source_two: subtitles from OCR source two
            stop_at_idx: stop processing at this index
        Returns:
            fused subtitles
        """
        # Validate series
        if not are_series_one_to_one(source_one, source_two):
            raise ScinoephileError(
                "Series from OCR sources one and two must have the same number of "
                "subtitles."
            )

        # Fuse subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(source_one)
        for sub_idx, (sub_one, sub_two) in enumerate(zip(source_one, source_two)):
            if sub_idx >= stop_at_idx:
                break
            text_one = sub_one.text
            text_two = sub_two.text

            # Handle missing data
            if not text_one and not text_two:
                output_subtitles.append(
                    Subtitle(start=sub_one.start, end=sub_one.end, text="")
                )
                info(f"Subtitle {sub_idx + 1} empty.")
                continue
            if text_one == text_two:
                output_subtitles.append(sub_one)
                info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{text_one.replace('\n', ' ')}"
                )
                continue
            if not text_two:
                output_subtitles.append(sub_one)
                info(
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.source_one_field}: "
                    f"{text_one.replace('\n', ' ')}"
                )
                continue
            if not text_one:
                output_subtitles.append(sub_two)
                info(
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.source_two_field}: "
                    f"{text_two.replace('\n', ' ')}"
                )
                continue

            # Query LLM
            test_case_cls = FusionTestCase.get_test_case_cls(self.prompt_cls)
            query_cls = test_case_cls.query_cls
            query_attrs = {
                self.prompt_cls.source_one_field: sub_one.text,
                self.prompt_cls.source_two_field: sub_two.text,
            }
            query = query_cls(**query_attrs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            fused_text = getattr(test_case.answer, self.prompt_cls.fused_field)
            sub = Subtitle(start=sub_one.start, end=sub_one.end, text=fused_text)
            info(
                f"Subtitle {sub_idx + 1} fused:         {sub.text.replace('\n', '\\n')}"
            )
            output_subtitles.append(sub)

        # Log test cases
        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        # Organize and return
        output_series = Series()
        output_series.events = output_subtitles
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
