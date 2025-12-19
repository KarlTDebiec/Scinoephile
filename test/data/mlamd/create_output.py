#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

import asyncio
from logging import info
from pathlib import Path

from scinoephile.audio import AudioSeries
from scinoephile.audio.cantonese import CantoneseTranscriptionReviewer
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
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
from scinoephile.multilang.yue_zho import (
    get_yue_from_zho_translated,
    get_yue_vs_zho_proofread,
    get_yue_vs_zho_reviewed,
)
from scinoephile.multilang.yue_zho.proofreading import get_yue_vs_zho_proofreader
from scinoephile.multilang.yue_zho.review import get_yue_vs_zho_processor
from scinoephile.multilang.yue_zho.translation import get_yue_from_zho_translator
from scinoephile.testing import test_data_root
from test.data.kob import (
    get_kob_eng_ocr_fusion_test_cases,
    get_kob_eng_proofreading_test_cases,
    get_kob_zho_ocr_fusion_test_cases,
    get_kob_zho_proofreading_test_cases,
)
from test.data.mlamd import (
    get_mlamd_yue_merging_test_cases,
    get_mlamd_yue_shifting_test_cases,
    get_mlamd_yue_vs_zho_proofreading_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_eng_proofreading_test_cases,
    get_mnt_zho_ocr_fusion_test_cases,
    get_mnt_zho_proofreading_test_cases,
)
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_eng_proofreading_test_cases,
    get_t_zho_ocr_fusion_test_cases,
    get_t_zho_proofreading_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "简体中文 (OCR)",
    "English (OCR)",
    "简体粤文 (Transcription)",
    "Bilingual 简体中文 and English",
    "Bilingual 简体粤文 and English",
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
        + get_mnt_zho_ocr_fusion_test_cases()
        + get_t_zho_ocr_fusion_test_cases(),
        test_case_path=title_root / "lang" / "zho" / "ocr_fusion.json",
        auto_verify=True,
    )
    zho_hans_fuse = get_zho_ocr_fused(zho_hans_lens, zho_hans_paddle, zho_ocr_fuser)
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zho_cleaned(zho_hans_fuse)
    zho_hans_fuse = get_zho_converted(zho_hans_fuse)
    zho_proofreader = get_zho_proofreader(
        test_cases=get_kob_zho_proofreading_test_cases()
        + get_mnt_zho_proofreading_test_cases()
        + get_t_zho_proofreading_test_cases(),
        test_case_path=title_root / "lang" / "zho" / "proofreading.json",
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
    eng_ocr_fuser = get_eng_ocr_fuser(
        test_cases=get_kob_eng_ocr_fusion_test_cases()
        + get_mnt_eng_ocr_fusion_test_cases()
        + get_t_eng_ocr_fusion_test_cases(),
        test_case_path=title_root / "lang" / "eng" / "ocr_fusion.json",
        auto_verify=True,
    )
    eng_fuse = get_eng_ocr_fused(eng_lens, eng_tesseract, eng_ocr_fuser)
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_proofreader = get_eng_proofreader(
        test_cases=get_kob_eng_proofreading_test_cases()
        + get_mnt_eng_proofreading_test_cases()
        + get_t_eng_proofreading_test_cases(),
        test_case_path=title_root / "lang" / "eng" / "proofreading.json",
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

if "简体粤文 (Transcription)" in actions:
    zho_hans = Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")
    if (
        zho_hans.events[539].text == "不知道为什么"
        and zho_hans.events[540].text == "「珊你个头」却特别刺耳"
    ):
        info(
            "Merging 中文 subtitles 539 and 540, which comprise one sentence whose "
            "structure is reversed in the 粤文."
        )
        zho_hans = get_series_with_subs_merged(zho_hans, 539)
    yue_hans = AudioSeries.load(output_dir / "yue-Hans_audio")
    reviewer = CantoneseTranscriptionReviewer(
        test_case_directory_path=test_data_root / "mlamd",
        shifting_test_cases=get_mlamd_yue_shifting_test_cases(),
        merging_test_cases=get_mlamd_yue_merging_test_cases(),
    )
    yue_hans = asyncio.run(reviewer.process_all_blocks(yue_hans, zho_hans))
    outfile_path = output_dir / "yue-Hans.srt"
    yue_hans.save(outfile_path)
    yue_hans = Series.load(outfile_path)

    proofreader = get_yue_vs_zho_proofreader(
        default_test_cases=get_mlamd_yue_vs_zho_proofreading_test_cases(),
        test_case_path=title_root / "multilang" / "yue_zho" / "proofreading.json",
        auto_verify=True,
    )
    yue_hans_proofread = get_yue_vs_zho_proofread(
        yue_hans, zho_hans, processor=proofreader
    )
    outfile_path = output_dir / "yue-Hans_proofread.srt"
    yue_hans_proofread.save(outfile_path)

    translator = get_yue_from_zho_translator(
        default_test_cases=[],
        test_case_path=title_root / "multilang" / "yue_zho" / "translation.json",
        auto_verify=True,
    )
    yue_hans_proofread_translate = get_yue_from_zho_translated(
        yue_hans_proofread, zho_hans, translator=translator
    )
    outfile_path = output_dir / "yue-Hans_proofread_translate.srt"
    yue_hans_proofread_translate.save(outfile_path)

    reviewer = get_yue_vs_zho_processor(
        default_test_cases=[],
        test_case_path=title_root / "multilang" / "yue_zho" / "review.json",
        auto_verify=True,
    )
    yue_hans_proofread_translate_review = get_yue_vs_zho_reviewed(
        yue_hans_proofread_translate, zho_hans, processor=reviewer
    )
    outfile_path = output_dir / "yue-Hans_proofread_translate_review.srt"
    yue_hans_proofread_translate_review.save(outfile_path)

if "Bilingual 简体中文 and English" in actions:
    zho_hans_fuse_proofread_clean_flatten = Series.load(
        output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt"
    )
    eng_fuse_proofread_clean_flatten = Series.load(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
    )
    zho_hans_eng = get_synced_series(
        zho_hans_fuse_proofread_clean_flatten, eng_fuse_proofread_clean_flatten
    )
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")

if "Bilingual 简体粤文 and English" in actions:
    yue_hans_proofread_translate_review = Series.load(
        output_dir / "yue-Hans_proofread_translate_review.srt"
    )
    eng_fuse_proofread_clean_flatten = Series.load(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
    )
    yue_hans_eng = get_synced_series(
        yue_hans_proofread_translate_review, eng_fuse_proofread_clean_flatten
    )
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
