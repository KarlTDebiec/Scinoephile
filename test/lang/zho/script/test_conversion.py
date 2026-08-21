#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_converted."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.core.script import OpenCCConfig
from scinoephile.lang.zho.script.conversion import (
    S2HK_EXCLUSIONS,
    T2S_EXCLUSIONS,
    get_zho_character_variants,
    get_zho_converted,
    get_zho_converter,
    get_zho_text_converted,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("text", "config", "expected"),
    [
        ("台臺", OpenCCConfig.s2t, "臺臺"),
        ("你吃吓晒啦", OpenCCConfig.s2hk, "你吃吓晒啦"),
        ("你吃吓晒啦", OpenCCConfig.s2hkp, "你吃吓晒啦"),
        ("唔好郁，响邊扑你", OpenCCConfig.s2hk, "唔好郁，响邊扑你"),
        ("唔好郁，响邊扑你", OpenCCConfig.s2hkp, "唔好郁，响邊扑你"),
        ("一群牛虱", OpenCCConfig.s2hk, "一群牛蝨"),
        ("一群牛虱", OpenCCConfig.s2hkp, "一群牛蝨"),
        ("萬里長城說，瞓床搵你", OpenCCConfig.s2hk, "萬里長城說，瞓床搵你"),
        ("萬里長城說，瞓床搵你", OpenCCConfig.s2hkp, "萬里長城說，瞓床搵你"),
        ("台臺", OpenCCConfig.t2s, "台台"),
        ("呢個嗰度喎", OpenCCConfig.t2s, "呢个嗰度㖞"),
        ("劏唓嗰餸繁體", OpenCCConfig.t2s, "劏唓嗰餸繁体"),
    ],
)
def test_get_zho_text_converted_applies_exclusions(
    text: str, config: OpenCCConfig, expected: str
):
    """Test conversion exclusions preserve only excluded text spans.

    Arguments:
        text: Text to convert
        config: Conversion configuration
        expected: Expected converted text
    """
    assert get_zho_text_converted(text, config) == expected


def test_get_zho_text_converted_only_applies_s2hk_exclusions_to_hk_configs():
    """Test Hong Kong exclusions affect only Hong Kong conversion configs."""
    assert get_zho_text_converted("說", OpenCCConfig.s2t) == "說"
    assert get_zho_text_converted("萬里長城說", OpenCCConfig.t2jp) == "万里長城説"


@parametrize(
    ("text", "config"),
    [
        (text, config)
        for text in sorted(S2HK_EXCLUSIONS)
        for config in (OpenCCConfig.s2hk, OpenCCConfig.s2hkp)
    ],
)
def test_s2hk_exclusions_are_raw_opencc_changes(text: str, config: OpenCCConfig):
    """Test every Hong Kong exclusion changes raw and is preserved when applied.

    Arguments:
        text: excluded text span
        config: Hong Kong conversion configuration
    """
    converted_text = get_zho_converter(config).convert(text)
    assert converted_text != text
    assert get_zho_text_converted(text, config) == text


@parametrize("text", sorted(T2S_EXCLUSIONS))
def test_t2s_exclusions_are_raw_opencc_changes(text: str):
    """Test every traditional-to-simplified exclusion changes under raw OpenCC.

    Arguments:
        text: excluded text span
    """
    converted_text = get_zho_converter(OpenCCConfig.t2s).convert(text)
    assert converted_text != text


@parametrize(
    ("series_fixture", "expected_fixture"),
    [
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="acopopb-yue-hant",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="acopopb-zho-hant",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="acoptc-yue-hant",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="acoptc-zho-hant",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="kob-zho-hant",
        ),
        param(
            "kob_yue_hant_clean_review_flatten_timewarp",
            "kob_yue_hant_clean_review_flatten_timewarp_simplify",
            id="kob-yue-hant-srt",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review_flatten",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify",
            id="mlamd-zho-hant",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review_flatten",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify",
            id="mnt-zho-hant",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review_flatten",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
            id="t-zho-hant",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="tmm-yue-hant",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            id="tmm-zho-hant",
        ),
    ],
)
def test_get_zho_converted(
    request: FixtureRequest, series_fixture: str, expected_fixture: str
):
    """Test get_zho_converted with traditional standard Chinese subtitles.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    series = request.getfixturevalue(series_fixture)
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_converted(series, OpenCCConfig.t2s)
    assert len(series) == len(output)
    assert_series_equal(output, expected)


@parametrize(
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


def test_get_zho_character_variants():
    """Test character variants include both standard Chinese scripts."""
    assert get_zho_character_variants(("错这",)) == ("这", "這", "錯", "错")
