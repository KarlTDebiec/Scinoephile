#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.core.subtitles import (
    get_pair_strings_with_proportional_timings,
    get_pair_with_zero_start,
)
from scinoephile.open_ai import (
    OpenAiService,
    SubtitleSeriesResponse,
)
from ..data.mnt import mnt_input_english, mnt_input_hanzi, mnt_test_cases


@pytest.fixture
def openai_service():
    return OpenAiService()


@pytest.mark.parametrize(
    (
        "hanzi_start",
        "hanzi_end",
        "english_start",
        "english_end",
        "expected",
    ),
    mnt_test_cases,
)
def test_mnt(
    openai_service: OpenAiService,
    mnt_input_hanzi: SubtitleSeries,
    hanzi_start: int,
    hanzi_end: int,
    mnt_input_english: SubtitleSeries,
    english_start: int,
    english_end: int,
    expected: SubtitleSeriesResponse,
) -> None:
    hanzi_block = mnt_input_hanzi.slice(hanzi_start, hanzi_end)
    english_block = mnt_input_english.slice(english_start, english_end)
    hanzi_block, english_block = get_pair_with_zero_start(hanzi_block, english_block)
    hanzi_str, english_str = get_pair_strings_with_proportional_timings(
        hanzi_block, english_block
    )

    received = openai_service.get_synchronization(hanzi_block, english_block)

    print(f"CHINESE:\n{hanzi_str}\n")
    print(f"ENGLISH:\n{english_str}\n")
    print(f"Expected synchronization:\n{pformat(expected.synchronization)}\n")
    print(f"Received synchronization:\n{pformat(received.synchronization)}\n")
    print(f"Received explanation (not validated for accuracy):\n{received.explanation}")

    assert received.synchronization == expected.synchronization
