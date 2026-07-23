#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from pytest import fixture

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.lang.zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant
from scinoephile.llms.ocr_fusion import OcrFusionManager, OcrFusionPrompt
from scinoephile.llms.review import ReviewManager, ReviewPrompt
from test.helpers import test_data_root

__all__ = [
    "t_eng",
    "t_zho_hans",
    "t_zho_hant",
    "get_t_eng_ocr_fusion_test_cases",
    "get_t_eng_review_test_cases",
    "get_t_zho_hans_ocr_fusion_test_cases",
    "get_t_zho_hans_review_test_cases",
    "get_t_zho_hant_ocr_fusion_test_cases",
    "get_t_zho_hant_review_test_cases",
    "get_t_zho_hant_simplify_review_test_cases",
    "t_eng_fuse",
    "t_eng_fuse_clean",
    "t_eng_fuse_clean_validate",
    "t_eng_fuse_clean_validate_review",
    "t_eng_fuse_clean_validate_review_flatten",
    "t_eng_ocr_lens",
    "t_eng_ocr_lens_clean",
    "t_eng_ocr_tesseract",
    "t_eng_ocr_tesseract_clean",
    "t_zho_hans_eng",
    "t_zho_hans_fuse",
    "t_zho_hans_fuse_clean",
    "t_zho_hans_fuse_clean_validate",
    "t_zho_hans_fuse_clean_validate_review",
    "t_zho_hans_fuse_clean_validate_review_flatten",
    "t_zho_hans_fuse_clean_validate_review_flatten_romanize",
    "t_zho_hans_ocr_lens",
    "t_zho_hans_ocr_lens_clean",
    "t_zho_hans_ocr_paddle",
    "t_zho_hans_ocr_paddle_clean",
    "t_zho_hant_fuse",
    "t_zho_hant_fuse_clean",
    "t_zho_hant_fuse_clean_validate",
    "t_zho_hant_fuse_clean_validate_review",
    "t_zho_hant_fuse_clean_validate_review_flatten",
    "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
    "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
    "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "t_zho_hant_ocr_lens",
    "t_zho_hant_ocr_lens_clean",
    "t_zho_hant_ocr_paddle",
    "t_zho_hant_ocr_paddle_clean",
    "t_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@fixture
def t_zho_hans() -> Series:
    """T zho-Hans series."""
    return Series.load(input_dir / "zho-Hans.srt")


@fixture
def t_zho_hant() -> Series:
    """T zho-Hant series."""
    return Series.load(input_dir / "zho-Hant.srt")


@cache
def get_t_eng_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T English OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_t_eng_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptEng, **kwargs: Any
) -> list[TestCase]:
    """Get T English review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English review test cases
    """
    path = output_dir / "eng_ocr/lang/eng/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_t_zho_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T zho-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_t_zho_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get T zho-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_t_zho_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T zho-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_t_zho_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHant, **kwargs: Any
) -> list[TestCase]:
    """Get T zho-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_t_zho_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get T zho-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@fixture
def t_eng_fuse() -> Series:
    """T English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@fixture
def t_eng_fuse_clean() -> Series:
    """T English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@fixture
def t_eng_fuse_clean_validate() -> Series:
    """T English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@fixture
def t_eng_fuse_clean_validate_review() -> Series:
    """T English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@fixture
def t_eng_fuse_clean_validate_review_flatten() -> Series:
    """T English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@fixture
def t_eng_ocr_lens() -> Series:
    """T English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@fixture
def t_eng_ocr_lens_clean() -> Series:
    """T English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@fixture
