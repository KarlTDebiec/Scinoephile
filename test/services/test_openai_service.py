#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat
from typing import Any

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.services import OpenAiService
from ..fixtures import mnt_english, mnt_hanzi  # noqa: F401


@pytest.fixture
def openai_service():
    return OpenAiService()


@pytest.mark.parametrize(
    (
        "hanzi",
        "hanzi_start",
        "hanzi_end",
        "english",
        "english_start",
        "english_end",
        "expected_synchronization",
    ),
    [
        (
            "mnt_hanzi",
            1,
            7,
            "mnt_english",
            24,
            30,
            [
                {
                    "chinese": [1],
                    "end": ["chinese", 1],
                    "english": [1],
                    "start": ["chinese", 1],
                },
                {
                    "chinese": [2, 3],
                    "end": ["chinese", 3],
                    "english": [2],
                    "start": ["chinese", 2],
                },
                {
                    "chinese": [4],
                    "end": ["chinese", 4],
                    "english": [4],
                    "start": ["chinese", 4],
                },
                {
                    "chinese": [5],
                    "end": ["chinese", 5],
                    "english": [5],
                    "start": ["chinese", 5],
                },
                {
                    "chinese": [6],
                    "end": ["chinese", 6],
                    "english": [6],
                    "start": ["chinese", 6],
                },
            ],
        ),
        (
            "mnt_hanzi",
            30,
            41,
            "mnt_english",
            53,
            64,
            [
                {
                    "chinese": [1],
                    "end": ["chinese", 1],
                    "english": [1],
                    "start": ["chinese", 1],
                },
                {
                    "chinese": [2],
                    "end": ["chinese", 2],
                    "english": [2],
                    "start": ["chinese", 2],
                },
                {
                    "chinese": [3],
                    "end": ["chinese", 3],
                    "english": [3],
                    "start": ["chinese", 3],
                },
                {
                    "chinese": [4],
                    "end": ["chinese", 4],
                    "english": [4],
                    "start": ["chinese", 4],
                },
                {
                    "chinese": [5],
                    "end": ["chinese", 5],
                    "english": [5],
                    "start": ["chinese", 5],
                },
                {
                    "chinese": [6],
                    "end": ["chinese", 6],
                    "english": [6],
                    "start": ["chinese", 6],
                },
                {
                    "chinese": [7],
                    "end": ["chinese", 7],
                    "english": [],
                    "start": ["chinese", 7],
                },
                {
                    "chinese": [8],
                    "end": ["chinese", 8],
                    "english": [8],
                    "start": ["chinese", 8],
                },
                {
                    "chinese": [9],
                    "end": ["chinese", 9],
                    "english": [9],
                    "start": ["chinese", 9],
                },
                {
                    "chinese": [10],
                    "end": ["chinese", 10],
                    "english": [10],
                    "start": ["chinese", 10],
                },
                {
                    "chinese": [11],
                    "end": ["chinese", 11],
                    "english": [11],
                    "start": ["chinese", 11],
                },
            ],
        ),
        (
            "mnt_hanzi",
            45,
            57,
            "mnt_english",
            68,
            78,
            [
                {
                    "chinese": [1],
                    "end": ["chinese", 1],
                    "english": [1],
                    "start": ["chinese", 1],
                },
                {
                    "chinese": [2],
                    "end": ["chinese", 2],
                    "english": [2],
                    "start": ["chinese", 2],
                },
                {
                    "chinese": [3],
                    "end": ["chinese", 3],
                    "english": [3],
                    "start": ["chinese", 3],
                },
                {
                    "chinese": [4],
                    "end": ["chinese", 4],
                    "english": [4],
                    "start": ["chinese", 4],
                },
                {
                    "chinese": [5],
                    "end": ["chinese", 5],
                    "english": [5],
                    "start": ["chinese", 5],
                },
                {
                    "chinese": [6, 7],
                    "end": ["chinese", 7],
                    "english": [6],
                    "start": ["chinese", 6],
                },
                {
                    "chinese": [8],
                    "end": ["chinese", 8],
                    "english": [],
                    "start": ["chinese", 8],
                },
                {
                    "chinese": [9],
                    "end": ["chinese", 9],
                    "english": [7],
                    "start": ["chinese", 9],
                },
                {
                    "chinese": [10],
                    "end": ["chinese", 10],
                    "english": [8],
                    "start": ["chinese", 10],
                },
                {
                    "chinese": [11],
                    "end": ["chinese", 11],
                    "english": [9],
                    "start": ["chinese", 11],
                },
                {
                    "chinese": [12],
                    "end": ["chinese", 12],
                    "english": [10],
                    "start": ["chinese", 12],
                },
            ],
        ),
    ],
    indirect=["hanzi", "english"],
)
def test_block(
    openai_service: OpenAiService,
    hanzi: SubtitleSeries,
    hanzi_start: int,
    hanzi_end: int,
    english: SubtitleSeries,
    english_start: int,
    english_end: int,
    expected_synchronization: list[dict[str, Any]],
) -> None:
    hanzi_block = hanzi.slice(hanzi_start, hanzi_end)
    english_block = english.slice(english_start, english_end)

    received = openai_service.get_synchronization(hanzi_block, english_block)
    recieved_explanation = received.get("explanation")
    received_synchronization = received.get("synchronization")

    print()
    print(f"Chinese input:\n{hanzi_block.to_string('srt')}")
    print(f"English input:\n{english_block.to_string('srt')}")
    print(f"Expected synchronization:\n{pformat(expected_synchronization)}")
    print(f"Received synchronization:\n{pformat(received_synchronization)}")
    print(
        "Received explanation (not validated for accuracy):\n"
        f"{pformat(recieved_explanation)}"
    )

    assert received_synchronization == expected_synchronization
