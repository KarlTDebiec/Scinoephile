#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Unpack

import pytest

from scinoephile.core.llms import TestCase, load_test_cases_from_json
from scinoephile.core.llms.manager import TestCaseClsKwargs
from scinoephile.core.subtitles import Series
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
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from test.helpers import test_data_root

__all__ = [
    "t_eng",
    "t_eng_lens",
    "t_eng_tesseract",
    "t_zho_hans",
    "t_zho_hans_lens",
    "t_zho_hans_paddle",
    "t_zho_hant",
    "t_zho_hant_lens",
    "t_zho_hant_paddle",
    "get_t_eng_ocr_fusion_test_cases",
    "get_t_eng_proofreading_test_cases",
    "get_t_zho_hans_ocr_fusion_test_cases",
    "get_t_zho_hans_proofreading_test_cases",
    "get_t_zho_hant_ocr_fusion_test_cases",
    "get_t_zho_hant_proofreading_test_cases",
    "get_t_zho_hant_simplify_proofreading_test_cases",
    "t_eng_fuse",
    "t_eng_fuse_clean",
    "t_eng_fuse_clean_validate",
    "t_eng_fuse_clean_validate_proofread",
    "t_eng_fuse_clean_validate_proofread_flatten",
    "t_eng_image",
    "t_zho_hans_eng",
    "t_zho_hans_fuse",
    "t_zho_hans_fuse_clean",
    "t_zho_hans_fuse_clean_validate",
    "t_zho_hans_fuse_clean_validate_proofread",
    "t_zho_hans_fuse_clean_validate_proofread_flatten",
    "t_zho_hans_fuse_clean_validate_proofread_flatten_romanize",
    "t_zho_hans_image",
    "t_zho_hant_fuse",
    "t_zho_hant_fuse_clean",
    "t_zho_hant_fuse_clean_validate",
    "t_zho_hant_fuse_clean_validate_proofread",
    "t_zho_hant_fuse_clean_validate_proofread_flatten",
    "t_zho_hant_fuse_clean_validate_proofread_flatten_simplify",
    "t_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread",
    "t_zho_hant_image",
    "t_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_lens() -> Series:
    """T English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def t_eng_tesseract() -> Series:
    """T English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def t_zho_hans() -> Series:
    """T 简体中文 series."""
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_lens() -> Series:
    """T 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def t_zho_hans_paddle() -> Series:
    """T 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def t_zho_hant() -> Series:
    """T 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_lens() -> Series:
    """T 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def t_zho_hant_paddle() -> Series:
    """T 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@cache
def get_t_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English proofreading test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_hans_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T 简体中文 proofreading test cases.

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
def get_t_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T 繁体中文 proofreading test cases.

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
def get_t_zho_hant_simplify_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T 繁体中文 simplification proofreading test cases.

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


@cache
def get_t_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T English OCR fusion test cases.

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
def get_t_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T 简体中文 OCR fusion test cases.

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
def get_t_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Unpack[TestCaseClsKwargs],
) -> list[TestCase]:
    """Get T 繁体中文 OCR fusion test cases.

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


@pytest.fixture
def t_eng_fuse() -> Series:
    """T English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def t_eng_fuse_clean() -> Series:
    """T English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def t_eng_fuse_clean_validate() -> Series:
    """T English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def t_eng_fuse_clean_validate_proofread() -> Series:
    """T English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """T English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def t_eng_image() -> ImageSeries:
    """T English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@pytest.fixture
def t_zho_hans_fuse() -> Series:
    """T 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def t_zho_hans_fuse_clean() -> Series:
    """T 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate() -> Series:
    """T 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread() -> Series:
    """T 简体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread_flatten() -> Series:
    """T 简体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread_flatten_romanize() -> Series:
    """T 简体中文 fused/cleaned/validated/proofread/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten_romanize.srt"
    )


