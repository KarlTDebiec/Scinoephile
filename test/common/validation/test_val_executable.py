#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_executable."""

from __future__ import annotations

from pathlib import Path
from platform import system

import pytest
from common.exception import (  # ty:ignore[unresolved-import]
    ExecutableNotFoundError,
    UnsupportedPlatformError,
)
from common.validation import val_executable  # ty:ignore[unresolved-import]


def test_val_executable_valid():
    """Test validation of valid executable."""
    # Python should be available on all platforms
    result = val_executable("python3")
    assert isinstance(result, Path)
    assert result.exists()


def test_val_executable_not_found():
    """Test validation of non-existent executable."""
    with pytest.raises(ExecutableNotFoundError):
        val_executable("nonexistent_executable_12345")


def test_val_executable_unsupported_platform():
    """Test validation with unsupported platform."""
    current_platform = system()
    # Create a list of other platforms
    all_platforms = {"Darwin", "Linux", "Windows"}
    other_platforms = all_platforms - {current_platform}

    with pytest.raises(UnsupportedPlatformError):
        val_executable("python3", supported_platforms=other_platforms)


def test_val_executable_supported_platform():
    """Test validation with explicitly supported platform."""
    current_platform = system()
    result = val_executable("python3", supported_platforms={current_platform})
    assert isinstance(result, Path)
    assert result.exists()


def test_val_executable_returns_absolute_path():
    """Test that returned path is absolute."""
    result = val_executable("python3")
    assert result.is_absolute()
