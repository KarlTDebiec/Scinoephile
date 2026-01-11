#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
)
from scinoephile.llms.base import TestCase, load_test_cases_from_json
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
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    YueZhoProofreadingManager,
)
from scinoephile.multilang.yue_zho.review import YueHansReviewPrompt
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)
from scinoephile.multilang.yue_zho.translation import YueHansFromZhoTranslationPrompt

__all__ = [
    "mlamd_eng_lens",
    "mlamd_eng_sup_path",
    "mlamd_eng_tesseract",
    "mlamd_zho_hans_lens",
    "mlamd_zho_hans_paddle",
    "mlamd_zho_hans_sup_path",
    "mlamd_zho_hant_lens",
    "mlamd_zho_hant_paddle",
    "mlamd_zho_hant_sup_path",
    "mlamd_eng_clean",
    "mlamd_eng_fuse",
    "mlamd_eng_fuse_clean",
    "mlamd_eng_fuse_clean_validate",
    "mlamd_eng_fuse_clean_validate_proofread",
    "mlamd_eng_fuse_clean_validate_proofread_flatten",
    "mlamd_eng_image",
    "mlamd_eng_image_path",
    "mlamd_yue_hans",
    "mlamd_yue_hans_audio",
    "mlamd_yue_hans_audio_path",
    "mlamd_yue_hans_eng",
    "mlamd_yue_hans_proofread",
    "mlamd_yue_hans_proofread_translate",
    "mlamd_yue_hans_proofread_translate_review",
    "mlamd_zho_hans_eng",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_clean",
    "mlamd_zho_hans_fuse_clean_validate",
    "mlamd_zho_hans_fuse_clean_validate_proofread",
    "mlamd_zho_hans_fuse_clean_validate_proofread_flatten",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_image_path",
    "mlamd_zho_hant_fuse",
    "mlamd_zho_hant_fuse_clean",
    "mlamd_zho_hant_fuse_clean_validate",
    "mlamd_zho_hant_fuse_clean_validate_proofread",
    "mlamd_zho_hant_fuse_clean_validate_proofread_flatten",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_image_path",
    "get_mlamd_eng_ocr_fusion_test_cases",
    "get_mlamd_eng_proofreading_test_cases",
    "get_mlamd_yue_from_zho_translation_test_cases",
    "get_mlamd_yue_merging_test_cases",
    "get_mlamd_yue_shifting_test_cases",
    "get_mlamd_yue_vs_zho_proofreading_test_cases",
    "get_mlamd_yue_vs_zho_review_test_cases",
    "get_mlamd_zho_hans_ocr_fusion_test_cases",
    "get_mlamd_zho_hans_proofreading_test_cases",
    "get_mlamd_zho_hant_ocr_fusion_test_cases",
    "get_mlamd_zho_hant_proofreading_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# English (OCR input)
@pytest.fixture
def mlamd_eng_sup_path() -> Path:
    """Path to MLAMD English SUP subtitles."""
    return input_dir / "eng.sup"


@pytest.fixture
def mlamd_eng_lens() -> Series:
    """MLAMD English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def mlamd_eng_tesseract() -> Series:
    """MLAMD English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


# ???? (OCR input)
@pytest.fixture
def mlamd_zho_hans_sup_path() -> Path:
    """Path to MLAMD ???? SUP subtitles."""
    return input_dir / "zho-Hans.sup"


@pytest.fixture
def mlamd_zho_hans_lens() -> Series:
    """MLAMD ???? subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mlamd_zho_hans_paddle() -> Series:
    """MLAMD ???? subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


# ???? (OCR input)
@pytest.fixture
def mlamd_zho_hant_sup_path() -> Path:
    """Path to MLAMD ???? SUP subtitles."""
    return input_dir / "zho-Hant.sup"


@pytest.fixture
def mlamd_zho_hant_lens() -> Series:
    """MLAMD ???? subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def mlamd_zho_hant_paddle() -> Series:
    """MLAMD ???? subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


# English (Output)
@pytest.fixture
def mlamd_eng_image_path() -> Path:
    """Path to MLAMD English image subtitles."""
    return output_dir / "eng_image"


@pytest.fixture
def mlamd_eng_image() -> ImageSeries:
    """MLAMD English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def mlamd_eng_fuse() -> Series:
    """MLAMD English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def mlamd_eng_fuse_clean() -> Series:
    """MLAMD English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate() -> Series:
    """MLAMD English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate_proofread() -> Series:
    """MLAMD English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """MLAMD English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def mlamd_eng_clean() -> Series:
    """MLAMD English cleaned subtitles."""
    return Series.load(output_dir / "eng_clean.srt")


# ???? (Output)
@pytest.fixture
def mlamd_yue_hans_audio_path() -> Path:
    """Path to MLAMD ???? audio subtitles."""
    return output_dir / "yue-Hans_audio"


@pytest.fixture
def mlamd_yue_hans_audio() -> AudioSeries:
    """MLAMD ???? audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_audio")


@pytest.fixture
def mlamd_yue_hans() -> Series:
    """MLAMD ???? subtitles."""
    return Series.load(output_dir / "yue-Hans.srt")


@pytest.fixture
def mlamd_yue_hans_proofread() -> Series:
    """MLAMD ???? proofread subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread.srt")


@pytest.fixture
def mlamd_yue_hans_proofread_translate() -> Series:
    """MLAMD ???? proofread and translated subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread_translate.srt")


@pytest.fixture
def mlamd_yue_hans_proofread_translate_review() -> Series:
    """MLAMD ???? proofread, translated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread_translate_review.srt")


@pytest.fixture
def mlamd_yue_hans_eng() -> Series:
    """MLAMD Bilingual ???? and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@pytest.fixture
def mlamd_zho_hans_eng() -> Series:
    """MLAMD Bilingual ???? and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


# ???? (OCR output)
@pytest.fixture
def mlamd_zho_hans_image_path() -> Path:
    """Path to MLAMD ???? image subtitles."""
    return output_dir / "zho-Hans_image"


@pytest.fixture
def mlamd_zho_hans_image() -> ImageSeries:
    """MLAMD ???? image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_image", encoding="utf-8")


@pytest.fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD ???? fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean() -> Series:
    """MLAMD ???? fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate() -> Series:
    """MLAMD ???? fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_proofread() -> Series:
    """MLAMD ???? fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_proofread_flatten() -> Series:
    """MLAMD ???? fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def mlamd_zho_hant_image_path() -> Path:
    """Path to MLAMD ???? image subtitles."""
    return output_dir / "zho-Hant_image"


@pytest.fixture
def mlamd_zho_hant_image() -> ImageSeries:
    """MLAMD ???? image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")


@pytest.fixture
def mlamd_zho_hant_fuse() -> Series:
    """MLAMD ???? fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean() -> Series:
    """MLAMD ???? fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate() -> Series:
    """MLAMD ???? fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_proofread() -> Series:
    """MLAMD ???? fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """MLAMD ???? fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@cache
def get_mlamd_yue_shifting_test_cases(
    prompt_cls: type[DualPairPrompt] = YueZhoHansShiftingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ???? shifting test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "transcription" / "shifting.json"
    return load_test_cases_from_json(
        path, DualPairManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_merging_test_cases(
    prompt_cls: type[DualBlockGappedPrompt] = YueZhoHansMergingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ???? merging test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "transcription" / "merging.json"
    return load_test_cases_from_json(
        path, DualBlockGappedManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualBlockPrompt] = YueZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ???? vs ???? proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, DualBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_from_zho_translation_test_cases(
    prompt_cls: type[DualMultiSinglePrompt] = YueHansFromZhoTranslationPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ???? from ???? translation test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "translation.json"
    return load_test_cases_from_json(
        path, YueZhoProofreadingManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_review_test_cases(
    prompt_cls: type[DualBlockPrompt] = YueHansReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ???? vs ???? review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "review.json"
    return load_test_cases_from_json(
        path, DualBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hans_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ?? proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hans.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ?? proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hant.json"
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
    path = title_root / "lang" / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ?? OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hans.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD ?? OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hant.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )
