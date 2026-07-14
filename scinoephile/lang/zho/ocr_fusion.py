#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for standard Chinese OCR fusion."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.llms.ocr_fusion import OcrFusionPrompt

from .prompts import ZHO_HANT_PROMPT_FIELDS
from .script.conversion import OpenCCConfig, get_zho_text_converted

__all__ = [
    "OcrFusionPromptZhoHans",
    "OcrFusionPromptZhoHant",
]


OcrFusionPromptZhoHant = OcrFusionPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將來自兩個不同來源的中文字幕 OCR 結果進行融合：Google Lens 和 PaddleOCR。
        請遵循以下原則：
        * Google Lens 在識別漢字方面更可靠。
        * Google Lens 在標點符號方面更可靠。
        * PaddleOCR 在換行格式方面更可靠。"""),
    src_1="lens",
    src_1_desc="Google Lens 提取的字幕文本",
    src_2="paddle",
    src_2_desc="PaddleOCR 提取的字幕文本",
    src_1_missing_err="缺少 Google Lens 的中文字幕文本。",
    src_2_missing_err="缺少 PaddleOCR 的中文字幕文本。",
    src_1_src_2_equal_err="Google Lens 與 PaddleOCR 的字幕文本不能完全相同。",
    output="ronghe",
    output_desc="融合後的字幕文本",
    note="beizhu",
    note_desc="對所做更正的說明",
    output_missing_err="融合後的字幕文本不能爲空。",
    note_missing_err="更正說明不能爲空。",
)
"""Text for LLM correspondence for traditional standard Chinese OCR fusion."""

OcrFusionPromptZhoHans = OcrFusionPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for LLM correspondence for simplified standard Chinese OCR fusion."""
