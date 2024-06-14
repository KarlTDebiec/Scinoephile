#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scinoephile general testing package."""
from __future__ import annotations

from scinoephile.testing.file import get_test_file_path
from scinoephile.testing.fixture import parametrized_fixture

__all__ = [
    "get_test_file_path",
    "parametrized_fixture",
]
