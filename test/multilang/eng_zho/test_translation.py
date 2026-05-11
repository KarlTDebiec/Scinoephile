#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English translation from Chinese with English guidance."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_block_cardinality import DualBlockCardinalityProcessor
from scinoephile.multilang.eng_zho.translation import (
    EngVsZhoTranslationPrompt,
    get_eng_translated_vs_zho,
    get_eng_vs_zho_translator,
)


def test_eng_vs_zho_translation_prompt_field_names():
    """Test English-from-Chinese prompt uses domain-specific field names."""
    assert EngVsZhoTranslationPrompt.src_1(1) == "zho_1"
    assert EngVsZhoTranslationPrompt.src_2(1) == "eng_reference_1"
    assert EngVsZhoTranslationPrompt.output(1) == "eng_1"


def test_get_eng_vs_zho_translator_wires_processor():
    """Test English-from-Chinese translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_eng_vs_zho_translator(test_cases=[], provider=provider)

    assert isinstance(processor, DualBlockCardinalityProcessor)
    assert processor.prompt_cls is EngVsZhoTranslationPrompt
    assert processor.queryer.provider is provider


def test_get_eng_translated_vs_zho_delegates_to_processor():
    """Test English-from-Chinese wrapper delegates to provided processor."""
    zho = Series(
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

    output = get_eng_translated_vs_zho(zho, eng, translator=translator)

    assert output == expected
    translator.process.assert_called_once_with(zho, eng)
