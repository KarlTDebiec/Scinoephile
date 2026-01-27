#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.exception."""

from __future__ import annotations

import pytest
from common.exception import (  # ty:ignore[unresolved-import]
    ArgumentConflictError,
    DirectoryExistsError,
    DirectoryNotFoundError,
    ExecutableNotFoundError,
    GetterError,
    IsAFileError,
    NotAFileError,
    NotAFileOrDirectoryError,
    UnsupportedPlatformError,
)


def test_argument_conflict_error():
    """Test ArgumentConflictError can be raised and caught."""
    with pytest.raises(ArgumentConflictError, match="test message"):
        raise ArgumentConflictError("test message")


def test_directory_exists_error():
    """Test DirectoryExistsError can be raised and caught."""
    with pytest.raises(DirectoryExistsError, match="test message"):
        raise DirectoryExistsError("test message")


def test_directory_not_found_error():
    """Test DirectoryNotFoundError can be raised and caught."""
    with pytest.raises(DirectoryNotFoundError, match="test message"):
        raise DirectoryNotFoundError("test message")


def test_executable_not_found_error():
    """Test ExecutableNotFoundError can be raised and caught."""
    with pytest.raises(ExecutableNotFoundError, match="test message"):
        raise ExecutableNotFoundError("test message")


def test_getter_error():
    """Test GetterError can be raised and caught."""
    with pytest.raises(GetterError, match="test message"):
        raise GetterError("test message")


def test_is_a_file_error():
    """Test IsAFileError can be raised and caught."""
    with pytest.raises(IsAFileError, match="test message"):
        raise IsAFileError("test message")


def test_not_a_file_error():
    """Test NotAFileError can be raised and caught."""
    with pytest.raises(NotAFileError, match="test message"):
        raise NotAFileError("test message")


def test_not_a_file_or_directory_error():
    """Test NotAFileOrDirectoryError can be raised and caught."""
    with pytest.raises(NotAFileOrDirectoryError, match="test message"):
        raise NotAFileOrDirectoryError("test message")


def test_unsupported_platform_error():
    """Test UnsupportedPlatformError can be raised and caught."""
    with pytest.raises(UnsupportedPlatformError, match="test message"):
        raise UnsupportedPlatformError("test message")


def test_exception_inheritance():
    """Test that custom exceptions inherit from correct base classes."""
    assert issubclass(ArgumentConflictError, Exception)
    assert issubclass(DirectoryExistsError, OSError)
    assert issubclass(DirectoryNotFoundError, OSError)
    assert issubclass(ExecutableNotFoundError, OSError)
    assert issubclass(GetterError, TypeError)
    assert issubclass(IsAFileError, OSError)
    assert issubclass(NotAFileError, OSError)
    assert issubclass(NotAFileOrDirectoryError, OSError)
    assert issubclass(UnsupportedPlatformError, OSError)