def t_eng_ocr_tesseract() -> Series:
    """T English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@fixture
def t_eng_ocr_tesseract_clean() -> Series:
    """T English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual zho-Hans and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def t_zho_hans_fuse() -> Series:
    """T zho-Hans fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def t_zho_hans_fuse_clean() -> Series:
    """T zho-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def t_zho_hans_fuse_clean_validate() -> Series:
    """T zho-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def t_zho_hans_fuse_clean_validate_review() -> Series:
    """T zho-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def t_zho_hans_fuse_clean_validate_review_flatten() -> Series:
    """T zho-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def t_zho_hans_fuse_clean_validate_review_flatten_romanize() -> Series:
    """T zho-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def t_zho_hans_ocr_lens() -> Series:
    """T zho-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def t_zho_hans_ocr_lens_clean() -> Series:
    """T zho-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def t_zho_hans_ocr_paddle() -> Series:
    """T zho-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def t_zho_hans_ocr_paddle_clean() -> Series:
    """T zho-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def t_zho_hant_fuse() -> Series:
    """T zho-Hant fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def t_zho_hant_fuse_clean() -> Series:
    """T zho-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def t_zho_hant_fuse_clean_validate() -> Series:
    """T zho-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def t_zho_hant_fuse_clean_validate_review() -> Series:
    """T zho-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def t_zho_hant_fuse_clean_validate_review_flatten() -> Series:
    """T zho-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def t_zho_hant_fuse_clean_validate_review_flatten_simplify() -> Series:
    """T zho-Hant fused/cleaned/validated/reviewed/flattened/simplified subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def t_zho_hant_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """T zho-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def t_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize() -> Series:
    """T zho-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def t_zho_hant_ocr_lens() -> Series:
    """T zho-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def t_zho_hant_ocr_lens_clean() -> Series:
    """T zho-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def t_zho_hant_ocr_paddle() -> Series:
    """T zho-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def t_zho_hant_ocr_paddle_clean() -> Series:
    """T zho-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def t_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for T Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[4] -> TRAD[4]: '袋子里装什么？\\u3000\\u3000总机' -> '袋子里装甚么？ 总机'",
        "edit: SIMP[5] -> TRAD[5]: '打开来看看\\u3000\\u3000身份证号码 C 5 3 2 7 4 3' -> '打开来看看 身份证号码C 5 3 2 7 4 3'",
        "edit: SIMP[64] -> TRAD[64]: '什么「易发」？' -> '甚么「易发」？'",
        "edit: SIMP[94] -> TRAD[94]: '还谈什么？' -> '还谈甚么？'",
        "edit: SIMP[100] -> TRAD[100]: '那我先还一半儿给你' -> '那我先还一半儿子给你'",
        "edit: SIMP[118] -> TRAD[118]: '你耍我的吧？' -> '你要我的吧？'",
        "edit: SIMP[146] -> TRAD[146]: '什么？' -> '甚么？'",
        "edit: SIMP[163] -> TRAD[163]: '拿着\\u3000\\u3000什么？' -> '拿着，甚么？'",
        "edit: SIMP[184] -> TRAD[184]: '干呀！' -> '干啊！'",
        "edit: SIMP[210] -> TRAD[210]: '张总，看看想吃什么？' -> '张总，看看想吃甚么？'",
        "edit: SIMP[258] -> TRAD[258]: '那你想到什么好主意？' -> '那你想到甚么好主意？'",
        "edit: SIMP[287] -> TRAD[287]: '他看什么？' -> '他看甚么？'",
        "edit: SIMP[326] -> TRAD[326]: '什么事？' -> '甚么事？'",
        "edit: SIMP[332] -> TRAD[332]: '你什么时候回来的？' -> '你甚么时候回来的？'",
        "edit: SIMP[334] -> TRAD[334]: '你干什么？这么客气，进来坐' -> '你干甚么？这么客气，进来坐'",
        "edit: SIMP[391] -> TRAD[391]: '最近在干什么？' -> '最近在干甚么？'",
        "edit: SIMP[392] -> TRAD[392]: '我可以干什么？' -> '我可以干甚么？'",
        "edit: SIMP[409] -> TRAD[409]: '又不是赚很多，也不知为了什么' -> '又不是赚很多，也不知为了甚么'",
        "edit: SIMP[448] -> TRAD[448]: '快点\\u3000\\u3000什么事？' -> '快点\\u3000\\u3000甚么事？'",
        "edit: SIMP[450] -> TRAD[450]: '什么事？' -> '甚么事？'",
        "edit: SIMP[505] -> TRAD[505]: '不是托着' -> '不是托著'",
        "edit: SIMP[506] -> TRAD[506]: '而是按着' -> '而是按著'",
        "edit: SIMP[525] -> TRAD[525]: '搞什么？' -> '搞甚么？'",
        "edit: SIMP[527] -> TRAD[527]: '唱什么歌？' -> '唱甚么歌？'",
        "edit: SIMP[528] -> TRAD[528]: '唱什么也听不到，有什么好听？' -> '唱甚么也听不到，有甚么好听？'",
        "edit: SIMP[530] -> TRAD[530]: '唱什么也很厉害' -> '唱甚么也很厉害'",
        "edit: SIMP[555] -> TRAD[555]: '辉，你朋友要住到什么时候？' -> '辉，你朋友要住到甚么时候？'",
        "edit: SIMP[560] -> TRAD[560]: '他做什么工作的？' -> '他做甚么工作的？'",
        "edit: SIMP[582] -> TRAD[582]: '什么事？' -> '甚么事？'",
        "edit: SIMP[633] -> TRAD[633]: '吃什么？吃什么？' -> '吃甚么？吃甚么？'",
        "edit: SIMP[634] -> TRAD[634]: '吃什么？' -> '吃甚么？'",
        "edit: SIMP[640] -> TRAD[640]: '你，叫什么总？' -> '你，叫甚么总？'",
        "edit: SIMP[727] -> TRAD[727]: '打劫前，最重要教他们什么？' -> '打劫前，最重要教他们甚么？'",
        "edit: SIMP[787] -> TRAD[787]: '我刚好顺路，吓坏我们了' -> '我刚好顺路 吓坏我们了'",
        "edit: SIMP[790] -> TRAD[790]: '什么事？' -> '甚么事？'",
        "edit: SIMP[793] -> TRAD[793]: '不好意思 把小女孩吓坏了' -> '不好意思，把小女孩吓坏了'",
        "edit: SIMP[799] -> TRAD[799]: '爸爸疼妳' -> '爸爸疼你'",
        "edit: SIMP[806] -> TRAD[806]: '算不了什么' -> '算不了甚么'",
        "edit: SIMP[846] -> TRAD[846]: '你做什么？' -> '你做甚么？'",
        "edit: SIMP[850] -> TRAD[850]: '你知道你有多难跟吧？' -> '你知道你有多难找吧？'",
        "edit: SIMP[860] -> TRAD[860]: '脱什么节？' -> '脱甚么节？'",
        "edit: SIMP[903] -> TRAD[903]: '一场3 T就抢光香港人的钱了' -> '一场3T就抢光香港人的钱了'",
        "edit: SIMP[904] -> TRAD[904]: '3 T什么意思？' -> '3T甚么意思？'",
        "edit: SIMP[937] -> TRAD[937]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[953] -> TRAD[953]: '总不能，就这样回去吧？' -> '总不能就这样回去吧？'",
        "edit: SIMP[960] -> TRAD[960]: '我知道的了，您放心' -> '我知道了，您放心'",
        "edit: SIMP[975] -> TRAD[975]: '还有什么好说？' -> '还有甚么好说？'",
        "edit: SIMP[1003] -> TRAD[1003]: '吃完找两个发花帮你洗头' -> '吃完找两个发婆帮你洗头'",
        "edit: SIMP[1006] -> TRAD[1006]: '什么货我都有' -> '甚么货我都有'",
        "edit: SIMP[1010] -> TRAD[1010]: '炸什么都行！' -> '炸甚么都行！'",
        "edit: SIMP[1012] -> TRAD[1012]: '全都不是部队出身' -> '全都是部队出身'",
        "edit: SIMP[1042] -> TRAD[1042]: '我叶国欢有鳞有角！' -> '我叶国欢有棱有角！'",
        "edit: SIMP[1046] -> TRAD[1046]: '等什么？喂？' -> '等甚么？喂？'",
        "edit: SIMP[1072] -> TRAD[1072]: '刚刚最后一句你说什么？' -> '刚刚最后一句你说甚么？'",
        "edit: SIMP[1098] -> TRAD[1098]: '怎样也要留着吧？' -> '怎样也要留下些什么吧？'",
        "edit: SIMP[1107] -> TRAD[1107]: '当我说的是废话？' -> '你当我说的是废话？'",
        "edit: SIMP[1114] -> TRAD[1114]: '老大，你说什么就是什么' -> '老大，你说甚么就是甚么'",
        "edit: SIMP[1121] -> TRAD[1121]: '这么晚在吵什么？' -> '这么晚在吵甚么？'",
        "edit: SIMP[1124] -> TRAD[1124]: '现在楼上投诉' -> '现在楼上投诉了'",
        "edit: SIMP[1130] -> TRAD[1130]: '报上电台' -> '报上电台。'",
        "edit: SIMP[1143] -> TRAD[1143]: '到时无论要挟英女皇，还是中央政府' -> '到时无论要胁英女皇，还是中央政府'",
        "edit: SIMP[1148] -> TRAD[1148]: '现在位置在投诉大厦楼下' -> '现在位置在投诉人大厦楼下'",
        "edit: SIMP[1149] -> TRAD[1149]: '这里水静鹅飞，什么人也没有，完毕' -> '这里鸦雀无声，甚么人也没有，完毕'",
    ]
