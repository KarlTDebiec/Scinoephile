#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block review LLM processing."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.block_review import BlockReviewProcessor, BlockReviewPrompt


class _ReviewPrompt(BlockReviewPrompt):
    """Review prompt fixture for block review processor tests."""


def test_process_applies_changed_output():
    """Test block review processing applies changed output text."""
    provider = Mock(spec=LLMProvider)
    processor = BlockReviewProcessor(prompt_cls=_ReviewPrompt, provider=provider)

    def fake_queryer(test_case):
        """Return deterministic changed answer text."""
        answer = test_case.answer_cls.model_validate(
            {"output_1": "Edited text", "note_1": "Fixed typo"}
        )
        return type(test_case)(query=test_case.query, answer=answer)

    processor.queryer = fake_queryer
    source = Series([Subtitle(start=1000, end=2000, text="Source text")])

    output = processor.process(source)

    assert output == Series([Subtitle(start=1000, end=2000, text="Edited text")])


def test_process_keeps_source_text_for_empty_output():
    """Test block review empty outputs leave source text unchanged."""
    provider = Mock(spec=LLMProvider)
    processor = BlockReviewProcessor(prompt_cls=_ReviewPrompt, provider=provider)

    def fake_queryer(test_case):
        """Return deterministic no-change answer text."""
        answer = test_case.answer_cls.model_validate({"output_1": "", "note_1": ""})
        return type(test_case)(query=test_case.query, answer=answer)

    processor.queryer = fake_queryer
    source = Series([Subtitle(start=1000, end=2000, text="Source text")])

    output = processor.process(source)

    assert output == Series([Subtitle(start=1000, end=2000, text="Source text")])
