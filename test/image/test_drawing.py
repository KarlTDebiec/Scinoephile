#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.drawing"""
from __future__ import annotations

from PIL import Image

from scinoephile.image import ImageSeries
from scinoephile.image.drawing import get_image_of_text, get_stacked_image_diff
from ..data.mlamd import (
    mlamd_en_hk,
    mlamd_en_hk_image,
)


def _test_get_image_of_text(series: ImageSeries, image: Image.Image):
    image_from_text = get_image_of_text(series.events[0].text, image.size)
    image_stack = get_stacked_image_diff(image, image_from_text)
    image_stack.show()


# get_upscaled_image
# def test_get_upscaled_image_mlamd_cmn_hans_hk(
#     mlamd_cmn_hans_hk: ImageSeries, mlamd_cmn_hans_hk_image: Image
# ):
#     _test_get_image_of_text(mlamd_cmn_hans_hk, mlamd_cmn_hans_hk_image)
#
#
# def test_get_upscaled_image_mlamd_cmn_hant_hk(
#     mlamd_cmn_hant_hk: ImageSeries, mlamd_cmn_hant_hk_image: Image
# ):
#     _test_get_image_of_text(mlamd_cmn_hant_hk, mlamd_cmn_hant_hk_image)


def test_get_upscaled_image_mlamd_en_hk(
    mlamd_en_hk: ImageSeries, mlamd_en_hk_image: Image
):
    _test_get_image_of_text(mlamd_en_hk, mlamd_en_hk_image)
