#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""File-related functions for testing."""
from __future__ import annotations

from os import getenv
from pathlib import Path

if getenv("PACKAGE_ROOT"):
    package_root = Path(str(getenv("PACKAGE_ROOT")))
else:
    from scinoephile.common import package_root


def get_test_file_path(relative_path: str) -> Path:
    """Get full path of infile within test data directory.

    Arguments:
        relative_path: relative path to infile within test/data/
    Returns:
        Full path to infile
    """
    full_path = package_root.parent / "test" / "data" / Path(relative_path)
    if not full_path.exists():
        raise FileNotFoundError()

    return full_path
