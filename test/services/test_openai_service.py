#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.core.openai import (
    OpenAiService,
    SubtitleGroupResponse,
    SubtitleSeriesResponse,
)
from scinoephile.core.subtitles import (
    get_pair_strings_with_proportional_timings,
    get_pair_with_zero_start,
)
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
            4,
            0,
            4,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                ],
            ),
        ),
        (
            22,
            26,
            22,
            26,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                ],
            ),
        ),
        (
            27,
            29,
            27,
            29,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                ],
            ),
        ),
        (
            32,
            36,
            32,
            36,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3, 4], english=[3]),
                ],
            ),
        ),
        (
            36,
            39,
            35,
            39,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[2]),
                    SubtitleGroupResponse(chinese=[2], english=[3]),
                    SubtitleGroupResponse(chinese=[3], english=[4]),
                ],
            ),
        ),
        (
            58,
            65,
            56,
            62,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                    SubtitleGroupResponse(chinese=[5, 6, 7], english=[5]),
                ],
            ),
        ),
        (
            65,
            71,
            62,
            66,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3, 4], english=[3]),
                    SubtitleGroupResponse(chinese=[5, 6], english=[4]),
                ],
            ),
        ),
        (
            71,
            76,
            66,
            70,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4, 5], english=[4]),
                ],
            ),
        ),
        (
            76,
            82,
            70,
            74,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1, 2], english=[1]),
                    SubtitleGroupResponse(chinese=[3, 4], english=[2]),
                    SubtitleGroupResponse(chinese=[5], english=[3]),
                    SubtitleGroupResponse(chinese=[6], english=[4]),
                ],
            ),
        ),
        (
            82,
            87,
            74,
            76,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[]),
                    SubtitleGroupResponse(chinese=[4], english=[]),
                    SubtitleGroupResponse(chinese=[5], english=[]),
                ],
            ),
        ),
        (
            87,
            90,
            76,
            78,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[]),
                    SubtitleGroupResponse(chinese=[2], english=[1]),
                    SubtitleGroupResponse(chinese=[3], english=[2]),
                ],
            ),
        ),
        (
            95,
            97,
            83,
            84,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
            ),
        ),
        (
            97,
            101,
            84,
            87,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[3]),
                ],
            ),
        ),
        (
            136,
            146,
            109,
            117,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                    SubtitleGroupResponse(chinese=[5, 6], english=[5]),
                    SubtitleGroupResponse(chinese=[7, 8], english=[6]),
                    SubtitleGroupResponse(chinese=[9], english=[7]),
                    SubtitleGroupResponse(chinese=[10], english=[8]),
                ],
            ),
        ),
        (
            148,
            152,
            119,
            122,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[3]),
                ],
            ),
        ),
        (
            159,
            164,
            129,
            133,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[3]),
                    SubtitleGroupResponse(chinese=[5], english=[4]),
                ],
            ),
        ),
        (
            168,
            172,
            137,
            140,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1, 2], english=[1]),
                    SubtitleGroupResponse(chinese=[3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[3]),
                ],
            ),
        ),
        (
            172,
            175,
            140,
            142,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                ],
            ),
        ),
        (
            177,
            185,
            144,
            150,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                    SubtitleGroupResponse(chinese=[5], english=[5]),
                    SubtitleGroupResponse(chinese=[6, 7], english=[6]),
                    SubtitleGroupResponse(chinese=[8], english=[]),
                ],
            ),
        ),
        (
            225,
            234,
            182,
            190,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                    SubtitleGroupResponse(chinese=[4], english=[3]),
                    SubtitleGroupResponse(chinese=[5], english=[4]),
                    SubtitleGroupResponse(chinese=[6], english=[5]),
                    SubtitleGroupResponse(chinese=[7], english=[6]),
                    SubtitleGroupResponse(chinese=[8], english=[7]),
                    SubtitleGroupResponse(chinese=[9], english=[8]),
                ],
            ),
        ),
        (
            234,
            236,
            190,
            191,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
            ),
        ),
        (
            258,
            262,
            213,
            217,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                    SubtitleGroupResponse(chinese=[3], english=[3]),
                    SubtitleGroupResponse(chinese=[4], english=[4]),
                ],
            ),
        ),
        (
            262,
            264,
            217,
            219,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[2]),
                ],
            ),
        ),
        (
            268,
            270,
            223,
            224,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
            ),
        ),
        (
            271,
            273,
            225,
            226,
            SubtitleSeriesResponse(
                explanation="",
                synchronization=[
                    SubtitleGroupResponse(chinese=[1], english=[1]),
                    SubtitleGroupResponse(chinese=[2], english=[]),
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
