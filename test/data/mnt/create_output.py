#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.zhongwen import (
    get_zhongwen_cleaned,
    get_zhongwen_converted,
)
from scinoephile.image.zhongwen.fusion import ZhongwenFuser, get_zhongwen_ocr_fused
from scinoephile.testing import test_data_root
from test.data.kob import kob_zhongwen_fusion_test_cases
from test.data.mlamd import mlamd_zhongwen_fusion_test_cases
from test.data.t import t_zhongwen_fusion_test_cases

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
        + t_zhongwen_fusion_test_cases,
        test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
        auto_verify=True,
    ),
    stop_at_idx=100,
)
zho_hant_fused.save(output_dir / "zho-Hans_fuse.srt")

# 繁體中文
# zho_hant = Series.load(input_dir / "zho-Hant.srt")
# zho_hant_clean = get_zhongwen_cleaned(zho_hant)
# zho_hant_clean.save(output_dir / "zho-Hant_clean.srt")
# zho_hant_flatten = get_zhongwen_flattened(zho_hant)
# zho_hant_flatten.save(output_dir / "zho-Hant_flatten.srt")
# zho_hant_simplify = get_zhongwen_converted(zho_hant)
# zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")
# zho_hant_clean_flatten_simplify = get_zhongwen_converted(
#     get_zhongwen_flattened(zho_hant_clean)
# )
# zho_hant_clean_flatten_simplify.save(
#     output_dir / "zho-Hant_clean_flatten_simplify.srt"
# )

# English
# eng = Series.load(input_dir / "eng.srt")
# eng_clean = get_english_cleaned(eng)
# eng_clean.save(output_dir / "eng_clean.srt")
# eng_flatten = get_english_flattened(eng)
# eng_flatten.save(output_dir / "eng_flatten.srt")
# eng_clean_flatten = get_english_flattened(eng_clean)
# eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

# Bilingual 简体中文 and English
# zho_hans_eng = get_synced_series(zho_hant_clean_flatten_simplify, eng_clean_flatten)
# zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
