#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for written Cantonese guided translation from Chinese."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_to_m import DualNToMProcessor
from scinoephile.multilang.yue_zho.guided_translation import (
    YueGuidedTranslationVsZhoPromptYueHans,
    get_yue_translated_from_zho_with_yue_guidance,
    get_yue_zho_guided_translator,
)


def test_yue_zho_guided_translation_prompt_field_names():
    """Test guided translation prompt uses domain-specific field names."""
    assert YueGuidedTranslationVsZhoPromptYueHans.src_1(1) == "zhongwen_1"
    assert YueGuidedTranslationVsZhoPromptYueHans.src_2(1) == "yuewen_reference_1"
    assert YueGuidedTranslationVsZhoPromptYueHans.output(1) == "yuewen_1"


def test_get_yue_zho_guided_translator_wires_processor():
    """Test written Cantonese-from-Chinese guided translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_yue_zho_guided_translator(
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert isinstance(processor, DualNToMProcessor)
    assert processor.prompt_cls is YueGuidedTranslationVsZhoPromptYueHans
    assert processor.queryer.provider is provider


def test_get_yue_translated_from_zho_with_yue_guidance_delegates_to_processor():
    """Test guided translation wrapper delegates to provided processor."""
    zhongwen = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    yuewen = Series([Subtitle(start=900, end=3100, text="参考粤文")])
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句粤文"),
            Subtitle(start=2100, end=3000, text="第二句粤文"),
        ]
    )
    translator = Mock(spec=DualNToMProcessor)
    translator.process.return_value = expected

    output = get_yue_translated_from_zho_with_yue_guidance(
        zhongwen,
        yuewen,
        translator=translator,
    )

    assert output == expected
    translator.process.assert_called_once_with(zhongwen, yuewen)