@pytest.fixture
def t_zho_hans_image() -> ImageSeries:
    """T 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_image", encoding="utf-8")


@pytest.fixture
def t_zho_hant_fuse() -> Series:
    """T 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def t_zho_hant_fuse_clean() -> Series:
    """T 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate() -> Series:
    """T 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread() -> Series:
    """T 繁体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """T 繁体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten_simplify() -> Series:
    """T 繁体中文 fused/cleaned/validated/proofread/flattened/simplified subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread() -> Series:
    """T 繁体中文 simplified/proofread fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify_proofread.srt"
    )


@pytest.fixture
def t_zho_hant_image() -> ImageSeries:
    """T 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")


@pytest.fixture
def t_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for T Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[95] -> TRAD[95]: '还谈什么？' -> '还谈甚么？'",
        "edit: SIMP[119] -> TRAD[119]: '你耍我的吧？' -> '你要我的吧？'",
        "edit: SIMP[211] -> TRAD[211]: '张总，看看想吃什么？' -> '张总，看看想吃甚么？'",
        "edit: SIMP[288] -> TRAD[288]: '他看什么？' -> '他看甚么？'",
        "edit: SIMP[314] -> TRAD[314]: '这潮哥是什么来头？' -> '这潮哥是什麽来头？'",
        "edit: SIMP[315] -> TRAD[315]: '他就是不让你知道他什么来头' -> '他就是不让你知道他什麽来头'",
        "edit: SIMP[410] -> TRAD[410]: '又不是赚很多，也不知为了什么' -> '又不是赚很多，也不知为什么'",
        "edit: SIMP[432] -> TRAD[432]: '我家的VCD机坏了' -> '我家的 VCD 机坏了'",
        "edit: SIMP[441] -> TRAD[441]: '还有一部VCD机' -> '还有一部 VCD 机'",
        "edit: SIMP[451] -> TRAD[451]: '什么事？' -> '甚么事？'",
        "edit: SIMP[526] -> TRAD[526]: '搞什么？' -> '搞甚么？'",
        "shift: SIMP[528-529] -> TRAD[528-529]: ['唱什么歌？', '唱什么也听不到，有什么好听？'] -> ['唱甚么歌？', '唱甚么也听不到，有甚么好听？']",
        "edit: SIMP[531] -> TRAD[531]: '唱什么也很厉害' -> '唱甚么也很厉害'",
        "edit: SIMP[552] -> TRAD[552]: '喜玛拉雅山！' -> '喜马拉雅山！'",
        "edit: SIMP[615] -> TRAD[615]: '海关龙科' -> '海关龙柯'",
        "edit: SIMP[617] -> TRAD[617]: '龙科你好' -> '龙柯你好'",
        "edit: SIMP[625] -> TRAD[625]: '龙科，他是我的好兄弟' -> '龙柯，他是我的好兄弟'",
        "shift: SIMP[634-635] -> TRAD[634-635]: ['吃什么？吃什么？', '吃什么？'] -> ['吃甚么？吃甚么？', '吃甚么？']",
        "edit: SIMP[722] -> TRAD[722]: '大家都一起开AK' -> '大家都一起开 AK'",
        "edit: SIMP[848] -> TRAD[848]: '你做什么？' -> '你做甚么？'",
        "edit: SIMP[862] -> TRAD[862]: '脱什么节？' -> '脱甚么节？'",
        "edit: SIMP[905] -> TRAD[905]: '一场3T就抢光香港人的钱了' -> '一场 3T 就抢光香港人的钱了'",
        "edit: SIMP[906] -> TRAD[906]: '3T什么意思？' -> '3T 什么意思？'",
        "edit: SIMP[1044] -> TRAD[1044]: '我叶国欢有麟有角！' -> '我叶国欢有鳞有角！'",
        "edit: SIMP[1100] -> TRAD[1100]: '怎样也要留下些什么吧？' -> '怎样也要留下些甚么吧？'",
        "edit: SIMP[1116] -> TRAD[1116]: '老大，你说什么就是什么' -> '老大，你说甚么就是甚么'",
    ]
