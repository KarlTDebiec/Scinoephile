#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

import pytest

from scinoephile.core import SubtitleSeries
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
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=22,
        hanzi_end=26,
        english_start=22,
        english_end=26,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=27,
        hanzi_end=29,
        english_start=27,
        english_end=29,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=32,
        hanzi_end=36,
        english_start=32,
        english_end=36,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=36,
        hanzi_end=39,
        english_start=35,
        english_end=39,
        sync_groups=[
            [[1], [2]],
            [[2], [3]],
            [[3], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=58,
        hanzi_end=65,
        english_start=56,
        english_end=62,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5, 6, 7], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=65,
        hanzi_end=71,
        english_start=62,
        english_end=66,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
            [[5, 6], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=71,
        hanzi_end=76,
        english_start=66,
        english_end=70,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4, 5], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=76,
        hanzi_end=82,
        english_start=70,
        english_end=74,
        sync_groups=[
            [[1, 2], [1]],
            [[3, 4], [2]],
            [[5], [3]],
            [[6], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=82,
        hanzi_end=87,
        english_start=74,
        english_end=76,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], []],
            [[4], []],
            [[5], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=87,
        hanzi_end=90,
        english_start=76,
        english_end=78,
        sync_groups=[
            [[1], []],
            [[2], [1]],
            [[3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=95,
        hanzi_end=97,
        english_start=83,
        english_end=84,
        sync_groups=[
            [[1, 2], [1]],
        ],
    ),
    SyncTestCase(
        hanzi_start=97,
        hanzi_end=101,
        english_start=84,
        english_end=87,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=136,
        hanzi_end=146,
        english_start=109,
        english_end=117,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5, 6], [5]],
            [[7, 8], [6]],
            [[9], [7]],
            [[10], [8]],
        ],
    ),
    SyncTestCase(
        hanzi_start=148,
        hanzi_end=152,
        english_start=119,
        english_end=122,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=159,
        hanzi_end=164,
        english_start=129,
        english_end=133,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=168,
        hanzi_end=172,
        english_start=137,
        english_end=140,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=172,
        hanzi_end=175,
        english_start=140,
        english_end=142,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=177,
        hanzi_end=185,
        english_start=144,
        english_end=150,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], [5]],
            [[6, 7], [6]],
            [[8], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=225,
        hanzi_end=234,
        english_start=182,
        english_end=190,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], [5]],
            [[7], [6]],
            [[8], [7]],
            [[9], [8]],
        ],
    ),
    SyncTestCase(
        hanzi_start=234,
        hanzi_end=236,
        english_start=190,
        english_end=191,
        sync_groups=[
            [[1, 2], [1]],
        ],
    ),
    SyncTestCase(
        hanzi_start=258,
        hanzi_end=262,
        english_start=213,
        english_end=217,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=262,
        hanzi_end=264,
        english_start=217,
        english_end=219,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=268,
        hanzi_end=270,
        english_start=223,
        english_end=224,
        sync_groups=[
            [[1, 2], [1]],
        ],
    ),
    SyncTestCase(
        hanzi_start=271,
        hanzi_end=273,
        english_start=225,
        english_end=226,
        sync_groups=[
            [[1], [1]],
            [[2], []],
        ],
    ),
]
___all__ = [
    "mnt_input_english",
    "mnt_input_hanzi",
    "test_cases",
]
