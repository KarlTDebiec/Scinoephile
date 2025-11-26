#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import Series
from scinoephile.testing import SyncTestCase, test_data_root

# ruff: noqa: F401 F403
from test.data.mnt.core.english.proofreading import (
    test_cases as mnt_english_proofreading_test_cases,
)
from test.data.mnt.core.zhongwen.proofreading import (
    test_cases as mnt_zhongwen_proofreading_test_cases,
)
from test.data.mnt.image.english.fusion import (
    test_cases as mnt_english_fusion_test_cases,
)
from test.data.mnt.image.zhongwen.fusion import (
    test_cases as mnt_zhongwen_fusion_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"


# 简体中文 (OCR)
@pytest.fixture
def mnt_zho_hans_lens() -> Series:
    """MNT 简体中文 subtitles OCRed using Google Lens OCR."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mnt_zho_hans_paddle() -> Series:
    """MNT 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def mnt_zho_hans_fuse() -> Series:
    """MNT 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread() -> Series:
    """MNT 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread_clean() -> Series:
    """MNT 简体中文 fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread_clean_flatten() -> Series:
    """MNT 简体中文 fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")


# 繁体中文
@pytest.fixture
def mnt_zho_hant() -> Series:
    """MNT 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def mnt_zho_hant_clean() -> Series:
    """MNT 繁体中文 cleaned series."""
    return Series.load(output_dir / "zho-Hant_clean.srt")


@pytest.fixture
def mnt_zho_hant_flatten() -> Series:
    """MNT 繁体中文 flattened series."""
    return Series.load(output_dir / "zho-Hant_flatten.srt")


@pytest.fixture
def mnt_zho_hant_simplify() -> Series:
    """MNT 繁体中文 simplified series."""
    return Series.load(output_dir / "zho-Hant_simplify.srt")


@pytest.fixture
def mnt_zho_hant_clean_flatten_simplify() -> Series:
    """MNT 繁体中文 cleaned, flattened, and simplified series."""
    return Series.load(output_dir / "zho-Hant_clean_flatten_simplify.srt")


# English (OCR)
@pytest.fixture
def mnt_eng_lens() -> Series:
    """MNT English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def mnt_eng_tesseract() -> Series:
    """MNT English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def mnt_eng_fuse() -> Series:
    """MNT English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


# Bilingual 简体中文 and English
@pytest.fixture
def mnt_zho_hans_eng() -> Series:
    """MNT Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


# region 简体中文 and English synchronization test cases
mnt_sync_test_cases = [
    SyncTestCase(
        one_start=0,
        one_end=4,
        two_start=0,
        two_end=4,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([], [2]),
            ([3], [3]),
        ],
    ),
    SyncTestCase(
        one_start=22,
        one_end=26,
        two_start=22,
        two_end=26,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
        ],
    ),
    SyncTestCase(
        one_start=27,
        one_end=29,
        two_start=27,
        two_end=29,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
        ],
    ),
    SyncTestCase(
        one_start=32,
        one_end=36,
        two_start=32,
        two_end=36,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([], [3]),
        ],
    ),
    SyncTestCase(
        one_start=36,
        one_end=39,
        two_start=35,
        two_end=39,
        sync_groups=[
            ([], [0]),
            ([0], [1]),
            ([1], [2]),
            ([2], [3]),
        ],
    ),
    SyncTestCase(
        one_start=44,
        one_end=56,
        two_start=44,
        two_end=54,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], [4]),
            ([5, 6], [5]),
            ([7], []),
            ([8], [6]),
            ([9], [7]),
            ([10], [8]),
            ([11], [9]),
        ],
    ),
    SyncTestCase(
        one_start=58,
        one_end=65,
        two_start=56,
        two_end=62,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4, 5, 6], [4]),
            ([], [5]),
        ],
    ),
    SyncTestCase(
        one_start=65,
        one_end=71,
        two_start=62,
        two_end=66,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([4, 5], [3]),
        ],
    ),
    SyncTestCase(
        one_start=71,
        one_end=76,
        two_start=66,
        two_end=70,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3, 4], [3]),
        ],
    ),
    SyncTestCase(
        one_start=76,
        one_end=82,
        two_start=70,
        two_end=74,
        sync_groups=[
            ([0, 1], [0]),
            ([2, 3], [1]),
            ([4], [2]),
            ([5], [3]),
        ],
    ),
    SyncTestCase(
        one_start=82,
        one_end=87,
        two_start=74,
        two_end=76,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], []),
            ([3], []),
            ([4], []),
        ],
    ),
    SyncTestCase(
        one_start=87,
        one_end=90,
        two_start=76,
        two_end=78,
        sync_groups=[
            ([0], []),
            ([1], [0]),
            ([2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=95,
        one_end=97,
        two_start=83,
        two_end=84,
        sync_groups=[
            ([0, 1], [0]),
        ],
    ),
    SyncTestCase(
        one_start=97,
        one_end=101,
        two_start=84,
        two_end=87,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
        ],
    ),
    SyncTestCase(
        one_start=103,
        one_end=120,
        two_start=89,
        two_end=99,
        sync_groups=[
            ([0], [0]),
            ([1, 2, 3], [1]),
            ([4, 5], [2]),
            ([6], [3]),
            ([7, 8, 9], [4]),
            ([10], [5]),
            ([11, 12], [6]),
            ([13, 14], [7]),
            ([15], [8]),
            ([16], [9]),
        ],
    ),
    SyncTestCase(
        one_start=120,
        one_end=136,
        two_start=99,
        two_end=109,
        sync_groups=[
            ([0], [0]),
            ([1], []),
            ([2], [1]),
            ([3, 4, 5], [2]),
            ([6, 7], [3]),
            ([8], [4]),
            ([9, 10], [5]),
            ([11], [6]),
            ([12], [7]),
            ([13, 14], [8]),
            ([15], [9]),
        ],
    ),
    SyncTestCase(
        one_start=136,
        one_end=146,
        two_start=109,
        two_end=117,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4, 5], [4]),
            ([6, 7], [5]),
            ([8], [6]),
            ([9], [7]),
        ],
    ),
    SyncTestCase(
        one_start=148,
        one_end=152,
        two_start=119,
        two_end=122,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
        ],
    ),
    SyncTestCase(
        one_start=159,
        one_end=164,
        two_start=129,
        two_end=133,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4], [3]),
        ],
    ),
    SyncTestCase(
        one_start=168,
        one_end=172,
        two_start=137,
        two_end=140,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3], [2]),
        ],
    ),
    SyncTestCase(
        one_start=172,
        one_end=175,
        two_start=140,
        two_end=142,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=177,
        one_end=185,
        two_start=144,
        two_end=150,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], [4]),
            ([5, 6], [5]),
            ([7], []),
        ],
    ),
    SyncTestCase(
        one_start=186,
        one_end=199,
        two_start=151,
        two_end=162,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], [4]),
            ([5, 6], [5]),
            ([7], [6]),
            ([8], [7]),
            ([9], [8]),
            ([10], [9]),
            ([11, 12], [10]),
        ],
    ),
    SyncTestCase(
        one_start=199,
        one_end=225,
        two_start=162,
        two_end=182,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([4], [3]),
            ([5, 6], [4]),
            ([7], [5]),
            ([8], [6]),
            ([9], [7]),
            ([10], [8]),
            ([11, 12], [9]),
            ([13], [10]),
            ([14], [11]),
            ([15], [12]),
            ([16], [13]),
            ([17], [14]),
            ([18], [15]),
            ([19], [16]),
            ([20, 21], [17]),
            ([22, 23], [18]),
            ([24, 25], [19]),
        ],
    ),
    SyncTestCase(
        one_start=225,
        one_end=234,
        two_start=182,
        two_end=190,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], [4]),
            ([6], [5]),
            ([7], [6]),
            ([8], [7]),
        ],
    ),
    SyncTestCase(
        one_start=234,
        one_end=236,
        two_start=190,
        two_end=191,
        sync_groups=[
            ([0, 1], [0]),
        ],
    ),
    SyncTestCase(
        one_start=237,
        one_end=248,
        two_start=192,
        two_end=202,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], [4]),
            ([5], [5]),
            ([6], [6]),
            ([7], [7]),
            ([8], [8]),
            ([9], []),
            ([10], [9]),
        ],
    ),
    SyncTestCase(
        one_start=248,
        one_end=258,
        two_start=202,
        two_end=213,
        sync_groups=[
            ([0], [0]),
            ([1], [1, 2]),
            ([2], [3]),
            ([3], [4]),
            ([4], [5]),
            ([5], [6]),
            ([6], [7]),
            ([7], [8]),
            ([8], [9]),
            ([9], [10]),
        ],
    ),
    SyncTestCase(
        one_start=258,
        one_end=262,
        two_start=213,
        two_end=217,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
        ],
    ),
    SyncTestCase(
        one_start=262,
        one_end=264,
        two_start=217,
        two_end=219,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
        ],
    ),
    SyncTestCase(
        one_start=268,
        one_end=270,
        two_start=223,
        two_end=224,
        sync_groups=[
            ([0, 1], [0]),
        ],
    ),
    SyncTestCase(
        one_start=271,
        one_end=273,
        two_start=225,
        two_end=226,
        sync_groups=[
            ([0], [0]),
            ([1], []),
        ],
    ),
    SyncTestCase(
        one_start=273,
        one_end=284,
        two_start=226,
        two_end=233,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3, 4], [3]),
            ([5], [4]),
            ([6, 7], [5]),
            ([8], []),
            ([9], [6]),
            ([10], []),
        ],
    ),
    SyncTestCase(
        one_start=284,
        one_end=285,
        two_start=233,
        two_end=233,
        sync_groups=[
            ([0], []),
        ],
    ),
    SyncTestCase(
        one_start=286,
        one_end=287,
        two_start=234,
        two_end=234,
        sync_groups=[
            ([0], []),
        ],
    ),
    SyncTestCase(
        one_start=302,
        one_end=309,
        two_start=244,
        two_end=249,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3, 4], [2]),
            ([5], [3]),
            ([6], [4]),
        ],
    ),
    SyncTestCase(
        one_start=287,
        one_end=302,
        two_start=234,
        two_end=244,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], [4]),
            ([5], [5]),
            ([6], [6]),
            ([7, 8], [7]),
            ([9, 10, 11], [8]),
            ([12, 13, 14], [9]),
        ],
    ),
    SyncTestCase(
        one_start=309,
        one_end=315,
        two_start=249,
        two_end=256,
        sync_groups=[
            ([0], [0]),
            ([], [1]),
            ([1], [2]),
            ([], [3]),
            ([2], [4]),
            ([3], [5]),
            ([4], [6]),
            ([5], []),
        ],
    ),
    SyncTestCase(
        one_start=315,
        one_end=318,
        two_start=256,
        two_end=258,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=318,
        one_end=328,
        two_start=258,
        two_end=266,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([4, 5], [3]),
            ([6], [4]),
            ([7], [5]),
            ([8], [6]),
            ([9], [7]),
        ],
    ),
    SyncTestCase(
        one_start=334,
        one_end=365,
        two_start=272,
        two_end=294,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3, 4], [3]),
            ([5, 6], [4]),
            ([7], [5]),
            ([8], [6]),
            ([9, 10], [7]),
            ([11, 12], [8]),
            ([13, 14, 15], [9]),
            ([16, 17], [10]),
            ([18], [11]),
            ([19], [12]),
            ([20], [13]),
            ([21, 22], [14]),
            ([23], [15]),
            ([24], [16]),
            ([25], []),
            ([26], [17]),
            ([27], [18]),
            ([28], [19]),
            ([29], [20]),
            ([30], [21]),
        ],
    ),
    SyncTestCase(
        one_start=366,
        one_end=368,
        two_start=295,
        two_end=296,
        sync_groups=[
            ([0, 1], [0]),
        ],
    ),
    SyncTestCase(
        one_start=372,
        one_end=383,
        two_start=300,
        two_end=306,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3, 4, 5], [2]),
            ([6, 7], [3]),
            ([8, 9], [4]),
            ([10], [5]),
        ],
    ),
    SyncTestCase(
        one_start=384,
        one_end=388,
        two_start=307,
        two_end=308,
        sync_groups=[
            ([0, 1, 2], [0]),
            ([3], []),
        ],
    ),
    SyncTestCase(
        one_start=391,
        one_end=398,
        two_start=312,
        two_end=318,
        sync_groups=[
            ([0], []),
            ([1], [0]),
            ([2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], []),
            ([6], [4]),
            ([], [5]),
        ],
    ),
    SyncTestCase(
        one_start=399,
        one_end=399,
        two_start=319,
        two_end=320,
        sync_groups=[],
    ),
    SyncTestCase(
        one_start=407,
        one_end=413,
        two_start=328,
        two_end=333,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], [4]),
        ],
    ),
    SyncTestCase(
        one_start=413,
        one_end=431,
        two_start=333,
        two_end=346,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], [4]),
            ([6, 7], [5]),
            ([8], [6]),
            ([9, 10], [7]),
            ([11, 12, 13], [8]),
            ([14], [9]),
            ([], [10]),
            ([15], [11]),
            ([16, 17], [12]),
        ],
    ),
    SyncTestCase(
        one_start=431,
        one_end=433,
        two_start=346,
        two_end=347,
        sync_groups=[
            ([0], [0]),
            ([1], []),
        ],
    ),
    SyncTestCase(
        one_start=436,
        one_end=439,
        two_start=350,
        two_end=352,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=440,
        one_end=445,
        two_start=353,
        two_end=356,
        sync_groups=[
            ([0], []),
            ([1], [0]),
            ([2, 3], [1]),
            ([4], [2]),
        ],
    ),
    SyncTestCase(
        one_start=454,
        one_end=467,
        two_start=365,
        two_end=376,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([4], [3]),
            ([5], [4]),
            ([6], [5]),
            ([], [6]),
            ([7], [7]),
            ([8, 9], [8]),
            ([10], [9]),
            ([11, 12], [10]),
        ],
    ),
    SyncTestCase(
        one_start=467,
        one_end=467,
        two_start=376,
        two_end=377,
        sync_groups=[],
    ),
    SyncTestCase(
        one_start=467,
        one_end=475,
        two_start=377,
        two_end=382,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3], [2]),
            ([4, 5], [3]),
            ([6, 7], [4]),
        ],
    ),
    SyncTestCase(
        one_start=475,
        one_end=482,
        two_start=382,
        two_end=385,
        sync_groups=[
            ([0, 1, 2], [0]),
            ([3, 4, 5], [1]),
            ([6], [2]),
        ],
    ),
    SyncTestCase(
        one_start=482,
        one_end=485,
        two_start=385,
        two_end=387,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=485,
        one_end=485,
        two_start=387,
        two_end=388,
        sync_groups=[],
    ),
    SyncTestCase(
        one_start=485,
        one_end=491,
        two_start=388,
        two_end=392,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3, 4, 5], [3]),
        ],
    ),
    SyncTestCase(
        one_start=497,
        one_end=503,
        two_start=398,
        two_end=401,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], []),
            ([4, 5], [2]),
        ],
    ),
    SyncTestCase(
        one_start=503,
        one_end=507,
        two_start=401,
        two_end=403,
        sync_groups=[
            ([0, 1], [0]),
            ([2], []),
            ([3], [1]),
        ],
    ),
    SyncTestCase(
        one_start=516,
        one_end=534,
        two_start=412,
        two_end=424,
        sync_groups=[
            ([0], [0]),
            ([1, 2, 3], [1]),
            ([4], [2]),
            ([5, 6, 7], [3]),
            ([8], [4]),
            ([9], [5]),
            ([10], [6]),
            ([11, 12, 13], [7]),
            ([14, 15], [8]),
            ([16], [9]),
            ([17], [10]),
            ([], [11]),
        ],
    ),
    SyncTestCase(
        one_start=534,
        one_end=537,
        two_start=424,
        two_end=426,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=539,
        one_end=549,
        two_start=428,
        two_end=434,
        sync_groups=[
            ([0], [0]),
            ([1, 2, 3], [1]),
            ([4], [2]),
            ([5, 6], [3]),
            ([7, 8], [4]),
            ([9], [5]),
        ],
    ),
    SyncTestCase(
        one_start=551,
        one_end=559,
        two_start=436,
        two_end=442,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5, 6], [4]),
            ([7], [5]),
        ],
    ),
    SyncTestCase(
        one_start=559,
        one_end=572,
        two_start=442,
        two_end=450,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3], [2]),
            ([4, 5], [3]),
            ([6, 7, 8], [4]),
            ([9], [5]),
            ([10, 11], [6]),
            ([12], [7]),
        ],
    ),
    SyncTestCase(
        one_start=573,
        one_end=577,
        two_start=451,
        two_end=453,
        sync_groups=[
            ([0, 1], [0]),
            ([2, 3], [1]),
        ],
    ),
    SyncTestCase(
        one_start=577,
        one_end=590,
        two_start=453,
        two_end=460,
        sync_groups=[
            ([0, 1, 2], [0]),
            ([3], [1]),
            ([4, 5], [2]),
            ([6], [3]),
            ([7], [4]),
            ([8], []),
            ([9], [5]),
            ([10], []),
            ([11, 12], [6]),
        ],
    ),
    SyncTestCase(
        one_start=592,
        one_end=596,
        two_start=462,
        two_end=464,
        sync_groups=[
            ([0], [0]),
            ([1, 2, 3], [1]),
        ],
    ),
    SyncTestCase(
        one_start=596,
        one_end=599,
        two_start=464,
        two_end=466,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
        ],
    ),
    SyncTestCase(
        one_start=599,
        one_end=605,
        two_start=466,
        two_end=471,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], [4]),
        ],
    ),
    SyncTestCase(
        one_start=605,
        one_end=610,
        two_start=471,
        two_end=474,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3, 4], [2]),
        ],
    ),
    SyncTestCase(
        one_start=611,
        one_end=625,
        two_start=475,
        two_end=485,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4, 5], [4]),
            ([6, 7], [5]),
            ([8], [6]),
            ([9, 10], [7]),
            ([11], [8]),
            ([12, 13], [9]),
        ],
    ),
    SyncTestCase(
        one_start=627,
        one_end=633,
        two_start=487,
        two_end=491,
        sync_groups=[
            ([0], [0]),
            ([1, 2], [1]),
            ([3, 4], [2]),
            ([5], [3]),
        ],
    ),
    SyncTestCase(
        one_start=636,
        one_end=652,
        two_start=494,
        two_end=506,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2, 3], [2]),
            ([4], [3]),
            ([5, 6], [4]),
            ([7], [5]),
            ([8, 9], [6]),
            ([10], [7]),
            ([11], [8]),
            ([12], [9]),
            ([13], []),
            ([14], [10]),
            ([15], [11]),
        ],
    ),
    SyncTestCase(
        one_start=652,
        one_end=663,
        two_start=506,
        two_end=514,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4, 5], [4]),
            ([6], [5]),
            ([7, 8, 9], [6]),
            ([10], [7]),
        ],
    ),
    SyncTestCase(
        one_start=672,
        one_end=681,
        two_start=523,
        two_end=531,
        sync_groups=[
            ([0, 1], [0]),
            ([2], [1]),
            ([3], [2]),
            ([4], [3]),
            ([5], [4]),
            ([6], [5]),
            ([7, 8], [6]),
            ([], [7]),
        ],
    ),
    SyncTestCase(
        one_start=681,
        one_end=686,
        two_start=531,
        two_end=533,
        sync_groups=[
            ([0, 1], [0]),
            ([2, 3, 4], [1]),
        ],
    ),
    SyncTestCase(
        one_start=686,
        one_end=693,
        two_start=533,
        two_end=537,
        sync_groups=[
            ([0], [0]),
            ([1, 2, 3], [1]),
            ([4, 5], [2]),
            ([6], [3]),
        ],
    ),
    SyncTestCase(
        one_start=694,
        one_end=695,
        two_start=538,
        two_end=541,
        sync_groups=[
            ([], [0]),
            ([], [1]),
            ([0], [2]),
        ],
    ),
    SyncTestCase(
        one_start=697,
        one_end=698,
        two_start=543,
        two_end=543,
        sync_groups=[
            ([0], []),
        ],
    ),
    SyncTestCase(
        one_start=698,
        one_end=701,
        two_start=543,
        two_end=544,
        sync_groups=[
            ([0], [0]),
            ([1], []),
            ([2], []),
        ],
    ),
    SyncTestCase(
        one_start=701,
        one_end=706,
        two_start=544,
        two_end=548,
        sync_groups=[
            ([0], [0]),
            ([1], []),
            ([2], [1]),
            ([3], [2]),
            ([4], [3]),
        ],
    ),
    SyncTestCase(
        one_start=709,
        one_end=722,
        two_start=551,
        two_end=560,
        sync_groups=[
            ([0, 1], [0]),
            ([2, 3], [1]),
            ([4], [2]),
            ([5, 6, 7], [3]),
            ([8], [4]),
            ([9], [5]),
            ([10], [6]),
            ([11], [7]),
            ([12], [8]),
        ],
    ),
    SyncTestCase(
        one_start=724,
        one_end=726,
        two_start=562,
        two_end=564,
        sync_groups=[
            ([0], [0]),
            ([1], []),
            ([], [1]),
        ],
    ),
    SyncTestCase(
        one_start=726,
        one_end=732,
        two_start=564,
        two_end=569,
        sync_groups=[
            ([0], [0]),
            ([1], [1]),
            ([2], [2]),
            ([3], [3]),
            ([4], []),
            ([5], [4]),
        ],
    ),
]
"""MNT 简体中文 and English synchronization test cases."""
# endregion

___all__ = [
    "mnt_zho_hans_lens",
    "mnt_zho_hans_paddle",
    "mnt_zho_hans_fuse",
    "mnt_zho_hans_fuse_proofread",
    "mnt_zho_hans_fuse_proofread_clean",
    "mnt_zho_hans_fuse_proofread_clean_flatten",
    "mnt_zho_hant",
    "mnt_zho_hant_clean",
    "mnt_zho_hant_flatten",
    "mnt_zho_hant_simplify",
    "mnt_zho_hant_clean_flatten_simplify",
    "mnt_eng_lens",
    "mnt_eng_tesseract",
    "mnt_eng_fuse",
    "mnt_zho_hans_eng",
    "mnt_sync_test_cases",
    "mnt_english_fusion_test_cases",
    "mnt_english_proofreading_test_cases",
    "mnt_zhongwen_fusion_test_cases",
    "mnt_zhongwen_proofreading_test_cases",
]
