#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

import asyncio
from logging import info
from pathlib import Path

from data.mlamd import (
    mlamd_distribute_test_cases,
    mlamd_merge_test_cases,
    mlamd_proof_test_cases,
    mlamd_review_test_cases,
    mlamd_shift_test_cases,
    mlamd_translate_test_cases,
)

from scinoephile.audio import AudioSeries
from scinoephile.audio.cantonese import CantoneseTranscriptionReviewer
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series, get_series_with_subs_merged
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.english.proofreading import (
    EnglishProofreader,
    get_english_proofread,
)
from scinoephile.core.synchronization import get_synced_series
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
    # "简体中文 (OCR)",
    # "English (OCR)",
    "简体粤文 (Transcription)"
    # "Bilingual 简体中文 and English",
    # "Bilingual 简体粤文 and English",
}

if "简体中文 (OCR)" in actions:
    zho_hans_paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
    zho_hans_paddle = get_zhongwen_cleaned(zho_hans_paddle, remove_empty=False)
    zho_hans_paddle = get_zhongwen_converted(zho_hans_paddle)
    zho_hans_lens = Series.load(input_dir / "zho-Hans_lens.srt")
    zho_hans_lens = get_zhongwen_cleaned(zho_hans_lens, remove_empty=False)
    zho_hans_lens = get_zhongwen_converted(zho_hans_lens)
    zho_hans_fuse = get_zhongwen_ocr_fused(
        zho_hans_paddle,
        zho_hans_lens,
        ZhongwenFuser(
            test_cases=kob_zhongwen_fusion_test_cases
            + mnt_zhongwen_fusion_test_cases
            + t_zhongwen_fusion_test_cases,
            test_case_path=test_data_root / title / "image" / "zhongwen" / "fusion.py",
            auto_verify=True,
        ),
    )
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zhongwen_cleaned(zho_hans_fuse)
    zho_hans_fuse = get_zhongwen_converted(zho_hans_fuse)
    zho_hans_fuse_proofread = get_zhongwen_proofread(
        zho_hans_fuse,
        ZhongwenProofreader(
            test_cases=kob_zhongwen_proofreading_test_cases
            + mnt_zhongwen_proofreading_test_cases
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
    zho_hans_fuse_proofread_clean.save(output_dir / "zho-Hans_fuse_proofread_clean.srt")
    zho_hans_fuse_proofread_clean_flatten = get_zhongwen_flattened(
        zho_hans_fuse_proofread_clean
    )
    zho_hans_fuse_proofread_clean_flatten.save(
        output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt"
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
            test_cases=kob_english_proofreading_test_cases
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
    eng_fuse_proofread_clean = get_english_cleaned(eng_fuse_proofread)
    eng_fuse_proofread_clean.save(output_dir / "eng_fuse_proofread_clean.srt")
    eng_fuse_proofread_clean_flatten = get_english_flattened(eng_fuse_proofread_clean)
    eng_fuse_proofread_clean_flatten.save(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
    )

if "简体粤文 (Transcription)" in actions:
    zhongwen = Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")
    if (
        zhongwen.events[539].text == "不知道为什么"
        and zhongwen.events[540].text == "「珊你个头」却特别刺耳"
    ):
        info(
            "Merging 中文 subtitles 539 and 540, which comprise one sentence whose "
            "structure is reversed in the 粤文."
        )
        zhongwen = get_series_with_subs_merged(zhongwen, 539)

    # 粤文
    yuewen = AudioSeries.load(output_dir / "yue-Hans_audio")

    # Utilities
    reviewer = CantoneseTranscriptionReviewer(
        test_case_directory_path=test_data_root / "mlamd",
        distribute_test_cases=mlamd_distribute_test_cases,
        shift_test_cases=mlamd_shift_test_cases,
        merge_test_cases=mlamd_merge_test_cases,
        proof_test_cases=mlamd_proof_test_cases,
        translate_test_cases=mlamd_translate_test_cases,
        review_test_cases=mlamd_review_test_cases,
    )

    # Process all blocks
    # yuewen_series = await reviewer.process_all_blocks(yuewen, zhongwen)
    yuewen_series = asyncio.run(reviewer.process_all_blocks(yuewen, zhongwen))

    # Update output file
    # if len(zhongwen.blocks) == len(yuewen.blocks):
    #     outfile_path = output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt"
    #     if outfile_path.exists():
    #         outfile_path.unlink()
    #     yuewen_series.save(outfile_path)
    #     info(f"Saved 粤文 subtitles to {outfile_path}")

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
    yue_hans = Series.load(output_dir / "yue-Hans.srt")
    eng_fuse_proofread_clean_flatten = Series.load(
        output_dir / "eng_fuse_proofread_clean_flatten.srt"
    )
    yue_hans_eng = get_synced_series(yue_hans, eng_fuse_proofread_clean_flatten)
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
