#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common exception types."""

from __future__ import annotations

from scinoephile.common.exceptions import (
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
from test.helpers import parametrize


@parametrize(
    ("exception_cls", "base_cls"),
    [
        (ArgumentConflictError, Exception),
        (DirectoryExistsError, OSError),
        (DirectoryNotFoundError, OSError),
        (ExecutableNotFoundError, OSError),
        (GetterError, TypeError),
        (IsAFileError, OSError),
        (NotAFileError, OSError),
        (NotAFileOrDirectoryError, OSError),
        (UnsupportedPlatformError, OSError),
    ],
)
def test_exception_inheritance(
    exception_cls: type[Exception],
    base_cls: type[Exception],
):
    """Test custom exception inheritance.

    Arguments:
        exception_cls: custom exception class
        base_cls: expected base exception class
    """
    assert issubclass(exception_cls, base_cls)
