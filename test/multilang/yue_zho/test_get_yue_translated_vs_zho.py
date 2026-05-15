#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for written Cantonese translation from Chinese."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_to_m import DualNToMProcessor
from scinoephile.multilang.yue_zho.translation import (
    YueTranslationVsZhoPromptYueHans,
    get_yue_translated_from_zho,
    get_yue_zho_translator,
)


def test_yue_zho_translation_prompt_field_names():
    """Test translation prompt uses domain-specific field names."""
    assert YueTranslationVsZhoPromptYueHans.src_1(1) == "zhongwen_1"
    assert YueTranslationVsZhoPromptYueHans.src_2(1) == "context_1"
    assert YueTranslationVsZhoPromptYueHans.output(1) == "yuewen_1"


def test_get_yue_zho_translator_wires_processor():
    """Test written Cantonese-from-Chinese translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_yue_zho_translator(
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert isinstance(processor, DualNToMProcessor)
    assert processor.prompt_cls is YueTranslationVsZhoPromptYueHans
    assert processor.queryer.provider is provider


def test_get_yue_translated_from_zho_delegates_to_processor_with_empty_context():
    """Test regular translation wrapper delegates to the provided processor."""
    zhongwen = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句粤文"),
            Subtitle(start=2100, end=3000, text="第二句粤文"),
        ]
    )
    translator = Mock(spec=DualNToMProcessor)
    translator.process.return_value = expected

    output = get_yue_translated_from_zho(zhongwen, translator=translator)

    assert output == expected
    call_args = translator.process.call_args.args
    assert call_args[0] is zhongwen
    assert isinstance(call_args[1], Series)
    assert len(call_args[1].events) == 0
