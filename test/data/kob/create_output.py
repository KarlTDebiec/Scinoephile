#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis import get_series_cer
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import get_backend
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
from scinoephile.multilang.yue_zho import (
    get_yue_block_reviewed_vs_zho,
    get_yue_line_reviewed_vs_zho,
    get_yue_transcribed_vs_zho,
    get_yue_translated_vs_zho,
)
from scinoephile.multilang.yue_zho.block_review import get_yue_vs_zho_block_reviewer
from scinoephile.multilang.yue_zho.line_review import get_yue_vs_zho_line_reviewer
from scinoephile.multilang.yue_zho.transcription import (
    DemucsMode,
    VADMode,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.translation import get_yue_vs_zho_translator
from test.conftest import get_mlamd_yue_deliniation_test_cases
from test.data.mlamd import get_mlamd_yue_punctuation_test_cases
from test.data.ocr import process_eng_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    # "繁體中文 (OCR)",
    # "English (OCR)",
    # "Bilingual 繁體中文 and English",
    # "繁體粵文 (SRT)",
    # "简体粤文 (SRT)",
    # "English (SRT)",
    # "Bilingual 简体粤文 and English",
    # "简体粤文 (Transcription)",
    # "简体粤文 (Diff)",
    # "简体粤文 (Transcription Test VAD Off)",
    # "简体粤文 (Transcription Test VAD On)",
    "简体粤文 (Transcription Test Demucs On VAD Auto)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(title_root, overwrite_srt=False, force_validation=False)
if "English (OCR)" in actions:
    reviewer_kw = dict(
        test_case_path=title_root / "lang" / "eng" / "block_review" / "eng_ocr.json",
    )
    process_eng_ocr(
        title_root,
        reviewer_kw=reviewer_kw,
        overwrite_srt=True,
        force_validation=True,
    )
if "Bilingual 繁體中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir
        / "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_review_flatten.srt",
        overwrite=True,
    )
if "繁體粵文 (SRT)" in actions:
    zho_hant = Series.load(output_dir / "zho-Hant_fuse_clean_validate_review.srt")
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_timewarp = get_series_timewarped(
        zho_hant, yue_hant, one_end_idx=1421, two_end_idx=1461
    )
    yue_hant_timewarp.save(output_dir / "yue-Hant_timewarp.srt")
    clean = get_zho_cleaned(yue_hant_timewarp)
    clean.save(output_dir / "yue-Hant_timewarp_clean.srt")
    flatten = get_zho_flattened(clean)
    flatten.save(output_dir / "yue-Hant_timewarp_clean_flatten.srt")
if "简体粤文 (SRT)" in actions:
    zho_hant = Series.load(output_dir / "zho-Hant_fuse_clean_validate_review.srt")
    yue_hans = Series.load(input_dir / "yue-Hans.srt")
    yue_hans_timewarp = get_series_timewarped(
        zho_hant, yue_hans, one_end_idx=1421, two_end_idx=1461
    )
    yue_hans_timewarp.save(output_dir / "yue-Hans_timewarp.srt")
    yue_hans_clean = get_zho_cleaned(yue_hans_timewarp)
    yue_hans_clean.save(output_dir / "yue-Hans_timewarp_clean.srt")
    yue_hans_reference = get_zho_flattened(yue_hans_clean)
    yue_hans_reference.save(output_dir / "yue-Hans_timewarp_clean_flatten.srt")
    yue_hans_romanized = get_yue_romanized(yue_hans_reference, append=True)
    yue_hans_romanized.save(output_dir / "yue-Hans_timewarp_clean_flatten_romanize.srt")
if "English (SRT)" in actions:
    eng_ocr = Series.load(output_dir / "eng_fuse_clean_validate_review.srt")
    eng_srt = Series.load(input_dir / "eng.srt")
    eng_timewarp = get_series_timewarped(eng_ocr, eng_srt, one_end_idx=1421)
    eng_timewarp.save(output_dir / "eng_timewarp.srt")
    eng_clean = get_eng_cleaned(eng_timewarp)
    eng_clean.save(output_dir / "eng_timewarp_clean.srt")
    eng_proofreader = get_eng_block_reviewer(
        test_case_path=title_root / "lang" / "eng" / "block_review" / "eng_srt.json",
        auto_verify=True,
    )
    eng_proofread = get_eng_block_reviewed(eng_clean, eng_proofreader)
    eng_proofread.save(output_dir / "eng_timewarp_clean_review.srt")
    eng_flatten = get_eng_flattened(eng_proofread)
    eng_flatten.save(output_dir / "eng_timewarp_clean_review_flatten.srt")
if "Bilingual 简体粤文 and English" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=output_dir / "yue-Hans_timewarp_clean_flatten.srt",
        eng_path=output_dir / "eng_timewarp_clean_review_flatten.srt",
        overwrite=True,
    )
