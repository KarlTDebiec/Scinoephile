#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose exceptions."""

from __future__ import annotations


class ArgumentConflictError(Exception):
    """Two or more arguments are in conflict with one another."""


class DirectoryExistsError(OSError):
    """Directory already exists."""


class DirectoryNotFoundError(OSError):
    """Directory not found."""


class ExecutableNotFoundError(OSError):
    """Executable not found."""


class GetterError(TypeError):
    """Error encountered in getter method."""


class IsAFileError(OSError):
    """Is a file."""


class NotAFileError(OSError):
    """Is not a file."""


class NotAFileOrDirectoryError(OSError):
    """Is not a file or directory."""


class UnsupportedPlatformError(OSError):
    """Platform is unsupported."""
