#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of language-aware subtitle cleaning."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.core import Language
from scinoephile.workflows.cleaning import clean_series
from test.helpers import assert_series_equal, parametrize
from test.helpers.series_files import get_text_series

_ENG_SERIES_FIXTURE_NAMES = [
    *[
        f"{dataset_name}_eng_ocr_{stage_name}"
        for dataset_name in ("acopopb", "acoptc", "kob", "tmm")
        for stage_name in ("fuse", "lens", "tesseract")
    ],
    "kob_eng",
    *[f"{dataset_name}_eng_fuse" for dataset_name in ("mlamd", "mnt", "t")],
    *[
        f"{dataset_name}_eng_ocr_{stage_name}"
        for dataset_name in ("mlamd", "mnt", "t")
        for stage_name in ("lens", "tesseract")
    ],
]
"""English input series fixture names."""

_CHINESE_LANGUAGES = (
    ("yue_hans", Language.yue_hans),
    ("yue_hant", Language.yue_hant),
    ("zho_hans", Language.zho_hans),
    ("zho_hant", Language.zho_hant),
)
"""Chinese fixture name stems and languages."""

_CHINESE_SERIES_FIXTURES = [
    *[
        (f"{dataset_name}_{language_stem}_ocr_{stage_name}", language)
        for dataset_name in ("acopopb", "acoptc")
        for language_stem, language in _CHINESE_LANGUAGES
        for stage_name in ("fuse", "lens", "paddle")
    ],
    *[
        (f"kob_zho_hant_ocr_{stage_name}", Language.zho_hant)
        for stage_name in ("fuse", "lens", "paddle")
    ],
    ("kob_yue_hans", Language.yue_hans),
    ("kob_yue_hant", Language.yue_hant),
    *[
        (f"{dataset_name}_{language_stem}_fuse", language)
        for dataset_name in ("mlamd", "mnt", "t")
        for language_stem, language in _CHINESE_LANGUAGES[2:]
    ],
    *[
        (f"{dataset_name}_{language_stem}_ocr_{stage_name}", language)
        for dataset_name in ("mlamd", "mnt", "t")
        for language_stem, language in _CHINESE_LANGUAGES[2:]
        for stage_name in ("lens", "paddle")
    ],
    *[
        (f"tmm_{language_stem}_ocr_{stage_name}", language)
        for language_stem, language in _CHINESE_LANGUAGES
        for stage_name in ("fuse", "lens", "paddle")
    ],
]
"""Chinese input series fixture names and languages."""

_CLEAN_SERIES_CASES = [
    *[
        param(
            fixture_name,
            f"{fixture_name}_clean",
            Language.eng,
            id=fixture_name.replace("_", "-"),
        )
        for fixture_name in _ENG_SERIES_FIXTURE_NAMES
    ],
    *[
        param(
            fixture_name,
            f"{fixture_name}_clean",
            language,
            id=fixture_name.replace("_", "-"),
        )
        for fixture_name, language in _CHINESE_SERIES_FIXTURES
    ],
]
"""Language-aware series cleaning cases."""


@parametrize(
    ("language", "text", "expected"),
    [
        param(
            Language.eng,
            "hello\\N-\\Nworld",
            "hello\\Nworld",
            id="eng-empty-dialogue-line",
        ),
        param(
            Language.eng,
            '<font face="Monospace">{\\an7}WOODY:\xa0Look out!</font>',
            "WOODY: Look out!",
            id="eng-extraction-markup",
        ),
        param(
            Language.eng,
            "hello\x00world",
            "hello world",
            id="eng-null-character",
        ),
        param(
            Language.eng,
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
            id="eng-full-width-alphanumerics",
        ),
        param(Language.eng, "ΟΚ, οκ.", "OK, ok.", id="eng-greek-lookalikes"),
        param(
            Language.zho_hant,
            '<font face="Monospace">{\\an7}中文\xa0測試</font>',
            "中文 測試",
            id="zho-extraction-markup",
        ),
        param(
            Language.zho_hans,
            "ΟΚ\x00中文",
            "OK 中文",
            id="zho-null-character",
        ),
        param(
            Language.yue_hans,
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
            id="zho-full-width-alphanumerics",
        ),
        param(
            Language.yue_hant,
            "｢你好､世界｡｣周·星馳･劉德華",
            "「你好、世界。」周・星馳・劉德華",
            id="zho-punctuation",
        ),
    ],
)
def test_clean_series_normalization(language: Language, text: str, expected: str):
    """Test language-specific text cleaning.

    Arguments:
        language: language to use for cleaning
        text: text to clean
        expected: expected cleaned text
    """
    output = clean_series(
        get_text_series(text),
        language=language,
        remove_empty=False,
    )

    assert next(iter(output)).text == expected


@parametrize(
    ("series_fixture", "expected_fixture", "language"),
    _CLEAN_SERIES_CASES,
)
def test_clean_series_outputs(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    language: Language,
):
    """Test cleaning against expected subtitle series.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        language: language to use for cleaning
    """
    output = clean_series(
        request.getfixturevalue(series_fixture),
        language=language,
        remove_empty=False,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
