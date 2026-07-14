#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.analysis.diff import SeriesDiff
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.processor import DemucsMode, VADMode
from scinoephile.lang.yue_zho.review import (
    YueZhoGuidedReviewPromptYueHans,
    YueZhoGuidedReviewPromptYueHant,
    YueZhoPairwiseReviewPromptYueHans,
    YueZhoPairwiseReviewPromptYueHant,
)
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHans,
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHans,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.lang.yue_zho.translation import (
    YueZhoGapTranslationPromptYueHans,
    YueZhoGapTranslationPromptYueHant,
)
from test.data.ocr import process_ocr
from test.data.srt import process_srt
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_yue_hans_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
eng_path = output_path / "eng"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
yue_hant_path = output_path / "yue-Hant"
yue_hans_path = output_path / "yue-Hans"
yue_hans_transcribe_path = output_path / "yue-Hans_transcribe"

actions = {
    # "eng_ocr",
    # "zho-Hant_ocr",
    # "eng",
    # "yue-Hans",
    # "yue-Hant",
    # "zho-Hans_eng",
    # "yue-Hans_eng",
    # "yue-Hans_transcribe",
    "yue-Hans_diff",
}

if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "zho-Hans_eng" in actions:
    zho_hans_srt_path = (
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    eng_srt_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_srt_path, eng_srt_path, overwrite=False)
if "eng" in actions:
    process_srt(
        title_root,
        Language.eng,
        eng_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        overwrite=True,
    )
if "yue-Hans" in actions:
    process_srt(
        title_root,
        Language.yue_hans,
        zho_hant_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        two_end_idx=1461,
        overwrite=True,
    )
if "yue-Hant" in actions:
    process_srt(
        title_root,
        Language.yue_hant,
        zho_hant_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        two_end_idx=1461,
        overwrite=True,
    )
if "yue-Hans_eng" in actions:
    yue_hans_srt_path = yue_hans_path / "clean_review_flatten_timewarp.srt"
    eng_srt_path = eng_path / "clean_review_flatten_timewarp.srt"
    process_yue_hans_eng(title_root, yue_hans_srt_path, eng_srt_path, overwrite=True)
if "yue-Hans_transcribe" in actions:
    zh_hant_path = zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt"
    zho_hans_path = (
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    simplified_reference_path = yue_hans_path / "clean_review_flatten_timewarp.srt"
    traditional_reference_path = yue_hant_path / "clean_review_flatten_timewarp.srt"
    audio_path = yue_hans_transcribe_path / "audio/yue-Hans_audio.wav"

    process_yue_hans_transcription(
        title_root,
        zho_path=zho_hans_path,
        reference_path=simplified_reference_path,
        output_dir_path=yue_hans_transcribe_path / "test_simplified",
        audio_path=audio_path,
        name="KOB transcription test 1 (simplified)",
        transcriber_kw={
            "model_name": "khleeloo/whisper-large-v3-cantonese",
            "demucs_mode": DemucsMode.ON,
            "vad_mode": VADMode.AUTO,
            "delineation_prompt": YueZhoDelineationPromptYueHans,
            "punctuation_prompt": YueZhoPunctuationPromptYueHans,
        },
        pairwise_reviewer_kw={"prompt": YueZhoPairwiseReviewPromptYueHans},
        translator_kw={"prompt": YueZhoGapTranslationPromptYueHans},
        guided_reviewer_kw={"prompt": YueZhoGuidedReviewPromptYueHans},
        overwrite_srt=False,
    )

    process_yue_hans_transcription(
        title_root,
        zho_path=zh_hant_path,
        reference_path=traditional_reference_path,
        output_dir_path=yue_hans_transcribe_path / "test_traditional",
        audio_path=audio_path,
        name="KOB transcription test 2 (traditional)",
        transcriber_kw={
            "model_name": "khleeloo/whisper-large-v3-cantonese",
            "demucs_mode": DemucsMode.ON,
            "vad_mode": VADMode.AUTO,
            "delineation_prompt": YueZhoDelineationPromptYueHant,
            "punctuation_prompt": YueZhoPunctuationPromptYueHant,
        },
        pairwise_reviewer_kw={"prompt": YueZhoPairwiseReviewPromptYueHant},
        translator_kw={"prompt": YueZhoGapTranslationPromptYueHant},
        guided_reviewer_kw={"prompt": YueZhoGuidedReviewPromptYueHant},
        overwrite_srt=False,
    )
if "yue-Hans_diff" in actions:
    # yue_hans_transcribe = Series.load(
    #     yue_hans_transcribe_path / "test_simplified/transcribe.srt"
    # )
    yue_hans_transcribe = Series.load(
        yue_hans_transcribe_path
        / "test_simplified"
        / "transcribe_review_translate_guided_review.srt"
    )
    yue_hans_reference = Series.load(
        yue_hans_path / "clean_review_flatten_timewarp.srt"
    )
    zho_hans_reference = Series.load(
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    diff = SeriesDiff(
        yue_hans_transcribe,
        yue_hans_reference,
        one_lbl="TRANSCRIBE",
        two_lbl="REFERENCE",
    )
    # print(diff)
    print(
        diff.get_stacked_str(
            # three=zho_hans_reference,
            include_equal=True,
        )
    )
    print(SeriesCER(yue_hans_reference, yue_hans_transcribe))
