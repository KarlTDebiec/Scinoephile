#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose code not tied to a particular project."""

from __future__ import annotations

from pathlib import Path

from .command_line_interface import CommandLineInterface
from .exception import (
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

package_root = Path(__file__).resolve().parent.parent
"""Absolute path of the package containing this submodule.

If this file is '/path/to/package/common/__init__.py', the value is
'/path/to/package'.
"""

__all__ = [
    "ArgumentConflictError",
    "CommandLineInterface",
    "DirectoryExistsError",
    "DirectoryNotFoundError",
    "ExecutableNotFoundError",
    "GetterError",
    "IsAFileError",
    "NotAFileError",
    "NotAFileOrDirectoryError",
    "UnsupportedPlatformError",
    "package_root",
]
