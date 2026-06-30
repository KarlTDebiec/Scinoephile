#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.get_yue_romanized."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.lang.yue.romanization import (
    get_yue_char_romanized,
    get_yue_romanized,
    get_yue_text_romanized,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("series_fixture", "expected_fixture"),
    [
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="acopopb-yue-hans",
        ),
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="acopopb-yue-hant",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="acoptc-yue-hans",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="acoptc-yue-hant",
        ),
        param(
            "kob_yue_hans_clean_review_flatten_timewarp",
            "kob_yue_hans_clean_review_flatten_timewarp_romanize",
            id="kob-yue-hans",
        ),
        param(
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review",
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review_romanize",
            id="kob-yue-hant",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="tmm-yue-hans",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="tmm-yue-hant",
        ),
    ],
)
def test_get_yue_romanized(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_yue_romanized against expected romanized outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: Fixture name for input series
        expected_fixture: Fixture name for expected output series
    """
    output = get_yue_romanized(
        request.getfixturevalue(series_fixture),
        append=True,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))


@parametrize(
    ("text", "expected"),
    [
        ("广东话", "gwóngdūngwá"),
        ("你好世界", "néih hóu saigaai"),
        ("你好,世界!", "néih hóu, saigaai!"),
        ("「你好」世界？", "｢néih hóu｣ saigaai?"),
        ("＂你好＂世界", '"néih hóu" saigaai'),
        ("＇你好＇世界", "'néih hóu' saigaai"),
        ("佢话＇你好＇", "kéuih wah 'néih hóu'"),
        ("你好：世界；再见。", "néih hóu: saigaai; joigin｡"),
        ("don't你好", "don't néih hóu"),
        ("rock'n'roll你好", "rock'n'roll néih hóu"),
        ('"t i"你好', '"t i" néih hóu'),
        ("你好　世界", "néih hóu  saigaai"),
        (
            "乱讲，啫啫一 fling fling 吖嘛",
            "lyuhn góng, jē jē yāt fling fling ā ma",
        ),
        (
            "骑呢怪，做咩搞到咁乌 where ？",
            "kèh nē gwaai, jouh mē gáau dou gam wū where ?",
        ),
        ("原来少爷", "yùhnlòih siuyèh"),
        ("龙飞凤舞，苏察哈尔灿", "lùhngfēifuhngmóuh, sōuchaathāyíhchaan"),
    ],
)
def test_get_yue_text_romanized(text: str, expected: str):
    """Test get_yue_text_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_yue_text_romanized(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("你", "néih"),
        ("，", ""),
        ("？", ""),
    ],
)
def test_get_yue_char_romanized(text: str, expected: str):
    """Test get_yue_char_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_yue_char_romanized(text) == expected
