#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation helpers."""

# ruff: noqa: E501

from __future__ import annotations

import logging

import pytest

from scinoephile.core.testing import assert_expected_warnings, get_warning_messages
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng import validate_eng_ocr
from scinoephile.lang.zho import validate_zho_ocr


def test_validate_eng_ocr_mlamd(
    mlamd_eng_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_eng_ocr with MLAMD English image subtitles.

    Arguments:
        mlamd_eng_image: MLAMD English image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_eng_ocr(mlamd_eng_image, interactive=False)
    warnings = get_warning_messages(caplog.records)
    assert_expected_warnings(warnings, [], "English")


def test_validate_zho_ocr_mlamd_hans(
    mlamd_zho_hans_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_zho_ocr with MLAMD 简体中文 image subtitles.

    Arguments:
        mlamd_zho_hans_image: MLAMD 简体中文 image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_zho_ocr(mlamd_zho_hans_image, interactive=False)
    warnings = get_warning_messages(caplog.records)
    expected = [
        "Sub   57 | Char 13 | 对！深水埗地铁站步行不用10分钟！ | '1,0' -> 24 | expected ' ' observed ''",
        "Sub   90 | Char  8 | 就是有点游魂的Miss Chan | 'M,i' -> 24 | expected ' ' observed ''",
        "Sub   90 | Char  9 | 就是有点游魂的Miss Chan | 'i,s' -> 27 | expected ' ' observed ''",
        "Sub  103 | Char  1 | Miss Chan，我点过两次了！ | 'M,i' -> 24 | expected ' ' observed ''",
        "Sub  103 | Char  2 | Miss Chan，我点过两次了！ | 'i,s' -> 27 | expected ' ' observed ''",
        "Sub  165 | Char  6 | 有一首歌，Miss Chan唱的好听 | 'M,i' -> 24 | expected ' ' observed ''",
        "Sub  165 | Char  7 | 有一首歌，Miss Chan唱的好听 | 'i,s' -> 27 | expected ' ' observed ''",
        "Sub  168 | Char  2 | 是All Things Bright and Beautiful吧？ | 'A,l' -> 25 | expected ' ' observed ''",
        "Sub  168 | Char  3 | 是All Things Bright and Beautiful吧？ | 'l,l' -> 38 | expected ' ' observed ''",
        "Sub  168 | Char  7 | 是All Things Bright and Beautiful吧？ | 'h,i' -> 26 | expected ' ' observed ''",
        "Sub  168 | Char  8 | 是All Things Bright and Beautiful吧？ | 'i,n' -> 26 | expected ' ' observed ''",
        "Sub  168 | Char 14 | 是All Things Bright and Beautiful吧？ | 'r,i' -> 28 | expected ' ' observed ''",
        "Sub  168 | Char 15 | 是All Things Bright and Beautiful吧？ | 'i,g' -> 26 | expected ' ' observed ''",
        "Sub  168 | Char 28 | 是All Things Bright and Beautiful吧？ | 't,i' -> 31 | expected ' ' observed ''",
        "Sub  168 | Char 29 | 是All Things Bright and Beautiful吧？ | 'i,f' -> 30 | expected ' ' observed ''",
        "Sub  168 | Char 31 | 是All Things Bright and Beautiful吧？ | 'u,l' -> 26 | expected ' ' observed ''",
        "Sub  180 | Char 13 | 除了兼任保险，地产经纪及trading⋯ | 't,r' -> 28 | expected ' ' observed ''",
        "Sub  180 | Char 16 | 除了兼任保险，地产经纪及trading⋯ | 'd,i' -> 25 | expected ' ' observed ''",
        "Sub  180 | Char 17 | 除了兼任保险，地产经纪及trading⋯ | 'i,n' -> 26 | expected ' ' observed ''",
        "Sub  266 | Char  4 | 那儿有Disneyland 和Hello Kitty Land | 'D,i' -> 25 | expected ' ' observed ''",
        "Sub  266 | Char  5 | 那儿有Disneyland 和Hello Kitty Land | 'i,s' -> 27 | expected ' ' observed ''",
        "Sub  266 | Char  9 | 那儿有Disneyland 和Hello Kitty Land | 'y,l' -> 27 | expected ' ' observed ''",
        "Sub  266 | Char 10 | 那儿有Disneyland 和Hello Kitty Land | 'l,a' -> 26 | expected ' ' observed ''",
        "Sub  266 | Char 17 | 那儿有Disneyland 和Hello Kitty Land | 'e,l' -> 26 | expected ' ' observed ''",
        "Sub  266 | Char 18 | 那儿有Disneyland 和Hello Kitty Land | 'l,l' -> 38 | expected ' ' observed ''",
        "Sub  266 | Char 19 | 那儿有Disneyland 和Hello Kitty Land | 'l,o' -> 25 | expected ' ' observed ''",
        "Sub  266 | Char 22 | 那儿有Disneyland 和Hello Kitty Land | 'K,i' -> 26 | expected ' ' observed ''",
        "Sub  266 | Char 23 | 那儿有Disneyland 和Hello Kitty Land | 'i,t' -> 31 | expected ' ' observed ''",
        "Sub  266 | Char 24 | 那儿有Disneyland 和Hello Kitty Land | 't,t' -> 24 | expected ' ' observed ''",
        "Sub  266 | Char 25 | 那儿有Disneyland 和Hello Kitty Land | 't,y' -> 20 | expected ' ' observed ''",
        "Sub  517 | Char  2 | 在1978年两座包山忽然倒下，多人重伤 | '1,9' -> 25 | expected ' ' observed ''",
        "Sub  685 | Char  1 | 12月24日 | '1,2' -> 26 | expected ' ' observed ''",
    ]
    assert_expected_warnings(warnings, expected, "Simplified Chinese")


def test_validate_zho_ocr_mlamd_hant(
    mlamd_zho_hant_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_zho_ocr with MLAMD 繁体中文 image subtitles.

    Arguments:
        mlamd_zho_hant_image: MLAMD 繁体中文 image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_zho_ocr(mlamd_zho_hant_image, interactive=False)
    warnings = get_warning_messages(caplog.records)
    expected = [
        "Sub   57 | Char 13 | 對！深水埗地鐵站步行不用10分鐘！ | '1,0' -> 25 | expected ' ' observed ''",
        "Sub  517 | Char  2 | 在1978年兩座包山忽然倒下，多人重傷 | '1,9' -> 27 | expected ' ' observed ''",
        "Sub  685 | Char  1 | 12月24日 | '1,2' -> 27 | expected ' ' observed ''",
    ]
    assert_expected_warnings(warnings, expected, "Traditional Chinese")
