#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media language tag helpers."""

from __future__ import annotations

from scinoephile.core.media.language import is_chinese


def test_is_chinese():
    """Test Chinese language tag detection."""
    assert is_chinese("chi")
    assert is_chinese("zho")
    assert is_chinese("zho-Hant")
    assert is_chinese("yue")
    assert not is_chinese(None)
    assert not is_chinese("eng")
