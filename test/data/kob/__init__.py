#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


# region Simplified Cantonese Chinese
@pytest.fixture
def kob_yue_hans_hk() -> Series:
    return Series.load(get_test_file_path("kob/input/yue-Hans-HK.srt"))


@pytest.fixture
def kob_yue_hans_hk_clean() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans-HK_clean.srt"))


@pytest.fixture
def kob_yue_hans_hk_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans-HK_flatten.srt"))


@pytest.fixture
def kob_yue_hans_hk_clean_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans-HK_clean_flatten.srt"))


# endregion


# region Traditional Cantonese Chinese
@pytest.fixture
def kob_yue_hant_hk() -> Series:
    return Series.load(get_test_file_path("kob/input/yue-Hant-HK.srt"))


@pytest.fixture
def kob_yue_hant_hk_simplify() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hant-HK_simplify.srt"))


# endregion


# region English
@pytest.fixture
def kob_en_hk() -> Series:
    return Series.load(get_test_file_path("kob/input/en-HK.srt"))


@pytest.fixture
def kob_en_hk_clean() -> Series:
    return Series.load(get_test_file_path("kob/output/en-HK_clean.srt"))


@pytest.fixture
def kob_en_hk_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/en-HK_flatten.srt"))


@pytest.fixture
def kob_en_hk_clean_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/en-HK_clean_flatten.srt"))


# endregion


# region Bilingual Simplified Cantonese Chinese and English
@pytest.fixture()
def kob_yue_hans_hk_en_hk() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans-HK_en-HK.srt"))


# endregion

___all__ = [
    "kob_yue_hans_hk",
    "kob_yue_hans_hk_clean",
    "kob_yue_hans_hk_flatten",
    "kob_yue_hans_hk_clean_flatten",
    "kob_yue_hant_hk",
    "kob_yue_hant_hk_simplify",
    "kob_en_hk",
    "kob_en_hk_clean",
    "kob_en_hk_flatten",
    "kob_en_hk_clean_flatten",
    "kob_yue_hans_hk_en_hk",
]
