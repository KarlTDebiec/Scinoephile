#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_converted."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.lang.zho.script.conversion import (
    S2T_EXCLUSIONS,
    T2S_EXCLUSIONS,
    OpenCCConfig,
    get_zho_character_variants,
    get_zho_converted,
    get_zho_converter,
    get_zho_text_converted,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("text", "config", "expected"),
    [
        ("台臺", OpenCCConfig.s2t, "台臺"),
        ("台臺", OpenCCConfig.t2s, "台台"),
        ("你吃吓晒啦", OpenCCConfig.s2t, "你吃吓晒啦"),
        ("一群牛虱", OpenCCConfig.s2t, "一群牛虱"),
        ("这家伙", OpenCCConfig.s2t, "這家伙"),
        ("呢個嗰度喎", OpenCCConfig.t2s, "呢个嗰度㖞"),
        ("希望藉此答覆", OpenCCConfig.t2s, "希望借此答复"),
        ("丑大了", OpenCCConfig.s2t, "丑大了"),
        ("移形換影", OpenCCConfig.t2s, "移形换影"),
        ("黃大富", OpenCCConfig.t2s, "黄大富"),
        ("干杯", OpenCCConfig.s2t, "乾杯"),
        ("一只猫", OpenCCConfig.s2t, "一隻貓"),
        ("方便面", OpenCCConfig.s2t, "方便麪"),
        ("家具", OpenCCConfig.s2t, "傢俱"),
        ("制作", OpenCCConfig.s2t, "製作"),
        ("制定", OpenCCConfig.s2t, "制定"),
        ("注定", OpenCCConfig.s2t, "注定"),
        ("标准", OpenCCConfig.s2t, "標準"),
        ("無厘頭", OpenCCConfig.s2t, "無厘頭"),
        ("无厘頭", OpenCCConfig.s2t, "無釐頭"),
        ("答覆", OpenCCConfig.t2s, "答复"),
        ("藉口", OpenCCConfig.t2s, "借口"),
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


@parametrize("text", sorted(S2T_EXCLUSIONS))
def test_s2t_exclusions_are_raw_opencc_changes(text: str):
    """Test every simplified-to-traditional exclusion changes under raw OpenCC.

    Arguments:
        text: excluded text span
    """
    converted_text = get_zho_converter(OpenCCConfig.s2t).convert(text)
    assert converted_text != text


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
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_zho_converted with traditional standard Chinese subtitles.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    series = request.getfixturevalue(series_fixture)
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_converted(
        series,
        OpenCCConfig.t2s,
    )
    assert len(series) == len(output)
    assert_series_equal(
        output,
        expected,
    )


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
