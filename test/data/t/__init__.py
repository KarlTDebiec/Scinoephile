#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


# region Simplified Standard Chinese
@pytest.fixture
def t_cmn_hans() -> Series:
    return Series.load(get_test_file_path("t/input/cmn-Hans.srt"))


@pytest.fixture
def t_cmn_hans_clean() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans_clean.srt"))


@pytest.fixture
def t_cmn_hans_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans_flatten.srt"))


@pytest.fixture
def t_cmn_hans_clean_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans_clean_flatten.srt"))


# endregion


# region Traditional Standard Chinese
@pytest.fixture
def t_cmn_hant() -> Series:
    return Series.load(get_test_file_path("t/input/cmn-Hant.srt"))


@pytest.fixture
def t_cmn_hant_simplify() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hant_simplify.srt"))


# endregion


# region English
@pytest.fixture
def t_eng() -> Series:
    return Series.load(get_test_file_path("t/input/eng.srt"))


@pytest.fixture
def t_eng_clean() -> Series:
    return Series.load(get_test_file_path("t/output/eng_clean.srt"))


@pytest.fixture
def t_eng_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/eng_flatten.srt"))


@pytest.fixture
def t_eng_clean_flatten() -> Series:
    return Series.load(get_test_file_path("t/output/eng_clean_flatten.srt"))


# endregion


# region Bilingual Simplified Chinese and English
@pytest.fixture
def t_cmn_hans_eng() -> Series:
    return Series.load(get_test_file_path("t/output/cmn-Hans_eng.srt"))


# endregion

___all__ = [
    "t_cmn_hans",
    "t_cmn_hans_clean",
    "t_cmn_hans_flatten",
    "t_cmn_hans_clean_flatten",
    "t_cmn_hant",
    "t_cmn_hant_simplify",
    "t_eng",
    "t_eng_clean",
    "t_eng_flatten",
    "t_eng_clean_flatten",
    "t_cmn_hans_eng",
]
