#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared test cases for Cantonese romanization detection helpers."""

from __future__ import annotations

RomanizationCase = tuple[str, bool, bool]
"""(text, is_accented_yale_expected, is_numbered_jyutping_expected)."""

ROMANIZATION_CASES: list[RomanizationCase] = [
    ("néih hóu", True, False),
    ("gwóngdūngwá", True, False),
    ("nei5 hou2", False, True),
    ("gwong2 dung1 waa2", False, True),
    ("", False, False),
]
