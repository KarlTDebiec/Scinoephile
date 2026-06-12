#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for runtime path helpers."""

from __future__ import annotations

from os import environ
from unittest.mock import patch

from scinoephile.core.paths import get_runtime_cache_dir_path


def test_get_runtime_cache_dir_path_handles_missing_home_environment():
    """Test cache path resolution survives intentionally cleared environments."""
    with patch.dict(environ, {}, clear=True):
        cache_dir_path = get_runtime_cache_dir_path(create=False)

    assert cache_dir_path.name == "scinoephile"