if "简体粤文 (Transcription)" in actions:
    # Stage
    zho_hans = Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")
    yue_hans_reference = Series.load(output_dir / "yue-Hans_timewarp_clean_flatten.srt")

    # Transcribe
    yue_hans_audio = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = get_yue_vs_zho_transcriber(
        test_case_directory_path=(
            title_root / "multilang" / "yue_zho" / "transcription"
        ),
        deliniation_test_cases=get_mlamd_yue_deliniation_test_cases(),
        punctuation_test_cases=get_mlamd_yue_punctuation_test_cases(),
        vad_mode=VADMode.AUTO,
    )
    yue_hans_transcribe = get_yue_transcribed_vs_zho(
        yue_hans_audio, zho_hans, transcriber=transcriber
    )
    outfile_path = output_dir / "yue-Hans_transcribe.srt"
    yue_hans_transcribe.save(outfile_path)
    print("VAD Auto transcription CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe))

    # Review (line-by-line)
    yue_hans_transcribe = Series.load(outfile_path)
    line_reviewer = get_yue_vs_zho_line_reviewer(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "line_review"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_transcribe_review = get_yue_line_reviewed_vs_zho(
        yue_hans_transcribe, zho_hans, processor=line_reviewer
    )
    outfile_path = output_dir / "yue-Hans_transcribe_review.srt"
    yue_hans_transcribe_review.save(outfile_path)
    print("VAD Auto transcription -> line review CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe_review))

    # Translate
    translator = get_yue_vs_zho_translator(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "translation"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_transcribe_review_translate = get_yue_translated_vs_zho(
        yue_hans_transcribe_review, zho_hans, translator=translator
    )
    outfile_path = output_dir / "yue-Hans_transcribe_review_translate.srt"
    yue_hans_transcribe_review_translate.save(outfile_path)
    print("VAD Auto transcription -> line review -> translate CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe_review_translate))

    # Review (block-by-block)
    reviewer = get_yue_vs_zho_block_reviewer(
        test_case_path=title_root
        / "multilang"
        / "yue_zho"
        / "block_review"
        / f"{get_backend()}.json",
        auto_verify=True,
    )
    yue_hans_transcribe_review_translate_block_review = get_yue_block_reviewed_vs_zho(
        yue_hans_transcribe_review_translate, zho_hans, reviewer=reviewer
    )
    outfile_path = output_dir / "yue-Hans_transcribe_review_translate_block_review.srt"
    yue_hans_transcribe_review_translate_block_review.save(outfile_path)
    print("VAD Auto transcription -> line review -> translate -> review CER:")
    print(
        get_series_cer(
            yue_hans_reference, yue_hans_transcribe_review_translate_block_review
        )
    )

if "简体粤文 (Transcription Test VAD Off)" in actions:
    # Stage
    yue_hans_reference = Series.load(output_dir / "yue-Hans_timewarp_clean_flatten.srt")
    zho_hans = Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")

    yue_hans_audio = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = get_yue_vs_zho_transcriber(
        test_case_directory_path=(
            title_root / "multilang" / "yue_zho" / "transcription"
        ),
        vad_mode=VADMode.OFF,
        deliniation_test_cases=get_mlamd_yue_deliniation_test_cases(),
        punctuation_test_cases=get_mlamd_yue_punctuation_test_cases(),
    )
    yue_hans_transcribe = get_yue_transcribed_vs_zho(
        yue_hans_audio, zho_hans, transcriber=transcriber
    )
    print("VAD Off transcription CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe))

if "简体粤文 (Transcription Test VAD On)" in actions:
    yue_hans_reference = Series.load(output_dir / "yue-Hans_timewarp_clean_flatten.srt")
    zho_hans = Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")

    yue_hans_audio = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = get_yue_vs_zho_transcriber(
        test_case_directory_path=(
            title_root / "multilang" / "yue_zho" / "transcription"
        ),
        deliniation_test_cases=get_mlamd_yue_deliniation_test_cases(),
        punctuation_test_cases=get_mlamd_yue_punctuation_test_cases(),
        vad_mode=VADMode.ON,
    )
    yue_hans_transcribe = get_yue_transcribed_vs_zho(
        yue_hans_audio, zho_hans, transcriber=transcriber
    )
    print("VAD On transcription CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe))

if "简体粤文 (Transcription Test Demucs On VAD Auto)" in actions:
    yue_hans_reference = Series.load(output_dir / "yue-Hans_timewarp_clean_flatten.srt")
    zho_hans = Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    zho_hans.save(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")

    yue_hans_audio = AudioSeries.load(output_dir / "yue-Hans_audio")
    transcriber = get_yue_vs_zho_transcriber(
        test_case_directory_path=(
            title_root / "multilang" / "yue_zho" / "transcription"
        ),
        deliniation_test_cases=get_mlamd_yue_deliniation_test_cases(),
        punctuation_test_cases=get_mlamd_yue_punctuation_test_cases(),
        demucs_mode=DemucsMode.ON,
        vad_mode=VADMode.AUTO,
    )
    yue_hans_transcribe = get_yue_transcribed_vs_zho(
        yue_hans_audio, zho_hans, transcriber=transcriber
    )
    print("Demucs On VAD Auto transcription CER:")
    print(get_series_cer(yue_hans_reference, yue_hans_transcribe))
