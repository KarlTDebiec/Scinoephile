#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.lang.eng import (
    get_eng_cleaned,
    get_eng_flattened,
    get_eng_ocr_fused,
    get_eng_proofread,
)
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fuser
from scinoephile.lang.eng.proofreading import get_eng_proofreader
from scinoephile.lang.zho import (
    get_zho_cleaned,
    get_zho_converted,
    get_zho_flattened,
    get_zho_ocr_fused,
    get_zho_proofread,
)
from scinoephile.lang.zho.ocr_fusion import get_zho_ocr_fuser
from scinoephile.lang.zho.proofreading import get_zho_proofreader
from scinoephile.multilang import get_synced_series
from scinoephile.testing import test_data_root
from test.data.kob import (
    get_kob_eng_ocr_fusion_test_cases,
    get_kob_eng_proofreading_test_cases,
    get_kob_zho_ocr_fusion_test_cases,
    get_kob_zho_proofreading_test_cases,
)
from test.data.mlamd import (
    get_mlamd_eng_ocr_fusion_test_cases,
    get_mlamd_eng_proofreading_test_cases,
    get_mlamd_zho_ocr_fusion_test_cases,
    get_mlamd_zho_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_eng_proofreading_test_cases,
    get_mnt_zho_ocr_fusion_test_cases,
    get_mnt_zho_proofreading_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "简体中文 (OCR)",
    "English (OCR)",
    "简体中文 (SRT)",
    "繁體中文 (SRT)",
    "English (SRT)",
    "Bilingual 简体中文 and English",
}

if "简体中文 (OCR)" in actions:
    zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
    zho_hans_lens = get_zho_cleaned(zho_hans_lens, remove_empty=False)
    zho_hans_lens = get_zho_converted(zho_hans_lens)
    zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
    zho_hans_paddle = get_zho_cleaned(zho_hans_paddle, remove_empty=False)
    zho_hans_paddle = get_zho_converted(zho_hans_paddle)
    zho_ocr_fuser = get_zho_ocr_fuser(
        test_cases=get_kob_zho_ocr_fusion_test_cases()
        + get_mlamd_zho_ocr_fusion_test_cases()
        + get_mnt_zho_ocr_fusion_test_cases(),
        test_case_path=title_root / "lang" / "zho" / "ocr_fusion.json",
        auto_verify=True,
    )
    zho_hans_fuse = get_zho_ocr_fused(zho_hans_lens, zho_hans_paddle, zho_ocr_fuser)
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zho_cleaned(zho_hans_fuse, remove_empty=False)
    zho_proofreader = get_zho_proofreader(
        test_cases=get_kob_zho_proofreading_test_cases()
        + get_mlamd_zho_proofreading_test_cases()
        + get_mnt_zho_proofreading_test_cases(),
        test_case_path=title_root / "lang" / "zho" / "proofreading.json",
        auto_verify=True,
    )
    zho_hans_fuse_proofread = get_zho_proofread(zho_hans_fuse, zho_proofreader)
    zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")

if "English (OCR)" in actions:
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_eng_cleaned(eng_lens, remove_empty=False)
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_eng_cleaned(eng_tesseract, remove_empty=False)
    eng_ocr_fuser = get_eng_ocr_fuser(
        test_cases=get_kob_eng_ocr_fusion_test_cases()
        + get_mlamd_eng_ocr_fusion_test_cases()
        + get_mnt_eng_ocr_fusion_test_cases(),
        test_case_path=title_root / "lang" / "eng" / "ocr_fusion.json",
        auto_verify=True,
    )
    eng_fuse = get_eng_ocr_fused(eng_lens, eng_tesseract, eng_ocr_fuser)
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_proofreader = get_eng_proofreader(
        test_cases=get_kob_eng_proofreading_test_cases()
        + get_mlamd_eng_proofreading_test_cases()
        + get_mnt_eng_proofreading_test_cases(),
        test_case_path=title_root / "lang" / "eng" / "proofreading.json",
        auto_verify=True,
    )
    eng_fuse_proofread = get_eng_proofread(eng_fuse, eng_proofreader)
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")

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
