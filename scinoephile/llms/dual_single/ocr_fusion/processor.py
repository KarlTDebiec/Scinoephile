#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes OCR fusion."""

from __future__ import annotations

from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.testing import test_data_root
from scinoephile.llms.base import (
    Queryer,
    TestCase,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.multilang.synchronization import are_series_one_to_one

from .manager import OcrFusionManager
from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionProcessor"]


class OcrFusionProcessor:
    """Processes OCR fusion."""

    def __init__(
        self,
        prompt_cls: type[OcrFusionPrompt],
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
            if test_case_path.exists():
                test_cases.extend(
                    load_test_cases_from_json(
                        test_case_path,
                        OcrFusionManager,
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

    def process(
        self, source_one: Series, source_two: Series, stop_at_idx: int | None = None
    ) -> Series:
        """Processes OCR fusion dual track / single subtitle matters.

        Arguments:
            source_one: subtitles from source one
            source_two: subtitles from source two
            stop_at_idx: stop processing at this index
        Returns:
            processed subtitles
        """
        # Validate series
        if not are_series_one_to_one(source_one, source_two):
            raise ScinoephileError(
                "Series from sources one and two must have the same number of "
                f"subtitles; got {len(source_one)} and {len(source_two)}."
            )

        # Process subtitles
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
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.src_1}: "
                    f"{text_one.replace('\n', ' ')}"
                )
                continue
            if not text_one:
                output_subtitles.append(sub_two)
                info(
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.src_2}: "
                    f"{text_two.replace('\n', ' ')}"
                )
                continue

            # Query LLM
            test_case_cls = OcrFusionManager.get_test_case_cls(self.prompt_cls)
            query_cls = test_case_cls.query_cls
            query_kwargs = {
                self.prompt_cls.src_1: sub_one.text,
                self.prompt_cls.src_2: sub_two.text,
            }
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_text = getattr(test_case.answer, self.prompt_cls.output)
            sub = Subtitle(start=sub_one.start, end=sub_one.end, text=output_text)
            info(
                f"Subtitle {sub_idx + 1} processed:     {sub.text.replace('\n', '\\n')}"
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
