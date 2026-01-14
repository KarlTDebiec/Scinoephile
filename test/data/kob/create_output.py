#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

import asyncio
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho import get_yue_vs_zho_proofread
from scinoephile.multilang.yue_zho.proofreading import get_yue_vs_zho_proofreader
from scinoephile.multilang.yue_zho.transcription import YueTranscriber
from test.data.mlamd import (
    get_mlamd_eng_ocr_fusion_test_cases,
    get_mlamd_eng_proofreading_test_cases,
    get_mlamd_yue_merging_test_cases,
    get_mlamd_yue_shifting_test_cases,
    get_mlamd_zho_hant_ocr_fusion_test_cases,
    get_mlamd_zho_hant_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_eng_proofreading_test_cases,
    get_mnt_zho_hant_ocr_fusion_test_cases,
    get_mnt_zho_hant_proofreading_test_cases,
)
from test.data.ocr import process_eng_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_eng_proofreading_test_cases,
    get_t_zho_hant_ocr_fusion_test_cases,
    get_t_zho_hant_proofreading_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "繁體中文 (OCR)",
    "English (OCR)",
    "Bilingual 简体中文 and English",
    "繁體粵文 (SRT)",
    # "Bilingual 简体粵文 and English",
    # "简体粤文 (Transcription)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        fuser_kw={
            "test_cases": get_mlamd_zho_hant_ocr_fusion_test_cases()
            + get_mnt_zho_hant_ocr_fusion_test_cases()
            + get_t_zho_hant_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_mlamd_zho_hant_proofreading_test_cases()
            + get_mnt_zho_hant_proofreading_test_cases()
            + get_t_zho_hant_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )
if "English (OCR)" in actions:
    process_eng_ocr(
        title_root,
        title_root / "input" / "zho-Hant.sup",
        fuser_kw={
            "test_cases": get_mlamd_eng_ocr_fusion_test_cases()
            + get_mnt_eng_ocr_fusion_test_cases()
            + get_t_eng_ocr_fusion_test_cases()
        },
        proofreader_kw={
            "test_cases": get_mlamd_eng_proofreading_test_cases()
            + get_mnt_eng_proofreading_test_cases()
            + get_t_eng_proofreading_test_cases()
        },
        overwrite_srt=True,
        force_validation=True,
    )
if "Bilingual 简体中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_proofread_flatten.srt",
        overwrite=True,
    )
if "繁體粵文 (SRT)" in actions:
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    clean = get_zho_cleaned(yue_hant)
    clean.save(output_dir / "yue-Hant_clean.srt")
    flatten = get_zho_flattened(clean)
    flatten.save(output_dir / "yue-Hant_clean_flatten.srt")
    simplify = get_zho_converted(flatten, OpenCCConfig.hk2s)
    simplify.save(output_dir / "yue-Hant_clean_flatten_simplify.srt")
if "Bilingual 简体粵文 and English" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=output_dir / "yue-Hant_clean_flatten_simplify.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_proofread_flatten.srt",
        overwrite=True,
    )
if "简体粤文 (Transcription)" in actions:
    zho_hans = Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")
    yue_hans = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = YueTranscriber(
        test_case_directory_path=test_data_root / "kob",
        shifting_test_cases=get_mlamd_yue_shifting_test_cases(),
        merging_test_cases=get_mlamd_yue_merging_test_cases(),
    )
    yue_hans = asyncio.run(transcriber.process_all_blocks(yue_hans, zho_hans))
    outfile_path = output_dir / "yue-Hans_transcribed.srt"
    yue_hans.save(outfile_path)

    yue_hans = Series.load(outfile_path)
    proofreader = get_yue_vs_zho_proofreader(
        default_test_cases=[],
        test_case_path=title_root / "multilang" / "yue_zho" / "proofreading.json",
        auto_verify=True,
    )
    yue_hans_proofread = get_yue_vs_zho_proofread(
        yue_hans, zho_hans, processor=proofreader
    )
    outfile_path = output_dir / "yue-Hans_transcribed_proofread.srt"
    yue_hans_proofread.save(outfile_path)
