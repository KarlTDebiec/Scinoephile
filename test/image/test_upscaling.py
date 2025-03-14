#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.upscale."""
from __future__ import annotations

from PIL import Image

from scinoephile.image.upscaling import get_upscaled_image
from scinoephile.testing.mark import skip_if_ci
from ..data.mlamd import (
    mlamd_zho_hans_image,
    mlamd_zho_hant_image,
    mlamd_eng_image,
)


def _test_get_upscaled_image(image: Image.Image):
    upscaled = get_upscaled_image(image)
    assert max(upscaled.size) == 2000


# get_upscaled_image
@skip_if_ci()
def test_get_upscaled_image_mlamd_zho_hans(mlamd_zho_hans_image: Image.Image):
    _test_get_upscaled_image(mlamd_zho_hans_image)


@skip_if_ci()
def test_get_upscaled_image_mlamd_zho_hant(mlamd_zho_hant_image: Image.Image):
    _test_get_upscaled_image(mlamd_zho_hant_image)


@skip_if_ci()
def test_get_upscaled_image_mlamd_eng(mlamd_eng_image: Image.Image):
    _test_get_upscaled_image(mlamd_eng_image)
