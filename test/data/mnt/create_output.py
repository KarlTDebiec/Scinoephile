#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.testing import test_data_root
from test.data.kob import (
    get_kob_eng_ocr_fusion_test_cases,
    get_kob_eng_proofreading_test_cases,
    get_kob_zho_hant_ocr_fusion_test_cases,
    get_kob_zho_hant_proofreading_test_cases,
)
from test.data.mlamd import (
    get_mlamd_eng_ocr_fusion_test_cases,
    get_mlamd_eng_proofreading_test_cases,
    get_mlamd_zho_hans_ocr_fusion_test_cases,
    get_mlamd_zho_hans_proofreading_test_cases,
    get_mlamd_zho_hant_ocr_fusion_test_cases,
    get_mlamd_zho_hant_proofreading_test_cases,
)
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.synchronization import process_zho_hans_eng
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_eng_proofreading_test_cases,
    get_t_zho_hans_ocr_fusion_test_cases,
    get_t_zho_hans_proofreading_test_cases,
    get_t_zho_hant_ocr_fusion_test_cases,
    get_t_zho_hant_proofreading_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "繁體中文 (OCR)",
    "简体中文 (OCR)",
    "English (OCR)",
    "Bilingual 简体中文 and English",
}
if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_kob_zho_hant_ocr_fusion_test_cases()
            + get_mlamd_zho_hant_ocr_fusion_test_cases()
            + get_t_zho_hant_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_zho_hant_proofreading_test_cases()
            + get_mlamd_zho_hant_proofreading_test_cases()
            + get_t_zho_hant_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )
if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_mlamd_zho_hans_ocr_fusion_test_cases()
            + get_t_zho_hans_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_mlamd_zho_hans_proofreading_test_cases()
            + get_t_zho_hans_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )
if "English (OCR)" in actions:
    process_eng_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_kob_eng_ocr_fusion_test_cases()
            + get_mlamd_eng_ocr_fusion_test_cases()
            + get_t_eng_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_eng_proofreading_test_cases()
            + get_mlamd_eng_proofreading_test_cases()
            + get_t_eng_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )
if "Bilingual 简体中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_proofread_flatten.srt",
        overwrite=True,
    )
