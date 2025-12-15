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
from scinoephile.core import Series, get_series_with_subs_merged
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
    get_mlamd_yue_merging_test_cases,
    get_mlamd_yue_proofing_test_cases,
    get_mlamd_yue_review_test_cases,
    get_mlamd_yue_shifting_test_cases,
    get_mlamd_yue_translation_test_cases,
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

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"
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
    zho_hans_fuse = get_zho_fused(
        zho_hans_lens,
        zho_hans_paddle,
        get_zho_fuser(
            test_cases=get_kob_zho_fusion_test_cases()
            + get_mnt_zho_fusion_test_cases()
            + get_t_zho_fusion_test_cases(),
            test_case_path=test_data_root
            / title
            / "image"
            / "zhongwen"
            / "fusion.json",
            auto_verify=True,
        ),
    )
    zho_hans_fuse.save(output_dir / "zho-Hans_fuse.srt")
    zho_hans_fuse = get_zho_cleaned(zho_hans_fuse)
    zho_hans_fuse = get_zho_converted(zho_hans_fuse)
    zho_hans_fuse_proofread = get_zho_proofread(
        zho_hans_fuse,
        get_zho_proofreader(
            test_cases=get_kob_zho_proofreading_test_cases()
            + get_mnt_zho_proofreading_test_cases()
            + get_t_zho_proofreading_test_cases(),
            test_case_path=test_data_root
            / title
            / "core"
            / "zhongwen"
            / "proofreading.json",
            auto_verify=True,
        ),
    )
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
    eng_fuse = get_eng_fused(
        eng_lens,
        eng_tesseract,
        get_eng_fuser(
            test_cases=get_kob_eng_fusion_test_cases()
            + get_mnt_eng_fusion_test_cases()
            + get_t_eng_fusion_test_cases(),
            test_case_path=test_data_root / title / "image" / "english" / "fusion.json",
            auto_verify=True,
        ),
    )
    eng_fuse.save(output_dir / "eng_fuse.srt")
    eng_fuse_proofread = get_eng_proofread(
        eng_fuse,
        get_eng_proofreader(
            test_cases=get_kob_eng_proofreading_test_cases()
            + get_mnt_eng_proofreading_test_cases()
            + get_t_eng_proofreading_test_cases(),
            test_case_path=test_data_root
            / title
            / "core"
            / "english"
            / "proofreading.json",
            auto_verify=True,
        ),
    )
    eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")
    eng_fuse_proofread_clean = get_eng_cleaned(eng_fuse_proofread)
    eng_fuse_proofread_clean.save(output_dir / "eng_fuse_proofread_clean.srt")
    eng_fuse_proofread_clean_flatten = get_eng_flattened(eng_fuse_proofread_clean)
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
        shifting_test_cases=get_mlamd_yue_shifting_test_cases(),
        merging_test_cases=get_mlamd_yue_merging_test_cases(),
        proofing_test_cases=get_mlamd_yue_proofing_test_cases(),
        translation_test_cases=get_mlamd_yue_translation_test_cases(),
        review_test_cases=get_mlamd_yue_review_test_cases(),
    )

    # Process all blocks
    yuewen_series = asyncio.run(reviewer.process_all_blocks(yuewen, zhongwen))

    # Update output file
    if len(zhongwen.blocks) == len(yuewen.blocks):
        outfile_path = output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt"
        if outfile_path.exists():
            outfile_path.unlink()
        yuewen_series.save(outfile_path)
        info(f"Saved 粤文 subtitles to {outfile_path}")

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
