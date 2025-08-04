#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase

review_test_case_block_0: list[ReviewTestCase] = []

mnt_review_test_cases: list[ReviewTestCase] = sum(
    (globals()[f"review_test_case_block_{i}"] for i in range(1)), []
)
"""MNT 粤文 review test cases."""

__all__ = ["mnt_review_test_cases"]
