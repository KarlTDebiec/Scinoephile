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
from test.data.ocr import process_ocr
from test.data.srt import process_srt
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
eng_path = output_path / "eng"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
yue_hant_path = output_path / "yue-Hant"
yue_hans_path = output_path / "yue-Hans"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"

actions = {
    # "eng_ocr",
    # "zho-Hant_ocr",
    # "eng",
    # "yue-Hans",
    # "yue-Hant",
    # "zho-Hans_eng",
    # "yue-Hans_eng",
    "yue-Hant_transcribe",
    # "yue-Hant_diff",
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
if "yue-Hant_transcribe" in actions:
    process_transcription(
        title_root,
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        reference_path=yue_hant_path / "clean_review_flatten_timewarp.srt",
        output_dir_path=yue_hant_transcribe_path,
        name="KOB yue-Hant transcription",
        transcription_kw={
            "delineation_test_cases": [],
            "demucs_mode": DemucsMode.ON,
            "punctuation_test_cases": [],
            "vad_mode": VADMode.AUTO,
        },
        overwrite_srt=False,
    )
if "yue-Hant_diff" in actions:
    yue_hant_transcribe = Series.load(yue_hant_transcribe_path / "transcribe.srt")
    yue_hant_reference = Series.load(
        yue_hant_path / "clean_review_flatten_timewarp.srt"
    )
    diff = SeriesDiff(
        yue_hant_transcribe,
        yue_hant_reference,
        one_lbl="TRANSCRIBE",
        two_lbl="REFERENCE",
    )
    print(diff.get_stacked_str(include_equal=True))
    print(SeriesCER(yue_hant_reference, yue_hant_transcribe))
