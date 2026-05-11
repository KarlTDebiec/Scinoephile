#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English translation from Cantonese with English guidance."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_block_cardinality import DualBlockCardinalityProcessor
from scinoephile.multilang.eng_yue.translation import (
    EngVsYueTranslationPrompt,
    get_eng_translated_vs_yue,
    get_eng_vs_yue_translator,
)


def test_eng_vs_yue_translation_prompt_field_names():
    """Test English-from-Cantonese prompt uses domain-specific field names."""
    assert EngVsYueTranslationPrompt.src_1(1) == "yue_1"
    assert EngVsYueTranslationPrompt.src_2(1) == "eng_reference_1"
    assert EngVsYueTranslationPrompt.output(1) == "eng_1"


def test_get_eng_vs_yue_translator_wires_processor():
    """Test English-from-Cantonese translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_eng_vs_yue_translator(test_cases=[], provider=provider)

    assert isinstance(processor, DualBlockCardinalityProcessor)
    assert processor.prompt_cls is EngVsYueTranslationPrompt
    assert processor.queryer.provider is provider


def test_get_eng_translated_vs_yue_delegates_to_processor():
    """Test English-from-Cantonese wrapper delegates to provided processor."""
    yue = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    eng = Series([Subtitle(start=900, end=3100, text="Reference line")])
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="First translated"),
            Subtitle(start=2100, end=3000, text="Second translated"),
        ]
    )
    translator = Mock(spec=DualBlockCardinalityProcessor)
    translator.process.return_value = expected

    output = get_eng_translated_vs_yue(yue, eng, translator=translator)

    assert output == expected
    translator.process.assert_called_once_with(yue, eng)
