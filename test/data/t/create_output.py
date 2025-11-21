#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.zhongwen import (
    get_zhongwen_cleaned,
    get_zhongwen_converted,
)
from scinoephile.core.zhongwen.proofreading import (
    ZhongwenProofreader,
    get_zhongwen_proofread,
)
from scinoephile.image.zhongwen.fusion import ZhongwenFuser, get_zhongwen_ocr_fused
from scinoephile.testing import test_data_root
from test.data.kob import (
    kob_zhongwen_fusion_test_cases,
    kob_zhongwen_proofreading_test_cases,
)
from test.data.mlamd import (
    mlamd_zhongwen_fusion_test_cases,
    mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mnt import (
    mnt_zhongwen_fusion_test_cases,
    mnt_zhongwen_proofreading_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"
set_logging_verbosity(2)

# 简体中文
zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
zho_hans_paddle = get_zhongwen_cleaned(zho_hans_paddle, remove_empty=False)
zho_hans_paddle = get_zhongwen_converted(zho_hans_paddle)
zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
zho_hans_lens = get_zhongwen_cleaned(zho_hans_lens, remove_empty=False)
zho_hans_lens = get_zhongwen_converted(zho_hans_lens)
zho_hant_fused = get_zhongwen_ocr_fused(
    zho_hans_paddle,
    zho_hans_lens,
    ZhongwenFuser(
        test_cases=kob_zhongwen_fusion_test_cases
        + mlamd_zhongwen_fusion_test_cases
        + mnt_zhongwen_fusion_test_cases,
        test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
        auto_verify=True,
    ),
)
zho_hant_fused.save(output_dir / "zho-Hans_fuse.srt")
zho_hans_fuse = Series.load(output_dir / "zho-Hans_fuse.srt")
zho_hans_fuse = get_zhongwen_cleaned(zho_hans_fuse)
zho_hans_fuse = get_zhongwen_converted(zho_hans_fuse)
zho_hans_fused_proofread = get_zhongwen_proofread(
    zho_hans_fuse,
    ZhongwenProofreader(
        test_cases=kob_zhongwen_proofreading_test_cases
        + mlamd_zhongwen_proofreading_test_cases
        + mnt_zhongwen_proofreading_test_cases,
        test_case_path=test_data_root / title / "core" / "zhongwen" / "proofreading.py",
        auto_verify=True,
    ),
)
zho_hans_fused_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")
# zho_hans = Series.load(input_dir / "zho-Hans.srt")
# zho_hans_clean = get_zhongwen_cleaned(zho_hans)
# zho_hans_clean.save(output_dir / "zho-Hans_clean.srt")
# zho_hans_flatten = get_zhongwen_flattened(zho_hans)
# zho_hans_flatten.save(output_dir / "zho-Hans_flatten.srt")
# zho_hans_clean_flatten = get_zhongwen_flattened(zho_hans_clean)
# zho_hans_clean_flatten.save(output_dir / "zho-Hans_clean_flatten.srt")

# 繁體中文
# zho_hant = Series.load(input_dir / "zho-Hant.srt")
# zho_hant_simplify = get_zhongwen_converted(zho_hant)
# zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")

# English
# eng = Series.load(input_dir / "eng.srt")
# eng_clean = get_english_cleaned(eng)
# eng_clean.save(output_dir / "eng_clean.srt")
# eng_flatten = get_english_flattened(eng)
# eng_flatten.save(output_dir / "eng_flatten.srt")
# proofer = EnglishProofer(
#     test_case_path=test_data_root / "t" / "core" / "english" / "proof.py",
# )
# eng_proof = get_english_proofed(eng, proofer)
# eng_proof.save(output_dir / "eng_proof.srt")
# eng_proof_clean = get_english_cleaned(eng_proof)
# eng_proof_clean_flatten = get_english_flattened(eng_proof_clean)
# eng_proof_clean_flatten.save(output_dir / "eng_proof_clean_flatten.srt")

# Bilingual 简体中文 and English
# zho_hans_eng = get_synced_series(zho_hans_flatten, eng_proof_clean_flatten)
# zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
