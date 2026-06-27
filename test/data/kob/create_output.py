#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.analysis.diff import SeriesDiff
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.subtitles import Series
from scinoephile.core.timing import get_series_timewarped
from scinoephile.lang.eng.block_review import (
    get_eng_block_reviewed,
    get_eng_block_reviewer,
)
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.flattening import get_eng_flattened
from scinoephile.lang.yue.romanization import get_yue_romanized
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.flattening import get_zho_flattened
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.multilang.yue_zho.block_review import (
    YueBlockReviewVsZhoPromptYueHans,
    YueBlockReviewVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
    YueGappedTranslationVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueLineReviewVsZhoPromptYueHans,
    YueLineReviewVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription import DemucsMode, VADMode
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueDeliniationVsZhoPromptYueHans,
    YueDeliniationVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YuePunctuationVsZhoPromptYueHant,
)
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_yue_hans_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
eng_path = output_path / "eng"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
yue_hant_path = output_path / "yue-Hant"
yue_hans_path = output_path / "yue-Hans"
yue_hans_transcribe_path = output_path / "yue-Hans_transcribe"


def review_yue(
    series: Series,
    outfile_path: Path,
    prompt_cls: type[BlockReviewPromptZhoHans],
    *,
    test_case_name: str = "block_review.json",
    overwrite: bool = False,
) -> Series:
    """Load or create reviewed KOB written Cantonese subtitles.

    Arguments:
        series: series to review
        outfile_path: output SRT path
        prompt_cls: review prompt class
        test_case_name: review test case JSON filename
        overwrite: whether to overwrite existing output
    Returns:
        reviewed series
    """
    test_case_path = outfile_path.parent / "lang" / "yue" / test_case_name
    if outfile_path.exists() and test_case_path.exists() and not overwrite:
        return Series.load(outfile_path)

    reviewer = get_zho_reviewer(
        prompt_cls=prompt_cls,
        test_case_path=test_case_path,
        auto_verify=True,
    )
    reviewed = get_zho_block_reviewed(series, processor=reviewer)
    test_cases = list(reviewer.queryer.encountered_test_cases.values())
    for test_case in test_cases:
        test_case.verified = True
    save_test_cases_to_json(test_case_path, test_cases)
    reviewed.save(outfile_path)
    return reviewed


