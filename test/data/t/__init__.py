#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root

input_dir = test_data_root / "t" / "input"
output_dir = test_data_root / "t" / "output"


# region Simplified Standard Chinese
@pytest.fixture
def t_zho_hans() -> Series:
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_clean() -> Series:
    return Series.load(output_dir / "zho-Hans_clean.srt")


@pytest.fixture
def t_zho_hans_flatten() -> Series:
    return Series.load(output_dir / "zho-Hans_flatten.srt")


@pytest.fixture
def t_zho_hans_clean_flatten() -> Series:
    return Series.load(output_dir / "zho-Hans_clean_flatten.srt")


# endregion


# region Traditional Standard Chinese
@pytest.fixture
def t_zho_hant() -> Series:
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_simplify() -> Series:
    return Series.load(output_dir / "zho-Hant_simplify.srt")


# endregion


# region English
@pytest.fixture
def t_eng() -> Series:
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_clean() -> Series:
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def t_eng_flatten() -> Series:
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def t_eng_clean_flatten() -> Series:
    return Series.load(output_dir / "eng_clean_flatten.srt")


# endregion


# region Bilingual Simplified Chinese and English
@pytest.fixture
def t_zho_hans_eng() -> Series:
    return Series.load(output_dir / "zho-Hans_eng.srt")


# endregion

___all__ = [
    "t_zho_hans",
    "t_zho_hans_clean",
    "t_zho_hans_flatten",
    "t_zho_hans_clean_flatten",
    "t_zho_hant",
    "t_zho_hant_simplify",
    "t_eng",
    "t_eng_clean",
    "t_eng_flatten",
    "t_eng_clean_flatten",
    "t_zho_hans_eng",
]
