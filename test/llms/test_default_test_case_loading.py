#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression tests for default test-case loading."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

import pytest

from scinoephile.common import package_root
from scinoephile.lang.eng.ocr_fusion import (
    EngOcrFusionPrompt,
    get_default_eng_ocr_fusion_test_cases,
)
from scinoephile.lang.eng.proofreading import (
    EngProofreadingPrompt,
    get_default_eng_proofreading_test_cases,
)
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
    get_default_zho_ocr_fusion_test_cases,
)
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
    get_default_zho_proofreading_test_cases,
)
from scinoephile.llms.base import TestCase
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    get_default_yue_vs_zho_proofreading_test_cases,
)
from scinoephile.multilang.yue_zho.review import (
    YueHansReviewPrompt,
    get_default_yue_vs_zho_test_cases,
)
from scinoephile.multilang.yue_zho.translation import (
    YueHansFromZhoTranslationPrompt,
    get_default_yue_from_zho_translation_test_cases,
)

Loader = Callable[[], list[TestCase]]


def _get_repo_root() -> Path:
    """Get repository root."""
    return package_root.parent


def _get_expected_case_count(relative_paths: list[str]) -> int:
    """Get expected number of test cases from JSON files.

    Arguments:
        relative_paths: paths relative to repository test data root
    Returns:
        expected number of test cases
    """
    test_data_root = _get_repo_root() / "test" / "data"
    count = 0
    for relative_path in relative_paths:
        with open(test_data_root / relative_path, encoding="utf-8") as file_handle:
            count += len(json.load(file_handle))
    return count


@pytest.mark.parametrize(
    ("name", "loader", "relative_paths"),
    [
        (
            "eng_proofreading",
            lambda: get_default_eng_proofreading_test_cases(EngProofreadingPrompt),
            [
                "kob/lang/eng/proofreading/eng_ocr.json",
                "kob/lang/eng/proofreading/eng_srt.json",
                "mlamd/lang/eng/proofreading.json",
                "mnt/lang/eng/proofreading.json",
                "t/lang/eng/proofreading.json",
            ],
        ),
        (
            "eng_ocr_fusion",
            lambda: get_default_eng_ocr_fusion_test_cases(EngOcrFusionPrompt),
            [
                "kob/lang/eng/ocr_fusion.json",
                "mlamd/lang/eng/ocr_fusion.json",
                "mnt/lang/eng/ocr_fusion.json",
                "t/lang/eng/ocr_fusion.json",
            ],
        ),
        (
            "zho_hans_proofreading",
            lambda: get_default_zho_proofreading_test_cases(ZhoHansProofreadingPrompt),
            [
                "mlamd/lang/zho/proofreading/zho-Hans.json",
                "mnt/lang/zho/proofreading/zho-Hans.json",
                "t/lang/zho/proofreading/zho-Hans.json",
            ],
        ),
        (
            "zho_hant_proofreading",
            lambda: get_default_zho_proofreading_test_cases(ZhoHantProofreadingPrompt),
            [
                "kob/lang/zho/proofreading/zho-Hant.json",
                "mlamd/lang/zho/proofreading/zho-Hant.json",
                "mnt/lang/zho/proofreading/zho-Hant.json",
                "t/lang/zho/proofreading/zho-Hant.json",
            ],
        ),
        (
            "zho_hans_ocr_fusion",
            lambda: get_default_zho_ocr_fusion_test_cases(ZhoHansOcrFusionPrompt),
            [
                "mlamd/lang/zho/ocr_fusion/zho-Hans.json",
                "mnt/lang/zho/ocr_fusion/zho-Hans.json",
                "t/lang/zho/ocr_fusion/zho-Hans.json",
            ],
        ),
        (
            "zho_hant_ocr_fusion",
            lambda: get_default_zho_ocr_fusion_test_cases(ZhoHantOcrFusionPrompt),
            [
                "kob/lang/zho/ocr_fusion/zho-Hant.json",
                "mlamd/lang/zho/ocr_fusion/zho-Hant.json",
                "mnt/lang/zho/ocr_fusion/zho-Hant.json",
                "t/lang/zho/ocr_fusion/zho-Hant.json",
            ],
        ),
        (
            "yue_zho_proofreading",
            lambda: get_default_yue_vs_zho_proofreading_test_cases(
                YueZhoHansProofreadingPrompt
            ),
            ["mlamd/multilang/yue_zho/proofreading.json"],
        ),
        (
            "yue_zho_review",
            lambda: get_default_yue_vs_zho_test_cases(YueHansReviewPrompt),
            ["mlamd/multilang/yue_zho/review.json"],
        ),
        (
            "yue_from_zho_translation",
            lambda: get_default_yue_from_zho_translation_test_cases(
                YueHansFromZhoTranslationPrompt
            ),
            ["mlamd/multilang/yue_zho/translation.json"],
        ),
    ],
)
def test_default_loader_coverage(
    name: str,
    loader: Loader,
    relative_paths: list[str],
):
    """Test that each default loader includes all configured repository cases.

    Arguments:
        name: short name of loader under test
        loader: callable that loads default test cases
        relative_paths: expected JSON paths for this loader
    """
    expected_count = _get_expected_case_count(relative_paths)
    loaded_count = len(loader())
    assert loaded_count == expected_count, (
        f"{name} loaded {loaded_count} cases, expected {expected_count}"
    )


def test_no_test_imports_under_scinoephile():
    """Test that runtime package does not import from test modules."""
    pattern = re.compile(r"^\s*(?:from|import)\s+test(?:\.|\b)", re.MULTILINE)
    offenders: list[Path] = []
    for path in (_get_repo_root() / "scinoephile").rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        if pattern.search(content):
            offenders.append(path.relative_to(_get_repo_root()))
    assert not offenders, f"Found forbidden test imports: {offenders}"
