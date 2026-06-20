#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression tests for default test-case loading."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import mark as _mark

from scinoephile.common import package_root
from scinoephile.core.llms import Manager, Prompt
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
    YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_LINE_REVIEW_JSON_PATHS,
    YUE_ZHO_TRANSLATION_JSON_PATHS,
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
from scinoephile.multilang.yue_zho.guided_translation import (
    YueGuidedTranslationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.line_review import YueLineReviewVsZhoPromptYueHans
from scinoephile.multilang.yue_zho.line_review.manager import YueZhoLineReviewManager
from scinoephile.multilang.yue_zho.translation import YueTranslationVsZhoPromptYueHans

parametrize = _mark.parametrize


def _get_expected_case_count(relative_paths: tuple[Path, ...]) -> int:
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


@parametrize(
    ("name", "manager_cls", "prompt_cls", "json_paths", "expected_paths"),
    [
        (
            "eng_block_review",
            MonoNManager,
            BlockReviewPromptEng,
            ENG_BLOCK_REVIEW_JSON_PATHS,
            (
                Path("kob/output/eng_ocr/lang/eng/block_review.json"),
                Path("kob/output/eng/lang/eng/block_review.json"),
                Path("mlamd/output/eng_ocr/lang/eng/block_review.json"),
                Path("mnt/output/eng_ocr/lang/eng/block_review.json"),
                Path("t/output/eng_ocr/lang/eng/block_review.json"),
            ),
        ),
        (
            "eng_ocr_fusion",
            OcrFusionManager,
            OcrFusionPromptEng,
            ENG_OCR_FUSION_JSON_PATHS,
            (
                Path("kob/output/eng_ocr/lang/eng/ocr_fusion.json"),
                Path("mlamd/output/eng_ocr/lang/eng/ocr_fusion.json"),
                Path("mnt/output/eng_ocr/lang/eng/ocr_fusion.json"),
                Path("t/output/eng_ocr/lang/eng/ocr_fusion.json"),
            ),
        ),
        (
            "eng_zho_translation",
            DualNToMManager,
            EngTranslationVsZhoPrompt,
            ENG_ZHO_TRANSLATION_JSON_PATHS,
            (),
        ),
        (
            "eng_zho_gapped_translation",
            DualNMinusMToNManager,
            EngGappedTranslationVsZhoPrompt,
            ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
            (),
        ),
        (
            "zho_hans_block_review",
            MonoNManager,
            BlockReviewPromptZhoHans,
            ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
            (
                Path("mlamd/output/zho-Hans_ocr/lang/zho/block_review.json"),
                Path("mnt/output/zho-Hans_ocr/lang/zho/block_review.json"),
                Path("t/output/zho-Hans_ocr/lang/zho/block_review.json"),
            ),
        ),
        (
            "zho_hant_block_review",
            MonoNManager,
            BlockReviewPromptZhoHant,
            ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
            (
                Path("kob/output/zho-Hant_ocr/lang/zho/block_review.json"),
                Path("mlamd/output/zho-Hant_ocr/lang/zho/block_review.json"),
                Path("mnt/output/zho-Hant_ocr/lang/zho/block_review.json"),
                Path("t/output/zho-Hant_ocr/lang/zho/block_review.json"),
            ),
        ),
        (
            "zho_hans_ocr_fusion",
            OcrFusionManager,
            OcrFusionPromptZhoHans,
            ZHO_HANS_OCR_FUSION_JSON_PATHS,
            (
                Path("mlamd/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
                Path("mnt/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
                Path("t/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
            ),
        ),
        (
            "zho_hant_ocr_fusion",
            OcrFusionManager,
            OcrFusionPromptZhoHant,
            ZHO_HANT_OCR_FUSION_JSON_PATHS,
            (
                Path("kob/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
                Path("mlamd/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
                Path("mnt/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
                Path("t/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
            ),
        ),
        (
            "yue_zho_line_review",
            YueZhoLineReviewManager,
            YueLineReviewVsZhoPromptYueHans,
            YUE_ZHO_LINE_REVIEW_JSON_PATHS,
            (
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "line_review/cuda.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "line_review/cpu.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "line_review/mps.json"
                ),
            ),
        ),
        (
            "yue_zho_block_review",
            DualNToNManager,
            YueBlockReviewVsZhoPromptYueHans,
            YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
            (
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "block_review/cuda.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "block_review/cpu.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "block_review/mps.json"
                ),
            ),
        ),
        (
            "yue_vs_zho_gapped_translation",
            DualNMinusMToNManager,
            YueGappedTranslationVsZhoPromptYueHans,
            YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
            (
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "gap_translation/cuda.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "gap_translation/cpu.json"
                ),
                Path(
                    "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/"
                    "gap_translation/mps.json"
                ),
            ),
        ),
        (
            "yue_zho_translation",
            DualNToMManager,
            YueTranslationVsZhoPromptYueHans,
            YUE_ZHO_TRANSLATION_JSON_PATHS,
            (),
        ),
        (
            "yue_zho_guided_translation",
            DualNToMManager,
            YueGuidedTranslationVsZhoPromptYueHans,
            YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
            (),
        ),
    ],
)
def test_default_loader_coverage(
    name: str,
    manager_cls: type[Manager],
    prompt_cls: type[Prompt],
    json_paths: tuple[Path, ...],
    expected_paths: tuple[Path, ...],
):
    """Test that each default loader includes all configured repository cases.

    Arguments:
        name: short name of loader under test
        manager_cls: manager class used to load default test cases
        prompt_cls: prompt class used to load default test cases
        json_paths: configured JSON paths for this loader
        expected_paths: expected JSON paths for this loader
    """
    expected_count = _get_expected_case_count(expected_paths)
    loaded_count = len(load_default_test_cases(manager_cls, prompt_cls, json_paths))
    assert loaded_count == expected_count, (
        f"{name} loaded {loaded_count} cases, expected {expected_count}"
    )
