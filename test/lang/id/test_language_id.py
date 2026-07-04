#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.id."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.id import LanguageId, get_series_language
from test.helpers import parametrize, test_data_root

LANGUAGE_ID_TEST_CASES: list[LanguageId] = [
    LanguageId(
        text="nǐ hǎo",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lüè",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="ni3 hao3",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lu:e4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lv4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="ni hao",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="néih hóu",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="gwóngdūngwá",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="nei5 hou2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="gwong2 dung1 waa2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="简体中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
        language=Language.zho_hans,
    ),
    LanguageId(
        text="汉字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
    ),
    LanguageId(
        text="繁體中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    LanguageId(
        text="漢字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    LanguageId(
        text="中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=True,
    ),
    LanguageId(
        text="",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
]


@parametrize("case", LANGUAGE_ID_TEST_CASES)
def test_language_id_from_text(case: LanguageId):
    """Detect language ID features from text.

    Arguments:
        case: expected language ID result
    """
    result = LanguageId.from_text(case.text)

    assert result.is_accented_pinyin is case.is_accented_pinyin
    assert result.is_numbered_pinyin is case.is_numbered_pinyin
    assert result.is_accented_yale is case.is_accented_yale
    assert result.is_numbered_jyutping is case.is_numbered_jyutping
    assert result.is_simplified is case.is_simplified
    assert result.is_traditional is case.is_traditional
    assert result.language is case.language


@parametrize(
    ("text", "expected"),
    [
        ("English subtitles are ready", Language.eng),
        ("他在这里了", Language.zho_hans),
        ("她在這裡了", Language.zho_hant),
        ("是吗", Language.zho_hans),
        ("是嗎", Language.zho_hant),
        ("關係", Language.zho_hant),
        ("佢唔该咗", Language.yue_hans),
        ("佢唔該咗", Language.yue_hant),
        ("系咪该", Language.yue_hans),
        ("係咪該", Language.yue_hant),
        ("哋该", Language.yue_hans),
        ("哋該", Language.yue_hant),
        ("", None),
        ("nǐ hǎo", None),
        ("nei5 hou2", None),
        ("中文", None),
        ("系统", None),
    ],
)
def test_language_id_detects_language(text: str, expected: Language | None):
    """Detect language from one text input.

    Arguments:
        text: text to classify
        expected: expected language, if conclusive
    """
    assert LanguageId.from_text(text).language is expected


@parametrize(
    ("texts", "expected"),
    [
        (
            [
                "中文",
                "{\\i1}English\\Nsubtitle line",
                "Another English line",
                "Final English subtitle",
            ],
            Language.eng,
        ),
        (
            [
                "English subtitle line",
                "Another English line",
            ],
            None,
        ),
    ],
)
def test_get_series_language_counts_threshold(
    texts: list[str], expected: Language | None
):
    """Detect series language only after enough conclusive subtitles agree.

    Arguments:
        texts: subtitle texts to classify as a series
        expected: expected series language, if conclusive
    """
    series = Series(
        events=[
            Subtitle(start=idx * 1000, end=(idx * 1000) + 500, text=text)
            for idx, text in enumerate(texts)
        ]
    )

    assert get_series_language(series) is expected


@parametrize(
    ("relative_path", "expected"),
    [
        (Path("acopopb/input/eng.srt"), Language.eng),
        (Path("acopopb/input/zho-Hans.srt"), Language.zho_hans),
        (Path("acopopb/input/zho-Hant.srt"), Language.zho_hant),
        (Path("kob/input/yue-Hans.srt"), Language.yue_hans),
        (Path("kob/input/yue-Hant.srt"), Language.yue_hant),
        (Path("acopopb/output/eng_ocr/fuse.srt"), Language.eng),
        (Path("acopopb/output/zho-Hans_ocr/fuse.srt"), Language.zho_hans),
        (Path("acopopb/output/zho-Hant_ocr/fuse.srt"), Language.zho_hant),
        (Path("tmm/output/yue-Hans_ocr/fuse.srt"), Language.yue_hans),
        (Path("tmm/output/yue-Hant_ocr/fuse.srt"), Language.yue_hant),
    ],
)
def test_get_series_language_fixture(relative_path: Path, expected: Language):
    """Detect language of monolingual subtitle fixtures.

    Arguments:
        relative_path: subtitle fixture path relative to the test data root
        expected: expected language from the fixture path
    """
    series = Series.load(test_data_root / relative_path)

    assert get_series_language(series) is expected
