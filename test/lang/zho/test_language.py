#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese language tag helpers."""

from __future__ import annotations

from scinoephile.lang.zho.language import get_zho_script_language, is_zho_language


def test_get_zho_script_language():
    """Test Chinese script language tag generation."""
    assert get_zho_script_language("zho", "zho-Hant") == "zho-Hant"
    assert get_zho_script_language("yue", None) == "yue-Unknown"


def test_is_zho_language():
    """Test Chinese language tag detection."""
    assert is_zho_language("chi")
    assert is_zho_language("zho")
    assert is_zho_language("zho-Hant")
    assert is_zho_language("yue")
    assert not is_zho_language(None)
    assert not is_zho_language("eng")
