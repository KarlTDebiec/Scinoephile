#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase

translate_test_case_block_0: list[TranslateTestCase] = []

t_translate_test_cases: list[TranslateTestCase] = sum(
    (globals()[f"translate_test_case_block_{i}"] for i in range(1)), []
)
"""T 粤文 translation test cases."""

__all__ = ["t_translate_test_cases"]
