#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English gapped translation from Chinese."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNProcessor
from scinoephile.multilang.eng_zho.gapped_translation import (
    EngGappedTranslationVsZhoPrompt,
    get_eng_gapped_translated_vs_zho,
    get_eng_vs_zho_gapped_translator,
)


def test_eng_zho_gapped_translation_prompt_field_names():
    """Test gapped translation prompt uses domain-specific field names."""
    assert EngGappedTranslationVsZhoPrompt.src_1(1) == "eng_1"
    assert EngGappedTranslationVsZhoPrompt.src_2(1) == "zho_1"
    assert EngGappedTranslationVsZhoPrompt.output(1) == "eng_1"


def test_get_eng_vs_zho_gapped_translator_wires_processor():
    """Test English-from-Chinese gapped translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_eng_vs_zho_gapped_translator(test_cases=[], provider=provider)

    assert isinstance(processor, DualNMinusMToNProcessor)
    assert processor.prompt_cls is EngGappedTranslationVsZhoPrompt
    assert processor.queryer.provider is provider


def test_get_eng_gapped_translated_vs_zho_delegates_to_processor():
    """Test gapped translation wrapper delegates to the provided processor."""
    eng = Series([Subtitle(start=1000, end=2000, text="Existing line")])
    zho = Series(
        [
            Subtitle(start=1000, end=2000, text="已有行"),
            Subtitle(start=2100, end=3000, text="缺失行"),
        ]
    )
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="Existing line"),
            Subtitle(start=2100, end=3000, text="Missing line"),
        ]
    )
    translator = Mock(spec=DualNMinusMToNProcessor)
    translator.process.return_value = expected

    output = get_eng_gapped_translated_vs_zho(
        eng,
        zho,
        translator=translator,
    )

    assert output == expected
    translator.process.assert_called_once_with(eng, zho)
