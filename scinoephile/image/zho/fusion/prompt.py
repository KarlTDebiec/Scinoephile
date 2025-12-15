#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 中文 fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zho import OpenCCConfig, ZhoPrompt, get_zho_text_converted
from scinoephile.image.fusion import FusionPrompt

__all__ = [
    "ZhoHansFusionPrompt",
    "ZhoHantFusionPrompt",
]


class ZhoHansFusionPrompt(FusionPrompt, ZhoPrompt):
    """LLM correspondence text for 简体中文 fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将来自两个不同来源的中文字幕 OCR 结果进行融合：Google Lens 和 PaddleOCR。
        请遵循以下原则：
        * Google Lens 在识别汉字方面更可靠。
        * Google Lens 在标点符号方面更可靠。
        * PaddleOCR 在换行格式方面更可靠。""")
    """Base system prompt."""

    # Query fields
    source_one_field: ClassVar[str] = "lens"
    """Field name for OCR source one."""

    source_one_description: ClassVar[str] = "Google Lens 提取的字幕文本"
    """Description of source one field."""

    source_two_field: ClassVar[str] = "paddle"
    """Field name for OCR source two."""

    source_two_description: ClassVar[str] = "PaddleOCR 提取的字幕文本"
    """Description of source two field."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = "缺少 Google Lens 的中文字幕文本。"
    """Error message when source one field is missing."""

    source_two_missing_error: ClassVar[str] = "缺少 PaddleOCR 的中文字幕文本。"
    """Error message when source two field is missing."""

    sources_equal_error: ClassVar[str] = (
        "Google Lens 与 PaddleOCR 的字幕文本不能完全相同。"
    )
    """Error message when source one and two fields are equal."""

    # Answer fields
    fused_field: ClassVar[str] = "ronghe"
    """Field name for fused subtitle text."""

    fused_description: ClassVar[str] = "融合后的字幕文本"
    """Description of fused field."""

    note_field: ClassVar[str] = "beizhu"
    """Field name for explanation of changes."""

    note_description: ClassVar[str] = "对所做更正的说明"
    """Description of note field."""

    # Answer validation errors
    fused_missing_error: ClassVar[str] = "融合后的字幕文本不能为空。"
    """Error message when fused field is missing."""

    note_missing_error: ClassVar[str] = "更正说明不能为空。"
    """Error message when note field is missing."""


class ZhoHantFusionPrompt(FusionPrompt, ZhoPrompt):
    """LLM correspondence text for 繁体中文 fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.base_system_prompt, OpenCCConfig.s2t
    )
    """Base system prompt."""

    # Query fields
    source_one_field: ClassVar[str] = "lens"
    """Field name for OCR source one."""

    source_one_description: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.source_one_description, OpenCCConfig.s2t
    )
    """Description of source one field."""

    source_two_field: ClassVar[str] = "paddle"
    """Field name for OCR source two."""

    source_two_description: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.source_two_description, OpenCCConfig.s2t
    )
    """Description of source two field."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.source_one_missing_error, OpenCCConfig.s2t
    )
    """Error message when source one field is missing."""

    source_two_missing_error: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.source_two_missing_error, OpenCCConfig.s2t
    )
    """Error message when source two field is missing."""

    sources_equal_error: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.sources_equal_error, OpenCCConfig.s2t
    )
    """Error message when source one and two fields are equal."""

    # Answer fields
    fused_field: ClassVar[str] = "ronghe"
    """Field name for fused subtitle text."""

    fused_description: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.fused_description, OpenCCConfig.s2t
    )
    """Description of fused field."""

    note_field: ClassVar[str] = "beizhu"
    """Field name for explanation of changes."""

    note_description: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.note_description, OpenCCConfig.s2t
    )
    """Description of note field."""

    # Answer validation errors
    fused_missing_error: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.fused_missing_error, OpenCCConfig.s2t
    )
    """Error message when fused field is missing."""

    note_missing_error: ClassVar[str] = get_zho_text_converted(
        ZhoHansFusionPrompt.note_missing_error, OpenCCConfig.s2t
    )
    """Error message when note field is missing."""
