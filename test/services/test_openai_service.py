#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from typing import Any

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.services import OpenAiService
from scinoephile.testing import get_test_file_path


@pytest.fixture
def openai_service():
    return OpenAiService()


@pytest.fixture
def lm_english():
    return SubtitleSeries.load(get_test_file_path("lm/input/en-US.srt"))


@pytest.fixture
def lm_hanzi():
    return SubtitleSeries.load(get_test_file_path("lm/input/cmn-Hant.srt"))


@pytest.mark.parametrize(
    (
        "hanzi_start",
        "hanzi_end",
        "english_start",
        "english_end",
        "expected",
    ),
    [
        (
            1,
            7,
            24,
            30,
            [
                {
                    "chinese": [1],
                    "end": ["chinese", 1],
                    "english": [1],
                    "merge": "one_one",
                    "start": ["chinese", 1],
                },
                {
                    "chinese": [2, 3],
                    "end": ["chinese", 3],
                    "english": [2],
                    "merge": "two_one",
                    "start": ["chinese", 2],
                },
                {
                    "chinese": [4],
                    "end": ["chinese", 4],
                    "english": [4],
                    "merge": "one_one",
                    "start": ["chinese", 4],
                },
                {
                    "chinese": [5],
                    "end": ["chinese", 5],
                    "english": [5],
                    "merge": "one_one",
                    "start": ["chinese", 5],
                },
                {
                    "chinese": [6],
                    "end": ["chinese", 6],
                    "english": [6],
                    "merge": "one_one",
                    "start": ["chinese", 6],
                },
            ],
        ),
    ],
)
def test_1(
    openai_service: OpenAiService,
    lm_hanzi: SubtitleSeries,
    lm_english: SubtitleSeries,
    hanzi_start: int,
    hanzi_end: int,
    english_start: int,
    english_end: int,
    expected: list[dict[str, Any]],
) -> None:
    hanzi_block = lm_hanzi.slice(hanzi_start, hanzi_end)
    english_block = lm_english.slice(english_start, english_end)

    received = openai_service.get_synchronization(hanzi_block, english_block)
    received_synchronization = received.get("synchronization")

    assert received_synchronization == expected
