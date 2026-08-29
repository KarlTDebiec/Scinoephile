#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for runtime path helpers."""

from __future__ import annotations

from os import environ
from pathlib import Path
from unittest.mock import patch

from scinoephile.core.paths import (
    get_runtime_cache_root_path,
    get_runtime_data_root_path,
)


def test_get_runtime_cache_root_path_uses_configured_path(tmp_path: Path):
    """Test configured cache path is used as the exact cache root.

    Arguments:
        tmp_path: temporary directory path
    """
    with patch.dict(environ, {"SCINOEPHILE_CACHE_DIR": str(tmp_path)}):
        cache_root_path = get_runtime_cache_root_path(create=False)

    assert cache_root_path == tmp_path


def test_get_runtime_cache_root_path_handles_windows_missing_home_environment():
    """Test Windows cache path resolution survives cleared environments."""
    with patch("scinoephile.core.paths.system", return_value="Windows"):
        with patch.dict(environ, {}, clear=True):
            cache_root_path = get_runtime_cache_root_path(create=False)

    assert cache_root_path.name == "scinoephile"


def test_get_runtime_data_root_path_uses_configured_path(tmp_path: Path):
    """Test configured data path is used as the exact data root.

    Arguments:
        tmp_path: temporary directory path
    """
    with patch.dict(environ, {"SCINOEPHILE_DATA_DIR": str(tmp_path)}):
        data_root_path = get_runtime_data_root_path(create=False)

    assert data_root_path == tmp_path


def test_get_runtime_data_root_path_handles_windows_missing_home_environment():
    """Test Windows data path resolution survives cleared environments."""
    with patch("scinoephile.core.paths.system", return_value="Windows"):
        with patch.dict(environ, {}, clear=True):
            data_root_path = get_runtime_data_root_path(create=False)

    assert data_root_path.name == "scinoephile"
