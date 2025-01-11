#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.drawing"""
from __future__ import annotations

from pathlib import Path

from scinoephile.image import ImageSeries
from scinoephile.image.validation import validate_ocr
from ..data.mlamd import (
    mlamd_cmn_hans_hk,
    mlamd_cmn_hans_hk_validation_directory,
    mlamd_cmn_hant_hk,
    mlamd_cmn_hant_hk_validation_directory,
    mlamd_en_hk,
    mlamd_en_hk_validation_directory,
)


def _test_get_image_of_text(series: ImageSeries):
    series.events[0].image_stack.show()


# diff
def test_get_upscaled_image_mlamd_cmn_hans_hk(mlamd_cmn_hans_hk: ImageSeries):
    _test_get_image_of_text(mlamd_cmn_hans_hk)


def test_get_upscaled_image_mlamd_cmn_hant_hk(mlamd_cmn_hant_hk: ImageSeries):
    _test_get_image_of_text(mlamd_cmn_hant_hk)


def test_get_upscaled_image_mlamd_en_hk(mlamd_en_hk: ImageSeries):
    _test_get_image_of_text(mlamd_en_hk)


# validation
def test_validation_mlamd_cmn_hans_hk(
    mlamd_cmn_hans_hk: ImageSeries, mlamd_cmn_hans_hk_validation_directory: Path
):
    validate_ocr(mlamd_cmn_hans_hk, mlamd_cmn_hans_hk_validation_directory)


def test_validation_mlamd_cmn_hant_hk(
    mlamd_cmn_hant_hk: ImageSeries, mlamd_cmn_hant_hk_validation_directory: Path
):
    validate_ocr(mlamd_cmn_hant_hk, mlamd_cmn_hant_hk_validation_directory)


def test_validation_mlamd_en_hk(
    mlamd_en_hk: ImageSeries, mlamd_en_hk_validation_directory: Path
):
    validate_ocr(mlamd_en_hk, mlamd_en_hk_validation_directory)
