#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.kob.core.english.proof import kob_english_proof_test_cases

input_dir = test_data_root / "kob" / "input"
output_dir = test_data_root / "kob" / "output"


# region 简体粤文
@pytest.fixture
def kob_yue_hans() -> Series:
    """KOB 简体粤文 series."""
    return Series.load(input_dir / "yue-Hans.srt")


@pytest.fixture
def kob_yue_hans_clean() -> Series:
    """KOB 简体粤文 cleaned series."""
    return Series.load(output_dir / "yue-Hans_clean.srt")


@pytest.fixture
def kob_yue_hans_flatten() -> Series:
    """KOB 简体粤文 flattened series."""
    return Series.load(output_dir / "yue-Hans_flatten.srt")


@pytest.fixture
def kob_yue_hans_clean_flatten() -> Series:
    """KOB 简体粤文 cleaned and flattened series."""
    return Series.load(output_dir / "yue-Hans_clean_flatten.srt")


# endregion


# region 繁体粤文
@pytest.fixture
def kob_yue_hant() -> Series:
    """KOB 繁体粤文 series."""
    return Series.load(input_dir / "yue-Hant.srt")


@pytest.fixture
def kob_yue_hant_simplify() -> Series:
    """KOB 繁体粤文 simplified series."""
    return Series.load(output_dir / "yue-Hant_simplify.srt")


# endregion


# region English
@pytest.fixture
def kob_eng() -> Series:
    """KOB English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def kob_eng_clean() -> Series:
    """KOB English cleaned series."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def kob_eng_flatten() -> Series:
    """KOB English flattened series."""
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def kob_eng_proof() -> Series:
    """KOB English proofed series."""
    return Series.load(output_dir / "eng_proof.srt")


@pytest.fixture
def kob_eng_proof_clean_flatten() -> Series:
    """KOB English proofed, cleaned and flattened series."""
    return Series.load(output_dir / "eng_proof_clean_flatten.srt")


# endregion


# region Bilingual 简体粤文 and English
@pytest.fixture()
def kob_yue_hans_eng() -> Series:
    """KOB Bilingual 简体粤文 and English series."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


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
    "kob_eng_proof",
    "kob_eng_proof_clean_flatten",
    "kob_yue_hans_eng",
    "kob_english_proof_test_cases",
]
