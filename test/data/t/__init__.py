#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


# region Simplified Standard Chinese
@pytest.fixture
def t_cmn_hans_hk() -> Series:
    return Series.load(get_test_file_path("t/input/cmn-Hans-HK.srt"))


@pytest.fixture
def t_cmn_hans_hk_clean() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans-HK_clean.srt"))


@pytest.fixture
def t_cmn_hans_hk_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans-HK_flatten.srt"))


@pytest.fixture
def t_cmn_hans_hk_clean_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans-HK_clean_flatten.srt"))


# endregion


# region Traditional Standard Chinese
@pytest.fixture
def t_cmn_hant_hk() -> Series:
    return Series.load(get_test_file_path("t/input/cmn-Hant-HK.srt"))


@pytest.fixture
def t_cmn_hant_hk_simplify() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hant-HK_simplify.srt"))


# endregion


# region English
@pytest.fixture
def t_en_hk() -> Series:
    return Series.load(get_test_file_path("t/input/en-HK.srt"))


@pytest.fixture
def t_en_hk_clean() -> Series:
    return Series.load(get_test_file_path("t/output/en-HK_clean.srt"))


@pytest.fixture
def t_en_hk_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/en-HK_flatten.srt"))


@pytest.fixture
def t_en_hk_clean_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/en-HK_clean_flatten.srt"))


# endregion


# region Bilingual Simplified Chinese and English
@pytest.fixture
def t_cmn_hans_hk_en_hk() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans-HK_en-HK.srt"))


# endregion

___all__ = [
    "t_cmn_hans_hk",
    "t_cmn_hans_hk_clean",
    "t_cmn_hans_hk_flatten",
    "t_cmn_hans_hk_clean_flatten",
    "t_cmn_hant_hk",
    "t_cmn_hant_hk_simplify",
    "t_en_hk",
    "t_en_hk_clean",
    "t_en_hk_flatten",
    "t_en_hk_clean_flatten",
    "t_cmn_hans_hk_en_hk",
]
