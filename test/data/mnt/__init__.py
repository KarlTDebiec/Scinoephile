#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.open_ai import (
    SubtitleGroupResponse,
    SubtitleSeriesResponse,
    SyncNotesResponse,
)
from scinoephile.testing import SyncTestCase, get_test_file_path


@pytest.fixture
def mnt_input_english():
    return SubtitleSeries.load(get_test_file_path("mnt/input/en-US.srt"))


@pytest.fixture
def mnt_input_hanzi():
    return SubtitleSeries.load(get_test_file_path("mnt/input/cmn-Hans.srt"))


mnt_test_cases = [
    SyncTestCase(
        hanzi_start=0,
        hanzi_end=4,
        english_start=0,
        english_end=4,
        example_sync_notes=SyncNotesResponse(
            chinese=[
                "Chinese 1 corresponds to English 1; "
                "both express offering or referencing caramel to Dad.",
                "Chinese 2 corresponds to the first part of English 2; "
                "both saying 'thanks.'",
                "Chinese 3 corresponds to the second part of English 2; "
                "both asking about being tired.",
                "Chinese 4 corresponds to English 4; "
                "both indicating that they are almost there.",
            ],
            english=[
                "English 1 corresponds to Chinese 1; "
                "both involve offering or referencing caramel to Dad.",
                "English 2 corresponds to Chinese 2 and Chinese 3; "
                "starting with 'thanks,' then asking about tiredness.",
                "English 3 has no corresponding Chinese; "
                "as it says 'All right,' which is not present in the Chinese set, and "
                "no Chinese subtitle is displayed at that time.",
                "English 4 corresponds to Chinese 4; "
                "both indicating that they are almost there.",
            ],
        ),
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                SubtitleGroupResponse(chinese=[4], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=22,
        hanzi_end=26,
        english_start=22,
        english_end=26,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
                SubtitleGroupResponse(chinese=[3], english=[3]),
                SubtitleGroupResponse(chinese=[4], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=27,
        hanzi_end=29,
        english_start=27,
        english_end=29,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=32,
        hanzi_end=36,
        english_start=32,
        english_end=36,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
                SubtitleGroupResponse(chinese=[3, 4], english=[3]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=36,
        hanzi_end=39,
        english_start=35,
        english_end=39,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[2]),
                SubtitleGroupResponse(chinese=[2], english=[3]),
                SubtitleGroupResponse(chinese=[3], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=58,
        hanzi_end=65,
        english_start=56,
        english_end=62,
        expected_sync_response=SubtitleSeriesResponse(
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
    SyncTestCase(
        hanzi_start=65,
        hanzi_end=71,
        english_start=62,
        english_end=66,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
                SubtitleGroupResponse(chinese=[3, 4], english=[3]),
                SubtitleGroupResponse(chinese=[5, 6], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=71,
        hanzi_end=76,
        english_start=66,
        english_end=70,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
                SubtitleGroupResponse(chinese=[3], english=[3]),
                SubtitleGroupResponse(chinese=[4, 5], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=76,
        hanzi_end=82,
        english_start=70,
        english_end=74,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1, 2], english=[1]),
                SubtitleGroupResponse(chinese=[3, 4], english=[2]),
                SubtitleGroupResponse(chinese=[5], english=[3]),
                SubtitleGroupResponse(chinese=[6], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=82,
        hanzi_end=87,
        english_start=74,
        english_end=76,
        expected_sync_response=SubtitleSeriesResponse(
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
    SyncTestCase(
        hanzi_start=87,
        hanzi_end=90,
        english_start=76,
        english_end=78,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[]),
                SubtitleGroupResponse(chinese=[2], english=[1]),
                SubtitleGroupResponse(chinese=[3], english=[2]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=95,
        hanzi_end=97,
        english_start=83,
        english_end=84,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
        ),
    ),
    SyncTestCase(
        hanzi_start=97,
        hanzi_end=101,
        english_start=84,
        english_end=87,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                SubtitleGroupResponse(chinese=[4], english=[3]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=136,
        hanzi_end=146,
        english_start=109,
        english_end=117,
        expected_sync_response=SubtitleSeriesResponse(
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
    SyncTestCase(
        hanzi_start=148,
        hanzi_end=152,
        english_start=119,
        english_end=122,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                SubtitleGroupResponse(chinese=[4], english=[3]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=159,
        hanzi_end=164,
        english_start=129,
        english_end=133,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2, 3], english=[2]),
                SubtitleGroupResponse(chinese=[4], english=[3]),
                SubtitleGroupResponse(chinese=[5], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=168,
        hanzi_end=172,
        english_start=137,
        english_end=140,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1, 2], english=[1]),
                SubtitleGroupResponse(chinese=[3], english=[2]),
                SubtitleGroupResponse(chinese=[4], english=[3]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=172,
        hanzi_end=175,
        english_start=140,
        english_end=142,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2, 3], english=[2]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=177,
        hanzi_end=185,
        english_start=144,
        english_end=150,
        expected_sync_response=SubtitleSeriesResponse(
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
    SyncTestCase(
        hanzi_start=225,
        hanzi_end=234,
        english_start=182,
        english_end=190,
        expected_sync_response=SubtitleSeriesResponse(
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
    SyncTestCase(
        hanzi_start=234,
        hanzi_end=236,
        english_start=190,
        english_end=191,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
        ),
    ),
    SyncTestCase(
        hanzi_start=258,
        hanzi_end=262,
        english_start=213,
        english_end=217,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
                SubtitleGroupResponse(chinese=[3], english=[3]),
                SubtitleGroupResponse(chinese=[4], english=[4]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=262,
        hanzi_end=264,
        english_start=217,
        english_end=219,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[2]),
            ],
        ),
    ),
    SyncTestCase(
        hanzi_start=268,
        hanzi_end=270,
        english_start=223,
        english_end=224,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[SubtitleGroupResponse(chinese=[1, 2], english=[1])],
        ),
    ),
    SyncTestCase(
        hanzi_start=271,
        hanzi_end=273,
        english_start=225,
        english_end=226,
        expected_sync_response=SubtitleSeriesResponse(
            explanation="",
            synchronization=[
                SubtitleGroupResponse(chinese=[1], english=[1]),
                SubtitleGroupResponse(chinese=[2], english=[]),
            ],
        ),
    ),
]

___all__ = [
    "mnt_input_english",
    "mnt_input_hanzi",
    "test_cases",
]
