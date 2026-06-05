#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of test data OCR processing helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core.subtitles import Series, Subtitle
from test.data.ocr import _romanize


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("yue-Hans", "你好世界\\Nnéih hóu sai gaai"),
        ("yue-Hant", "你好世界\\Nnéih hóu sai gaai"),
        ("zho-Hans", "你好世界\\Nnǐhǎo shìjiè"),
    ],
)
def test_romanize_uses_language_specific_romanization(
    tmp_path: Path, lang: str, expected: str
):
    """Test OCR romanization uses Yale for Yue and pinyin for zho.

    Arguments:
        tmp_path: pytest temporary path
        lang: language tag
        expected: expected romanized subtitle text
    """
    output_path = tmp_path / "romanized.srt"
    series = Series(events=[Subtitle(start=0, end=1000, text="你好世界")])

    output = _romanize(output_path, lang, series, overwrite=True)

    assert output.events[0].text == expected
    assert Series.load(output_path).events[0].text == expected
