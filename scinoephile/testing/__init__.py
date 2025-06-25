#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scinoephile general testing package."""

from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.testing.sync_test_case import SyncTestCase

test_data_root = package_root.parent / "test" / "data"

__all__ = [
    "SyncTestCase",
    "test_data_root",
]
