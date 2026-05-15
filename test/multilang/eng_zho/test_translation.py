#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English translation from Chinese."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_to_m import DualNToMProcessor
from scinoephile.multilang.eng_zho.translation import (
    EngTranslationVsZhoPrompt,
    get_eng_translated_from_zho,
    get_eng_zho_translator,
)


def test_eng_zho_translation_prompt_field_names():
    """Test translation prompt uses domain-specific field names."""
    assert EngTranslationVsZhoPrompt.src_1(1) == "zho_1"
    assert EngTranslationVsZhoPrompt.src_2(1) == "context_1"
    assert EngTranslationVsZhoPrompt.output(1) == "eng_1"


def test_get_eng_zho_translator_wires_processor():
    """Test English-from-Chinese translator factory wiring."""
    provider = Mock(spec=LLMProvider)

    processor = get_eng_zho_translator(test_cases=[], provider=provider)

    assert isinstance(processor, DualNToMProcessor)
    assert processor.prompt_cls is EngTranslationVsZhoPrompt
    assert processor.queryer.provider is provider


def test_get_eng_translated_from_zho_delegates_to_processor_with_empty_context():
    """Test regular translation wrapper delegates to the provided processor."""
    zho = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="First translated"),
            Subtitle(start=2100, end=3000, text="Second translated"),
        ]
    )
    translator = Mock(spec=DualNToMProcessor)
    translator.process.return_value = expected

    output = get_eng_translated_from_zho(zho, translator=translator)

    assert output == expected
    call_args = translator.process.call_args.args
    assert call_args[0] is zho
    assert isinstance(call_args[1], Series)
    assert len(call_args[1].events) == 0
