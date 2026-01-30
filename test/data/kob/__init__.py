#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import TypedDict, Unpack

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
)
from scinoephile.llms.base import TestCase, load_test_cases_from_json
from scinoephile.llms.base.manager import TestCaseClsKwargs
from scinoephile.llms.dual_multi_single import DualMultiSinglePrompt
from scinoephile.llms.dual_pair import DualPairManager, DualPairPrompt
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    YueZhoProofreadingManager,
)
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
    YueZhoMergingManager,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)


__all__ = [
    "kob_eng",
    "kob_eng_lens",
    "kob_eng_tesseract",
    "kob_yue_hans",
    "kob_yue_hant",
    "kob_zho_hant_lens",
    "kob_zho_hant_paddle",
    "get_kob_eng_ocr_fusion_test_cases",
    "get_kob_eng_proofreading_test_cases",
    "get_kob_yue_merging_test_cases",
    "get_kob_yue_shifting_test_cases",
    "get_kob_yue_vs_zho_proofreading_test_cases",
    "get_kob_zho_hant_ocr_fusion_test_cases",
    "get_kob_zho_hant_proofreading_test_cases",
    "get_kob_zho_hant_simplify_proofreading_test_cases",
    "kob_eng_fuse",
    "kob_eng_fuse_clean",
    "kob_eng_fuse_clean_validate",
    "kob_eng_fuse_clean_validate_proofread",
    "kob_eng_fuse_clean_validate_proofread_flatten",
    "kob_eng_timewarp",
    "kob_eng_timewarp_clean",
    "kob_eng_timewarp_clean_proofread",
    "kob_eng_timewarp_clean_proofread_flatten",
    "kob_eng_image",
    "kob_yue_hans_audio",
    "kob_yue_hans_timewarp",
    "kob_yue_hans_timewarp_clean",
    "kob_yue_hans_timewarp_clean_flatten",
    "kob_yue_hans_timewarp_clean_flatten_romanize",
    "kob_yue_hant_timewarp",
    "kob_yue_hant_timewarp_clean",
    "kob_yue_hant_timewarp_clean_flatten",
    "kob_zho_hans_eng",
    "kob_zho_hant_fuse",
    "kob_zho_hant_fuse_clean",
    "kob_zho_hant_fuse_clean_validate",
    "kob_zho_hant_fuse_clean_validate_proofread",
    "kob_zho_hant_fuse_clean_validate_proofread_flatten",
    "kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify",
    "kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread",
    "kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread_romanize",
    "kob_zho_hant_image",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def kob_eng() -> Series:
    """KOB English subtitles."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def kob_eng_lens() -> Series:
    """KOB English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def kob_eng_tesseract() -> Series:
    """KOB English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def kob_yue_hans() -> Series:
    """KOB 简体粤文 subtitles (input)."""
    return Series.load(input_dir / "yue-Hans.srt")


@pytest.fixture
def kob_yue_hant() -> Series:
    """KOB 繁体粤文 subtitles."""
    return Series.load(input_dir / "yue-Hant.srt")


@pytest.fixture
def kob_zho_hant_lens() -> Series:
    """KOB 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def kob_zho_hant_paddle() -> Series:
    """KOB 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@cache
def get_kob_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB English OCR fusion test cases.

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
def get_kob_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    ocr_path = title_root / "lang" / "eng" / "proofreading" / "eng_ocr.json"
    srt_path = title_root / "lang" / "eng" / "proofreading" / "eng_srt.json"
    ocr_test_cases = load_test_cases_from_json(
        ocr_path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )
    srt_test_cases = load_test_cases_from_json(
        srt_path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )
    return ocr_test_cases + srt_test_cases


@cache
def get_kob_yue_shifting_test_cases(
    prompt_cls: type[DualPairPrompt] = YueZhoHansShiftingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 简体粤文 shifting test cases.

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
def get_kob_yue_merging_test_cases(
    prompt_cls: type[DualMultiSinglePrompt] = YueZhoHansMergingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 简体粤文 merging test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "transcription" / "merging.json"
    return load_test_cases_from_json(
        path, YueZhoMergingManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueZhoHansProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 简体粤文 vs 简体中文 proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, YueZhoProofreadingManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 繁体中文 OCR fusion test cases.

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


@cache
def get_kob_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 繁体中文 proofreading test cases.

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
def get_kob_zho_hant_simplify_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get KOB 繁体中文 simplification proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hant_simplify.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@pytest.fixture
def kob_eng_fuse() -> Series:
    """KOB English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def kob_eng_fuse_clean() -> Series:
    """KOB English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate() -> Series:
    """KOB English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate_proofread() -> Series:
    """KOB English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """KOB English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def kob_eng_timewarp() -> Series:
    """KOB English timewarp subtitles."""
    return Series.load(output_dir / "eng_timewarp.srt")


@pytest.fixture
def kob_eng_timewarp_clean() -> Series:
    """KOB English timewarp and cleaned subtitles."""
    return Series.load(output_dir / "eng_timewarp_clean.srt")


@pytest.fixture
def kob_eng_timewarp_clean_proofread() -> Series:
    """KOB English timewarp, cleaned, and proofread subtitles."""
    return Series.load(output_dir / "eng_timewarp_clean_proofread.srt")


@pytest.fixture
def kob_eng_timewarp_clean_proofread_flatten() -> Series:
    """KOB English timewarp, cleaned, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_timewarp_clean_proofread_flatten.srt")


@pytest.fixture
def kob_eng_image() -> ImageSeries:
    """KOB English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def kob_yue_hans_audio() -> AudioSeries:
    """KOB 简体粤文 audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_audio")


@pytest.fixture
def kob_yue_hans_timewarp() -> Series:
    """KOB 简体粤文 timewarp subtitles."""
    return Series.load(output_dir / "yue-Hans_timewarp.srt")


@pytest.fixture
def kob_yue_hans_timewarp_clean() -> Series:
    """KOB 简体粤文 timewarp and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_timewarp_clean.srt")


@pytest.fixture
def kob_yue_hans_timewarp_clean_flatten() -> Series:
    """KOB 简体粤文 timewarp, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "yue-Hans_timewarp_clean_flatten.srt")


@pytest.fixture
def kob_yue_hans_timewarp_clean_flatten_romanize() -> Series:
    """KOB 简体粤文 timewarp/cleaned/flattened romanized subtitles."""
    return Series.load(output_dir / "yue-Hans_timewarp_clean_flatten_romanize.srt")


@pytest.fixture
def kob_yue_hant_timewarp() -> Series:
    """KOB 繁體粵文 timewarp subtitles."""
    return Series.load(output_dir / "yue-Hant_timewarp.srt")


@pytest.fixture
def kob_yue_hant_timewarp_clean() -> Series:
    """KOB 繁體粵文 timewarp and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_timewarp_clean.srt")


@pytest.fixture
def kob_yue_hant_timewarp_clean_flatten() -> Series:
    """KOB 繁體粵文 timewarp, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "yue-Hant_timewarp_clean_flatten.srt")


@pytest.fixture
def kob_zho_hans_eng() -> Series:
    """KOB Bilingual 简体中文 and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@pytest.fixture
def kob_zho_hant_fuse() -> Series:
    """KOB 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean() -> Series:
    """KOB 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate() -> Series:
    """KOB 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread() -> Series:
    """KOB 繁体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """KOB 繁体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify() -> Series:
    """KOB 繁体中文 simplified fused/cleaned/validated/proofread/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread() -> Series:
    """KOB 繁体中文 simplified/proofread fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify_proofread.srt"
    )


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread_romanize(  # noqa: E501
) -> Series:
    """KOB 简体中文 simplified/proofread fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_"
        "simplify_proofread_romanize.srt"
    )


@pytest.fixture
def kob_zho_hant_image() -> ImageSeries:
    """KOB 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")
