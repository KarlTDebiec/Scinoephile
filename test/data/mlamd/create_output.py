#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

import asyncio
from logging import info
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng import (
    get_eng_cleaned,
    get_eng_flattened,
    get_eng_ocr_fused,
    validate_eng_ocr,
)
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fuser
from scinoephile.lang.zho import (
    get_zho_cleaned,
    get_zho_converted,
    get_zho_flattened,
    get_zho_ocr_fused,
    validate_zho_ocr,
)
from scinoephile.lang.zho.ocr_fusion import get_zho_ocr_fuser
from scinoephile.multilang.synchronization import get_synced_series
from scinoephile.multilang.yue_zho import (
    get_yue_vs_zho_proofread,
    get_yue_vs_zho_reviewed,
)
from scinoephile.multilang.yue_zho.proofreading import get_yue_vs_zho_proofreader
from scinoephile.multilang.yue_zho.review import get_yue_vs_zho_processor
from scinoephile.multilang.yue_zho.transcription import YueTranscriber
from scinoephile.multilang.yue_zho.translation import (
    get_yue_from_zho_translated,
    get_yue_from_zho_translator,
)
from test.data.kob import (
    get_kob_eng_ocr_fusion_test_cases,
    get_kob_zho_ocr_fusion_test_cases,
)
from test.data.mlamd import (
    get_mlamd_yue_merging_test_cases,
    get_mlamd_yue_shifting_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_zho_ocr_fusion_test_cases,
)
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_zho_ocr_fusion_test_cases,
)

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    # "简体中文 (OCR)",
    "English (OCR)",
    # "简体粤文 (Transcription)",
    # "Bilingual 简体中文 and English",
    # "Bilingual 简体粤文 and English",
}


def process_zho_hans_ocr():
    # Fuse
    fuse_path = output_dir / "zho-Hans_fuse.srt"
    if fuse_path.exists():
        fuse = Series.load(fuse_path)
    else:
        lens = Series.load(input_dir / "zho-Hans_lens.srt")
        lens = get_zho_cleaned(lens, remove_empty=False)
        lens = get_zho_converted(lens)
        paddle = Series.load(input_dir / "zho-Hans_paddle.srt")
        paddle = get_zho_cleaned(paddle, remove_empty=False)
        paddle = get_zho_converted(paddle)
        fuser = get_zho_ocr_fuser(
            test_cases=get_kob_zho_ocr_fusion_test_cases()
            + get_mnt_zho_ocr_fusion_test_cases()
            + get_t_zho_ocr_fusion_test_cases(),
            test_case_path=title_root / "lang" / "zho" / "ocr_fusion.json",
            auto_verify=True,
        )
        fuse = get_zho_ocr_fused(lens, paddle, fuser)
        fuse.save(fuse_path)

    # Clean / Convert
    clean_path = output_dir / "zho-Hans_fuse_clean.srt"
    if clean_path.exists():
        fuse_clean = Series.load(clean_path)
    else:
        fuse_clean = get_zho_cleaned(fuse, remove_empty=False)
        fuse_clean = get_zho_converted(fuse_clean)
        fuse_clean.save(output_dir / "zho-Hans_fuse_clean.srt")

    # Validate
    image_path = output_dir / "zho-Hans_image"
    if image_path.exists():
        image = ImageSeries.load(image_path)
    else:
        image = ImageSeries.load(input_dir / "zho-Hans.sup")
        for text_sub, image_sub in zip(fuse_clean, image):
            image_sub.text = text_sub.text
        image.save(image_path)
    fuse_clean_validate = validate_zho_ocr(
        image,
        output_dir_path=output_dir / "zho-Hans_validation",
        interactive=True,
    )
    fuse_clean_validate = get_zho_cleaned(fuse_clean_validate)
    fuse_clean_validate.save(
        output_dir / "zho-Hans_fuse_clean_validate.srt", exist_ok=True
    )

    # Flatten
    fuse_clean_validate_flatten = get_zho_flattened(fuse_clean_validate)
    fuse_clean_validate_flatten.save(
        output_dir / "zho-Hans_fuse_clean_validate_flatten.srt", exist_ok=True
    )

    # # Proofread
    # zho_proofreader = get_zho_proofreader(
    #     test_cases=get_kob_zho_proofreading_test_cases()
    #     + get_mnt_zho_proofreading_test_cases()
    #     + get_t_zho_proofreading_test_cases(),
    #     test_case_path=title_root / "lang" / "zho" / "proofreading.json",
    #     auto_verify=True,
    # )
    # zho_hans_fuse_proofread = get_zho_proofread(zho_hans_fuse, zho_proofreader)
    # zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")


