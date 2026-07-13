#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese OCR fusion."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.ocr_fusion import OcrFusionPrompt

from .prompts import YUE_HANT_PROMPT_FIELDS

__all__ = [
    "OcrFusionPromptYueHans",
    "OcrFusionPromptYueHant",
]


OcrFusionPromptYueHant = OcrFusionPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將來自兩個唔同來源嘅粵文字幕 OCR 結果融合：Google Lens 同 PaddleOCR。
        請遵循以下原則：
        * Google Lens 喺識別漢字方面更加可靠。
        * Google Lens 喺標點符號方面更加可靠。
        * PaddleOCR 喺換行格式方面更加可靠。"""),
    src_1="lens",
    src_1_desc="Google Lens 提取嘅粵文字幕文本",
    src_2="paddle",
    src_2_desc="PaddleOCR 提取嘅粵文字幕文本",
    src_1_missing_err="缺少 Google Lens 嘅粵文字幕文本。",
    src_2_missing_err="缺少 PaddleOCR 嘅粵文字幕文本。",
    src_1_src_2_equal_err="Google Lens 同 PaddleOCR 嘅粵文字幕文本唔可以完全相同。",
    output="ronghe",
    output_desc="融合後嘅粵文字幕文本",
    note="beizhu",
    note_desc="對所做更正嘅說明",
    output_missing_err="融合後嘅粵文字幕文本唔可以爲空。",
    note_missing_err="更正說明唔可以爲空。",
)
"""LLM correspondence text for traditional written Cantonese OCR fusion."""

OcrFusionPromptYueHans = OcrFusionPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for simplified written Cantonese OCR fusion."""
