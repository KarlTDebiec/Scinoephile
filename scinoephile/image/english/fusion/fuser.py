#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed English subtitles from Google Lens and Tesseract."""

from __future__ import annotations

from logging import info, warning
from pathlib import Path
from textwrap import dedent

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.testing import (
    get_test_cases_from_file_path,
    test_data_root,
    update_test_cases,
)

from .queryer import EnglishFusionLLMQueryer
from .test_case import EnglishFusionTestCase

__all__ = ["EnglishFuser"]


class EnglishFuser:
    """Fuses OCRed English subtitles from Google Lens and Tesseract."""

    def __init__(
        self,
        test_cases: list[EnglishFusionTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
    ):
        """Initialize.

        Arguments:
            test_cases: test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
        """
        if test_cases is None:
            test_cases = self.get_default_test_cases()

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(get_test_cases_from_file_path(test_case_path))
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = EnglishFusionLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Queries LLM to fuse OCRed English subtitles from Google Lens and
        Tesseract."""

    def fuse(self, lens: Series, tesseract: Series, stop_at_idx: int | None = None):
        """Fuse OCRed English subtitles from Google Lens and Tesseract.

        Arguments:
            lens: English subtitles OCRed using Google Lens
            tesseract: English subtitles OCRed using Tesseract
            stop_at_idx: stop processing at this index
        """
        # Validate series
        if not are_series_one_to_one(lens, tesseract):
            raise ScinoephileError(
                "Google Lens and Tesseract series must have the same number of "
                "subtitles."
            )

        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.create_test_case_file(self.test_case_path)

        # Fuse subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(lens)
        for sub_idx, (lens_sub, tesseract_sub) in enumerate(zip(lens, tesseract)):
            if sub_idx >= stop_at_idx:
                break
            lens_text = lens_sub.text
            tesseract_text = tesseract_sub.text

            # Handle missing data
            if not lens_text and not tesseract_text:
                output_subtitles.append(
                    Subtitle(start=lens_sub.start, end=lens_sub.end, text="")
                )
                info(f"Subtitle {sub_idx + 1} empty.")
                continue
            if lens_text == tesseract_text:
                output_subtitles.append(lens_sub)
                info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{lens_text.replace('\n', ' ')}"
                )
                continue
            if not tesseract_text:
                output_subtitles.append(lens_sub)
                info(
                    f"Subtitle {sub_idx + 1} from Lens:      "
                    f"{lens_text.replace('\n', ' ')}"
                )
                continue
            if not lens_text:
                output_subtitles.append(tesseract_sub)
                info(
                    f"Subtitle {sub_idx + 1} from Tesseract: "
                    f"{tesseract_text.replace('\n', ' ')}"
                )
                continue

            # Query LLM
            test_case_cls = EnglishFusionTestCase.get_test_case_cls()
            query_cls = test_case_cls.query_cls
            answer_cls = test_case_cls.answer_cls
            query = query_cls(lens=lens_sub.text, tesseract=tesseract_sub.text)
            answer = self.llm_queryer(query, answer_cls, test_case_cls)
            sub = Subtitle(start=lens_sub.start, end=lens_sub.end, text=answer.fused)
            info(
                f"Subtitle {sub_idx + 1} fused:         {sub.text.replace('\n', '\\n')}"
            )
            output_subtitles.append(sub)

        # Log test cases
        if self.test_case_path is not None:
            update_test_cases(self.test_case_path, "test_cases", self.llm_queryer)

        # Organize and return
        output_series = Series()
        output_series.events = output_subtitles
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series

    @classmethod
    def get_default_test_cases(cls):
        """Get default test cases included with package.

        Returns:
            test cases
        """
        try:
            # noinspection PyUnusedImports
            from test.data.kob import kob_english_fusion_test_cases
            from test.data.mlamd import mlamd_english_fusion_test_cases
            from test.data.mnt import mnt_english_fusion_test_cases
            from test.data.t import t_english_fusion_test_cases

            return (
                kob_english_fusion_test_cases
                + mlamd_english_fusion_test_cases
                + mnt_english_fusion_test_cases
                + t_english_fusion_test_cases
            )
        except ImportError as exc:
            warning(
                f"Default test cases not available for {cls.__name__}, "
                f"encountered Exception:\n{exc}"
            )
            return []

    @staticmethod
    def create_test_case_file(test_case_path: Path):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
        """
        contents = dedent('''
            """English fusion test cases."""

            from __future__ import annotations

            from scinoephile.image.english.fusion import EnglishFusionTestCase

            # noinspection PyArgumentList
            test_cases = []  # test_cases
            """English fusion test cases."""

            __all__ = [
                "test_cases",
            ]''').strip()
        test_case_path.parent.mkdir(parents=True, exist_ok=True)
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")
