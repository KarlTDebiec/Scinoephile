#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for dictionary query language detection."""

from __future__ import annotations

import pycantonese
import pytest

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.multilang.cmn_yue.dictionaries.query_detection import (
    DictionaryQueryLanguage,
    detect_dictionary_query_language,
    get_dictionary_lookup_direction,
)


def test_detect_simplified_hanzi():
    """Detect simplified Hanzi queries."""
    assert (
        detect_dictionary_query_language("汉字") == DictionaryQueryLanguage.simplified
    )


def test_detect_traditional_hanzi():
    """Detect traditional Hanzi queries."""
    assert (
        detect_dictionary_query_language("漢字") == DictionaryQueryLanguage.traditional
    )


def test_detect_accented_pinyin():
    """Detect accented Mandarin pinyin queries."""
    assert (
        detect_dictionary_query_language("nǐ hǎo") == DictionaryQueryLanguage.cmn_pinyin
    )


def test_detect_accented_yale():
    """Detect accented Yale queries."""
    yale = " ".join(pycantonese.jyutping_to_yale("nei5hou2"))
    assert detect_dictionary_query_language(yale) == DictionaryQueryLanguage.yue_yale


def test_ambiguous_hanzi_errors():
    """Ambiguous Hanzi without distinctive characters should error."""
    with pytest.raises(ScinoephileError):
        detect_dictionary_query_language("中文")


def test_mixed_query_errors():
    """Mixed Hanzi and romanization should error."""
    with pytest.raises(ScinoephileError):
        detect_dictionary_query_language("漢字 nǐ")


def test_unaccented_pinyin_errors():
    """Unaccented romanization should error."""
    with pytest.raises(ScinoephileError):
        detect_dictionary_query_language("ni3 hao3")


def test_lookup_direction_mapping():
    """Ensure lookup direction mapping for detected languages."""
    assert (
        get_dictionary_lookup_direction(DictionaryQueryLanguage.cmn_pinyin).value
        == "cmn_to_yue"
    )
    assert (
        get_dictionary_lookup_direction(DictionaryQueryLanguage.yue_yale).value
        == "yue_to_cmn"
    )
