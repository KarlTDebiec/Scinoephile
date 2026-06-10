#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of core language tag handling."""

from __future__ import annotations

import pytest

from scinoephile.core import Language
from scinoephile.core.language import is_chinese_language_tag, normalize_language_tag


def test_language_enum_exposes_english_metadata():
    """Test English language enum metadata."""
    assert Language.eng.tag == "eng"
    assert Language.eng.script is None
    assert not Language.eng.is_chinese
    assert str(Language.eng) == "eng"


def test_language_enum_exposes_simplified_chinese_metadata():
    """Test simplified Chinese language enum metadata."""
    assert Language.zho_hans.tag == "zho-Hans"
    assert Language.zho_hans.script == "simplified"
    assert Language.zho_hans.is_chinese


def test_language_enum_exposes_traditional_chinese_metadata():
    """Test traditional Chinese language enum metadata."""
    assert Language.zho_hant.tag == "zho-Hant"
    assert Language.zho_hant.script == "traditional"
    assert Language.zho_hant.is_chinese


def test_language_enum_parses_tags():
    """Test language enum parses exact supported tags."""
    assert Language("eng") is Language.eng
    assert Language("zho-Hans") is Language.zho_hans
    assert Language("zho-Hant") is Language.zho_hant


def test_language_rejects_unsupported_tag():
    """Test unsupported language tags are rejected."""
    with pytest.raises(ValueError, match="is not a valid Language"):
        Language("")


def test_is_chinese_language_tag_detects_chinese_tags():
    """Test Chinese language tag detection."""
    assert is_chinese_language_tag(Language.zho_hans)
    assert is_chinese_language_tag(Language.zho_hant)
    assert is_chinese_language_tag("chi")
    assert is_chinese_language_tag("zho")
    assert is_chinese_language_tag("zho-Hant")
    assert is_chinese_language_tag("yue")
    assert not is_chinese_language_tag(Language.eng)
    assert not is_chinese_language_tag(None)
    assert not is_chinese_language_tag("eng")


def test_normalize_language_tag_normalizes_loose_tags():
    """Test loose language tag normalization."""
    assert normalize_language_tag("ZHO-hant") == "zho-Hant"
    assert normalize_language_tag("ENG-US") == "eng-US"
    assert normalize_language_tag("zho-unknown") == "zho-Unknown"
