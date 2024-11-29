#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.upscale."""
from __future__ import annotations

from PIL import Image

from scinoephile.image.upscale import get_upscaled_image
from scinoephile.testing.mark import skip_if_ci
from ..data.mlamd import (
    mlamd_cmn_hans_hk_image,
    mlamd_cmn_hant_hk_image,
    mlamd_en_hk_image,
)


def _test_get_upscaled_image(image: Image):
    upscaled = get_upscaled_image(image)
    assert max(upscaled.size) == 2000


# get_upscaled_image
@skip_if_ci()
def test_get_upscaled_image_mlamd_cmn_hans_hk(mlamd_cmn_hans_hk_image: Image):
    _test_get_upscaled_image(mlamd_cmn_hans_hk_image)


@skip_if_ci()
def test_get_upscaled_image_mlamd_cmn_hant_hk(mlamd_cmn_hant_hk_image: Image):
    _test_get_upscaled_image(mlamd_cmn_hant_hk_image)


@skip_if_ci()
def test_get_upscaled_image_mlamd_en_hk(mlamd_en_hk_image: Image):
    _test_get_upscaled_image(mlamd_en_hk_image)
