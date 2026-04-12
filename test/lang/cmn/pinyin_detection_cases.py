#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared test cases for pinyin detection helpers."""

from __future__ import annotations

PinyinCase = tuple[str, bool, bool]
"""(text, is_accented_pinyin_expected, is_numbered_pinyin_expected)."""

PINYIN_CASES: list[PinyinCase] = [
    ("nǐ hǎo", True, False),
    ("lüè", True, False),
    ("ni3 hao3", False, True),
    ("lu:e4", False, True),
    ("lv4", False, True),
    ("ni hao", False, False),
    ("", False, False),
]