actions = {
    # "eng_ocr",
    # "zho-Hant_ocr",
    # "zho-Hans_eng",
    "yue-Hant",
    "yue-Hans",
    "eng",
    "yue-Hans_eng",
    # "yue-Hans_transcribe",
    # "yue-Hans_diff",
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
if "yue-Hant" in actions:
    zho_hant = Series.load(zho_hant_ocr_path / "fuse_clean_validate_review.srt")
    yue_hant = Series.load(input_path / "yue-Hant.srt")
    yue_hant_review = review_yue(
        yue_hant,
        yue_hant_path / "review.srt",
        BlockReviewPromptZhoHant,
    )
    yue_hant_timewarp = get_series_timewarped(
        zho_hant, yue_hant_review, one_end_idx=1421, two_end_idx=1461
    )
    yue_hant_timewarp.save(yue_hant_path / "review_timewarp.srt")
    clean = get_zho_cleaned(yue_hant_timewarp)
    clean.save(yue_hant_path / "review_timewarp_clean.srt")
    flatten = get_zho_flattened(clean)
    flatten.save(yue_hant_path / "review_timewarp_clean_flatten.srt")
    simplify = get_zho_converted(flatten, OpenCCConfig.t2s)
    simplify.save(yue_hant_path / "review_timewarp_clean_flatten_simplify.srt")
    simplify_review = review_yue(
        simplify,
        yue_hant_path / "review_timewarp_clean_flatten_simplify_review.srt",
        BlockReviewPromptZhoHans,
        test_case_name="simplify_block_review.json",
    )
    simplify_romanized = get_yue_romanized(simplify_review, append=True)
    simplify_romanized.save(
        yue_hant_path / "review_timewarp_clean_flatten_simplify_review_romanize.srt"
    )
if "yue-Hans" in actions:
    zho_hant = Series.load(zho_hant_ocr_path / "fuse_clean_validate_review.srt")
    yue_hans = Series.load(input_path / "yue-Hans.srt")
    yue_hans_review = review_yue(
        yue_hans,
        yue_hans_path / "review.srt",
        BlockReviewPromptZhoHans,
    )
    yue_hans_timewarp = get_series_timewarped(
        zho_hant, yue_hans_review, one_end_idx=1421, two_end_idx=1461
    )
    yue_hans_timewarp.save(yue_hans_path / "review_timewarp.srt")
    yue_hans_clean = get_zho_cleaned(yue_hans_timewarp)
    yue_hans_clean.save(yue_hans_path / "review_timewarp_clean.srt")
    yue_hans_reference = get_zho_flattened(yue_hans_clean)
    yue_hans_reference.save(yue_hans_path / "review_timewarp_clean_flatten.srt")
    yue_hans_romanized = get_yue_romanized(yue_hans_reference, append=True)
    yue_hans_romanized.save(
        yue_hans_path / "review_timewarp_clean_flatten_romanize.srt"
    )
if "eng" in actions:
    eng_ocr = Series.load(eng_ocr_path / "fuse_clean_validate_review.srt")
    eng_srt = Series.load(input_path / "eng.srt")
    eng_timewarp = get_series_timewarped(eng_ocr, eng_srt, one_end_idx=1421)
    eng_timewarp.save(eng_path / "timewarp.srt")
    eng_clean = get_eng_cleaned(eng_timewarp)
    eng_clean.save(eng_path / "timewarp_clean.srt")
    eng_proofreader = get_eng_block_reviewer(
        test_case_path=eng_path / "lang/eng/block_review.json",
        auto_verify=True,
    )
    eng_proofread = get_eng_block_reviewed(eng_clean, eng_proofreader)
    eng_proofread.save(eng_path / "timewarp_clean_review.srt")
    eng_flatten = get_eng_flattened(eng_proofread)
    eng_flatten.save(eng_path / "timewarp_clean_review_flatten.srt")
if "yue-Hans_eng" in actions:
    yue_hans_srt_path = yue_hans_path / "review_timewarp_clean_flatten.srt"
    eng_srt_path = eng_path / "timewarp_clean_review_flatten.srt"
    process_yue_hans_eng(title_root, yue_hans_srt_path, eng_srt_path, overwrite=True)
if "yue-Hans_transcribe" in actions:
    zh_hant_path = zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt"
    zho_hans_path = (
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    simplified_reference_path = yue_hans_path / "review_timewarp_clean_flatten.srt"
    traditional_reference_path = yue_hant_path / "review_timewarp_clean_flatten.srt"
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
            "convert": OpenCCConfig.hk2s,
            "deliniation_prompt_cls": YueDeliniationVsZhoPromptYueHans,
            "punctuation_prompt_cls": YuePunctuationVsZhoPromptYueHans,
        },
        line_reviewer_kw={"prompt_cls": YueLineReviewVsZhoPromptYueHans},
        translator_kw={"prompt_cls": YueGappedTranslationVsZhoPromptYueHans},
        block_reviewer_kw={"prompt_cls": YueBlockReviewVsZhoPromptYueHans},
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
            "convert": OpenCCConfig.s2hk,
            "deliniation_prompt_cls": YueDeliniationVsZhoPromptYueHant,
            "punctuation_prompt_cls": YuePunctuationVsZhoPromptYueHant,
        },
        line_reviewer_kw={"prompt_cls": YueLineReviewVsZhoPromptYueHant},
        translator_kw={"prompt_cls": YueGappedTranslationVsZhoPromptYueHant},
        block_reviewer_kw={"prompt_cls": YueBlockReviewVsZhoPromptYueHant},
        overwrite_srt=False,
    )
if "yue-Hans_diff" in actions:
    # yue_hans_transcribe = Series.load(
    #     yue_hans_transcribe_path / "test_simplified/transcribe.srt"
    # )
    yue_hans_transcribe = Series.load(
        yue_hans_transcribe_path
        / "test_simplified"
        / "transcribe_review_translate_block_review.srt"
    )
    yue_hans_reference = Series.load(
        yue_hans_path / "review_timewarp_clean_flatten.srt"
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
    print(diff)
    print(diff.get_stacked_str(three=zho_hans_reference, include_equal=True))
    print(SeriesCER(yue_hans_reference, yue_hans_transcribe))
