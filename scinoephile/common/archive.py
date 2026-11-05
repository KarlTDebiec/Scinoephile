#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validation of portable ZIP archive member paths."""

from __future__ import annotations

from ntpath import isreserved
from pathlib import PurePosixPath

__all__ = ["ZipMemberPaths"]


class ZipMemberPaths:
    """Track relative member paths without traversal or filesystem collisions.

    Names use forward slashes. Redundant separators and `.` components are
    normalized. Windows reserved names, backslashes, parent traversal, duplicate
    names ignoring case, and conflicts between files and directories are rejected
    on every platform.
    """

    def __init__(self):
        """Initialize an empty collection of file and implied directory names."""
        self._file_names: set[str] = set()
        self._directory_names: set[str] = set()

    def add(self, member_name: str) -> PurePosixPath:
        """Validate and record a file member name.

        Arguments:
            member_name: relative file name within an archive
        Returns:
            normalized member path using forward slashes
        Raises:
            ValueError: if the name is unsafe or conflicts with a previous member
        """
        path = PurePosixPath(member_name)
        if (
            not path.parts
            or path.is_absolute()
            or "\\" in member_name
            or ":" in member_name
            or any(part == ".." or isreserved(part) for part in path.parts)
        ):
            raise ValueError(f"Unsafe ZIP member path: {member_name!r}")

        name = path.as_posix().casefold()
        parent_names = {
            parent.as_posix().casefold() for parent in path.parents if parent.parts
        }
        if (
            name in self._file_names
            or name in self._directory_names
            or parent_names.intersection(self._file_names)
        ):
            raise ValueError(f"Conflicting ZIP member path: {member_name!r}")
        self._file_names.add(name)
        self._directory_names.update(parent_names)
        return path
