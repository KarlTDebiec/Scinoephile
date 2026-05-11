#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for dual block cardinality LLM processing."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_block_cardinality import (
    DualBlockCardinalityProcessor,
    DualBlockCardinalityPrompt,
)


class _Prompt(DualBlockCardinalityPrompt):
    """Prompt fixture for dual block cardinality processor tests."""


def test_process_outputs_one_subtitle_per_source_one_subtitle():
    """Test processor output follows source one timing and answer cardinality."""
    provider = Mock(spec=LLMProvider)
    processor = DualBlockCardinalityProcessor(prompt_cls=_Prompt, provider=provider)

    def fake_queryer(test_case):
        """Return deterministic answer text."""
        answer = test_case.answer_cls(
            output_1="First translated",
            output_2="Second translated",
        )
        return type(test_case)(query=test_case.query, answer=answer)

    processor.queryer = fake_queryer
    source_one = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    source_two = Series(
        [
            Subtitle(start=900, end=1300, text="First reference"),
            Subtitle(start=1400, end=2200, text="Second reference"),
            Subtitle(start=2300, end=3100, text="Third reference"),
        ]
    )

    output = processor.process(source_one, source_two)

    assert output == Series(
        [
            Subtitle(start=1000, end=2000, text="First translated"),
            Subtitle(start=2100, end=3000, text="Second translated"),
        ]
    )
