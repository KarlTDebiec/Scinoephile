#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 中文 OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.prompts import ZhoHansPrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionPrompt

__all__ = [
    "ZhoHansOcrFusionPrompt",
    "ZhoHantOcrFusionPrompt",
]


class ZhoHansOcrFusionPrompt(OcrFusionPrompt, ZhoHansPrompt):
    """Text for LLM correspondence for 简体中文 OCR fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将来自两个不同来源的中文字幕 OCR 结果进行融合：Google Lens 和 PaddleOCR。
        请遵循以下原则：
        * Google Lens 在识别汉字方面更可靠。
        * Google Lens 在标点符号方面更可靠。
        * PaddleOCR 在换行格式方面更可靠。""")
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
        "Google Lens 与 PaddleOCR 的字幕文本不能完全相同。"
    )
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "ronghe"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "融合后的字幕文本"
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "对所做更正的说明"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "融合后的字幕文本不能为空。"
    """Error when output field is missing from answer."""

    note_missing_err: ClassVar[str] = "更正说明不能为空。"
    """Error when note field is missing from answer."""


class ZhoHantOcrFusionPrompt(ZhoHansOcrFusionPrompt):
    """Text for LLM correspondence for 繁体中文 OCR fusion."""

    opencc_config = OpenCCConfig.s2t
    """Config with which to convert characters from 简体中文 present in parent class."""
