#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from pytest import fixture

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.lang.yue_zho.review import YueZhoGuidedReviewPromptYueHans
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHans,
    YueZhoPunctuationPromptYueHans,
)
from scinoephile.lang.yue_zho.translation import (
    YueZhoGapTranslationPromptYueHans,
)
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.lang.zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant
from scinoephile.llms.delineation import DelineationManager, DelineationPrompt
from scinoephile.llms.gap_translation import (
    GapTranslationManager,
    GapTranslationPrompt,
)
from scinoephile.llms.guided_review import GuidedReviewManager, GuidedReviewPrompt
from scinoephile.llms.ocr_fusion import OcrFusionManager, OcrFusionPrompt
from scinoephile.llms.punctuation import PunctuationManager, PunctuationPrompt
from scinoephile.llms.review import ReviewManager, ReviewPrompt
from test.helpers import test_data_root

__all__ = [
    "mlamd_eng_ocr_sup_path",
    "mlamd_zho_hans_ocr_sup_path",
    "mlamd_zho_hant_ocr_sup_path",
    "get_mlamd_eng_ocr_fusion_test_cases",
    "get_mlamd_eng_review_test_cases",
    "get_mlamd_yue_delineation_test_cases",
    "get_mlamd_yue_from_zho_gap_translation_test_cases",
    "get_mlamd_yue_punctuation_test_cases",
    "get_mlamd_yue_vs_zho_guided_review_test_cases",
    "get_mlamd_zho_hans_ocr_fusion_test_cases",
    "get_mlamd_zho_hans_review_test_cases",
    "get_mlamd_zho_hant_ocr_fusion_test_cases",
    "get_mlamd_zho_hant_review_test_cases",
    "get_mlamd_zho_hant_simplify_review_test_cases",
    "mlamd_eng_fuse",
    "mlamd_eng_fuse_clean",
    "mlamd_eng_fuse_clean_validate",
    "mlamd_eng_fuse_clean_validate_review",
    "mlamd_eng_fuse_clean_validate_review_flatten",
    "mlamd_eng_image",
    "mlamd_eng_image_path",
    "mlamd_eng_ocr_lens",
    "mlamd_eng_ocr_lens_clean",
    "mlamd_eng_ocr_tesseract",
    "mlamd_eng_ocr_tesseract_clean",
    "mlamd_yue_hans_audio",
    "mlamd_yue_hans_audio_path",
    "mlamd_yue_hans_eng",
    "mlamd_yue_hans_transcribe",
    "mlamd_yue_hans_transcribe_translate",
    "mlamd_yue_hans_transcribe_translate_guided_review",
    "mlamd_yue_hans_transcribe_translation_input",
    "mlamd_zho_hans_eng",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_clean",
    "mlamd_zho_hans_fuse_clean_validate",
    "mlamd_zho_hans_fuse_clean_validate_review",
    "mlamd_zho_hans_fuse_clean_validate_review_flatten",
    "mlamd_zho_hans_fuse_clean_validate_review_flatten_merged_539",
    "mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_image_path",
    "mlamd_zho_hans_ocr_lens",
    "mlamd_zho_hans_ocr_lens_clean",
    "mlamd_zho_hans_ocr_paddle",
    "mlamd_zho_hans_ocr_paddle_clean",
    "mlamd_zho_hant_fuse",
    "mlamd_zho_hant_fuse_clean",
    "mlamd_zho_hant_fuse_clean_validate",
    "mlamd_zho_hant_fuse_clean_validate_review",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_image_path",
    "mlamd_zho_hant_ocr_lens",
    "mlamd_zho_hant_ocr_lens_clean",
    "mlamd_zho_hant_ocr_paddle",
    "mlamd_zho_hant_ocr_paddle_clean",
    "mlamd_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@fixture
def mlamd_eng_ocr_sup_path() -> Path:
    """Path to MLAMD English SUP subtitles."""
    return input_dir / "eng_ocr/source.sup"


@fixture
def mlamd_zho_hans_ocr_sup_path() -> Path:
    """Path to MLAMD zho-Hans SUP subtitles."""
    return input_dir / "zho-Hans_ocr/source.sup"


@fixture
def mlamd_zho_hant_ocr_sup_path() -> Path:
    """Path to MLAMD zho-Hant SUP subtitles."""
    return input_dir / "zho-Hant_ocr/source.sup"


@cache
def get_mlamd_eng_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_eng_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptEng, **kwargs: Any
) -> list[TestCase]:
    """Get MLAMD English review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_yue_delineation_test_cases(
    prompt: DelineationPrompt = YueZhoDelineationPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD yue-Hans delineation test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "lang"
        / "yue_zho"
        / "transcription"
        / "delineation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(path, DelineationManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_yue_from_zho_gap_translation_test_cases(
    prompt: GapTranslationPrompt = YueZhoGapTranslationPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD yue-Hans from zho-Hans gap translation test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "lang"
        / "yue_zho"
        / "gap_translation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, GapTranslationManager, prompt=prompt, **kwargs
    )


@cache
def get_mlamd_yue_punctuation_test_cases(
    prompt: PunctuationPrompt = YueZhoPunctuationPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD yue-Hans punctuation test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "lang"
        / "yue_zho"
        / "transcription"
        / "punctuation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(path, PunctuationManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_yue_vs_zho_guided_review_test_cases(
    prompt: GuidedReviewPrompt = YueZhoGuidedReviewPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD yue-Hans vs zho-Hans guided review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "lang"
        / "yue_zho"
        / "guided_review"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(path, GuidedReviewManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_zho_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD zho-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_zho_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get MLAMD zho-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_zho_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD zho-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_zho_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHant, **kwargs: Any
) -> list[TestCase]:
    """Get MLAMD zho-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_mlamd_zho_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get MLAMD zho-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@fixture
