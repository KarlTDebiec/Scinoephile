#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.lang.eng.fusion import get_eng_fused, get_eng_fuser
from scinoephile.lang.zho.fusion import (
    ZhoHantOcrFusionPrompt,
    get_zho_fused,
    get_zho_fuser,
)

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.synchronization import get_synced_series
from scinoephile.lang.eng import (
    get_eng_cleaned,
    get_eng_flattened,
    get_eng_proofread,
    get_eng_proofreader,
)
from scinoephile.lang.zho import (
    OpenCCConfig,
    ZhoHantProofreadingPrompt,
    get_zho_cleaned,
    get_zho_converted,
    get_zho_flattened,
    get_zho_proofread,
    get_zho_proofreader,
)
from scinoephile.testing import test_data_root
from test.data.mlamd import (
    get_mlamd_eng_fusion_test_cases,
    get_mlamd_eng_proofreading_test_cases,
    get_mlamd_zho_fusion_test_cases,
    get_mlamd_zho_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_fusion_test_cases,
    get_mnt_eng_proofreading_test_cases,
    get_mnt_zho_fusion_test_cases,
    get_mnt_zho_proofreading_test_cases,
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
    "繁體中文 (OCR)",
    "English (OCR)",
    "简体粵文 (SRT)",
    "繁體粵文 (SRT)",
    "English (SRT)",
    "Bilingual 简体粵文 and English",
}

if "繁體中文 (OCR)" in actions:
    zho_hant_lens = Series.load(input_dir / "zho-Hant_lens.srt")
    zho_hant_lens = get_zho_cleaned(zho_hant_lens, remove_empty=False)
    zho_hant_lens = get_zho_converted(zho_hant_lens, config=OpenCCConfig.s2t)
    zho_hant_paddle = Series.load(input_dir / "zho-Hant_paddle.srt")
    zho_hant_paddle = get_zho_cleaned(zho_hant_paddle, remove_empty=False)
    zho_hant_paddle = get_zho_converted(zho_hant_paddle, config=OpenCCConfig.s2t)
    zho_fuser = get_zho_fuser(
        prompt_cls=ZhoHantOcrFusionPrompt,
        test_cases=get_mlamd_zho_fusion_test_cases()
        + get_mnt_zho_fusion_test_cases()
        + get_t_zho_fusion_test_cases(),
        test_case_path=title_root / "image" / "zho" / "fusion.json",
        auto_verify=True,
    )
    zho_hant_fuse = get_zho_fused(zho_hant_lens, zho_hant_paddle, zho_fuser)
    zho_hant_fuse.save(output_dir / "zho-Hant_fuse.srt")
    zho_hant_fuse = get_zho_cleaned(zho_hant_fuse)
    zho_hant_fuse = get_zho_converted(zho_hant_fuse, config=OpenCCConfig.s2t)
    zho_proofreader = get_zho_proofreader(
        prompt_cls=ZhoHantProofreadingPrompt,
        test_cases=get_mlamd_zho_proofreading_test_cases()
        + get_mnt_zho_proofreading_test_cases()
        + get_t_zho_proofreading_test_cases(),
        test_case_path=title_root / "core" / "zho" / "proofreading.json",
        auto_verify=True,
    )
    zho_hant_fuse_proofread = get_zho_proofread(zho_hant_fuse, zho_proofreader)
    zho_hant_fuse_proofread.save(output_dir / "zho-Hant_fuse_proofread.srt")

if "English (OCR)" in actions:
    eng_lens = Series.load(input_dir / "eng_lens.srt")
    eng_lens = get_eng_cleaned(eng_lens, remove_empty=False)
    eng_tesseract = Series.load(input_dir / "eng_tesseract.srt")
    eng_tesseract = get_eng_cleaned(eng_tesseract, remove_empty=False)
    eng_fuser = get_eng_fuser(
        test_cases=get_mlamd_eng_fusion_test_cases()
        + get_mnt_eng_fusion_test_cases()
        + get_t_eng_fusion_test_cases(),
        test_case_path=title_root / "image" / "eng" / "fusion.json",
        auto_verify=True,
    )
    eng_fuse = get_eng_fused(eng_lens, eng_tesseract, eng_fuser)
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_proofreader = get_eng_proofreader(
        test_cases=get_mlamd_eng_proofreading_test_cases()
        + get_mnt_eng_proofreading_test_cases()
        + get_t_eng_proofreading_test_cases(),
        test_case_path=title_root / "core" / "eng" / "proofreading.json",
        auto_verify=True,
    )
    eng_fuse_proofread = get_eng_proofread(eng_fuse, eng_proofreader)
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")

if "简体粵文 (SRT)" in actions:
    yue_hans = Series.load(input_dir / "yue-Hans.srt")
    yue_hans_clean = get_zho_cleaned(yue_hans)
    yue_hans_clean.save(output_dir / "yue-Hans_clean.srt")
    yue_hans_clean_flatten = get_zho_flattened(yue_hans_clean)
    yue_hans_clean_flatten.save(output_dir / "yue-Hans_clean_flatten.srt")

if "繁體粵文 (SRT)" in actions:
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_simplify = get_zho_converted(yue_hant, OpenCCConfig.hk2s)
    yue_hant_simplify.save(output_dir / "yue-Hant_simplify.srt")

if "English (SRT)" in actions:
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_eng_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_clean_flatten = get_eng_flattened(eng_clean)
    eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

if "Bilingual 简体粵文 and English" in actions:
    yue_hans_clean_flatten = Series.load(output_dir / "yue-Hans_clean_flatten.srt")
    eng_clean_flatten = Series.load(output_dir / "eng_clean_flatten.srt")
    yue_hans_eng = get_synced_series(yue_hans_clean_flatten, eng_clean_flatten)
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
