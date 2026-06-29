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
from scinoephile.lang.eng.block_review import BlockReviewPromptEng
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
)
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionManager
from scinoephile.llms.dual_2_to_2 import Dual2To2Manager, Dual2To2Prompt
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.dual_n_to_1 import DualNTo1Prompt
from scinoephile.llms.dual_n_to_n import DualNToNManager, DualNToNPrompt
from scinoephile.llms.mono_n import MonoNManager, MonoNPrompt
from scinoephile.multilang.yue_zho.block_review import YueBlockReviewVsZhoPromptYueHans
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueLineReviewVsZhoPromptYueHans,
    YueZhoLineReviewManager,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueDeliniationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YueZhoPunctuationManager,
)
from test.helpers import test_data_root

__all__ = [
    "mlamd_eng_ocr_sup_path",
    "mlamd_zho_hans_ocr_sup_path",
    "mlamd_zho_hant_ocr_sup_path",
    "get_mlamd_eng_block_review_test_cases",
    "get_mlamd_eng_ocr_fusion_test_cases",
    "get_mlamd_yue_deliniation_test_cases",
    "get_mlamd_yue_vs_zho_gapped_translation_test_cases",
    "get_mlamd_yue_punctuation_test_cases",
    "get_mlamd_yue_vs_zho_block_review_test_cases",
    "get_mlamd_yue_vs_zho_line_review_test_cases",
    "get_mlamd_zho_hans_block_review_test_cases",
    "get_mlamd_zho_hans_ocr_fusion_test_cases",
    "get_mlamd_zho_hant_block_review_test_cases",
    "get_mlamd_zho_hant_ocr_fusion_test_cases",
    "get_mlamd_zho_hant_simplify_block_review_test_cases",
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
    "mlamd_yue_hans_transcribe_review",
    "mlamd_yue_hans_transcribe_review_translate",
    "mlamd_yue_hans_transcribe_review_translate_block_review",
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
    """Path to MLAMD 简体中文 SUP subtitles."""
    return input_dir / "zho-Hans_ocr/source.sup"


@fixture
def mlamd_zho_hant_ocr_sup_path() -> Path:
    """Path to MLAMD 繁体中文 SUP subtitles."""
    return input_dir / "zho-Hant_ocr/source.sup"


@cache
def get_mlamd_eng_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_deliniation_test_cases(
    prompt_cls: type[Dual2To2Prompt] = YueDeliniationVsZhoPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 deliniation test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "transcription"
        / "deliniation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, Dual2To2Manager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_gapped_translation_test_cases(
    prompt_cls: type[DualNMinusMToNPrompt] = YueGappedTranslationVsZhoPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 vs 简体中文 gapped translation test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "gap_translation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, DualNMinusMToNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_punctuation_test_cases(
    prompt_cls: type[DualNTo1Prompt] = YuePunctuationVsZhoPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 punctuation test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "transcription"
        / "punctuation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, YueZhoPunctuationManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_block_review_test_cases(
    prompt_cls: type[DualNToNPrompt] = YueBlockReviewVsZhoPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 vs 简体中文 review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "block_review"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, DualNToNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_line_review_test_cases(
    prompt_cls: type[Dual1To1Prompt] = YueLineReviewVsZhoPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 vs 简体中文 line-review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = (
        output_dir
        / "yue-Hans_transcribe"
        / "multilang"
        / "yue_zho"
        / "line_review"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, YueZhoLineReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


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
    """MLAMD 简体粤文 audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_transcribe/audio")


@fixture
def mlamd_yue_hans_audio_path() -> Path:
    """Path to MLAMD 简体粤文 audio subtitles."""
    return output_dir / "yue-Hans_transcribe/audio"


@fixture
def mlamd_yue_hans_eng() -> Series:
    """MLAMD Bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def mlamd_yue_hans_transcribe() -> Series:
    """MLAMD 简体粤文 transcribed subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe/transcribe.srt")


@fixture
def mlamd_yue_hans_transcribe_review() -> Series:
    """MLAMD 简体粤文 transcribed and line reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe/transcribe_review.srt")


@fixture
def mlamd_yue_hans_transcribe_review_translate() -> Series:
    """MLAMD 简体粤文 transcribed, line reviewed, and translated subtitles."""
    return Series.load(
        output_dir / "yue-Hans_transcribe/transcribe_review_translate.srt"
    )


@fixture
def mlamd_yue_hans_transcribe_review_translate_block_review() -> Series:
    """MLAMD 简体粤文 transcribed, line reviewed, translated, and block reviewed subtitles."""
    return Series.load(
        output_dir
        / "yue-Hans_transcribe"
        / "transcribe_review_translate_block_review.srt"
    )


@fixture
def mlamd_zho_hans_eng() -> Series:
    """MLAMD Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def mlamd_zho_hans_fuse_clean() -> Series:
    """MLAMD 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate() -> Series:
    """MLAMD 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate_review() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten_merged_539(
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
) -> Series:
    """MLAMD 简体中文 flattened subtitles with subtitle 539 merged."""
    return get_series_with_subs_merged(
        mlamd_zho_hans_fuse_clean_validate_review_flatten,
        539,
    )


@fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize() -> Series:
    """MLAMD 简体中文 fused/cleaned/validated/reviewed/flattened romanized subs."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt",
        keep_unknown_html_tags=True,
    )


@fixture
def mlamd_zho_hans_image() -> ImageSeries:
    """MLAMD 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_ocr/image", encoding="utf-8")


@fixture
def mlamd_zho_hans_image_path() -> Path:
    """Path to MLAMD 简体中文 image subtitles."""
    return output_dir / "zho-Hans_ocr/image"


@fixture
def mlamd_zho_hans_ocr_lens() -> Series:
    """MLAMD 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def mlamd_zho_hans_ocr_lens_clean() -> Series:
    """MLAMD 简体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def mlamd_zho_hans_ocr_paddle() -> Series:
    """MLAMD 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def mlamd_zho_hans_ocr_paddle_clean() -> Series:
    """MLAMD 简体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def mlamd_zho_hant_fuse() -> Series:
    """MLAMD 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def mlamd_zho_hant_fuse_clean() -> Series:
    """MLAMD 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate() -> Series:
    """MLAMD 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate_review() -> Series:
    """MLAMD 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify() -> Series:
    """MLAMD 繁体中文 simplified fused/cleaned/validated/reviewed/flattened subs."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """MLAMD 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """MLAMD 繁体中文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt",
        keep_unknown_html_tags=True,
    )


@fixture
def mlamd_zho_hant_image() -> ImageSeries:
    """MLAMD 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_ocr/image", encoding="utf-8")


@fixture
def mlamd_zho_hant_image_path() -> Path:
    """Path to MLAMD 繁体中文 image subtitles."""
    return output_dir / "zho-Hant_ocr/image"


@fixture
def mlamd_zho_hant_ocr_lens() -> Series:
    """MLAMD 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def mlamd_zho_hant_ocr_lens_clean() -> Series:
    """MLAMD 繁体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def mlamd_zho_hant_ocr_paddle() -> Series:
    """MLAMD 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def mlamd_zho_hant_ocr_paddle_clean() -> Series:
    """MLAMD 繁体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def mlamd_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for MLAMD Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[90] -> TRAD[90]: '就是有点游魂的 Miss Chan' -> '就是有点游魂的Miss Chan'",
        "edit: SIMP[125] -> TRAD[125]: '橙，为什么会是「疴－烂－煮」呢？' -> '橙，为什么会是「痾－烂－煮」呢？'",
        "edit: SIMP[127] -> TRAD[127]: '「疴」这个我明白，可是「烂－煮」呢？' -> '「痾」这个我明白，可是「烂－煮」呢？'",
        "edit: SIMP[131] -> TRAD[131]: '至多是疴烂煮，怎么会下起雨来呢？' -> '至多是痾烂煮，怎么会下起雨来呢？'",
        "edit: SIMP[161] -> TRAD[161]: '看著自己每天疴烂煮⋯' -> '看着自己每天痾烂煮⋯'",
        "edit: SIMP[167] -> TRAD[167]: '可每次我总唱成「疴」什么什么的⋯' -> '可每次我总唱成「痾」什么什么的⋯'",
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
        "edit: SIMP[683] -> TRAD[683]: '我说：火鸡「疴烂煮」！' -> '我说：火鸡「痾烂煮」！'",
        "edit: SIMP[709] -> TRAD[709]: '上面淋了老抽生粉献' -> '上面淋了老抽生粉芡'",
        "edit: SIMP[723] -> TRAD[723]: '栗子炆火鸡丝㷛' -> '栗子\\u3000\\u3000火鸡丝㷛'",
        "edit: SIMP[724] -> TRAD[724]: '花生火鸡骨煲粥' -> '花生火鸡骨㷛粥'",
        "edit: SIMP[728] -> TRAD[728]: '唉，我好后悔讲过一句「火鸡疴烂煮」' -> '唉，我好后悔讲过一句「火鸡痾烂煮」'",
        "edit: SIMP[730] -> TRAD[730]: '发现咸蛋旁边是一件火鸡背的时候⋯' -> '发现咸蛋旁边是一件火鸡背脊的时候⋯'",
        "edit: SIMP[740] -> TRAD[740]: '还要长过它的一生' -> '还要长过牠的一生'",
        "edit: SIMP[753] -> TRAD[753]: '那天，我看着天空几缕灰色的烟' -> '那天，我看著天空几缕灰色的烟'",
        "edit: SIMP[847] -> TRAD[847]: '足有一寸厚' -> '足有一吋厚'",
        "edit: SIMP[855] -> TRAD[855]: '可是楝一双脚瓜站这儿⋯' -> '可是冻一双脚瓜站这儿⋯'",
    ]
