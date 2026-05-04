#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.block_review import EngBlockReviewPrompt
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.zho.block_review import (
    ZhoHansBlockReviewPrompt,
    ZhoHantBlockReviewPrompt,
)
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.llms.dual_block import DualBlockManager, DualBlockPrompt
from scinoephile.llms.dual_block_gapped import (
    DualBlockGappedManager,
    DualBlockGappedPrompt,
)
from scinoephile.llms.dual_multi_single import DualMultiSinglePrompt
from scinoephile.llms.dual_pair import DualPairManager, DualPairPrompt
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from scinoephile.multilang.yue_zho.block_review import YueVsZhoYueHansBlockReviewPrompt
from scinoephile.multilang.yue_zho.line_review import (
    YueVsZhoYueHansLineReviewPrompt,
    YueZhoLineReviewManager,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueVsZhoYueHansDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueVsZhoYueHansPunctuationPrompt,
    YueZhoPunctuationManager,
)
from scinoephile.multilang.yue_zho.translation import YueVsZhoYueHansTranslationPrompt
from test.helpers import test_data_root

__all__ = [
    "mlamd_eng_ocr_lens",
    "mlamd_eng_ocr_sup_path",
    "mlamd_eng_ocr_tesseract",
    "mlamd_zho_hans_ocr_lens",
    "mlamd_zho_hans_ocr_paddle",
    "mlamd_zho_hans_ocr_sup_path",
    "mlamd_zho_hant_ocr_lens",
    "mlamd_zho_hant_ocr_paddle",
    "mlamd_zho_hant_ocr_sup_path",
    "get_mlamd_eng_block_review_test_cases",
    "get_mlamd_eng_ocr_fusion_test_cases",
    "get_mlamd_yue_deliniation_test_cases",
    "get_mlamd_yue_from_zho_translation_test_cases",
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
    "mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_image_path",
    "mlamd_zho_hant_fuse",
    "mlamd_zho_hant_fuse_clean",
    "mlamd_zho_hant_fuse_clean_validate",
    "mlamd_zho_hant_fuse_clean_validate_review",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify",
    "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_image_path",
    "mlamd_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def mlamd_eng_ocr_lens() -> Series:
    """MLAMD English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_ocr" / "lens.srt")


@pytest.fixture
def mlamd_eng_ocr_sup_path() -> Path:
    """Path to MLAMD English SUP subtitles."""
    return input_dir / "eng_ocr" / "source.sup"


@pytest.fixture
def mlamd_eng_ocr_tesseract() -> Series:
    """MLAMD English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_ocr" / "tesseract.srt")


@pytest.fixture
def mlamd_zho_hans_ocr_lens() -> Series:
    """MLAMD 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_ocr" / "lens.srt")


@pytest.fixture
def mlamd_zho_hans_ocr_paddle() -> Series:
    """MLAMD 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_ocr" / "paddle.srt")


@pytest.fixture
def mlamd_zho_hans_ocr_sup_path() -> Path:
    """Path to MLAMD 简体中文 SUP subtitles."""
    return input_dir / "zho-Hans_ocr" / "source.sup"


@pytest.fixture
def mlamd_zho_hant_ocr_lens() -> Series:
    """MLAMD 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_ocr" / "lens.srt")


@pytest.fixture
def mlamd_zho_hant_ocr_paddle() -> Series:
    """MLAMD 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_ocr" / "paddle.srt")


@pytest.fixture
def mlamd_zho_hant_ocr_sup_path() -> Path:
    """Path to MLAMD 繁体中文 SUP subtitles."""
    return input_dir / "zho-Hant_ocr" / "source.sup"


@cache
def get_mlamd_eng_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr" / "lang" / "eng" / "block_review.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr" / "lang" / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_deliniation_test_cases(
    prompt_cls: type[DualPairPrompt] = YueVsZhoYueHansDeliniationPrompt,
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
        path, DualPairManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_from_zho_translation_test_cases(
    prompt_cls: type[DualBlockGappedPrompt] = YueVsZhoYueHansTranslationPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体粤文 from 简体中文 translation test cases.

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
        / "translation"
        / f"{get_torch_device()}.json"
    )
    return load_test_cases_from_json(
        path, DualBlockGappedManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_punctuation_test_cases(
    prompt_cls: type[DualMultiSinglePrompt] = YueVsZhoYueHansPunctuationPrompt,
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
    prompt_cls: type[DualBlockPrompt] = YueVsZhoYueHansBlockReviewPrompt,
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
        path, DualBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_line_review_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueVsZhoYueHansLineReviewPrompt,
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
    prompt_cls: type[MonoBlockPrompt] = ZhoHansBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr" / "lang" / "zho" / "block_review.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 简体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr" / "lang" / "zho" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr" / "lang" / "zho" / "block_review.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr" / "lang" / "zho" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 繁体中文 simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr" / "lang" / "zho" / "simplify_block_review.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@pytest.fixture
def mlamd_eng_fuse() -> Series:
    """MLAMD English fused subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse.srt")


@pytest.fixture
def mlamd_eng_fuse_clean() -> Series:
    """MLAMD English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate() -> Series:
    """MLAMD English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate_review() -> Series:
    """MLAMD English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "eng_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mlamd_eng_image() -> ImageSeries:
    """MLAMD English image subtitles."""
    return ImageSeries.load(output_dir / "eng_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mlamd_eng_image_path() -> Path:
    """Path to MLAMD English image subtitles."""
    return output_dir / "eng_ocr" / "image"


@pytest.fixture
def mlamd_yue_hans_audio() -> AudioSeries:
    """MLAMD 简体粤文 audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_transcribe" / "audio")


@pytest.fixture
def mlamd_yue_hans_audio_path() -> Path:
    """Path to MLAMD 简体粤文 audio subtitles."""
    return output_dir / "yue-Hans_transcribe" / "audio"


@pytest.fixture
def mlamd_yue_hans_eng() -> Series:
    """MLAMD Bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@pytest.fixture
def mlamd_yue_hans_transcribe() -> Series:
    """MLAMD 简体粤文 transcribed subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe" / "transcribe.srt")


@pytest.fixture
def mlamd_yue_hans_transcribe_review() -> Series:
    """MLAMD 简体粤文 transcribed and line reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_transcribe" / "transcribe_review.srt")


@pytest.fixture
def mlamd_yue_hans_transcribe_review_translate() -> Series:
    """MLAMD 简体粤文 transcribed, line reviewed, and translated subtitles."""
    return Series.load(
        output_dir / "yue-Hans_transcribe" / "transcribe_review_translate.srt"
    )


@pytest.fixture
def mlamd_yue_hans_transcribe_review_translate_block_review() -> Series:
    """MLAMD 简体粤文 transcribed, line reviewed, translated, and block reviewed subtitles."""
    return Series.load(
        output_dir
        / "yue-Hans_transcribe"
        / "transcribe_review_translate_block_review.srt"
    )


@pytest.fixture
def mlamd_zho_hans_eng() -> Series:
    """MLAMD Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@pytest.fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean() -> Series:
    """MLAMD 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate() -> Series:
    """MLAMD 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_review() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize() -> Series:
    """MLAMD 简体中文 fused/cleaned/validated/reviewed/flattened romanized subs."""
    return Series.load(
        output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten_romanize.srt"
    )


@pytest.fixture
def mlamd_zho_hans_image() -> ImageSeries:
    """MLAMD 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mlamd_zho_hans_image_path() -> Path:
    """Path to MLAMD 简体中文 image subtitles."""
    return output_dir / "zho-Hans_ocr" / "image"


@pytest.fixture
def mlamd_zho_hant_fuse() -> Series:
    """MLAMD 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean() -> Series:
    """MLAMD 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate() -> Series:
    """MLAMD 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_review() -> Series:
    """MLAMD 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten() -> Series:
    """MLAMD 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify() -> Series:
    """MLAMD 繁体中文 simplified fused/cleaned/validated/reviewed/flattened subs."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """MLAMD 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@pytest.fixture
def mlamd_zho_hant_image() -> ImageSeries:
    """MLAMD 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mlamd_zho_hant_image_path() -> Path:
    """Path to MLAMD 繁体中文 image subtitles."""
    return output_dir / "zho-Hant_ocr" / "image"


@pytest.fixture
def mlamd_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for MLAMD Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[178] -> TRAD[178]: '一个女人背起整个世界！' -> '一个女人支起整个世界！'",
        "edit: SIMP[227] -> TRAD[227]: '他扭了脚骹！' -> '他扭了脚骸！'",
        "edit: SIMP[420] -> TRAD[420]: '脚趾甲有一寸厚，究竟⋯' -> '脚趾甲有一吋厚，究竟⋯'",
        "edit: SIMP[461] -> TRAD[461]: '不成了！我的脚瓜太痹了！' -> '不成了！我的脚瓜太痺了！'",
        "edit: SIMP[551] -> TRAD[551]: '黎根接著说了一大堆话⋯' -> '黎根接着说了一大堆话⋯'",
        "edit: SIMP[566] -> TRAD[566]: '脚趾甲有一寸厚，究竟⋯' -> '脚趾甲有一吋厚，究竟⋯'",
        "edit: SIMP[579] -> TRAD[579]: '难道⋯\\u3000不会吧？' -> '难道⋯不会吧？'",
        "edit: SIMP[580] -> TRAD[580]: '想不到真的让妈妈拿去了．吓得我！' -> '想不到真的让妈妈拿去了，吓得我！'",
        "edit: SIMP[663] -> TRAD[663]: '这关于火鸡的一切，不过是我的想像' -> '这关于火鸡的一切，不过是我的想象'",
        "edit: SIMP[665] -> TRAD[665]: '连它的气味也没嗅过' -> '连牠的气味也没嗅过'",
        "edit: SIMP[678] -> TRAD[678]: '我学著妈妈，把双手涂满盐⋯' -> '我学着妈妈，把双手涂满盐⋯'",
        "edit: SIMP[680] -> TRAD[680]: '联火鸡时⋯' -> '拎火鸡时⋯'",
        "edit: SIMP[723] -> TRAD[723]: '栗子炆火鸡丝㷛' -> '栗子火鸡丝堡'",
        "edit: SIMP[847] -> TRAD[847]: '足有一寸厚' -> '足有一吋厚'",
        "edit: SIMP[855] -> TRAD[855]: '可是楝一双脚瓜站这儿⋯' -> '可是冻一双脚瓜站这儿⋯'",
    ]
