#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

from logging import info
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import get_backend
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho import (
    get_yue_proofread_vs_zho,
    get_yue_reviewed_vs_zho,
)
from scinoephile.multilang.yue_zho.proofreading import get_yue_vs_zho_proofreader
from scinoephile.multilang.yue_zho.review import get_yue_vs_zho_reviewer
from scinoephile.multilang.yue_zho.transcription import (
    get_yue_transcribed_vs_zho,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.translation import (
    get_yue_translated_vs_zho,
    get_yue_vs_zho_translator,
)
from test.data.mlamd import (
    get_mlamd_yue_punctuating_test_cases,
    get_mlamd_yue_shifting_test_cases,
)
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    # "繁體中文 (OCR)",
    # "简体中文 (OCR)",
    # "English (OCR)",
    # "Bilingual 简体中文 and English",
    "Bilingual 简体粤文 and English",
    # "简体粤文 (Transcription)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        input_dir / "zho-Hant.sup",
        overwrite_srt=True,
        force_validation=True,
    )
if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        input_dir / "zho-Hans.sup",
        overwrite_srt=True,
        force_validation=True,
    )
if "English (OCR)" in actions:
    process_eng_ocr(
        title_root,
        input_dir / "zho-Hans.sup",
        overwrite_srt=True,
        force_validation=True,
    )
if "Bilingual 简体中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir / "zho-Hans_fuse_clean_validate_review_flatten.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_review_flatten.srt",
        overwrite=True,
    )
if "简体粤文 (Transcription)" in actions:
    # Stage
    zho_hans = Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_review_flatten.srt"
    )
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

    # Transcribe
    yue_hans = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = get_yue_vs_zho_transcriber(
        test_case_directory_path=test_data_root / "mlamd",
        shifting_test_cases=get_mlamd_yue_shifting_test_cases(),
        punctuating_test_cases=get_mlamd_yue_punctuating_test_cases(),
    )
    yue_hans = get_yue_transcribed_vs_zho(yue_hans, zho_hans, transcriber=transcriber)
    outfile_path = output_dir / "yue-Hans_transcribe.srt"
    yue_hans.save(outfile_path)

    # Proofread
    yue_hans = Series.load(outfile_path)
    proofreader = get_yue_vs_zho_proofreader(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "proofreading"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_proofread = get_yue_proofread_vs_zho(
        yue_hans, zho_hans, processor=proofreader
    )
    outfile_path = output_dir / "yue-Hans_transcribe_proofread.srt"
    yue_hans_proofread.save(outfile_path)

    # Translate
    translator = get_yue_vs_zho_translator(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "translation"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_proofread_translate = get_yue_translated_vs_zho(
        yue_hans_proofread, zho_hans, translator=translator
    )
    outfile_path = output_dir / "yue-Hans_transcribe_proofread_translate.srt"
    yue_hans_proofread_translate.save(outfile_path)

    # Review
    reviewer = get_yue_vs_zho_reviewer(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "review"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_proofread_translate_review = get_yue_reviewed_vs_zho(
        yue_hans_proofread_translate, zho_hans, reviewer=reviewer
    )
    outfile_path = output_dir / "yue-Hans_transcribe_proofread_translate_review.srt"
    yue_hans_proofread_translate_review.save(outfile_path)
if "Bilingual 简体粤文 and English" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=output_dir / "yue-Hans_transcribe_proofread_translate_review.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_review_flatten.srt",
        overwrite=True,
    )
