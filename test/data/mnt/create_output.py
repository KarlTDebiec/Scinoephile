#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.eng import get_eng_cleaned, get_eng_flattened
from scinoephile.core.eng.proofreading import get_eng_proofread, get_eng_proofreader
from scinoephile.core.synchronization import get_synced_series
from scinoephile.core.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.core.zho.proofreading import get_zho_proofread, get_zho_proofreader
from scinoephile.image.eng.fusion import get_eng_fused, get_eng_fuser
from scinoephile.image.zho.fusion import get_zho_fused, get_zho_fuser
from scinoephile.testing import test_data_root
from test.data.kob import (
    get_kob_eng_fusion_test_cases,
    get_kob_eng_proofreading_test_cases,
    get_kob_zho_fusion_test_cases,
    get_kob_zho_proofreading_test_cases,
)
from test.data.mlamd import (
    get_mlamd_eng_fusion_test_cases,
    get_mlamd_eng_proofreading_test_cases,
    get_mlamd_zho_fusion_test_cases,
    get_mlamd_zho_proofreading_test_cases,
)
from test.data.t import (
    get_t_eng_fusion_test_cases,
    get_t_eng_proofreading_test_cases,
    get_t_zho_fusion_test_cases,
    get_t_zho_proofreading_test_cases,
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
    zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
    zho_hans_lens = get_zho_cleaned(zho_hans_lens, remove_empty=False)
    zho_hans_lens = get_zho_converted(zho_hans_lens)
    zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
    zho_hans_paddle = get_zho_cleaned(zho_hans_paddle, remove_empty=False)
    zho_hans_paddle = get_zho_converted(zho_hans_paddle)
    zho_fuser = get_zho_fuser(
        test_cases=get_kob_zho_fusion_test_cases()
        + get_mlamd_zho_fusion_test_cases()
        + get_t_zho_fusion_test_cases(),
        test_case_path=title_root / "image" / "zho" / "fusion.json",
        auto_verify=True,
    )
    zho_hans_fuse = get_zho_fused(zho_hans_lens, zho_hans_paddle, zho_fuser)
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zho_cleaned(zho_hans_fuse)
    zho_hans_fuse = get_zho_converted(zho_hans_fuse)
    zho_proofreader = get_zho_proofreader(
        test_cases=get_kob_zho_proofreading_test_cases()
        + get_mlamd_zho_proofreading_test_cases()
        + get_t_zho_proofreading_test_cases(),
        test_case_path=title_root / "core" / "zho" / "proofreading.json",
        auto_verify=True,
    )
    zho_hans_fuse_proofread = get_zho_proofread(zho_hans_fuse, zho_proofreader)
    zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")
    zho_hans_fuse_proofread_clean = get_zho_cleaned(zho_hans_fuse_proofread)
    zho_hans_fuse_proofread_clean.save(output_dir / "zho-Hans_fuse_proofread_clean.srt")
    zho_hans_fuse_proofread_clean_flatten = get_zho_flattened(
        zho_hans_fuse_proofread_clean
    )
    zho_hans_fuse_proofread_clean_flatten.save(
        output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt"
    )

if "English (OCR)" in actions:
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_eng_cleaned(eng_lens, remove_empty=False)
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_eng_cleaned(eng_tesseract, remove_empty=False)
    eng_fuser = get_eng_fuser(
        test_cases=get_kob_eng_fusion_test_cases()
        + get_mlamd_eng_fusion_test_cases()
        + get_t_eng_fusion_test_cases(),
        test_case_path=title_root / "image" / "eng" / "fusion.json",
        auto_verify=True,
    )
    eng_fuse = get_eng_fused(eng_lens, eng_tesseract, eng_fuser)
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_proofreader = get_eng_proofreader(
        test_cases=get_kob_eng_proofreading_test_cases()
        + get_mlamd_eng_proofreading_test_cases()
        + get_t_eng_proofreading_test_cases(),
        test_case_path=title_root / "core" / "eng" / "proofreading.json",
        auto_verify=True,
    )
    eng_fuse_proofread = get_eng_proofread(eng_fuse, eng_proofreader)
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")
    eng_fuse_proofread_clean = get_eng_cleaned(eng_fuse_proofread)
    eng_fuse_proofread_clean.save(output_dir / "eng_fuse_proofread_clean.srt")
    eng_fuse_proofread_clean_flatten = get_eng_flattened(eng_fuse_proofread_clean)
    eng_fuse_proofread_clean_flatten.save(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
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
    zho_hans_fuse_proofread_clean_flatten = Series.load(
        output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt"
    )
    del zho_hans_fuse_proofread_clean_flatten.events[0]
    del zho_hans_fuse_proofread_clean_flatten.events[-1]
    eng_fuse_proofread_clean_flatten = Series.load(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
    )
    eng_fuse_proofread_clean_flatten.shift(s=-4.5)
    zho_hans_eng = get_synced_series(
        zho_hans_fuse_proofread_clean_flatten, eng_fuse_proofread_clean_flatten
    )
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
