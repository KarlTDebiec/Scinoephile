#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat

import pytest
from scinoephile.services import OpenAiService

from scinoephile.core import SubtitleSeries
from scinoephile.core.openai.openai_service import (
    SubtitleGroupResponse,
    SubtitleSeriesResponse,
)
from scinoephile.core.subtitles import get_pair_with_zero_start
from ..data import mnt_input_english, mnt_input_hanzi


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
    [
        (
            0,
            6,
            0,
            6,
            SubtitleSeriesResponse(
                explanation=[],
                synchronization=[
                    SubtitleGroupResponse(
                        chinese=[1],
                        english=[1],
                    ),
                    SubtitleGroupResponse(
                        chinese=[2, 3],
                        english=[2],
                    ),
                    SubtitleGroupResponse(
                        chinese=[4],
                        english=[4],
                    ),
                    SubtitleGroupResponse(
                        chinese=[5],
                        english=[5],
                    ),
                    SubtitleGroupResponse(
                        chinese=[6],
                        english=[6],
                    ),
                ],
            ),
        ),
        (
            29,
            40,
            29,
            40,
            SubtitleSeriesResponse(
                explanation=[],
                synchronization=[
                    SubtitleGroupResponse(
                        chinese=[1],
                        english=[1],
                    ),
                    SubtitleGroupResponse(
                        chinese=[2],
                        english=[2],
                    ),
                    SubtitleGroupResponse(
                        chinese=[3],
                        english=[3],
                    ),
                    SubtitleGroupResponse(
                        chinese=[4],
                        english=[4],
                    ),
                    SubtitleGroupResponse(
                        chinese=[5],
                        english=[5],
                    ),
                    SubtitleGroupResponse(
                        chinese=[6],
                        english=[6],
                    ),
                    SubtitleGroupResponse(
                        chinese=[7],
                        english=[],
                    ),
                    SubtitleGroupResponse(
                        chinese=[8],
                        english=[8],
                    ),
                    SubtitleGroupResponse(
                        chinese=[9],
                        english=[9],
                    ),
                    SubtitleGroupResponse(
                        chinese=[10],
                        english=[10],
                    ),
                    SubtitleGroupResponse(
                        chinese=[11],
                        english=[11],
                    ),
                ],
            ),
        ),
        (
            44,
            56,
            44,
            54,
            SubtitleSeriesResponse(
                explanation=[],
                synchronization=[
                    SubtitleGroupResponse(
                        chinese=[1],
                        english=[1],
                    ),
                    SubtitleGroupResponse(
                        chinese=[2],
                        english=[2],
                    ),
                    SubtitleGroupResponse(
                        chinese=[3],
                        english=[3],
                    ),
                    SubtitleGroupResponse(
                        chinese=[4],
                        english=[4],
                    ),
                    SubtitleGroupResponse(
                        chinese=[5],
                        english=[5],
                    ),
                    SubtitleGroupResponse(
                        chinese=[6, 7],
                        english=[6],
                    ),
                    SubtitleGroupResponse(
                        chinese=[8],
                        english=[],
                    ),
                    SubtitleGroupResponse(
                        chinese=[9],
                        english=[7],
                    ),
                    SubtitleGroupResponse(
                        chinese=[10],
                        english=[8],
                    ),
                    SubtitleGroupResponse(
                        chinese=[11],
                        english=[9],
                    ),
                    SubtitleGroupResponse(
                        chinese=[12],
                        english=[10],
                    ),
                ],
            ),
        ),
    ],
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

    received = openai_service.get_synchronization(hanzi_block, english_block)

    print()
    print(f"Chinese input:\n{hanzi_block.to_string('srt')}")
    print(f"English input:\n{english_block.to_string('srt')}")
    print(f"Expected synchronization:\n{pformat(expected.synchronization)}")
    print(f"Received synchronization:\n{pformat(received.synchronization)}")
    print(
        "Received explanation (not validated for accuracy):\n"
        f"{pformat(received.explanation)}"
    )

    assert received.synchronization == expected.synchronization
