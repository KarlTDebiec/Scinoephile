#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.romanization.is_accented_pinyin."""

from __future__ import annotations

from scinoephile.lang.cmn.romanization import is_accented_pinyin


def test_is_accented_pinyin_true():
    """Detect accented pinyin tokens."""
    assert is_accented_pinyin("nǐ hǎo") is True
    assert is_accented_pinyin("lüè") is True


def test_is_accented_pinyin_false():
    """Reject numbered or plain Latin tokens."""
    assert is_accented_pinyin("ni3 hao3") is False
    assert is_accented_pinyin("ni hao") is False
    assert is_accented_pinyin("") is False