def mlamd_eng_fuse() -> Series:
    """MLAMD English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@fixture
def mlamd_eng_fuse_clean() -> Series:
    """MLAMD English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@fixture
def mlamd_eng_fuse_clean_validate() -> Series:
    """MLAMD English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@fixture
def mlamd_eng_fuse_clean_validate_review() -> Series:
    """MLAMD English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@fixture
def mlamd_eng_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@fixture
def mlamd_eng_image() -> ImageSeries:
    """MLAMD English image subtitles."""
    return ImageSeries.load(output_dir / "eng_ocr/image", encoding="utf-8")


@fixture
def mlamd_eng_image_path() -> Path:
    """Path to MLAMD English image subtitles."""
    return output_dir / "eng_ocr/image"


@fixture
def mlamd_eng_ocr_lens() -> Series:
    """MLAMD English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@fixture
def mlamd_eng_ocr_lens_clean() -> Series:
    """MLAMD English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@fixture
def mlamd_eng_ocr_tesseract() -> Series:
    """MLAMD English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@fixture
def mlamd_eng_ocr_tesseract_clean() -> Series:
    """MLAMD English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@fixture
def mlamd_yue_hans_audio() -> AudioSeries:
    """MLAMD yue-Hans audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_transcribe/audio")


@fixture
def mlamd_yue_hans_audio_path() -> Path:
    """Path to MLAMD yue-Hans audio subtitles."""
    return output_dir / "yue-Hans_transcribe/audio"


@fixture
def mlamd_yue_hans_eng() -> Series:
    """MLAMD Bilingual yue-Hans and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def mlamd_yue_hans_transcribe() -> Series:
    """MLAMD yue-Hans transcribed subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe/transcribe.srt")


@fixture
def mlamd_yue_hans_transcribe_translation_input() -> Series:
    """MLAMD yue-Hans transcription curated as gap-translation input."""
    return Series.load(
        output_dir / "yue-Hans_transcribe/transcribe_translation_input.srt"
    )


@fixture
def mlamd_yue_hans_transcribe_translate() -> Series:
    """MLAMD yue-Hans transcribed and gap-translated subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe/transcribe_translate.srt")


@fixture
def mlamd_yue_hans_transcribe_translate_guided_review() -> Series:
    """MLAMD yue-Hans transcribed, gap-translated, and guided-reviewed subtitles."""
    return Series.load(
        output_dir / "yue-Hans_transcribe" / "transcribe_translate_guided_review.srt"
    )


@fixture
def mlamd_zho_hans_eng() -> Series:
    """MLAMD Bilingual zho-Hans and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD zho-Hans fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def mlamd_zho_hans_fuse_clean() -> Series:
    """MLAMD zho-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate() -> Series:
    """MLAMD zho-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate_review() -> Series:
    """MLAMD zho-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD zho-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten_merged_539(
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
) -> Series:
    """MLAMD zho-Hans flattened subtitles with subtitle 539 merged."""
    return get_series_with_subs_merged(
        mlamd_zho_hans_fuse_clean_validate_review_flatten,
        539,
    )


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize() -> Series:
    """MLAMD zho-Hans fused/cleaned/validated/reviewed/flattened romanized subs."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def mlamd_zho_hans_image() -> ImageSeries:
    """MLAMD zho-Hans image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_ocr/image", encoding="utf-8")


@fixture
def mlamd_zho_hans_image_path() -> Path:
    """Path to MLAMD zho-Hans image subtitles."""
    return output_dir / "zho-Hans_ocr/image"


