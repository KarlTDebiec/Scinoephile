#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of language-aware subtitle flattening."""

from __future__ import annotations

from pytest import FixtureRequest, fail, param, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.workflows.flatten import flatten_series
from test.helpers import assert_series_equal, parametrize
from test.helpers.series_files import get_text_series


@parametrize(
    ("language", "series_fixture", "expected_fixture"),
    [
        param(
            Language.eng,
            "acopopb_eng_ocr_fuse_clean_validate_review",
            "acopopb_eng_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-eng",
        ),
        param(
            Language.eng,
            "acoptc_eng_ocr_fuse_clean_validate_review",
            "acoptc_eng_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-eng",
        ),
        param(
            Language.eng,
            "kob_eng_ocr_fuse_clean_validate_review",
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
            id="kob-eng-ocr",
        ),
        param(
            Language.eng,
            "kob_eng_clean_review",
            "kob_eng_clean_review_flatten",
            id="kob-eng-srt",
        ),
        param(
            Language.eng,
            "mlamd_eng_fuse_clean_validate_review",
            "mlamd_eng_fuse_clean_validate_review_flatten",
            id="mlamd-eng",
        ),
        param(
            Language.eng,
            "mnt_eng_fuse_clean_validate_review",
            "mnt_eng_fuse_clean_validate_review_flatten",
            id="mnt-eng",
        ),
        param(
            Language.eng,
            "t_eng_fuse_clean_validate_review",
            "t_eng_fuse_clean_validate_review_flatten",
            id="t-eng",
        ),
        param(
            Language.eng,
            "tmm_eng_ocr_fuse_clean_validate_review",
            "tmm_eng_ocr_fuse_clean_validate_review_flatten",
            id="tmm-eng",
        ),
        param(
            Language.yue_hans,
            "acopopb_yue_hans_ocr_fuse_clean_validate_review",
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-yue-hans",
        ),
        param(
            Language.yue_hant,
            "acopopb_yue_hant_ocr_fuse_clean_validate_review",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-yue-hant",
        ),
        param(
            Language.zho_hans,
            "acopopb_zho_hans_ocr_fuse_clean_validate_review",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-zho-hans",
        ),
        param(
            Language.zho_hant,
            "acopopb_zho_hant_ocr_fuse_clean_validate_review",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-zho-hant",
        ),
        param(
            Language.yue_hans,
            "acoptc_yue_hans_ocr_fuse_clean_validate_review",
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-yue-hans",
        ),
        param(
            Language.yue_hant,
            "acoptc_yue_hant_ocr_fuse_clean_validate_review",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-yue-hant",
        ),
        param(
            Language.zho_hans,
            "acoptc_zho_hans_ocr_fuse_clean_validate_review",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-zho-hans",
        ),
        param(
            Language.zho_hant,
            "acoptc_zho_hant_ocr_fuse_clean_validate_review",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-zho-hant",
        ),
        param(
            Language.zho_hant,
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="kob-zho-hant",
        ),
        param(
            Language.yue_hans,
            "kob_yue_hans_clean_review",
            "kob_yue_hans_clean_review_flatten",
            id="kob-yue-hans-srt",
        ),
        param(
            Language.yue_hant,
            "kob_yue_hant_clean_review",
            "kob_yue_hant_clean_review_flatten",
            id="kob-yue-hant-srt",
        ),
        param(
            Language.zho_hans,
            "mlamd_zho_hans_fuse_clean_validate_review",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            id="mlamd-zho-hans",
        ),
        param(
            Language.zho_hant,
            "mlamd_zho_hant_fuse_clean_validate_review",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten",
            id="mlamd-zho-hant",
        ),
        param(
            Language.zho_hans,
            "mnt_zho_hans_fuse_clean_validate_review",
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            id="mnt-zho-hans",
        ),
        param(
            Language.zho_hant,
            "mnt_zho_hant_fuse_clean_validate_review",
            "mnt_zho_hant_fuse_clean_validate_review_flatten",
            id="mnt-zho-hant",
        ),
        param(
            Language.zho_hans,
            "t_zho_hans_fuse_clean_validate_review",
            "t_zho_hans_fuse_clean_validate_review_flatten",
            id="t-zho-hans",
        ),
        param(
            Language.zho_hant,
            "t_zho_hant_fuse_clean_validate_review",
            "t_zho_hant_fuse_clean_validate_review_flatten",
            id="t-zho-hant",
        ),
        param(
            Language.yue_hans,
            "tmm_yue_hans_ocr_fuse_clean_validate_review",
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
            id="tmm-yue-hans",
        ),
        param(
            Language.yue_hant,
            "tmm_yue_hant_ocr_fuse_clean_validate_review",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten",
            id="tmm-yue-hant",
        ),
        param(
            Language.zho_hans,
            "tmm_zho_hans_ocr_fuse_clean_validate_review",
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="tmm-zho-hans",
        ),
        param(
            Language.zho_hant,
            "tmm_zho_hant_ocr_fuse_clean_validate_review",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="tmm-zho-hant",
        ),
    ],
)
def test_flatten_series(
    request: FixtureRequest,
    language: Language,
    series_fixture: str,
    expected_fixture: str,
):
    """Test language-aware series flattening against expected outputs.

    Arguments:
        request: pytest request for fixture lookup
        language: subtitle language
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    series = request.getfixturevalue(series_fixture)
    output = flatten_series(series, language=language)

    assert len(series) == len(output)

    errors = []
    for i, event in enumerate(output, 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")

    if errors:
        for error in errors:
            print(error)
        fail(f"Found {len(errors)} discrepancies")
    assert_series_equal(output, request.getfixturevalue(expected_fixture))


def test_flatten_series_excludes_indexes():
    """Test series flattening skips excluded indexes without modifying its input."""
    source = get_text_series("first\nline", "second\nline")

    output = flatten_series(source, language=Language.eng, exclusions=[1])

    assert [event.text for event in output] == ["first\nline", "second line"]
    assert [event.text for event in source] == ["first\nline", "second\nline"]


def test_flatten_series_rejects_nonpositive_exclusions():
    """Test series flattening rejects nonpositive exclusion indexes."""
    with raises(
        ScinoephileError,
        match="Exclusion indexes must be positive",
    ):
        flatten_series(get_text_series("text"), language=Language.eng, exclusions=[0])
