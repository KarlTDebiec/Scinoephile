#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for dual n to m LLM processing."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_to_m import (
    DualNToMProcessor,
    DualNToMPrompt,
)


class _Prompt(DualNToMPrompt):
    """Prompt fixture for dual n to m processor tests."""


def test_process_outputs_one_subtitle_per_source_one_subtitle():
    """Test processor output follows source one timing and answer cardinality."""
    provider = Mock(spec=LLMProvider)
    processor = DualNToMProcessor(prompt_cls=_Prompt, provider=provider)

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


def test_process_stop_at_idx_zero_processes_no_blocks():
    """Test stop_at_idx 0 stops before processing any blocks."""
    provider = Mock(spec=LLMProvider)
    processor = DualNToMProcessor(prompt_cls=_Prompt, provider=provider)
    processor.queryer = Mock()
    source_one = Series([Subtitle(start=1000, end=2000, text="第一句")])
    source_two = Series([Subtitle(start=1000, end=2000, text="Reference")])

    output = processor.process(source_one, source_two, stop_at_idx=0)

    assert output == Series()
    processor.queryer.assert_not_called()


def test_process_rejects_negative_stop_at_idx():
    """Test negative stop_at_idx values are rejected."""
    provider = Mock(spec=LLMProvider)
    processor = DualNToMProcessor(prompt_cls=_Prompt, provider=provider)
    source_one = Series([Subtitle(start=1000, end=2000, text="第一句")])
    source_two = Series([Subtitle(start=1000, end=2000, text="Reference")])

    with pytest.raises(ValueError, match="stop_at_idx"):
        processor.process(source_one, source_two, stop_at_idx=-1)
