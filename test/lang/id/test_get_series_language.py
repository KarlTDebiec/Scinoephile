#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.id.get_series_language."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.core import Language
from scinoephile.lang.id import get_series_language
from test.helpers import parametrize


@parametrize(
    ("series_fixture", "expected"),
    [
        param(
            "acopopb_eng",
            Language.eng,
            id="acopopb-eng",
        ),
        param(
            "acopopb_eng_ocr_fuse_clean_validate",
            Language.eng,
            id="acopopb-eng-ocr",
        ),
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate",
            Language.yue_hans,
            id="acopopb-yue-hans-ocr",
        ),
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate",
            Language.yue_hant,
            id="acopopb-yue-hant-ocr",
        ),
        param(
            "acopopb_zho_hans",
            Language.zho_hans,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate",
            Language.zho_hans,
            id="acopopb-zho-hans-ocr",
        ),
        param(
            "acopopb_zho_hant",
            Language.zho_hant,
            id="acopopb-zho-hant",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate",
            Language.zho_hant,
            id="acopopb-zho-hant-ocr",
        ),
        param(
            "acoptc_eng",
            Language.eng,
            id="acoptc-eng",
        ),
        param(
            "acoptc_eng_ocr_fuse_clean_validate",
            Language.eng,
            id="acoptc-eng-ocr",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate",
            Language.yue_hans,
            id="acoptc-yue-hans-ocr",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate",
            Language.yue_hant,
            id="acoptc-yue-hant-ocr",
        ),
        param(
            "acoptc_zho_hans",
            Language.zho_hans,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate",
            Language.zho_hans,
            id="acoptc-zho-hans-ocr",
        ),
        param(
            "acoptc_zho_hant",
            Language.zho_hant,
            id="acoptc-zho-hant",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate",
            Language.zho_hant,
            id="acoptc-zho-hant-ocr",
        ),
        param(
            "kob_eng",
            Language.eng,
            id="kob-eng",
        ),
        param(
            "kob_eng_ocr_fuse_clean_validate",
            Language.eng,
            id="kob-eng-ocr",
        ),
        param(
            "kob_yue_hans",
            Language.yue_hans,
            id="kob-yue-hans",
        ),
        param(
            "kob_yue_hant",
            Language.yue_hant,
            id="kob-yue-hant-input",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate",
            Language.zho_hant,
            id="kob-zho-hant-ocr",
        ),
        param(
            "mlamd_eng_fuse_clean_validate",
            Language.eng,
            id="mlamd-eng-ocr",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate",
            Language.zho_hans,
            id="mlamd-zho-hans-ocr",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate",
            Language.zho_hant,
            id="mlamd-zho-hant-ocr",
        ),
        param(
            "mnt_eng_fuse_clean_validate",
            Language.eng,
            id="mnt-eng-ocr",
        ),
        param(
            "mnt_jpn_eng",
            Language.eng,
            id="mnt-jpn-eng",
        ),
        param(
            "mnt_yue_zho_hant",
            Language.zho_hant,
            id="mnt-yue-zho-hant",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate",
            Language.zho_hans,
            id="mnt-zho-hans-ocr",
        ),
        param(
            "mnt_zho_hant",
            Language.zho_hant,
            id="mnt-zho-hant",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate",
            Language.zho_hant,
            id="mnt-zho-hant-ocr",
        ),
        param(
            "t_eng",
            Language.eng,
            id="t-eng",
        ),
        param(
            "t_eng_fuse_clean_validate",
            Language.eng,
            id="t-eng-ocr",
        ),
        param(
            "t_zho_hans",
            Language.zho_hans,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hans_fuse_clean_validate",
            Language.zho_hans,
            id="t-zho-hans-ocr",
        ),
        param(
            "t_zho_hant",
            Language.zho_hant,
            id="t-zho-hant",
        ),
        param(
            "t_zho_hant_fuse_clean_validate",
            Language.zho_hant,
            id="t-zho-hant-ocr",
        ),
        param(
            "tmm_eng_ocr_fuse_clean_validate",
            Language.eng,
            id="tmm-eng-ocr",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate",
            Language.yue_hans,
            id="tmm-yue-hans-ocr",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate",
            Language.yue_hant,
            id="tmm-yue-hant-ocr",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate",
            Language.zho_hans,
            id="tmm-zho-hans-ocr",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate",
            Language.zho_hant,
            id="tmm-zho-hant-ocr",
        ),
    ],
)
def test_get_series_language(
    request: FixtureRequest,
    series_fixture: str,
    expected: Language | None,
):
    """Detect language of subtitle series.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected: expected language, if conclusive
    """
    series = request.getfixturevalue(series_fixture)

    assert get_series_language(series) is expected
