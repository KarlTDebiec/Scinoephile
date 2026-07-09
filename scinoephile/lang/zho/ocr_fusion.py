#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for standard Chinese OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.ocr_fusion import OcrFusionPrompt

__all__ = [
    "OcrFusionPromptZhoHans",
    "OcrFusionPromptZhoHant",
]


class OcrFusionPromptZhoHant(OcrFusionPrompt, PromptZhoHant):
    """Text for LLM correspondence for traditional standard Chinese OCR fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責將來自兩個不同來源的中文字幕 OCR 結果進行融合：Google Lens 和 PaddleOCR。
        請遵循以下原則：
        * Google Lens 在識別漢字方面更可靠。
        * Google Lens 在標點符號方面更可靠。
        * PaddleOCR 在換行格式方面更可靠。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "lens"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "Google Lens 提取的字幕文本"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "paddle"
    """Name for source two field in query."""

    src_2_desc: ClassVar[str] = "PaddleOCR 提取的字幕文本"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "缺少 Google Lens 的中文字幕文本。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "缺少 PaddleOCR 的中文字幕文本。"
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = (
        "Google Lens 與 PaddleOCR 的字幕文本不能完全相同。"
    )
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "ronghe"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "融合後的字幕文本"
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "對所做更正的說明"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "融合後的字幕文本不能爲空。"
    """Error when output field is missing from answer."""

    note_missing_err: ClassVar[str] = "更正說明不能爲空。"
    """Error when note field is missing from answer."""


class OcrFusionPromptZhoHans(OcrFusionPromptZhoHant):
    """Text for LLM correspondence for simplified standard Chinese OCR fusion."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""
