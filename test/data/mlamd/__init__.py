#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""
from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.image import ImageSeries
from scinoephile.testing.file import get_test_file_path


# Simplified Cantonese Chinese
@pytest.fixture
def mlamd_cmn_hans_hk() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hans-HK"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hans-HK.sup"))


# Traditional Cantonese Chinese
@pytest.fixture
def mlamd_cmn_hant_hk() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hant-HK"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hant-HK.sup"))


# English
@pytest.fixture
def mlamd_en_hk() -> ImageSeries:
    try:
        return ImageSeries.load(get_test_file_path("mlamd/output/en-HK"))
    except FileNotFoundError:
        return ImageSeries.load(get_test_file_path("mlamd/input/en-HK.sup"))


# Images
@pytest.fixture()
def mlamd_cmn_hans_hk_image() -> Image:
    return Image.open(
        get_test_file_path("mlamd/output/cmn-Hans-HK/0001_00048792_00051125.png")
    )


@pytest.fixture()
def mlamd_cmn_hant_hk_image() -> Image:
    return Image.open(
        get_test_file_path("mlamd/output/cmn-Hant-HK/0001_00048792_00051125.png")
    )


@pytest.fixture()
def mlamd_en_hk_image() -> Image:
    return Image.open(
        get_test_file_path("mlamd/output/en-HK/0001_00048792_00051125.png")
    )


___all__ = [
    "mlamd_cmn_hans_hk",
    "mlamd_cmn_hant_hk",
    "mlamd_en_hk",
    "mlamd_cmn_hans_hk_image",
    "mlamd_cmn_hant_hk_image",
    "mlamd_en_hk_image",
]
