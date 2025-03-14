#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import SyncTestCase, test_data_root

input_dir = test_data_root / "mnt" / "input"
output_dir = test_data_root / "mnt" / "output"


# region Traditional Standard Chinese
@pytest.fixture
def mnt_cmn_hant() -> Series:
    return Series.load(input_dir / "cmn-Hant.srt")


@pytest.fixture
def mnt_cmn_hant_clean() -> Series:
    return Series.load(output_dir / "cmn-Hant_clean.srt")


@pytest.fixture
def mnt_cmn_hant_flatten() -> Series:
    return Series.load(output_dir / "cmn-Hant_flatten.srt")


@pytest.fixture
def mnt_cmn_hant_simplify() -> Series:
    return Series.load(output_dir / "cmn-Hant_simplify.srt")


@pytest.fixture
def mnt_cmn_hant_clean_flatten_simplify() -> Series:
    return Series.load(output_dir / "cmn-Hant_clean_flatten_simplify.srt")


# endregion


# region English
@pytest.fixture
def mnt_eng() -> Series:
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def mnt_eng_clean() -> Series:
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def mnt_eng_flatten() -> Series:
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def mnt_eng_clean_flatten() -> Series:
    return Series.load(output_dir / "eng_clean_flatten.srt")


# endregion


# region Bilingual Simplified Standard Chinese and English
@pytest.fixture
def mnt_cmn_hans_eng() -> Series:
    return Series.load(output_dir / "cmn-Hans_eng.srt")


# endregion


