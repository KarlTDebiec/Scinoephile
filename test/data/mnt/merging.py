#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from scinoephile.audio.cantonese.merging import MergeTestCase

merge_test_cases_block_0 = []  # merge_test_cases_block_0

mnt_merge_test_cases: list[MergeTestCase] = sum(
    [
        test_case
        for name, test_case in globals().items()
        if name.startswith("merge_test_cases_block_") and test_case
    ]
)
"""MNT 粤文 merging test cases."""

__all__ = [
    "mnt_merge_test_cases",
]
