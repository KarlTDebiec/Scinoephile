#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese OCR fusion."""

from __future__ import annotations

from functools import partial
from typing import ClassVar

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHant
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)
from scinoephile.llms.ocr_fusion import OcrFusionPrompt
from scinoephile.llms.prompt_definition import define_prompt

__all__ = [
    "OcrFusionPromptYueHans",
    "OcrFusionPromptYueHant",
]


@define_prompt(OcrFusionPrompt, Language.yue_hant, parent=PromptYueHant)
class OcrFusionPromptYueHant:
    """LLM correspondence text for traditional written Cantonese OCR fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責將來自兩個唔同來源嘅粵文字幕 OCR 結果融合：Google Lens 同 PaddleOCR。
        請遵循以下原則：
        * Google Lens 喺識別漢字方面更加可靠。
        * Google Lens 喺標點符號方面更加可靠。
        * PaddleOCR 喺換行格式方面更加可靠。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "lens"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "Google Lens 提取嘅粵文字幕文本"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "paddle"
    """Name for source two field in query."""

    src_2_desc: ClassVar[str] = "PaddleOCR 提取嘅粵文字幕文本"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "缺少 Google Lens 嘅粵文字幕文本。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "缺少 PaddleOCR 嘅粵文字幕文本。"
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = (
        "Google Lens 同 PaddleOCR 嘅粵文字幕文本唔可以完全相同。"
    )
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "ronghe"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "融合後嘅粵文字幕文本"
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "對所做更正嘅說明"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "融合後嘅粵文字幕文本唔可以爲空。"
    """Error when output field is missing from answer."""

    note_missing_err: ClassVar[str] = "更正說明唔可以爲空。"
    """Error when note field is missing from answer."""


@define_prompt(
    OcrFusionPrompt,
    Language.yue_hans,
    parent=OcrFusionPromptYueHant,
    transform=partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
class OcrFusionPromptYueHans:
    """LLM correspondence text for simplified written Cantonese OCR fusion."""
