#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
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
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from test.helpers import test_data_root

__all__ = [
    "mnt_eng_ocr_lens",
    "mnt_eng_ocr_tesseract",
    "mnt_zho_hans_ocr_lens",
    "mnt_zho_hans_ocr_paddle",
    "mnt_zho_hant",
    "mnt_zho_hant_ocr_lens",
    "mnt_zho_hant_ocr_paddle",
    "get_mnt_eng_block_review_test_cases",
    "get_mnt_eng_ocr_fusion_test_cases",
    "get_mnt_zho_hans_block_review_test_cases",
    "get_mnt_zho_hans_ocr_fusion_test_cases",
    "get_mnt_zho_hant_block_review_test_cases",
    "get_mnt_zho_hant_ocr_fusion_test_cases",
    "get_mnt_zho_hant_simplify_block_review_test_cases",
    "mnt_eng_fuse",
    "mnt_eng_fuse_clean",
    "mnt_eng_fuse_clean_validate",
    "mnt_eng_fuse_clean_validate_review",
    "mnt_eng_fuse_clean_validate_review_flatten",
    "mnt_eng_image",
    "mnt_eng_image_path",
    "mnt_zho_hans_fuse",
    "mnt_zho_hans_fuse_clean",
    "mnt_zho_hans_fuse_clean_validate",
    "mnt_zho_hans_fuse_clean_validate_review",
    "mnt_zho_hans_fuse_clean_validate_review_flatten",
    "mnt_zho_hans_fuse_clean_validate_review_flatten_romanize",
    "mnt_zho_hans_image",
    "mnt_zho_hans_image_path",
    "mnt_zho_hant_fuse",
    "mnt_zho_hant_fuse_clean",
    "mnt_zho_hant_fuse_clean_validate",
    "mnt_zho_hant_fuse_clean_validate_review",
    "mnt_zho_hant_fuse_clean_validate_review_flatten",
    "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify",
    "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
    "mnt_zho_hant_image",
    "mnt_zho_hant_image_path",
    "mnt_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def mnt_eng_ocr_lens() -> Series:
    """MNT English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_ocr" / "lens.srt")


@pytest.fixture
def mnt_eng_ocr_tesseract() -> Series:
    """MNT English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_ocr" / "tesseract.srt")


@pytest.fixture
def mnt_zho_hans_ocr_lens() -> Series:
    """MNT 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_ocr" / "lens.srt")


@pytest.fixture
def mnt_zho_hans_ocr_paddle() -> Series:
    """MNT 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_ocr" / "paddle.srt")


@pytest.fixture
def mnt_zho_hant() -> Series:
    """MNT 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def mnt_zho_hant_ocr_lens() -> Series:
    """MNT 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_ocr" / "lens.srt")


@pytest.fixture
def mnt_zho_hant_ocr_paddle() -> Series:
    """MNT 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_ocr" / "paddle.srt")


@cache
def get_mnt_eng_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT English block review test cases.

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
def get_mnt_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT English OCR fusion test cases.

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
def get_mnt_zho_hans_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT 简体中文 block review test cases.

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
def get_mnt_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT 简体中文 OCR fusion test cases.

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
def get_mnt_zho_hant_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT 繁体中文 block review test cases.

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
def get_mnt_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT 繁体中文 OCR fusion test cases.

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
def get_mnt_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansBlockReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MNT 繁体中文 simplification block review test cases.

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
def mnt_eng_fuse() -> Series:
    """MNT English fused subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse.srt")


@pytest.fixture
def mnt_eng_fuse_clean() -> Series:
    """MNT English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate() -> Series:
    """MNT English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate_review() -> Series:
    """MNT English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate_review_flatten() -> Series:
    """MNT English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "eng_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mnt_eng_image() -> ImageSeries:
    """MNT English image subtitles."""
    return ImageSeries.load(output_dir / "eng_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mnt_eng_image_path() -> Path:
    """Path to MNT English image subtitles."""
    return output_dir / "eng_ocr" / "image"


@pytest.fixture
def mnt_zho_hans_fuse() -> Series:
    """MNT 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean() -> Series:
    """MNT 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate() -> Series:
    """MNT 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate_review() -> Series:
    """MNT 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate_review_flatten() -> Series:
    """MNT 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate_review_flatten_romanize() -> Series:
    """MNT 简体中文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten_romanize.srt"
    )


@pytest.fixture
def mnt_zho_hans_image() -> ImageSeries:
    """MNT 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mnt_zho_hans_image_path() -> Path:
    """Path to MNT 简体中文 image subtitles."""
    return output_dir / "zho-Hans_ocr" / "image"


@pytest.fixture
def mnt_zho_hant_fuse() -> Series:
    """MNT 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean() -> Series:
    """MNT 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate() -> Series:
    """MNT 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean_validate.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_review() -> Series:
    """MNT 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_review_flatten() -> Series:
    """MNT 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_review_flatten_simplify() -> Series:
    """MNT 繁体中文 fused/cleaned/validated/reviewed/flattened/simplified subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """MNT 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@pytest.fixture
def mnt_zho_hant_image() -> ImageSeries:
    """MNT 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_ocr" / "image", encoding="utf-8")


@pytest.fixture
def mnt_zho_hant_image_path() -> Path:
    """Path to MNT 繁体中文 image subtitles."""
    return output_dir / "zho-Hant_ocr" / "image"


@pytest.fixture
def mnt_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for MNT Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[1] -> TRAD[1]: '《龙猫》' -> '龙猫'",
        "edit: SIMP[4] -> TRAD[4]: '你们两个累不累啊' -> '妳们两个累不累啊'",
        "edit: SIMP[10] -> TRAD[10]: '我姓草壁\\u3000新搬来的' -> '我姓草壁，新搬来的'",
        "edit: SIMP[20] -> TRAD[20]: '爸爸，这里好棒啊' -> '爸爸，这里太好了'",
        "edit: SIMP[48] -> TRAD[48]: '还是\\u3000吃橡果子的老鼠呢？' -> '还是吃橡果子的老鼠呢？'",
        "edit: SIMP[56] -> TRAD[56]: '等人家嘛' -> '等等'",
        "edit: SIMP[58] -> TRAD[58]: '进去罗' -> '进去啰'",
        "edit: SIMP[68] -> TRAD[68]: '那一定是〝灰尘精灵〞' -> '那一定是「灰尘精灵」'",
        "edit: SIMP[79] -> TRAD[79]: '上二楼的楼梯\\u3000到底在哪里呢？' -> '上二楼的楼梯，到底在哪里呢？'",
        "edit: SIMP[83] -> TRAD[83]: '人家也要' -> '小美也要'",
        "edit: SIMP[85] -> TRAD[85]: '甚么？' -> '咦？'",
        "edit: SIMP[86] -> TRAD[86]: '甚么？' -> '咦？'",
        "edit: SIMP[87] -> TRAD[87]: '甚么？' -> '咦？'",
        "edit: SIMP[88] -> TRAD[88]: '甚么？' -> '咦？'",
        "edit: SIMP[89] -> TRAD[89]: '甚么？' -> '咦？'",
        "edit: SIMP[100] -> TRAD[100]: '那真是太棒了' -> '那真是太好了'",
        "edit: SIMP[101] -> TRAD[101]: '爸爸从小就梦想\\u3000能够住在鬼屋里面' -> '爸爸从小就梦想能够住在鬼屋里面'",
        "edit: SIMP[127] -> TRAD[127]: '〝哇啦哇啦〞的乱跑啊' -> '「哇啦哇啦」的乱跑啊'",
        "edit: SIMP[140] -> TRAD[140]: '可是要是来这么一大堆\\u3000该怎么办？' -> '可是要是来这么一大堆，该怎么办？'",
        "edit: SIMP[141] -> TRAD[141]: '人家才不怕那些' -> '小美才不怕那些'",
        "edit: SIMP[143] -> TRAD[143]: '那以后晚上\\u3000姐姐就不陪妳上厕所' -> '那以后晚上，姐姐就不陪妳上厕所'",
        "edit: SIMP[147] -> TRAD[147]: '人家也要去' -> '小美也要去'",
        "edit: SIMP[154] -> TRAD[154]: '你不是刚刚那个吗？\\u3000有事吗' -> '你不是刚刚那个吗？有事吗'",
        "edit: SIMP[163] -> TRAD[163]: '不过\\u3000婆婆这个糯米团很好吃' -> '不过婆婆这个糯米团很好吃'",
        "delete: SIMP[165] '婆婆，谢谢您的糯米团' not present in TRAD",
        "edit: SIMP[168] -> TRAD[168]: '爸爸，我们家\\u3000破破烂烂的会否倒下来' -> '爸爸，我们家破破烂烂的会否倒下来'",
        "edit: SIMP[172] -> TRAD[172]: '人家才不怕呢！' -> '小美才不怕呢！'",
        "edit: SIMP[173] -> TRAD[173]: '人家才不怕呢！' -> '小美才不怕呢！'",
        "edit: SIMP[174] -> TRAD[174]: '一、二、一、二、一、二' -> '一，二，一，二，一，二'",
        "edit: SIMP[177] -> TRAD[177]: '好了\\u3000衣服都洗好了' -> '好了，衣服都洗好了'",
        "edit: SIMP[185] -> TRAD[185]: '替我帮妳们妈妈问好' -> '替我帮你们妈妈问好'",
        "edit: SIMP[191] -> TRAD[191]: '小美妳也来啦' -> '小美妳也来啦！'",
        "edit: SIMP[195] -> TRAD[195]: '今天田里休息一天' -> '今天是农假，学校休息一天'",
        "edit: SIMP[201] -> TRAD[201]: '甚么？我们家是鬼屋啊' -> '什么？我们家是鬼屋啊'",
        "edit: SIMP[208] -> TRAD[208]: '那妳们两个呢？' -> '那你们两个呢？'",
        "edit: SIMP[211] -> TRAD[211]: '小美的头发都是妳梳的？' -> '小美的头发都是你梳的？'",
        "edit: SIMP[219] -> TRAD[219]: '人家也要！人家也要！' -> '小美也要！小美也要！'",
        "edit: SIMP[226] -> TRAD[226]: '因为妳跟妈妈最像了' -> '因为你跟妈妈最像了'",
        "edit: SIMP[229] -> TRAD[229]: '医生也说\\u3000再过不久就可以出院了' -> '医生也说，再过不久就可以出院了'",
        "edit: SIMP[231] -> TRAD[231]: '妳什么都是明天' -> '你什么都是明天'",
        "edit: SIMP[233] -> TRAD[233]: '可是人家好想要跟妈妈一起睡' -> '妈妈说想跟小美一起睡'",
        "edit: SIMP[234] -> TRAD[234]: '妳不是说妳已经长大\\u3000要自己一个人睡的吗？' -> '你不是说你已经长大，要自己一个人睡的吗？'",
        "edit: SIMP[251] -> TRAD[251]: '糟了，来啊' -> '糟了，来啊！'",
        "edit: SIMP[253] -> TRAD[253]: '叫得很真亲密呢' -> '叫得很真亲密呢。'",
        "edit: SIMP[259] -> TRAD[259]: '早，赶快走吧\\u3000好' -> '﹣早，赶快走吧\\u3000\\u3000﹣好。'",
        "edit: SIMP[287] -> TRAD[287]: '爸爸！\\u3000小美的帽子掉在这里' -> '爸爸！小美的帽子掉在这里'",
        "edit: SIMP[298] -> TRAD[298]: '它的名字叫做大龙猫啊' -> '牠的名字叫做大龙猫啊'",
        "edit: SIMP[299] -> TRAD[299]: '它的毛好多啊' -> '牠的毛好多啊'",
        "edit: SIMP[313] -> TRAD[313]: '它刚才\\u3000睡在一棵很大的树里面' -> '牠刚才睡在一棵很大的树下面'",
        "edit: SIMP[321] -> TRAD[321]: '人家没有骗你们' -> '我没有骗你们'",
        "edit: SIMP[324] -> TRAD[324]: '小美刚才一定是\\u3000遇到了森林的主人' -> '小美刚才一定是遇到了森林的主人'",
        "edit: SIMP[327] -> TRAD[327]: '来，我们去跟它打个招呼吧' -> '对了，我们还没有跟它打招呼'",
        "edit: SIMP[340] -> TRAD[340]: '那不是想看\\u3000随时就能看到的' -> '那不是想看，随时就能看到的'",
        "edit: SIMP[351] -> TRAD[351]: '而且知道\\u3000妈妈一定也会喜欢这里' -> '而且知道，妈妈一定也会喜欢这里'",
        "edit: SIMP[354] -> TRAD[354]: '对了\\u3000我跟小满约好要到她家去' -> '对了，我跟小满约好要到她家去'",
        "edit: SIMP[355] -> TRAD[355]: '人家也要去' -> '小美也要去'",
        "edit: SIMP[360] -> TRAD[360]: '我们比赛看谁先到家' -> '比赛跑回家'",
        "edit: SIMP[362] -> TRAD[362]: '等人家嘛' -> '等等'",
        "edit: SIMP[364] -> TRAD[364]: '等人家嘛' -> '等等嘛'",
        "edit: SIMP[366] -> TRAD[366]: '因为小美说她看到了\\u3000一只很大的龙猫精灵' -> '因为小美说她看到了，一只很大的龙猫精灵'",
        "edit: SIMP[367] -> TRAD[367]: '我好希望我也能够见它一面' -> '我好希望我也能够见牠一面'",
        "edit: SIMP[369] -> TRAD[369]: '再不快点就要迟到了\\u3000嗯' -> '﹣再不快点就要迟到了\\u3000﹣嗯'",
        "delete: SIMP[374] '你们看，你们看，她妹妹' not present in TRAD",
        "edit: SIMP[375] -> TRAD[374]: '婆婆、小美？' -> '婆婆，小美？'",
        "edit: SIMP[382] -> TRAD[381]: '你要在婆婆家\\u3000乖乖等姊姊放学的吗？' -> '你要在婆婆家\\u3000乖乖等姐姐放学的吗？'",
        "edit: SIMP[383] -> TRAD[382]: '姊姊还要再上两个小时的课' -> '姐姐还要再上两个小时的课'",
        "edit: SIMP[390] -> TRAD[389]: '好、好' -> '是的'",
        "edit: SIMP[402] -> TRAD[401]: '人家都没有哭，棒不棒？\\u3000嗯' -> '-小美都没有哭，了不起。 -嗯'",
        "edit: SIMP[404] -> TRAD[403]: '土地公爷爷\\u3000请您让我们躲一下雨' -> '土地公爷爷，请您让我们躲一下雨'",
        "edit: SIMP[406] -> TRAD[405]: '姊姊，有伞子真棒啊' -> '姐姐，有伞子真好啊'",
        "edit: SIMP[407] -> TRAD[406]: '可是伞子顶破了一个大洞' -> '伞子破了好多洞洞'",
        "edit: SIMP[409] -> TRAD[408]: '人家也要去接爸爸' -> '小美也要去接爸爸'",
        "edit: SIMP[412] -> TRAD[411]: '竟然还会傻得忘了带伞\\u3000你骗鬼啊！' -> '竟然还会傻得忘了带伞，你骗鬼啊！'",
        "edit: SIMP[414] -> TRAD[413]: '我看啊\\u3000你八成是把伞子弄坏了' -> '我看啊，你八成是把伞弄坏了'",
        "edit: SIMP[421] -> TRAD[420]: '对了\\u3000这是勘太今天借我们的伞' -> '对了，这是勘太今天借我们的伞'",
        "edit: SIMP[423] -> TRAD[422]: '这么破的伞子真不好意思' -> '这么破的伞真不好意思'",
        "edit: SIMP[453] -> TRAD[452]: '快点啊\\u3000小美快要掉下来了啦' -> '快点啊，小美快要掉下来了啦'",
        "edit: SIMP[462] -> TRAD[461]: '出现了，爸爸\\u3000真的出现了' -> '出现了，爸爸真的出现了'",
        "edit: SIMP[467] -> TRAD[466]: '看到了！\\u3000我看到大龙猫了！' -> '看到了！我看到大龙猫了！'",
        "edit: SIMP[468] -> TRAD[467]: '好棒啊' -> '太好了！'",
        "edit: SIMP[473] -> TRAD[472]: '而且大龙猫送给我们的礼物\\u3000实在是太棒了' -> '而且大龙猫送给我们的礼物\\u3000实在是妙极了'",
        "edit: SIMP[478] -> TRAD[477]: '我们想家里院子\\u3000变成森林的话一定很棒' -> '我们想家里院子变成森林的话一定很精彩'",
        "edit: SIMP[484] -> TRAD[483]: '就好像猴子螃蟹大战\\u3000里面那个螃蟹一样啊' -> '就好像猴子蟹大战里面那个螃蟹一样啊'",
        "edit: SIMP[486] -> TRAD[485]: '希望妈妈的病\\u3000能够快点好起来好吗？' -> '希望妈妈的病能够快点好起来好吗？'",
        "edit: SIMP[496] -> TRAD[495]: '太棒了！' -> '太好了！'",
        "edit: SIMP[525] -> TRAD[524]: '只要是\\u3000吃了婆婆田里种的东西' -> '只要是吃了婆婆田里种的东西'",
        "edit: SIMP[527] -> TRAD[526]: '这个星期六\\u3000我妈妈就会回来了' -> '这个星期六我妈妈就会回来了'",
        "edit: SIMP[529] -> TRAD[528]: '是吗？\\u3000马上就要出院了' -> '是吗？马上就要出院了'",
        "edit: SIMP[531] -> TRAD[530]: '星期一还得回去复诊' -> '星期一还得回去覆诊'",
        "edit: SIMP[535] -> TRAD[534]: '我要把我自己摘的\\u3000粟米给妈妈吃' -> '我要把我自己摘的粟米给妈妈吃'",
        "edit: SIMP[538] -> TRAD[537]: '你们不在\\u3000所以邮差送去我家' -> '你们不在，所以邮差送去我家'",
        "edit: SIMP[542] -> TRAD[541]: '发电处七国山医院' -> '发电出七国山医院'",
        "merge_edit: SIMP[546-547] -> TRAD[545]: ['婆婆，怎么办？', '医院要我们跟他们联络'] -> ['婆婆，怎么办？医院要我们跟他们联络']",
        "edit: SIMP[550] -> TRAD[548]: '爸爸研究室的电话号码\\u3000我是知道' -> '爸爸研究室的电话号码我是知道'",
        "edit: SIMP[556] -> TRAD[554]: '请接东京31局1382号' -> '请接东京 31 局 1382 号'",
        "edit: SIMP[561] -> TRAD[559]: '我爸爸⋯\\u3000麻烦请草壁先生听电话' -> '我爸爸⋯麻烦请找草壁先生听电话'",
        "edit: SIMP[566] -> TRAD[564]: '爸爸现在就\\u3000打电话到医院去问' -> '爸爸现在就打电话到医院去问'",
        "edit: SIMP[570] -> TRAD[568]: '爸爸给医院打过电话\\u3000就马上就回妳电话' -> '爸爸给医院打过电话就马上回妳电话'",
        "edit: SIMP[573] -> TRAD[571]: '婆婆\\u3000我还可以在这里待一会吗？' -> '婆婆，我还可以在这里待一会吗？'",
        "edit: SIMP[576] -> TRAD[574]: '姊姊' -> '姐姐'",
        "edit: SIMP[586] -> TRAD[584]: '妈妈要是勉强出院\\u3000反而更严重了那怎么办' -> '妈妈要是勉强出院，反而更严重了，那怎么办'",
        "edit: SIMP[590] -> TRAD[588]: '那妈妈死掉\\u3000也没有关系是不是' -> '那妈妈死掉，也没有关系是不是'",
        "edit: SIMP[595] -> TRAD[593]: '姊姊大坏蛋！' -> '姐姐是大坏蛋！'",
        "edit: SIMP[600] -> TRAD[598]: '你爸爸说他今天\\u3000要留在医院过夜' -> '你爸爸说他今天要留在医院过夜'",
        "edit: SIMP[604] -> TRAD[602]: '医生说只要住数天就会好了' -> '医生说只要住几天就会好了'",
        "edit: SIMP[606] -> TRAD[604]: '我妈妈要是死了该怎么办' -> '我妈妈要是死了，该怎么办'",
        "edit: SIMP[608] -> TRAD[606]: '我妈妈要是死了那我们⋯' -> '我妈妈要是死了，那我们⋯'",
        "edit: SIMP[610] -> TRAD[608]: '妳妈妈哪舍得下\\u3000妳们这些可爱的孩子' -> '妳妈妈哪舍得下妳们这些可爱的孩子'",
        "edit: SIMP[618] -> TRAD[616]: '没在公车站牌那边吗？' -> '没在巴士站牌那边吗？'",
        "edit: SIMP[623] -> TRAD[621]: '她会不会\\u3000跑去妈妈住的医院了' -> '她会不会跑去妈妈住的医院了'",
        "edit: SIMP[625] -> TRAD[623]: '可是就连大人也得\\u3000走上三个钟头才会到' -> '可是就连大人也得走上三个钟头才会到'",
        "edit: SIMP[632] -> TRAD[630]: '您有没有看见束辫子的小女孩\\u3000从这条路经过' -> '您有没有看见束辫子的小女孩，从这条路经过'",
        "edit: SIMP[641] -> TRAD[639]: '搞什么啊！危险啊' -> '搞什么啊！危险啊！'",
        "edit: SIMP[643] -> TRAD[641]: '你们有没有看一个小女孩' -> '你们有没有看到一个小女孩'",
        "edit: SIMP[648] -> TRAD[646]: '我们两个\\u3000就是从那个方向来的' -> '我们两个就是从那个方向来的'",
        "edit: SIMP[649] -> TRAD[647]: '不过\\u3000好像没有看到那样的小孩' -> '不过好像没有看到那样的小孩'",
        "edit: SIMP[651] -> TRAD[649]: '她从哪里来的？' -> '妳从哪里来的？'",
        "edit: SIMP[655] -> TRAD[653]: '就是啊' -> '再见啰'",
        "edit: SIMP[669] -> TRAD[667]: '喃呒阿弥陀佛' -> '南无阿弥陀佛'",
        "edit: SIMP[670] -> TRAD[668]: '池那边泥比较深一点\\u3000从那边开始啊' -> '池那边泥比较深一点，从那边开始啊'",
        "edit: SIMP[672] -> TRAD[670]: '喃呒阿弥陀佛\\u3000婆婆，小月来了' -> '婆婆，小月来了'",
        "edit: SIMP[677] -> TRAD[675]: '我还以\\u3000这是小美的' -> '我还以为这是小美的'",
        "edit: SIMP[683] -> TRAD[681]: '不好意思啊' -> '大家，不好意思啊'",
        "edit: SIMP[684] -> TRAD[682]: '大家辛苦你们\\u3000再回头去找找好了' -> '麻烦再分开找找'",
        "edit: SIMP[697] -> TRAD[695]: '大家都看不到它' -> '大家都看不到牠'",
        "insert: TRAD[696] '「小美」' not present in SIMP",
        "edit: SIMP[701] -> TRAD[700]: '姊姊' -> '姐姐'",
        "edit: SIMP[702] -> TRAD[701]: '姊姊' -> '姐姐'",
        "edit: SIMP[705] -> TRAD[704]: '姊姊' -> '姐姐'",
        "edit: SIMP[708] -> TRAD[707]: '妳是不是想要把粟米\\u3000送去医院给妈妈？' -> '妳是不是想要把粟米送去医院给妈妈？'",
        "edit: SIMP[709] -> TRAD[708]: '〝七国山医院〞' -> '「七国山医院」'",
        "edit: SIMP[713] -> TRAD[712]: '医院就擅自决定\\u3000发电报给家里了' -> '医院就擅自决定，发电报给家里了'",
        "edit: SIMP[720] -> TRAD[719]: '她们表面好像没事\\u3000可是心里一定很难过' -> '她们表面好像没事，可是心里一定很难过'",
        "edit: SIMP[721] -> TRAD[720]: '小月越是懂事\\u3000就越教人于心不忍' -> '小月越是懂事，就越教人于心不忍'",
        "merge_edit: SIMP[723-724] -> TRAD[722]: ['出院以后我一定要好好疼她们', '让她们尽情耍耍小脾气'] -> ['出院以后我要好好疼疼她们，让她们尽情耍耍小脾气']",
        "insert: TRAD[723] '妳呀' not present in SIMP",
        "edit: SIMP[733] -> TRAD[732]: '妳看' -> '你看'",
        "edit: SIMP[734] -> TRAD[733]: '〝送给妈妈〞' -> '「送给妈妈」'",
        "insert: TRAD[734] '「送给妈妈」' not present in SIMP",
        "insert: TRAD[735] '「送给妈妈」' not present in SIMP",
        "delete: SIMP[735] '谢谢观看' not present in TRAD",
        "insert: TRAD[736] '完' not present in SIMP",
    ]
