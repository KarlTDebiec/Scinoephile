#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for mono n LLM processing."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.mono_n import MonoNProcessor, MonoNPrompt


class _PlainPrompt(MonoNPrompt):
    """Plain transform prompt fixture for mono n processor tests."""


def test_process_can_write_empty_generated_output():
    """Test mono n prompts can replace source text with empty output."""
    provider = Mock(spec=LLMProvider)
    processor = MonoNProcessor(prompt_cls=_PlainPrompt, provider=provider)

    def fake_queryer(test_case):
        """Return deterministic empty answer text."""
        answer = test_case.answer_cls.model_validate({"output_1": ""})
        return type(test_case)(query=test_case.query, answer=answer)

    processor.queryer = fake_queryer
    source = Series([Subtitle(start=1000, end=2000, text="Source text")])

    output = processor.process(source)

    assert output == Series([Subtitle(start=1000, end=2000, text="")])


def test_process_does_not_mutate_source_series():
    """Test mono n processing leaves the source series unchanged."""
    provider = Mock(spec=LLMProvider)
    processor = MonoNProcessor(prompt_cls=_PlainPrompt, provider=provider)

    def fake_queryer(test_case):
        """Return deterministic generated answer text."""
        answer = test_case.answer_cls.model_validate({"output_1": "Generated text"})
        return type(test_case)(query=test_case.query, answer=answer)

    processor.queryer = fake_queryer
    source = Series([Subtitle(start=1000, end=2000, text="Source text")])

    output = processor.process(source)

    assert source == Series([Subtitle(start=1000, end=2000, text="Source text")])
    assert output == Series([Subtitle(start=1000, end=2000, text="Generated text")])
