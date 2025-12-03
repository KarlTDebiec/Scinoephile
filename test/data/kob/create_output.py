#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.english.proofreading import (
    EnglishProofreader,
    get_english_proofread,
)
from scinoephile.core.synchronization import get_synced_series
from scinoephile.core.zhongwen import (
    OpenCCConfig,
    get_zhongwen_cleaned,
    get_zhongwen_converted,
    get_zhongwen_flattened,
)
from scinoephile.core.zhongwen.proofreading import (
    ZhongwenProofreader,
    ZhongwenProofreadingTraditionalLLMText,
    get_zhongwen_proofread,
)
from scinoephile.image.english.fusion import EnglishFuser, get_english_ocr_fused
from scinoephile.image.zhongwen.fusion import ZhongwenFuser, get_zhongwen_ocr_fused
from scinoephile.testing import test_data_root
from test.data.mlamd import (
    mlamd_english_fusion_test_cases,
    mlamd_english_proofreading_test_cases,
    mlamd_zhongwen_fusion_test_cases,
    mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mnt import (
    mnt_english_fusion_test_cases,
    mnt_english_proofreading_test_cases,
    mnt_zhongwen_fusion_test_cases,
    mnt_zhongwen_proofreading_test_cases,
)
from test.data.t import (
    t_english_fusion_test_cases,
    t_english_proofreading_test_cases,
    t_zhongwen_fusion_test_cases,
    t_zhongwen_proofreading_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"
set_logging_verbosity(2)

actions = {
    "繁體中文 (OCR)",
    "English (OCR)",
    "简体粵文 (SRT)",
    "繁體粵文 (SRT)",
    "English (SRT)",
    "Bilingual 简体粵文 and English",
}

if "繁體中文 (OCR)" in actions:
    zho_hant_lens = Series.load(input_dir / "zho-Hant_lens.srt")
    zho_hant_lens = get_zhongwen_cleaned(zho_hant_lens, remove_empty=False)
    zho_hant_lens = get_zhongwen_converted(zho_hant_lens, config=OpenCCConfig.s2t)
    zho_hant_paddle = Series.load(input_dir / "zho-Hant_paddle.srt")
    zho_hant_paddle = get_zhongwen_cleaned(zho_hant_paddle, remove_empty=False)
    zho_hant_paddle = get_zhongwen_converted(zho_hant_paddle, config=OpenCCConfig.s2t)
    zho_hant_fuse = get_zhongwen_ocr_fused(
        zho_hant_lens,
        zho_hant_paddle,
        ZhongwenFuser(
            test_cases=mlamd_zhongwen_fusion_test_cases
            + mnt_zhongwen_fusion_test_cases
            + t_zhongwen_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
            auto_verify=True,
        ),
    )
    zho_hant_fuse.save(output_dir / "zho-Hant_fuse.srt")
    zho_hant_fuse = get_zhongwen_cleaned(zho_hant_fuse)
    zho_hant_fuse = get_zhongwen_converted(zho_hant_fuse, config=OpenCCConfig.s2t)
    zho_hant_fuse_proofread = get_zhongwen_proofread(
        zho_hant_fuse,
        ZhongwenProofreader(
            test_cases=mlamd_zhongwen_proofreading_test_cases
            + mnt_zhongwen_proofreading_test_cases
            + t_zhongwen_proofreading_test_cases,
            test_case_path=test_data_root
            / title
            / "core"
            / "zhongwen"
            / "proofreading.py",
            auto_verify=True,
            text=ZhongwenProofreadingTraditionalLLMText,
        ),
    )
    zho_hant_fuse_proofread.save(output_dir / "zho-Hant_fuse_proofread.srt")

if "English (OCR)" in actions:
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_english_cleaned(eng_lens, remove_empty=False)
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_english_cleaned(eng_tesseract, remove_empty=False)
    eng_fuse = get_english_ocr_fused(
        eng_lens,
        eng_tesseract,
        EnglishFuser(
            test_cases=mlamd_english_fusion_test_cases
            + mnt_english_fusion_test_cases
            + t_english_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "english" / "fusion.py",
            auto_verify=True,
        ),
    )
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_fuse_proofread = get_english_proofread(
        eng_fuse,
        EnglishProofreader(
            test_cases=mlamd_english_proofreading_test_cases
            + mnt_english_proofreading_test_cases
            + t_english_proofreading_test_cases,
            test_case_path=test_data_root
            / title
            / "core"
            / "english"
            / "proofreading.py",
            auto_verify=True,
        ),
    )
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")

if "简体粵文 (SRT)" in actions:
    yue_hans = Series.load(input_dir / "yue-Hans.srt")
    yue_hans_clean = get_zhongwen_cleaned(yue_hans)
    yue_hans_clean.save(output_dir / "yue-Hans_clean.srt")
    yue_hans_clean_flatten = get_zhongwen_flattened(yue_hans_clean)
    yue_hans_clean_flatten.save(output_dir / "yue-Hans_clean_flatten.srt")

if "繁體粵文 (SRT)" in actions:
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_simplify = get_zhongwen_converted(yue_hant, OpenCCConfig.hk2s)
    yue_hant_simplify.save(output_dir / "yue-Hant_simplify.srt")

if "English (SRT)" in actions:
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

if "Bilingual 简体粵文 and English" in actions:
    yue_hans_clean_flatten = Series.load(output_dir / "yue-Hans_clean_flatten.srt")
    eng_clean_flatten = Series.load(output_dir / "eng_clean_flatten.srt")
    yue_hans_eng = get_synced_series(yue_hans_clean_flatten, eng_clean_flatten)
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
