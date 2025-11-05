#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.core import Series
from scinoephile.image import ImageSeries
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.mlamd.core.english.proof import mlamd_english_proof_test_cases
from test.data.mlamd.distribution import mlamd_distribute_test_cases
from test.data.mlamd.merging import mlamd_merge_test_cases
from test.data.mlamd.proofing import mlamd_proof_test_cases
from test.data.mlamd.review import mlamd_review_test_cases
from test.data.mlamd.shifting import mlamd_shift_test_cases
from test.data.mlamd.translation import mlamd_translate_test_cases

input_dir = test_data_root / "mlamd" / "input"
output_dir = test_data_root / "mlamd" / "output"


# region 简体中文
@pytest.fixture
def mlamd_zho_hans() -> ImageSeries:
    """MLAMD 简体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hans")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hans.sup")


@pytest.fixture()
def mlamd_zho_hans_image() -> Image.Image:
    """MLAMD 简体中文 image."""
    return Image.open(output_dir / "zho-Hans" / "0001.png")


@pytest.fixture
def mlamd_zho_hans_validation_directory() -> str:
    """MLAMD 简体中文 validation directory."""
    return output_dir / "zho-Hans_validation"


# endregion


# region 繁体中文
@pytest.fixture
def mlamd_zho_hant() -> ImageSeries:
    """MLAMD 繁体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hant")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hant.sup")


@pytest.fixture()
def mlamd_zho_hant_image() -> Image.Image:
    """MLAMD 繁体中文 image."""
    return Image.open(output_dir / "zho-Hant" / "0001.png")


@pytest.fixture
def mlamd_zho_hant_validation_directory() -> str:
    """MLAMD 繁体中文 validation directory."""
    return output_dir / "zho-Hant_validation"


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> ImageSeries:
    """MLAMD English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def mlamd_eng_clean() -> Series:
    """MLAMD English cleaned series."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def mlamd_eng_flatten() -> Series:
    """MLAMD English flattened series."""
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def mlamd_eng_proof() -> Series:
    """MLAMD English proofed series."""
    return Series.load(output_dir / "eng_proof.srt")


@pytest.fixture
def mlamd_eng_proof_clean_flatten() -> Series:
    """MLAMD English proofed, cleaned and flattened series."""
    return Series.load(output_dir / "eng_proof_clean_flatten.srt")


# endregion


___all__ = [
    "mlamd_zho_hans",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_validation_directory",
    "mlamd_zho_hant",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_validation_directory",
    "mlamd_eng",
    "mlamd_eng_clean",
    "mlamd_eng_flatten",
    "mlamd_eng_proof",
    "mlamd_eng_proof_clean_flatten",
    "mlamd_distribute_test_cases",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
    "mlamd_translate_test_cases",
    "mlamd_review_test_cases",
    "mlamd_english_proof_test_cases",
]
