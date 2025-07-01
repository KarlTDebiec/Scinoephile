#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.image import ImageSeries
from scinoephile.testing import MergeTestCase, test_data_root

input_dir = test_data_root / "mlamd" / "input"
output_dir = test_data_root / "mlamd" / "output"


# region Simplified Standard Chinese
@pytest.fixture
def mlamd_zho_hans() -> ImageSeries:
    try:
        return ImageSeries.load(output_dir / "zho-Hans")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hans.sup")


@pytest.fixture()
def mlamd_zho_hans_image() -> Image:
    return Image.open(output_dir / "zho-Hans" / "0001.png")


@pytest.fixture
def mlamd_zho_hans_validation_directory() -> str:
    return output_dir / "zho-Hans_validation"


# endregion


# region Traditional Standard Chinese
@pytest.fixture
def mlamd_zho_hant() -> ImageSeries:
    try:
        return ImageSeries.load(output_dir / "zho-Hant")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hant.sup")


@pytest.fixture()
def mlamd_zho_hant_image() -> Image:
    return Image.open(output_dir / "zho-Hant" / "0001.png")


@pytest.fixture
def mlamd_zho_hant_validation_directory() -> str:
    return output_dir / "zho-Hant_validation"


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> ImageSeries:
    try:
        return ImageSeries.load(output_dir / "eng")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "eng.sup")


@pytest.fixture()
def mlamd_eng_image() -> Image:
    return Image.open(output_dir / "eng" / "0001.png")


@pytest.fixture
def mlamd_eng_validation_directory() -> str:
    return output_dir / "eng_validation"


# endregion

# region 粤文 Merging Test Cases

mlamd_merge_test_cases = [
    MergeTestCase(
        zhongwen_input="沿荔枝角道直出大角咀道",
        yuewen_input=[
            "沿住荔枝角度",
            "直出大角咀度",
        ],
        yuewen_output="沿住荔枝角度直出大角咀度",
    ),
    MergeTestCase(
        zhongwen_input="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen_input=[
            "经过好彩走家",
            "再左转返出花园街",
            "乐园牛园望对上",
        ],
        yuewen_output="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
    ),
    MergeTestCase(
        zhongwen_input="转呀，转⋯再更正一下",
        yuewen_input=[
            "转下",
            "转下",
            "都系唔好",
        ],
        yuewen_output="转下，转下⋯再更正一下：",
    ),
]

# endregion

___all__ = [
    "mlamd_zho_hans",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_validation_directory",
    "mlamd_zho_hant",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_validation_directory",
    "mlamd_eng",
    "mlamd_eng_image",
    "mlamd_eng_validation_directory",
]
