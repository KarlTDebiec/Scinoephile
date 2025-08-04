#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from scinoephile.audio.cantonese.distribution import DistributeTestCase

distribute_test_cases_block_0: list[DistributeTestCase] = []

mnt_distribute_test_cases: list[DistributeTestCase] = sum(
    (globals()[f"distribute_test_cases_block_{i}"] for i in range(1)), []
)
"""MNT 粤文 distribute test cases."""

__all__ = ["mnt_distribute_test_cases"]
