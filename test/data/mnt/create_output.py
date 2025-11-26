#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned
from scinoephile.core.english.proofreading import (
    EnglishProofreader,
    get_english_proofread,
)
from scinoephile.core.zhongwen import (
    get_zhongwen_cleaned,
    get_zhongwen_converted,
    get_zhongwen_flattened,
)
from scinoephile.core.zhongwen.proofreading import (
    ZhongwenProofreader,
    get_zhongwen_proofread,
)
from scinoephile.image.english.fusion import EnglishFuser, get_english_ocr_fused
from scinoephile.image.zhongwen.fusion import ZhongwenFuser, get_zhongwen_ocr_fused
from scinoephile.testing import test_data_root
from test.data.kob import (
    kob_english_fusion_test_cases,
    kob_english_proofreading_test_cases,
    kob_zhongwen_fusion_test_cases,
    kob_zhongwen_proofreading_test_cases,
)
from test.data.mlamd import (
    mlamd_english_fusion_test_cases,
    mlamd_english_proofreading_test_cases,
    mlamd_zhongwen_fusion_test_cases,
    mlamd_zhongwen_proofreading_test_cases,
)
from test.data.t import (
    t_english_fusion_test_cases,
    t_zhongwen_fusion_test_cases,
    t_zhongwen_proofreading_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"
set_logging_verbosity(2)
actions = {
    # "简体中文 (OCR)",
    "English (OCR)",
    # "繁體中文 (SRT)",
    # "Bilingual 简体中文 and English",
}

if "简体中文 (OCR)" in actions:
    zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
    zho_hans_paddle = get_zhongwen_cleaned(zho_hans_paddle, remove_empty=False)
    zho_hans_paddle = get_zhongwen_converted(zho_hans_paddle)
    zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
    zho_hans_lens = get_zhongwen_cleaned(zho_hans_lens, remove_empty=False)
    zho_hans_lens = get_zhongwen_converted(zho_hans_lens)
    zho_hans_fused = get_zhongwen_ocr_fused(
        zho_hans_paddle,
        zho_hans_lens,
        ZhongwenFuser(
            test_cases=kob_zhongwen_fusion_test_cases
            + mlamd_zhongwen_fusion_test_cases
            + t_zhongwen_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
            auto_verify=True,
        ),
    )
    zho_hans_fused.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = Series.load(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zhongwen_cleaned(zho_hans_fuse)
    zho_hans_fuse = get_zhongwen_converted(zho_hans_fuse)
    zho_hans_fuse_proofread = get_zhongwen_proofread(
        zho_hans_fuse,
        ZhongwenProofreader(
            test_cases=kob_zhongwen_proofreading_test_cases
            + mlamd_zhongwen_proofreading_test_cases
            + t_zhongwen_proofreading_test_cases,
            test_case_path=test_data_root
            / title
            / "core"
            / "zhongwen"
            / "proofreading.py",
            auto_verify=True,
        ),
    )
    zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")
    zho_hans_fuse_proofread_clean = get_zhongwen_cleaned(zho_hans_fuse_proofread)
    zho_hans_fuse_proofread_clean.save(
        output_dir / "zho-Hans" / "zho-Hans_fuse_proofread_clean.srt"
    )
    zho_hans_fuse_proofread_clean_flatten = get_zhongwen_flattened(
        zho_hans_fuse_proofread_clean
    )
    zho_hans_fuse_proofread_clean_flatten.save(
        output_dir / "zho-Hans" / "zho-Hans_fuse_proofread_clean_flatten.srt"
    )

if "English (OCR)" in actions:
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_english_cleaned(eng_tesseract, remove_empty=False)
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_english_cleaned(eng_lens, remove_empty=False)
    eng_fuse = get_english_ocr_fused(
        eng_tesseract,
        eng_lens,
        EnglishFuser(
            test_cases=kob_english_fusion_test_cases
            + mlamd_english_fusion_test_cases
            + t_english_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "english" / "fusion.py",
            auto_verify=True,
        ),
    )
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_fuse_proofread = get_english_proofread(
        eng_fuse,
        EnglishProofreader(
            test_cases=kob_english_proofreading_test_cases
            + mlamd_english_proofreading_test_cases,
            # + t_english_proofreading_test_cases,
            test_case_path=test_data_root
            / title
            / "core"
            / "english"
            / "proofreading.py",
            auto_verify=True,
        ),
    )
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")

if "繁體中文 (SRT)" in actions:
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_clean = get_zhongwen_cleaned(zho_hant)
    zho_hant_clean.save(output_dir / "zho-Hant_clean.srt")
    zho_hant_flatten = get_zhongwen_flattened(zho_hant)
    zho_hant_flatten.save(output_dir / "zho-Hant_flatten.srt")
    zho_hant_simplify = get_zhongwen_converted(zho_hant)
    zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")
    zho_hant_clean_flatten_simplify = get_zhongwen_converted(
        get_zhongwen_flattened(zho_hant_clean)
    )
    zho_hant_clean_flatten_simplify.save(
        output_dir / "zho-Hant_clean_flatten_simplify.srt"
    )

# if "Bilingual 简体中文 and English" in actions:
#     zho_hans_eng = get_synced_series(zho_hant_clean_flatten_simplify, eng_clean_flatten)
#     zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
