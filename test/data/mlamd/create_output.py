#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

from logging import info
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.review.guided import get_guided_reviewer
from scinoephile.multilang.review.pairwise import get_pairwise_reviewer
from scinoephile.multilang.transcription.guided import get_guided_transcriber
from scinoephile.multilang.transcription.processor import VADMode
from scinoephile.multilang.translation.gap import get_gap_translator
from scinoephile.workflows.review import review_series_guided, review_series_pairwise
from scinoephile.workflows.transcription import transcribe_series_guided
from scinoephile.workflows.translation import translate_series_gaps
from test.data.mlamd import (
    get_mlamd_yue_delineation_test_cases,
    get_mlamd_yue_punctuation_test_cases,
)
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
set_logging_verbosity(2)

actions = {
    "eng_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    "zho-Hans_eng",
    "yue-Hans_eng",
    # "yue-Hans_transcribe",
}

if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "zho-Hans_ocr" in actions:
    process_ocr(title_root, Language.zho_hans, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "zho-Hans_eng" in actions:
    zho_hans_path = (
        output_path / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten.srt"
    )
    eng_path = output_path / "eng_ocr" / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
if "yue-Hans_transcribe" in actions:
    # Stage
    zho_hans = Series.load(
        output_path / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten.srt"
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
    audio_path = output_path / "yue-Hans_transcribe" / "audio"
    audio_path.mkdir(parents=True, exist_ok=True)
    zho_hans.save(audio_path / "audio.srt")

    # Transcribe
    yue_hans = AudioSeries.load(audio_path)
    transcriber = get_guided_transcriber(
        Language.yue_hans,
        Language.zho_hans,
        vad_mode=VADMode.ON,
        test_case_dir_path=(
            output_path / "yue-Hans_transcribe" / "multilang/yue_zho/transcription"
        ),
        delineation_test_cases=get_mlamd_yue_delineation_test_cases(),
        punctuation_test_cases=get_mlamd_yue_punctuation_test_cases(),
    )
    yue_hans = transcribe_series_guided(
        yue_hans,
        zho_hans,
        language=Language.yue_hans,
        reference_language=Language.zho_hans,
        transcriber=transcriber,
    )
    outfile_path = output_path / "yue-Hans_transcribe" / "transcribe.srt"
    yue_hans.save(outfile_path)

    # Pairwise review
    yue_hans = Series.load(outfile_path)
    pairwise_reviewer = get_pairwise_reviewer(
        Language.yue_hans,
        Language.zho_hans,
        test_case_path=output_path
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "pairwise_review"
        / f"{get_torch_device()}.json",
        auto_verify=True,
    )
    yue_hans_pairwise_reviewed = review_series_pairwise(
        yue_hans,
        zho_hans,
        reviewer=pairwise_reviewer,
    )
    outfile_path = output_path / "yue-Hans_transcribe" / "transcribe_review.srt"
    yue_hans_pairwise_reviewed.save(outfile_path)

    # Translate
    translator = get_gap_translator(
        Language.zho_hans,
        Language.yue_hans,
        test_case_path=output_path
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "gap_translation"
        / f"{get_torch_device()}.json",
        auto_verify=True,
    )
    yue_hans_review_translate = translate_series_gaps(
        zho_hans,
        yue_hans_pairwise_reviewed,
        source_language=Language.zho_hans,
        target_language=Language.yue_hans,
        translator=translator,
    )
    outfile_path = (
        output_path / "yue-Hans_transcribe" / "transcribe_review_translate.srt"
    )
    yue_hans_review_translate.save(outfile_path)

    # Guided review
    reviewer = get_guided_reviewer(
        Language.yue_hans,
        Language.zho_hans,
        test_case_path=output_path
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "guided_review"
        / f"{get_torch_device()}.json",
        auto_verify=True,
    )
    yue_hans_review_translate_guided_review = review_series_guided(
        yue_hans_review_translate,
        zho_hans,
        reviewer=reviewer,
    )
    outfile_path = (
        output_path
        / "yue-Hans_transcribe"
        / "transcribe_review_translate_guided_review.srt"
    )
    yue_hans_review_translate_guided_review.save(outfile_path)
if "yue-Hans_eng" in actions:
    yue_hans_path = (
        output_path
        / "yue-Hans_transcribe"
        / "transcribe_review_translate_guided_review.srt"
    )
    eng_path = output_path / "eng_ocr" / "fuse_clean_validate_review_flatten.srt"
    process_yue_hans_eng(title_root, yue_hans_path, eng_path, overwrite=False)
