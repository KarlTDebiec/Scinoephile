#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.multilang.synchronization import get_synced_series
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
)
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_eng_proofreading_test_cases,
    get_t_zho_hans_ocr_fusion_test_cases,
    get_t_zho_hans_proofreading_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "简体中文 (OCR)",
    "English (OCR)",
    "繁體中文 (SRT)",
    "Bilingual 简体中文 and English",
}

if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_kob_zho_hant_ocr_fusion_test_cases()
            + get_mlamd_zho_hans_ocr_fusion_test_cases()
            + get_t_zho_hans_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_zho_hant_proofreading_test_cases()
            + get_mlamd_zho_hans_proofreading_test_cases()
            + get_t_zho_hans_proofreading_test_cases()
        },
        validate=False,
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
        validate=False,
    )

if "繁體中文 (SRT)" in actions:
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_clean = get_zho_cleaned(zho_hant)
    zho_hant_clean.save(output_dir / "zho-Hant_clean.srt")
    zho_hant_clean_flatten = get_zho_flattened(zho_hant_clean)
    zho_hant_clean_flatten.save(output_dir / "zho-Hant_clean_flatten.srt")
    zho_hant_clean_flatten_simplify = get_zho_converted(zho_hant_clean_flatten)
    zho_hant_clean_flatten_simplify.save(
        output_dir / "zho-Hant_clean_flatten_simplify.srt"
    )

if "Bilingual 简体中文 and English" in actions:
    zho_hans_fuse_clean_validate_proofread_flatten = Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )
    del zho_hans_fuse_clean_validate_proofread_flatten.events[0]
    del zho_hans_fuse_clean_validate_proofread_flatten.events[-1]
    eng_fuse_clean_validate_proofread_flatten = Series.load(
        output_dir / "eng_fuse_clean_validate_proofread_flatten.srt"
    )
    eng_fuse_clean_validate_proofread_flatten.shift(s=-4.5)
    zho_hans_eng = get_synced_series(
        zho_hans_fuse_clean_validate_proofread_flatten,
        eng_fuse_clean_validate_proofread_flatten,
    )
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
