#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from scinoephile.audio.cantonese.shifting import ShiftTestCase

shift_test_cases_block_0 = []  # shift_test_cases_block_0

mnt_shift_test_cases: list[ShiftTestCase] = sum(
    [
        test_case
        for name, test_case in globals().items()
        if name.startswith("shift_test_cases_block_") and test_case
    ]
)
"""MNT 粤文 shifting test cases."""

__all__ = [
    "mnt_shift_test_cases",
]