# region Synchronization Test Cases
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
        hanzi_start=44,
        hanzi_end=56,
        english_start=44,
        english_end=54,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], [5]],
            [[6, 7], [6]],
            [[8], []],
            [[9], [7]],
            [[10], [8]],
            [[11], [9]],
            [[12], [10]],
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
            [[4], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=103,
        hanzi_end=120,
        english_start=89,
        english_end=99,
        sync_groups=[
            [[1], [1]],
            [[2, 3, 4], [2]],
            [[5, 6], [3]],
            [[7], [4]],
            [[8, 9, 10], [5]],
            [[11], [6]],
            [[12, 13], [7]],
            [[14, 15], [8]],
            [[16], [9]],
            [[17], [10]],
        ],
    ),
    SyncTestCase(
        hanzi_start=120,
        hanzi_end=136,
        english_start=99,
        english_end=109,
        sync_groups=[
            [[1], [1]],
            [[2], []],
            [[3], [2]],
            [[4, 5, 6], [3]],
            [[7, 8], [4]],
            [[9], [5]],
            [[10, 11], [6]],
            [[12], [7]],
            [[13], [8]],
            [[14, 15], [9]],
            [[16], [10]],
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
        hanzi_start=186,
        hanzi_end=199,
        english_start=151,
        english_end=162,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], [5]],
            [[6, 7], [6]],
            [[8], [7]],
            [[9], [8]],
            [[10], [9]],
            [[11], [10]],
            [[12, 13], [11]],
        ],
    ),
    SyncTestCase(
        hanzi_start=199,
        hanzi_end=225,
        english_start=162,
        english_end=182,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
            [[5], [4]],
            [[6, 7], [5]],
            [[8], [6]],
            [[9], [7]],
            [[10], [8]],
            [[11], [9]],
            [[12, 13], [10]],
            [[14], [11]],
            [[15], [12]],
            [[16], [13]],
            [[17], [14]],
            [[18], [15]],
            [[19], [16]],
            [[20], [17]],
            [[21, 22], [18]],
            [[23, 24], [19]],
            [[25, 26], [20]],
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
        hanzi_start=237,
        hanzi_end=248,
        english_start=192,
        english_end=202,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], [5]],
            [[6], [6]],
            [[7], [7]],
            [[8], [8]],
            [[9], [9]],
            [[10], []],
            [[11], [10]],
        ],
    ),
    SyncTestCase(
        hanzi_start=248,
        hanzi_end=258,
        english_start=202,
        english_end=213,
        sync_groups=[
            [[1], [1]],
            [[2], [2, 3]],
            [[3], [4]],
            [[4], [5]],
            [[5], [6]],
            [[6], [7]],
            [[7], [8]],
            [[8], [9]],
            [[9], [10]],
            [[10], [11]],
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
    SyncTestCase(
        hanzi_start=273,
        hanzi_end=284,
        english_start=226,
        english_end=233,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4, 5], [4]],
            [[6], [5]],
            [[7, 8], [6]],
            [[9], []],
            [[10], [7]],
            [[11], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=284,
        hanzi_end=285,
        english_start=233,
        english_end=233,
        sync_groups=[
            [[0], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=286,
        hanzi_end=287,
        english_start=234,
        english_end=234,
        sync_groups=[
            [[0], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=302,
        hanzi_end=309,
        english_start=244,
        english_end=249,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4, 5], [3]],
            [[6], [4]],
            [[7], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=287,
        hanzi_end=302,
        english_start=234,
        english_end=244,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], [5]],
            [[6], [6]],
            [[7], [7]],
            [[8, 9], [8]],
            [[10, 11, 12], [9]],
            [[13, 14, 15], [10]],
        ],
    ),
    SyncTestCase(
        hanzi_start=309,
        hanzi_end=315,
        english_start=249,
        english_end=256,
        sync_groups=[
            [[1], [1]],
            [[2], [3]],
            [[3], [5]],
            [[4], [6]],
            [[5], [7]],
            [[6], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=315,
        hanzi_end=318,
        english_start=256,
        english_end=258,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=318,
        hanzi_end=328,
        english_start=258,
        english_end=266,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
            [[5, 6], [4]],
            [[7], [5]],
            [[8], [6]],
            [[9], [7]],
            [[10], [8]],
        ],
    ),
    SyncTestCase(
        hanzi_start=334,
        hanzi_end=365,
        english_start=272,
        english_end=294,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4, 5], [4]],
            [[6, 7], [5]],
            [[8], [6]],
            [[9], [7]],
            [[10, 11], [8]],
            [[12, 13], [9]],
            [[14, 15, 16], [10]],
            [[17, 18], [11]],
            [[19], [12]],
            [[20], [13]],
            [[21], [14]],
            [[22, 23], [15]],
            [[24], [16]],
            [[25], [17]],
            [[26], []],
            [[27], [18]],
            [[28], [19]],
            [[29], [20]],
            [[30], [21]],
            [[31], [22]],
        ],
    ),
    SyncTestCase(
        hanzi_start=366,
        hanzi_end=368,
        english_start=295,
        english_end=296,
        sync_groups=[
            [[1, 2], [1]],
        ],
    ),
    SyncTestCase(
        hanzi_start=372,
        hanzi_end=383,
        english_start=300,
        english_end=306,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4, 5, 6], [3]],
            [[7, 8], [4]],
            [[9, 10], [5]],
            [[11], [6]],
        ],
    ),
    SyncTestCase(
        hanzi_start=384,
        hanzi_end=388,
        english_start=307,
        english_end=308,
        sync_groups=[
            [[1, 2, 3], [1]],
            [[4], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=391,
        hanzi_end=398,
        english_start=312,
        english_end=318,
        sync_groups=[
            [[1], []],
            [[2], [1]],
            [[3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], []],
            [[7], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=399,
        hanzi_end=399,
        english_start=319,
        english_end=320,
        sync_groups=[],
    ),
    SyncTestCase(
        hanzi_start=407,
        hanzi_end=413,
        english_start=328,
        english_end=333,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=413,
        hanzi_end=431,
        english_start=333,
        english_end=346,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], [5]],
            [[7, 8], [6]],
            [[9], [7]],
            [[10, 11], [8]],
            [[12, 13, 14], [9]],
            [[15], [10]],
            [[16], [12]],
            [[17, 18], [13]],
        ],
    ),
    SyncTestCase(
        hanzi_start=431,
        hanzi_end=433,
        english_start=346,
        english_end=347,
        sync_groups=[
            [[1], [1]],
            [[2], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=436,
        hanzi_end=439,
        english_start=350,
        english_end=352,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=440,
        hanzi_end=445,
        english_start=353,
        english_end=356,
        sync_groups=[
            [[1], []],
            [[2], [1]],
            [[3, 4], [2]],
            [[5], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=454,
        hanzi_end=467,
        english_start=365,
        english_end=376,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
            [[5], [4]],
            [[6], [5]],
            [[7], [6]],
            [[8], [8]],
            [[9, 10], [9]],
            [[11], [10]],
            [[12, 13], [11]],
        ],
    ),
    SyncTestCase(
        hanzi_start=467,
        hanzi_end=467,
        english_start=376,
        english_end=377,
        sync_groups=[],
    ),
    SyncTestCase(
        hanzi_start=467,
        hanzi_end=475,
        english_start=377,
        english_end=382,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4], [3]],
            [[5, 6], [4]],
            [[7, 8], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=475,
        hanzi_end=482,
        english_start=382,
        english_end=385,
        sync_groups=[
            [[1, 2, 3], [1]],
            [[4, 5, 6], [2]],
            [[7], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=482,
        hanzi_end=485,
        english_start=385,
        english_end=387,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=485,
        hanzi_end=485,
        english_start=387,
        english_end=388,
        sync_groups=[],
    ),
    SyncTestCase(
        hanzi_start=485,
        hanzi_end=491,
        english_start=388,
        english_end=392,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4, 5, 6], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=497,
        hanzi_end=503,
        english_start=398,
        english_end=401,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], []],
            [[5, 6], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=503,
        hanzi_end=507,
        english_start=401,
        english_end=403,
        sync_groups=[
            [[1, 2], [1]],
            [[3], []],
            [[4], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=516,
        hanzi_end=534,
        english_start=412,
        english_end=424,
        sync_groups=[
            [[1], [1]],
            [[2, 3, 4], [2]],
            [[5], [3]],
            [[6, 7, 8], [4]],
            [[9], [5]],
            [[10], [6]],
            [[11], [7]],
            [[12, 13, 14], [8]],
            [[15, 16], [9]],
            [[17], [10]],
            [[18], [11]],
        ],
    ),
    SyncTestCase(
        hanzi_start=534,
        hanzi_end=537,
        english_start=424,
        english_end=426,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=539,
        hanzi_end=549,
        english_start=428,
        english_end=434,
        sync_groups=[
            [[1], [1]],
            [[2, 3, 4], [2]],
            [[5], [3]],
            [[6, 7], [4]],
            [[8, 9], [5]],
            [[10], [6]],
        ],
    ),
    SyncTestCase(
        hanzi_start=551,
        hanzi_end=559,
        english_start=436,
        english_end=442,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6, 7], [5]],
            [[8], [6]],
        ],
    ),
    SyncTestCase(  # Review
        hanzi_start=559,
        hanzi_end=572,
        english_start=442,
        english_end=450,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4], [3]],
            [[5, 6], [4]],
            [[7, 8, 9], [5]],
            [[10], [6]],
            [[11, 12], [7]],
            [[13], [8]],
        ],
    ),
    SyncTestCase(
        hanzi_start=573,
        hanzi_end=577,
        english_start=451,
        english_end=453,
        sync_groups=[
            [[1, 2], [1]],
            [[3, 4], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=577,
        hanzi_end=590,
        english_start=453,
        english_end=460,
        sync_groups=[
            [[1, 2, 3], [1]],
            [[4], [2]],
            [[5, 6], [3]],
            [[7], [4]],
            [[8], [5]],
            [[9], []],
            [[10], [6]],
            [[11], []],
            [[12, 13], [7]],
        ],
    ),
    SyncTestCase(
        hanzi_start=592,
        hanzi_end=596,
        english_start=462,
        english_end=464,
        sync_groups=[
            [[1], [1]],
            [[2, 3, 4], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=596,
        hanzi_end=599,
        english_start=464,
        english_end=466,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=599,
        hanzi_end=605,
        english_start=466,
        english_end=471,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], [5]],
        ],
    ),
    SyncTestCase(
        hanzi_start=605,
        hanzi_end=610,
        english_start=471,
        english_end=474,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4, 5], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=611,
        hanzi_end=625,
        english_start=475,
        english_end=485,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5, 6], [5]],
            [[7, 8], [6]],
            [[9], [7]],
            [[10, 11], [8]],
            [[12], [9]],
            [[13, 14], [10]],
        ],
    ),
    SyncTestCase(
        hanzi_start=627,
        hanzi_end=633,
        english_start=487,
        english_end=491,
        sync_groups=[
            [[1], [1]],
            [[2, 3], [2]],
            [[4, 5], [3]],
            [[6], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=636,
        hanzi_end=652,
        english_start=494,
        english_end=506,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3, 4], [3]],
            [[5], [4]],
            [[6, 7], [5]],
            [[8], [6]],
            [[9, 10], [7]],
            [[11], [8]],
            [[12], [9]],
            [[13], [10]],
            [[14], []],
            [[15], [11]],
            [[16], [12]],
        ],
    ),
    SyncTestCase(
        hanzi_start=652,
        hanzi_end=663,
        english_start=506,
        english_end=514,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5, 6], [5]],
            [[7], [6]],
            [[8, 9, 10], [7]],
            [[11], [8]],
        ],
    ),
    SyncTestCase(
        hanzi_start=672,
        hanzi_end=681,
        english_start=523,
        english_end=531,
        sync_groups=[
            [[1, 2], [1]],
            [[3], [2]],
            [[4], [3]],
            [[5], [4]],
            [[6], [5]],
            [[7], [6]],
            [[8, 9], [7]],
        ],
    ),
    SyncTestCase(
        hanzi_start=681,
        hanzi_end=686,
        english_start=531,
        english_end=533,
        sync_groups=[
            [[1, 2], [1]],
            [[3, 4, 5], [2]],
        ],
    ),
    SyncTestCase(
        hanzi_start=686,
        hanzi_end=693,
        english_start=533,
        english_end=537,
        sync_groups=[
            [[1], [1]],
            [[2, 3, 4], [2]],
            [[5, 6], [3]],
            [[7], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=694,
        hanzi_end=695,
        english_start=538,
        english_end=541,
        sync_groups=[
            [[1], [3]],
        ],
    ),
    SyncTestCase(
        hanzi_start=697,
        hanzi_end=698,
        english_start=543,
        english_end=543,
        sync_groups=[
            [[0], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=698,
        hanzi_end=701,
        english_start=543,
        english_end=544,
        sync_groups=[
            [[1], [1]],
            [[2], []],
            [[3], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=701,
        hanzi_end=706,
        english_start=544,
        english_end=548,
        sync_groups=[
            [[1], [1]],
            [[2], []],
            [[3], [2]],
            [[4], [3]],
            [[5], [4]],
        ],
    ),
    SyncTestCase(
        hanzi_start=709,
        hanzi_end=722,
        english_start=551,
        english_end=560,
        sync_groups=[
            [[1, 2], [1]],
            [[3, 4], [2]],
            [[5], [3]],
            [[6, 7, 8], [4]],
            [[9], [5]],
            [[10], [6]],
            [[11], [7]],
            [[12], [8]],
            [[13], [9]],
        ],
    ),
    SyncTestCase(
        hanzi_start=724,
        hanzi_end=726,
        english_start=562,
        english_end=564,
        sync_groups=[
            [[1], [1]],
            [[2], []],
        ],
    ),
    SyncTestCase(
        hanzi_start=726,
        hanzi_end=732,
        english_start=564,
        english_end=569,
        sync_groups=[
            [[1], [1]],
            [[2], [2]],
            [[3], [3]],
            [[4], [4]],
            [[5], []],
            [[6], [5]],
        ],
    ),
]
# endregion

___all__ = [
    "mnt_cmn_hant",
    "mnt_cmn_hant_clean",
    "mnt_cmn_hant_flatten",
    "mnt_cmn_hant_simplify",
    "mnt_cmn_hant_clean_flatten_simplify",
    "mnt_eng",
    "mnt_eng_clean",
    "mnt_eng_flatten",
    "mnt_cmn_hans_eng",
    "mnt_test_cases",
]
