#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase

review_test_case_block_0 = None  # review_test_case_block_0

mnt_review_test_cases: list[ReviewTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("review_test_case_block_") and test_case is not None
]
"""MNT 粤文 review test cases."""

__all__ = [
    "mnt_review_test_cases",
]
