#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root
from test.data.t.distribution import t_distribute_test_cases
from test.data.t.merging import t_merge_test_cases
from test.data.t.proofing import t_proof_test_cases
from test.data.t.review import t_review_test_cases
from test.data.t.shifting import t_shift_test_cases
from test.data.t.translation import t_translate_test_cases

input_dir = test_data_root / "t" / "input"
output_dir = test_data_root / "t" / "output"


# region 简体中文
@pytest.fixture
def t_zho_hans() -> Series:
    """T 简体中文 series."""
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_clean() -> Series:
    """T 简体中文 cleaned series."""
    return Series.load(output_dir / "zho-Hans_clean.srt")


@pytest.fixture
def t_zho_hans_flatten() -> Series:
    """T 简体中文 flattened series."""
    return Series.load(output_dir / "zho-Hans_flatten.srt")


@pytest.fixture
def t_zho_hans_clean_flatten() -> Series:
    """T 简体中文 cleaned and flattened series."""
    return Series.load(output_dir / "zho-Hans_clean_flatten.srt")


# endregion


# region 繁体中文
@pytest.fixture
def t_zho_hant() -> Series:
    """T 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_simplify() -> Series:
    """T 繁体中文 simplified series."""
    return Series.load(output_dir / "zho-Hant_simplify.srt")


# endregion


# region English
@pytest.fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_clean() -> Series:
    """T English cleaned series."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def t_eng_flatten() -> Series:
    """T English flattened series."""
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def t_eng_clean_flatten() -> Series:
    """T English cleaned and flattened series."""
    return Series.load(output_dir / "eng_clean_flatten.srt")


# endregion


# region Bilingual 简体中文 and English
@pytest.fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual 简体粤文 and English series."""
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
    "t_distribute_test_cases",
    "t_shift_test_cases",
    "t_merge_test_cases",
    "t_proof_test_cases",
    "t_translate_test_cases",
    "t_review_test_cases",
]