if "简体中文 (OCR Validation)" in actions:
    zho_hans = ImageSeries.load(output_dir / "zho-Hans_image")
    validate_zho_ocr(
        zho_hans,
        output_dir_path=output_dir / "zho-Hans_validation",
        interactive=True,
    )


def process_eng_ocr():
    # Fuse
    fuse_path = output_dir / "eng_fuse.srt"
    if fuse_path.exists():
        fuse = Series.load(fuse_path)
    else:
        lens = Series.load(input_dir / "eng_lens.srt")
        lens = get_eng_cleaned(lens, remove_empty=False)
        tesseract = Series.load(input_dir / "eng_tesseract.srt")
        tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        fuser = get_eng_ocr_fuser(
            test_cases=get_kob_eng_ocr_fusion_test_cases()
            + get_mnt_eng_ocr_fusion_test_cases()
            + get_t_eng_ocr_fusion_test_cases(),
            test_case_path=title_root / "lang" / "eng" / "ocr_fusion.json",
            auto_verify=True,
        )
        fuse = get_eng_ocr_fused(lens, tesseract, fuser)
        fuse.save(fuse_path)

    # Clean
    clean_path = output_dir / "eng_fuse_clean.srt"
    if clean_path.exists():
        fuse_clean = Series.load(clean_path)
    else:
        fuse_clean = get_eng_cleaned(fuse, remove_empty=False)
        fuse_clean.save(output_dir / "eng_fuse_clean.srt")

    # Validate
    image_path = output_dir / "eng_image"
    if image_path.exists():
        image = ImageSeries.load(image_path)
    else:
        image = ImageSeries.load(input_dir / "eng.sup")
        for text_sub, image_sub in zip(fuse_clean, image):
            image_sub.text = text_sub.text
        image.save(image_path)
    fuse_clean_validate = validate_eng_ocr(
        image,
        output_dir_path=output_dir / "eng_validation",
        interactive=True,
    )
    fuse_clean_validate = get_eng_cleaned(fuse_clean_validate)
    fuse_clean_validate.save(output_dir / "eng_fuse_clean_validate.srt", exist_ok=True)

    # Flatten
    fuse_clean_validate_flatten = get_eng_flattened(fuse_clean_validate)
    fuse_clean_validate_flatten.save(
        output_dir / "eng_fuse_clean_validate_flatten.srt", exist_ok=True
    )

    # Proofread
    # eng_proofreader = get_eng_proofreader(
    #     test_cases=get_kob_eng_proofreading_test_cases()
    #     + get_mnt_eng_proofreading_test_cases()
    #     + get_t_eng_proofreading_test_cases(),
    #     test_case_path=title_root / "lang" / "eng" / "proofreading.json",
    #     auto_verify=True,
    # )
    # eng_fuse_proofread = get_eng_proofread(eng_fuse, eng_proofreader)
    # eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")


if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr()

if "English (OCR)" in actions:
    process_eng_ocr()

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
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")
    yue_hans = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = YueTranscriber(
        test_case_directory_path=test_data_root / "mlamd",
        shifting_test_cases=get_mlamd_yue_shifting_test_cases(),
        merging_test_cases=get_mlamd_yue_merging_test_cases(),
    )
    yue_hans = asyncio.run(transcriber.process_all_blocks(yue_hans, zho_hans))
    outfile_path = output_dir / "yue-Hans.srt"
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

    transcriber = get_yue_vs_zho_processor(
        default_test_cases=[],
        test_case_path=title_root / "multilang" / "yue_zho" / "review.json",
        auto_verify=True,
    )
    yue_hans_proofread_translate_review = get_yue_vs_zho_reviewed(
        yue_hans_proofread_translate, zho_hans, processor=transcriber
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
