#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""
from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.image import ImageSeries
from scinoephile.testing.file import get_test_directory_path, get_test_file_path


# region Simplified Standard Chinese
@pytest.fixture
def mlamd_cmn_hans() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hans"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hans.sup"))


@pytest.fixture()
def mlamd_cmn_hans_image() -> Image:
    return Image.open(
        get_test_file_path("mlamd/output/cmn-Hans/0001_00048792_00051125.png")
    )


@pytest.fixture
def mlamd_cmn_hans_validation_directory() -> str:
    return get_test_directory_path("mlamd/output/cmn-Hans_validation")


# endregion


# region Traditional Standard Chinese
@pytest.fixture
def mlamd_cmn_hant() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hant"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hant.sup"))


@pytest.fixture()
def mlamd_cmn_hant_image() -> Image:
    return Image.open(
        get_test_file_path("mlamd/output/cmn-Hant/0001_00048792_00051125.png")
    )


@pytest.fixture
def mlamd_cmn_hant_validation_directory() -> str:
    return get_test_directory_path("mlamd/output/cmn-Hant_validation")


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/eng"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/eng.sup"))


@pytest.fixture()
def mlamd_eng_image() -> Image:
    return Image.open(get_test_file_path("mlamd/output/eng/0001_00048792_00051125.png"))


@pytest.fixture
def mlamd_eng_validation_directory() -> str:
    return get_test_directory_path("mlamd/output/eng_validation")


# endregion

___all__ = [
    "mlamd_cmn_hans",
    "mlamd_cmn_hans_image",
    "mlamd_cmn_hans_validation_directory",
    "mlamd_cmn_hant",
    "mlamd_cmn_hant_image",
    "mlamd_cmn_hant_validation_directory",
    "mlamd_eng",
    "mlamd_eng_image",
    "mlamd_eng_validation_directory",
]