@fixture
def mlamd_zho_hans_ocr_lens() -> Series:
    """MLAMD zho-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def mlamd_zho_hans_ocr_lens_clean() -> Series:
    """MLAMD zho-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def mlamd_zho_hans_ocr_paddle() -> Series:
    """MLAMD zho-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def mlamd_zho_hans_ocr_paddle_clean() -> Series:
    """MLAMD zho-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def mlamd_zho_hant_fuse() -> Series:
    """MLAMD zho-Hant fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def mlamd_zho_hant_fuse_clean() -> Series:
    """MLAMD zho-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate() -> Series:
    """MLAMD zho-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate_review() -> Series:
    """MLAMD zho-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD zho-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify() -> Series:
    """MLAMD zho-Hant simplified fused/cleaned/validated/reviewed/flattened subs."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """MLAMD zho-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """MLAMD zho-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def mlamd_zho_hant_image() -> ImageSeries:
    """MLAMD zho-Hant image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_ocr/image", encoding="utf-8")


@fixture
def mlamd_zho_hant_image_path() -> Path:
    """Path to MLAMD zho-Hant image subtitles."""
    return output_dir / "zho-Hant_ocr/image"


@fixture
def mlamd_zho_hant_ocr_lens() -> Series:
    """MLAMD zho-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def mlamd_zho_hant_ocr_lens_clean() -> Series:
    """MLAMD zho-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def mlamd_zho_hant_ocr_paddle() -> Series:
    """MLAMD zho-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def mlamd_zho_hant_ocr_paddle_clean() -> Series:
    """MLAMD zho-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def mlamd_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for MLAMD Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[90] -> TRAD[90]: '就是有点游魂的 Miss Chan' -> '就是有点游魂的Miss Chan'",
        "edit: SIMP[161] -> TRAD[161]: '看著自己每天屙烂煮⋯' -> '看着自己每天屙烂煮⋯'",
        "edit: SIMP[175] -> TRAD[175]: '这位喊得特劲的中年母猪' -> '这位喊得特劲的中年母豬'",
        "edit: SIMP[180] -> TRAD[180]: '除了兼任保险，地产经纪及 trading⋯' -> '除了兼任保险，地产经纪及trading⋯'",
        "edit: SIMP[227] -> TRAD[227]: '他扭了脚骹！' -> '他扭了脚骸！'",
        "edit: SIMP[420] -> TRAD[420]: '脚趾甲有一寸厚，究竟⋯' -> '脚趾甲有一吋厚，究竟⋯'",
        "edit: SIMP[461] -> TRAD[461]: '不成了！我的脚瓜太痹了！' -> '不成了！我的脚瓜太痺了！'",
        "edit: SIMP[551] -> TRAD[551]: '黎根接著说了一大堆话⋯' -> '黎根接着说了一大堆话⋯'",
        "edit: SIMP[566] -> TRAD[566]: '脚趾甲有一寸厚，究竟⋯' -> '脚趾甲有一吋厚，究竟⋯'",
        "edit: SIMP[579] -> TRAD[579]: '难道⋯\\u3000不会吧？' -> '难道⋯不会吧？'",
        "edit: SIMP[580] -> TRAD[580]: '想不到真的让妈妈拿去了．吓得我！' -> '想不到真的让妈妈拿去了，吓得我！'",
        "edit: SIMP[665] -> TRAD[665]: '连它的气味也没嗅过' -> '连牠的气味也没嗅过'",
        "edit: SIMP[674] -> TRAD[674]: '让我们明天去超级市场揪火鸡' -> '让我们明天去超级市场拣火鸡'",
        "edit: SIMP[675] -> TRAD[675]: '我跟妈妈把火鸡揪回家的路上⋯' -> '我跟妈妈把火鸡拣回家的路上⋯'",
        "edit: SIMP[680] -> TRAD[680]: '联火鸡时⋯' -> '烚火鸡时⋯'",
        "edit: SIMP[709] -> TRAD[709]: '上面淋了老抽生粉献' -> '上面淋了老抽生粉芡'",
        "edit: SIMP[723] -> TRAD[723]: '栗子炆火鸡丝㷛' -> '栗子\\u3000\\u3000火鸡丝㷛'",
        "edit: SIMP[724] -> TRAD[724]: '花生火鸡骨煲粥' -> '花生火鸡骨㷛粥'",
        "edit: SIMP[730] -> TRAD[730]: '发现咸蛋旁边是一件火鸡背的时候⋯' -> '发现咸蛋旁边是一件火鸡背脊的时候⋯'",
        "edit: SIMP[740] -> TRAD[740]: '还要长过它的一生' -> '还要长过牠的一生'",
        "edit: SIMP[753] -> TRAD[753]: '那天，我看着天空几缕灰色的烟' -> '那天，我看著天空几缕灰色的烟'",
        "edit: SIMP[847] -> TRAD[847]: '足有一寸厚' -> '足有一吋厚'",
        "edit: SIMP[855] -> TRAD[855]: '可是楝一双脚瓜站这儿⋯' -> '可是冻一双脚瓜站这儿⋯'",
    ]
