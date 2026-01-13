#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened
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
    get_mlamd_zho_hant_ocr_fusion_test_cases,
    get_mlamd_zho_hant_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_eng_proofreading_test_cases,
)
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "繁體中文 (OCR)",
    "简体中文 (OCR)",
    "English (OCR)",
    # "简体中文 (SRT)",
    # "繁體中文 (SRT)",
    # "English (SRT)",
    # "Bilingual 简体中文 and English",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_kob_zho_hant_ocr_fusion_test_cases()
            + get_mlamd_zho_hant_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_zho_hant_proofreading_test_cases()
            + get_mlamd_zho_hant_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )

if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        title_root / "input" / "zho-Hans.sup",
        fuser_kw={
            "test_cases": get_kob_zho_hant_ocr_fusion_test_cases()
            + get_mlamd_zho_hant_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_zho_hant_proofreading_test_cases()
            + get_mlamd_zho_hant_proofreading_test_cases()
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
            + get_mnt_eng_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_kob_eng_proofreading_test_cases()
            + get_mlamd_eng_proofreading_test_cases()
            + get_mnt_eng_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )

if "简体中文 (SRT)" in actions:
    zho_hans = Series.load(input_dir / "zho-Hans.srt")
    zho_hans_clean = get_zho_cleaned(zho_hans)
    zho_hans_clean.save(output_dir / "zho-Hans_clean.srt")
    zho_hans_clean_flatten = get_zho_flattened(zho_hans_clean)
    zho_hans_clean_flatten.save(output_dir / "zho-Hans_clean_flatten.srt")

if "繁體中文 (SRT)" in actions:
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_simplify = get_zho_converted(zho_hant)
    zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")

if "English (SRT)" in actions:
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_eng_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_clean_flatten = get_eng_flattened(eng_clean)
    eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

if "Bilingual 简体中文 and English" in actions:
    zho_hans_clean_flatten = Series.load(output_dir / "zho-Hans_clean_flatten.srt")
    eng_clean_flatten = Series.load(output_dir / "eng_clean_flatten.srt")
    zho_hans_eng = get_synced_series(zho_hans_clean_flatten, eng_clean_flatten)
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
