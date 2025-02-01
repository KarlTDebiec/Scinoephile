#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


# region Simplified Cantonese Chinese
@pytest.fixture
def kob_yue_hans() -> Series:
    return Series.load(get_test_file_path("kob/input/yue-Hans.srt"))


@pytest.fixture
def kob_yue_hans_clean() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans_clean.srt"))


@pytest.fixture
def kob_yue_hans_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans_flatten.srt"))


@pytest.fixture
def kob_yue_hans_clean_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans_clean_flatten.srt"))


# endregion


# region Traditional Cantonese Chinese
@pytest.fixture
def kob_yue_hant() -> Series:
    return Series.load(get_test_file_path("kob/input/yue-Hant.srt"))


@pytest.fixture
def kob_yue_hant_simplify() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hant_simplify.srt"))


# endregion


# region English
@pytest.fixture
def kob_eng() -> Series:
    return Series.load(get_test_file_path("kob/input/eng.srt"))


@pytest.fixture
def kob_eng_clean() -> Series:
    return Series.load(get_test_file_path("kob/output/eng_clean.srt"))


@pytest.fixture
def kob_eng_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/eng_flatten.srt"))


@pytest.fixture
def kob_eng_clean_flatten() -> Series:
    return Series.load(get_test_file_path("kob/output/eng_clean_flatten.srt"))


# endregion


# region Bilingual Simplified Cantonese Chinese and English
@pytest.fixture()
def kob_yue_hans_eng() -> Series:
    return Series.load(get_test_file_path("kob/output/yue-Hans_eng.srt"))


# endregion

___all__ = [
    "kob_yue_hans",
    "kob_yue_hans_clean",
    "kob_yue_hans_flatten",
    "kob_yue_hans_clean_flatten",
    "kob_yue_hant",
    "kob_yue_hant_simplify",
    "kob_eng",
    "kob_eng_clean",
    "kob_eng_flatten",
    "kob_eng_clean_flatten",
    "kob_yue_hans_eng",
]
