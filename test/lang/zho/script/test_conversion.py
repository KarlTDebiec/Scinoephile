#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_converted."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_converted,
    get_zho_converter,
    get_zho_text_converted,
)
from test.helpers import assert_series_equal


def test_opencc_config_metadata():
    """Test OpenCCConfig metadata."""
    config = OpenCCConfig.s2t
    assert config.code == "s2t"
    assert config.description == "Simplified Chinese to Traditional Chinese."
    assert str(config) == "s2t"
    assert OpenCCConfig("s2t") is config


@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("台臺", OpenCCConfig.s2t, "台臺"),
        ("台臺", OpenCCConfig.t2s, "台台"),
        ("你吃吓晒啦", OpenCCConfig.s2t, "你吃吓晒啦"),
        ("一群牛虱", OpenCCConfig.s2t, "一群牛虱"),
        ("这家伙", OpenCCConfig.s2t, "這家伙"),
        ("呢個嗰度喎", OpenCCConfig.t2s, "呢个嗰度喎"),
        ("希望藉此答覆", OpenCCConfig.t2s, "希望藉此答覆"),
        ("丑大了", OpenCCConfig.s2t, "丑大了"),
        ("移形換影", OpenCCConfig.t2s, "移形换影"),
        ("黃大富", OpenCCConfig.t2s, "黄大富"),
    ],
)
def test_get_zho_text_converted_applies_exclusions_by_character_position(
    text: str, config: OpenCCConfig, expected: str
):
    """Test conversion exclusions preserve only original excluded characters.

    Arguments:
        text: Text to convert
        config: Conversion configuration
        expected: Expected converted text
    """
    assert get_zho_text_converted(text, config) == expected


def test_get_zho_converted_kob(
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten: Series,
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify: Series,
):
    """Test get_zho_converted with KOB traditional standard Chinese subtitles.

    Arguments:
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten: KOB traditional
          standard Chinese series fixture
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify: Expected
          simplified
          KOB traditional standard Chinese series fixture
    """
    output = get_zho_converted(
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten,
        OpenCCConfig.t2s,
    )
    assert len(kob_zho_hant_ocr_fuse_clean_validate_review_flatten) == len(output)
    assert_series_equal(
        output,
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify,
    )


@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("繁體中文", OpenCCConfig.t2s, "繁体中文"),
        ("简体中文", OpenCCConfig.s2t, "簡體中文"),
    ],
)
def test_get_zho_converter(text: str, config: OpenCCConfig, expected: str):
    """Test get_zho_converter.

    Arguments:
        text: Text to convert
        config: Conversion configuration
        expected: Expected converted text
    """
    assert get_zho_converter(config).convert(text) == expected
