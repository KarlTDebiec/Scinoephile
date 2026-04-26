#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.subtitles import Series
from scinoephile.core.timing import get_series_timewarped
from scinoephile.lang.eng import (
    get_eng_block_reviewed,
    get_eng_cleaned,
    get_eng_flattened,
)
from scinoephile.lang.eng.block_review import get_eng_block_reviewer
from scinoephile.lang.yue import get_yue_romanized
from scinoephile.lang.zho import get_zho_cleaned, get_zho_flattened
from scinoephile.multilang.yue_zho.block_review import YueVsZhoYueHansBlockReviewPrompt
from scinoephile.multilang.yue_zho.line_review import YueVsZhoYueHansLineReviewPrompt
from scinoephile.multilang.yue_zho.transcription import (
    DemucsMode,
    VADMode,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueVsZhoYueHansDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueVsZhoYueHansPunctuationPrompt,
)
from scinoephile.multilang.yue_zho.translation import YueVsZhoYueHansTranslationPrompt
from test.data.ocr import process_eng_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_yue_hans_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

eng_ocr_dir = output_dir / "eng_ocr"
eng_dir = output_dir / "eng"
zho_hant_ocr_dir = output_dir / "zho-Hant_ocr"
yue_hant_dir = output_dir / "yue-Hant"
yue_hans_dir = output_dir / "yue-Hans"
yue_hans_transcribe_dir = output_dir / "yue-Hans_transcribe"

actions = {
    # "繁體中文 (OCR)",
    # "English (OCR)",
    # "Bilingual 繁體中文 and English",
    # "繁體粵文 (SRT)",
    # "简体粤文 (SRT)",
    # "English (SRT)",
    # "Bilingual 简体粤文 and English",
    "简体粤文 (Transcription)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(title_root, overwrite_srt=False, force_validation=False)
if "English (OCR)" in actions:
    process_eng_ocr(title_root, overwrite_srt=True, force_validation=True)
if "Bilingual 繁體中文 and English" in actions:
    zho_hans_path = (
        zho_hant_ocr_dir / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    eng_path = eng_ocr_dir / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(
        title_root, zho_hans_path=zho_hans_path, eng_path=eng_path, overwrite=True
    )
if "繁體粵文 (SRT)" in actions:
    zho_hant = Series.load(zho_hant_ocr_dir / "fuse_clean_validate_review.srt")
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_timewarp = get_series_timewarped(
        zho_hant, yue_hant, one_end_idx=1421, two_end_idx=1461
    )
    yue_hant_timewarp.save(yue_hant_dir / "timewarp.srt")
    clean = get_zho_cleaned(yue_hant_timewarp)
    clean.save(yue_hant_dir / "timewarp_clean.srt")
    flatten = get_zho_flattened(clean)
    flatten.save(yue_hant_dir / "timewarp_clean_flatten.srt")
if "简体粤文 (SRT)" in actions:
    zho_hant = Series.load(zho_hant_ocr_dir / "fuse_clean_validate_review.srt")
    yue_hans = Series.load(input_dir / "yue-Hans.srt")
    yue_hans_timewarp = get_series_timewarped(
        zho_hant, yue_hans, one_end_idx=1421, two_end_idx=1461
    )
    yue_hans_timewarp.save(yue_hans_dir / "timewarp.srt")
    yue_hans_clean = get_zho_cleaned(yue_hans_timewarp)
    yue_hans_clean.save(yue_hans_dir / "timewarp_clean.srt")
    yue_hans_reference = get_zho_flattened(yue_hans_clean)
    yue_hans_reference.save(yue_hans_dir / "timewarp_clean_flatten.srt")
    yue_hans_romanized = get_yue_romanized(yue_hans_reference, append=True)
    yue_hans_romanized.save(yue_hans_dir / "timewarp_clean_flatten_romanize.srt")
if "English (SRT)" in actions:
    eng_ocr = Series.load(eng_ocr_dir / "fuse_clean_validate_review.srt")
    eng_srt = Series.load(input_dir / "eng.srt")
    eng_timewarp = get_series_timewarped(eng_ocr, eng_srt, one_end_idx=1421)
    eng_timewarp.save(eng_dir / "timewarp.srt")
    eng_clean = get_eng_cleaned(eng_timewarp)
    eng_clean.save(eng_dir / "timewarp_clean.srt")
    eng_proofreader = get_eng_block_reviewer(
        test_case_path=eng_dir / "lang" / "eng" / "block_review.json",
        auto_verify=True,
    )
    eng_proofread = get_eng_block_reviewed(eng_clean, eng_proofreader)
    eng_proofread.save(eng_dir / "timewarp_clean_review.srt")
    eng_flatten = get_eng_flattened(eng_proofread)
    eng_flatten.save(eng_dir / "timewarp_clean_review_flatten.srt")
if "Bilingual 简体粤文 and English" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=yue_hans_dir / "timewarp_clean_flatten.srt",
        eng_path=eng_dir / "timewarp_clean_review_flatten.srt",
        overwrite=True,
    )
if "简体粤文 (Transcription)" in actions:
    zho_path = (
        zho_hant_ocr_dir / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    yue_hans_transcribe_review_translate_block_review = process_yue_hans_transcription(
        title_root,
        zho_path=zho_path,
        name="KOB transcription (Demucs ON, VAD AUTO)",
        transcriber_kw={
            "model_name": "khleeloo/whisper-large-v3-cantonese",
            "demucs_mode": DemucsMode.ON,
            "vad_mode": VADMode.AUTO,
            "deliniation_prompt_cls": YueVsZhoYueHansDeliniationPrompt,
            "punctuation_prompt_cls": YueVsZhoYueHansPunctuationPrompt,
        },
        line_reviewer_kw={"prompt_cls": YueVsZhoYueHansLineReviewPrompt},
        translator_kw={"prompt_cls": YueVsZhoYueHansTranslationPrompt},
        block_reviewer_kw={"prompt_cls": YueVsZhoYueHansBlockReviewPrompt},
        overwrite_srt=True,
    )
