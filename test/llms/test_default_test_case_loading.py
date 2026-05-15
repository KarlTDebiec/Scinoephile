#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression tests for default test-case loading."""

from __future__ import annotations

import json
from collections.abc import Callable

import pytest

from scinoephile.common import package_root
from scinoephile.core.llms import TestCase
from scinoephile.lang.eng.block_review import BlockReviewPromptEng
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
)
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.llms.default_test_cases import (
    ENG_BLOCK_REVIEW_JSON_PATHS,
    ENG_OCR_FUSION_JSON_PATHS,
    ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
    YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_LINE_REVIEW_JSON_PATHS,
    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANS_OCR_FUSION_JSON_PATHS,
    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANT_OCR_FUSION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_1_to_1.ocr_fusion.manager import OcrFusionManager
from scinoephile.llms.dual_n_minus_m_to_n.manager import DualNMinusMToNManager
from scinoephile.llms.dual_n_to_m.manager import DualNToMManager
from scinoephile.llms.dual_n_to_n.manager import DualNToNManager
from scinoephile.llms.mono_n.manager import MonoNManager
from scinoephile.multilang.eng_zho.gapped_translation import (
    EngGappedTranslationVsZhoPrompt,
)
from scinoephile.multilang.eng_zho.translation import EngTranslationVsZhoPrompt
from scinoephile.multilang.yue_zho.block_review import YueBlockReviewVsZhoPromptYueHans
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.line_review import YueLineReviewVsZhoPromptYueHans
from scinoephile.multilang.yue_zho.line_review.manager import YueZhoLineReviewManager


def _get_expected_case_count(relative_paths: list[str]) -> int:
    """Get expected number of test cases from JSON files.

    Arguments:
        relative_paths: paths relative to repository test data root
    Returns:
        expected number of test cases
    """
    test_data_root = package_root.parent / "test/data"
    count = 0
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as file_handle:
            count += len(json.load(file_handle))
    return count


@pytest.mark.parametrize(
    ("name", "loader", "relative_paths"),
    [
        (
            "eng_block_review",
            lambda: load_default_test_cases(
                MonoNManager, BlockReviewPromptEng, ENG_BLOCK_REVIEW_JSON_PATHS
            ),
            [
                "kob/output/eng_ocr/lang/eng/block_review.json",
                "kob/output/eng/lang/eng/block_review.json",
                "mlamd/output/eng_ocr/lang/eng/block_review.json",
                "mnt/output/eng_ocr/lang/eng/block_review.json",
                "t/output/eng_ocr/lang/eng/block_review.json",
            ],
        ),
        (
            "eng_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager, OcrFusionPromptEng, ENG_OCR_FUSION_JSON_PATHS
            ),
            [
                "kob/output/eng_ocr/lang/eng/ocr_fusion.json",
                "mlamd/output/eng_ocr/lang/eng/ocr_fusion.json",
                "mnt/output/eng_ocr/lang/eng/ocr_fusion.json",
                "t/output/eng_ocr/lang/eng/ocr_fusion.json",
            ],
        ),
        (
            "eng_zho_translation",
            lambda: load_default_test_cases(
                DualNToMManager,
                EngTranslationVsZhoPrompt,
                ENG_ZHO_TRANSLATION_JSON_PATHS,
            ),
            [],
        ),
        (
            "eng_zho_gapped_translation",
            lambda: load_default_test_cases(
                DualNMinusMToNManager,
                EngGappedTranslationVsZhoPrompt,
                ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
            ),
            [],
        ),
        (
            "zho_hans_block_review",
            lambda: load_default_test_cases(
                MonoNManager,
                BlockReviewPromptZhoHans,
                ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/zho-Hans_ocr/lang/zho/block_review.json",
                "mnt/output/zho-Hans_ocr/lang/zho/block_review.json",
                "t/output/zho-Hans_ocr/lang/zho/block_review.json",
            ],
        ),
        (
            "zho_hant_block_review",
            lambda: load_default_test_cases(
                MonoNManager,
                BlockReviewPromptZhoHant,
                ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "kob/output/zho-Hant_ocr/lang/zho/block_review.json",
                "mlamd/output/zho-Hant_ocr/lang/zho/block_review.json",
                "mnt/output/zho-Hant_ocr/lang/zho/block_review.json",
                "t/output/zho-Hant_ocr/lang/zho/block_review.json",
            ],
        ),
        (
            "zho_hans_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager,
                OcrFusionPromptZhoHans,
                ZHO_HANS_OCR_FUSION_JSON_PATHS,
            ),
            [
                "mlamd/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
                "mnt/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
                "t/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
            ],
        ),
        (
            "zho_hant_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager,
                OcrFusionPromptZhoHant,
                ZHO_HANT_OCR_FUSION_JSON_PATHS,
            ),
            [
                "kob/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "mlamd/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "mnt/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "t/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
            ],
        ),
        (
            "yue_zho_line_review",
            lambda: load_default_test_cases(
                YueZhoLineReviewManager,
                YueLineReviewVsZhoPromptYueHans,
                YUE_ZHO_LINE_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/mps.json",
            ],
        ),
        (
            "yue_zho_block_review",
            lambda: load_default_test_cases(
                DualNToNManager,
                YueBlockReviewVsZhoPromptYueHans,
                YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/mps.json",
            ],
        ),
        (
            "yue_vs_zho_gapped_translation",
            lambda: load_default_test_cases(
                DualNMinusMToNManager,
                YueGappedTranslationVsZhoPromptYueHans,
                YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/mps.json",
            ],
        ),
    ],
)
def test_default_loader_coverage(
    name: str,
    loader: Callable[[], list[TestCase]],
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
