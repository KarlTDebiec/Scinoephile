#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed English subtitles from Google Lens and Tesseract."""

from __future__ import annotations

import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.image.english.fusion.english_fusion_llm_queryer import (
    EnglishFusionLLMQueryer,
)
from scinoephile.image.english.fusion.english_fusion_query import EnglishFusionQuery
from scinoephile.image.english.fusion.english_fusion_test_case import (
    EnglishFusionTestCase,
)
from scinoephile.testing import test_data_root, update_test_cases

try:
    # noinspection PyUnusedImports
    from test.data.kob import kob_english_fusion_test_cases

    # noinspection PyUnusedImports
    from test.data.mlamd import mlamd_english_fusion_test_cases

    # noinspection PyUnusedImports
    from test.data.mnt import mnt_english_fusion_test_cases

    # noinspection PyUnusedImports
    from test.data.t import t_english_fusion_test_cases

    default_test_cases = (
        kob_english_fusion_test_cases
        + mlamd_english_fusion_test_cases
        + mnt_english_fusion_test_cases
        + t_english_fusion_test_cases
    )
except ImportError:
    default_test_cases = []


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
            test_cases = default_test_cases

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)

            if test_case_path.exists():
                spec = spec_from_file_location("test_cases", test_case_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                for name in getattr(module, "__all__", []):
                    if name.endswith("test_cases"):
                        if value := getattr(module, name, None):
                            test_cases.extend(value)

        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = EnglishFusionLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Queries LLM to fuse OCRed English subtitles from Google Lens and Tesseract."""

    def fuse(self, tesseract: Series, lens: Series, stop_at_idx: int | None = None):
        """Fuse OCRed English subtitles from Google Lens and Tesseract.

        Arguments:
            tesseract: English subtitles OCRed using Tesseract
            lens: English subtitles OCRed using Google Lens
            stop_at_idx: stop processing at this index
        """
        # Validate series
        if not are_series_one_to_one(tesseract, lens):
            raise ScinoephileError(
                "Tesseract and Google Lens OCRed series must have the same number of "
                "subtitles."
            )

        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.test_case_path.parent.mkdir(parents=True, exist_ok=True)
            self.create_test_case_file(self.test_case_path)

        # Fuse subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(tesseract)
        for sub_idx, (tesseract_sub, lens_sub) in enumerate(zip(tesseract, lens)):
            if sub_idx >= stop_at_idx:
                break
            tesseract_text = tesseract_sub.text
            lens_text = lens_sub.text
            if tesseract_text == lens_text:
                output_subtitles.append(tesseract_sub)
                info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{tesseract_text.replace('\n', ' ')}"
                )
                continue
            if not tesseract_text:
                if not lens_text:
                    continue
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
            query = EnglishFusionQuery(tesseract=tesseract_sub.text, lens=lens_sub.text)
            answer = self.llm_queryer(query)
            sub = Subtitle(
                start=tesseract_sub.start,
                end=tesseract_sub.end,
                text=answer.ronghe,
            )
            info(
                f"Subtitle {sub_idx + 1} fused:         {sub.text.replace('\n', '\\n')}"
            )
            output_subtitles.append(sub)

        # Concatenate and return
        output_series = Series()
        output_series.events = output_subtitles
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")

        if self.test_case_path is not None:
            asyncio.run(
                update_test_cases(self.test_case_path, "test_cases", self.llm_queryer)
            )
        return output_series

    @staticmethod
    def create_test_case_file(test_case_path: Path):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
        """
        contents = '''"""English fusion test cases."""

from __future__ import annotations

from scinoephile.image.english.fusion import EnglishFusionTestCase

test_cases = []  # test_cases
"""English fusion test cases."""

__all__ = [
    "test_cases",
]'''
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")
