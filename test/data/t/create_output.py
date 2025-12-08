#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path
from pprint import pprint

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.english.proofreading import (
    EnglishProofreader2,
    get_english_proofread2,
)
from scinoephile.core.llms import load_test_cases_from_json, save_test_cases_to_json
from scinoephile.core.synchronization import get_synced_series
from scinoephile.core.zhongwen import (
    get_zhongwen_cleaned,
    get_zhongwen_converted,
    get_zhongwen_flattened,
)
from scinoephile.core.zhongwen.proofreading import (
    ZhongwenProofreader,
    ZhongwenProofreadingTestCase2,
    get_zhongwen_proofread,
    migrate_zhongwen_proofreading_v1_to_v2,
)
from scinoephile.image.english.fusion import EnglishFuser, get_english_ocr_fused
from scinoephile.image.zhongwen.fusion import ZhongwenFuser, get_zhongwen_ocr_fused
from scinoephile.testing import test_data_root
from test.data.kob import (
    get_kob_english_proofreading_test_cases,
    kob_english_fusion_test_cases,
    kob_zhongwen_fusion_test_cases,
    kob_zhongwen_proofreading_test_cases,
)
from test.data.mlamd import (
    get_mlamd_english_proofreading_test_cases,
    mlamd_english_fusion_test_cases,
    mlamd_zhongwen_fusion_test_cases,
    mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_english_proofreading_test_cases,
    mnt_english_fusion_test_cases,
    mnt_zhongwen_fusion_test_cases,
    mnt_zhongwen_proofreading_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"
set_logging_verbosity(2)

# Load English proofreading test cases and migrate to v2, then write to JSON
# from test.data.t import t_english_proofreading_test_cases as test_cases
#
# test_cases_2 = migrate_english_proofreading_v1_to_v2(test_cases)
# pprint(test_cases_2[0:10])
# output_path = test_data_root / title / "core" / "english" / "proofreading.json"
# save_test_cases_to_json(output_path, test_cases_2)
# test_cases_2 = load_test_cases_from_json(output_path, EnglishProofreadingTestCase2)
# pprint(test_cases_2[0:10])
# from test.data.t.core.english import get_proofreading_test_cases
#
# test_cases_2 = get_proofreading_test_cases()
# pprint(test_cases_2[0:10])

# Load Zhongwen proofreading test cases and migrate to v2, then write to JSON
from test.data.t import t_zhongwen_proofreading_test_cases as test_cases

test_cases_2 = migrate_zhongwen_proofreading_v1_to_v2(test_cases)
pprint(test_cases_2[0:10])
output_path = test_data_root / title / "core" / "zhongwen" / "proofreading.json"
save_test_cases_to_json(output_path, test_cases_2)
test_cases_2 = load_test_cases_from_json(output_path, ZhongwenProofreadingTestCase2)
pprint(test_cases_2[0:10])
# from test.data.t.core.zhongwen import get_proofreading_test_cases

# test_cases_2 = get_proofreading_test_cases()
# pprint(test_cases_2[0:10])

actions = {
    # "简体中文 (OCR)",
    "English (OCR)",
    # "简体中文 (SRT)",
    # "繁體中文 (SRT)",
    # "English (SRT)",
    # "Bilingual 简体中文 and English",
}

if "简体中文 (OCR)" in actions:
    zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
    zho_hans_lens = get_zhongwen_cleaned(zho_hans_lens, remove_empty=False)
    zho_hans_lens = get_zhongwen_converted(zho_hans_lens)
    zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
    zho_hans_paddle = get_zhongwen_cleaned(zho_hans_paddle, remove_empty=False)
    zho_hans_paddle = get_zhongwen_converted(zho_hans_paddle)
    zho_hans_fuse = get_zhongwen_ocr_fused(
        zho_hans_lens,
        zho_hans_paddle,
        ZhongwenFuser(
            test_cases=kob_zhongwen_fusion_test_cases
            + mlamd_zhongwen_fusion_test_cases
            + mnt_zhongwen_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
            auto_verify=True,
        ),
    )
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zhongwen_cleaned(zho_hans_fuse, remove_empty=False)
    zho_hans_fuse_proofread = get_zhongwen_proofread(
        zho_hans_fuse,
        ZhongwenProofreader(
            test_cases=kob_zhongwen_proofreading_test_cases
            + mlamd_zhongwen_proofreading_test_cases
            + mnt_zhongwen_proofreading_test_cases,
            test_case_path=test_data_root
            / title
            / "core"
            / "zhongwen"
            / "proofreading.py",
            auto_verify=True,
        ),
    )
    zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")

if "English (OCR)" in actions:
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_english_cleaned(eng_lens, remove_empty=False)
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_english_cleaned(eng_tesseract, remove_empty=False)
    eng_fuse = get_english_ocr_fused(
        eng_lens,
        eng_tesseract,
        EnglishFuser(
            test_cases=kob_english_fusion_test_cases
            + mlamd_english_fusion_test_cases
            + mnt_english_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "english" / "fusion.py",
            auto_verify=True,
        ),
    )
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_fuse_proofread = get_english_proofread2(
        eng_fuse,
        EnglishProofreader2(
            test_cases=get_kob_english_proofreading_test_cases()
            + get_mlamd_english_proofreading_test_cases()
            + get_mnt_english_proofreading_test_cases(),
            test_case_path=test_data_root
            / title
            / "core"
            / "english"
            / "proofreading.json",
            auto_verify=True,
        ),
    )
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")

if "简体中文 (SRT)" in actions:
    zho_hans = Series.load(input_dir / "zho-Hans.srt")
    zho_hans_clean = get_zhongwen_cleaned(zho_hans)
    zho_hans_clean.save(output_dir / "zho-Hans_clean.srt")
    zho_hans_clean_flatten = get_zhongwen_flattened(zho_hans_clean)
    zho_hans_clean_flatten.save(output_dir / "zho-Hans_clean_flatten.srt")

if "繁體中文 (SRT)" in actions:
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_simplify = get_zhongwen_converted(zho_hant)
    zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")

if "English (SRT)" in actions:
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

if "Bilingual 简体中文 and English" in actions:
    zho_hans_clean_flatten = Series.load(output_dir / "zho-Hans_clean_flatten.srt")
    eng_clean_flatten = Series.load(output_dir / "eng_clean_flatten.srt")
    zho_hans_eng = get_synced_series(zho_hans_clean_flatten, eng_clean_flatten)
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
