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
from test.data.ocr import process_ocr
from test.data.srt import process_srt
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import (
    get_reference_for_guide_blocks,
    process_transcription,
    process_transcription_guided_review,
)
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
zho_hant_guide_path = zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt"

transcription_stop_at_idx: int | None = 20
yue_hant_transcribe_srt_path = yue_hant_transcribe_path / "transcribe.srt"
if transcription_stop_at_idx is not None:
    yue_hant_transcribe_srt_path = (
        yue_hant_transcribe_path
        / f"transcribe_first_{transcription_stop_at_idx}_blocks.srt"
    )
yue_hant_guided_review_srt_path = yue_hant_transcribe_srt_path.with_name(
    f"{yue_hant_transcribe_srt_path.stem}_guided_review.srt"
)

actions = {
    # "eng_ocr",
    # "zho-Hant_ocr",
    # "eng",
    # "yue-Hans",
    # "yue-Hant",
    # "zho-Hans_eng",
    # "yue-Hans_eng",
    "yue-Hant_transcribe",
    # "yue-Hant_guided_review",
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
        zho_hant_guide_path,
        reference_path=yue_hant_path / "clean_review_flatten_timewarp.srt",
        output_dir_path=yue_hant_transcribe_path,
        transcribe_path=yue_hant_transcribe_srt_path,
        name="KOB yue-Hant transcription",
        stop_at_idx=transcription_stop_at_idx,
        overwrite=True,
    )
if "yue-Hant_guided_review" in actions:
    process_transcription_guided_review(
        yue_hant_transcribe_srt_path,
        zho_hant_guide_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        reference_path=yue_hant_path / "clean_review_flatten_timewarp.srt",
        name="KOB yue-Hant transcription guided review",
        guided_review_path=yue_hant_guided_review_srt_path,
        stop_at_idx=transcription_stop_at_idx,
        reviewer_kw={"test_cases": []},
        overwrite=False,
    )
if "yue-Hant_diff" in actions:
    yue_hant_transcribe = Series.load(yue_hant_guided_review_srt_path)
    zho_hant_guide = Series.load(zho_hant_guide_path)
    yue_hant_reference = Series.load(
        yue_hant_path / "clean_review_flatten_timewarp.srt"
    )
    yue_hant_reference = get_reference_for_guide_blocks(
        yue_hant_reference,
        zho_hant_guide,
        transcription_stop_at_idx,
    )
    zho_hant_guide_by_timing = {
        (subtitle.start, subtitle.end): subtitle for subtitle in zho_hant_guide
    }
    aligned_zho_hant_guide = Series(
        events=[
            zho_hant_guide_by_timing[(subtitle.start, subtitle.end)]
            for subtitle in yue_hant_transcribe
        ]
    )
    diff = SeriesDiff(
        yue_hant_transcribe,
        yue_hant_reference,
        one_lbl="GUIDED REVIEW",
        two_lbl="REFERENCE",
    )
    print(
        diff.get_stacked_str(
            three=aligned_zho_hant_guide,
            include_equal=True,
        )
    )
    print(SeriesCER(yue_hant_reference, yue_hant_transcribe))
