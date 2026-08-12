#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generic cache namespace declaration."""

from __future__ import annotations

from enum import StrEnum
from ntpath import isreserved
from pathlib import Path, PurePosixPath, PureWindowsPath

from scinoephile.common.validation import val_output_dir_path

__all__ = ["CacheNamespace"]

_OPERATION_PLACEHOLDER = "<operation>"
"""Placeholder for a validated operation-specific namespace segment."""


class CacheNamespace(StrEnum):
    """Base class for owner-defined cache namespace enums."""

    def discover_names(self, cache_root_path: Path) -> list[str]:
        """Discover existing namespaces represented by this declaration.

        Arguments:
            cache_root_path: cache root directory path
        Returns:
            sorted portable namespace names
        """
        template_path = _get_namespace_template_path(self.value)
        if template_path.name != _OPERATION_PLACEHOLDER:
            if _is_discoverable_dir_path(cache_root_path, template_path):
                return [self.value]
            return []

        parent_dir_path = cache_root_path.joinpath(*template_path.parent.parts)
        if not _is_discoverable_dir_path(cache_root_path, template_path.parent):
            return []
        return sorted(
            (template_path.parent / child_path.name).as_posix()
            for child_path in parent_dir_path.iterdir()
            if child_path.is_dir()
            and not child_path.is_symlink()
            and _is_portable_child_name(child_path.name)
        )

    def get_dir_path(
        self, cache_root_path: Path, *, operation: str | None = None
    ) -> Path:
        """Get or create this namespace's directory beneath a cache root.

        Arguments:
            cache_root_path: cache root directory path
            operation: operation name required by parameterized namespaces
        Returns:
            validated cache namespace directory path
        Raises:
            NotADirectoryError: if the namespace path is not a directory
            ValueError: if an existing namespace ancestor is a symbolic link
        """
        namespace_path = PurePosixPath(self.get_name(operation=operation))
        namespace_dir_path = cache_root_path
        for part in namespace_path.parts:
            namespace_dir_path /= part
            if namespace_dir_path.is_symlink():
                raise ValueError(
                    f"Cache namespace {self.name} traverses symbolic link "
                    f"{namespace_dir_path}"
                )
        return val_output_dir_path(namespace_dir_path)

    def get_name(self, *, operation: str | None = None) -> str:
        """Get this namespace's portable name.

        Arguments:
            operation: operation name required by parameterized namespaces
        Returns:
            portable namespace name
        Raises:
            ValueError: if operation usage is invalid
        """
        template_path = _get_namespace_template_path(self.value)
        if template_path.name == _OPERATION_PLACEHOLDER:
            if operation is None:
                raise ValueError(f"Cache namespace {self.name} requires an operation")
            if not _is_portable_child_name(operation):
                raise ValueError(
                    f"Operation must be a single contained filename: {operation!r}"
                )
            return (template_path.parent / operation).as_posix()
        if operation is not None:
            raise ValueError(
                f"Cache namespace {self.name} does not accept an operation"
            )
        return self.value


def _get_namespace_template_path(value: str) -> PurePosixPath:
    """Validate and parse a portable cache namespace template.

    Arguments:
        value: namespace template value
    Returns:
        validated portable namespace template path
    Raises:
        ValueError: if the value is not a portable relative path
    """
    template_path = PurePosixPath(value)
    invalid_placeholder = (
        _OPERATION_PLACEHOLDER in value and template_path.name != _OPERATION_PLACEHOLDER
    )
    duplicate_placeholder = template_path.parts.count(_OPERATION_PLACEHOLDER) > 1
    if (
        not template_path.parts
        or template_path.is_absolute()
        or template_path.as_posix() != value
        or invalid_placeholder
        or duplicate_placeholder
        or any(
            part != _OPERATION_PLACEHOLDER and not _is_portable_child_name(part)
            for part in template_path.parts
        )
    ):
        raise ValueError(
            f"Cache namespace template must be a portable relative path: {value!r}"
        )
    return template_path


def _is_discoverable_dir_path(
    cache_root_path: Path, relative_dir_path: PurePosixPath
) -> bool:
    """Check whether a cache directory exists without traversing symlinks.

    Arguments:
        cache_root_path: cache root directory path
        relative_dir_path: portable directory path relative to the cache root
    Returns:
        whether the directory exists without symlinked namespace ancestors
    """
    dir_path = cache_root_path
    if not dir_path.is_dir():
        return False
    for part in relative_dir_path.parts:
        dir_path /= part
        if dir_path.is_symlink() or not dir_path.is_dir():
            return False
    return True


def _is_portable_child_name(name: str) -> bool:
    """Check whether a name is one portable contained path segment.

    Arguments:
        name: proposed child name
    Returns:
        whether the name is a portable contained path segment
    """
    posix_path = PurePosixPath(name)
    windows_path = PureWindowsPath(name)
    return bool(
        name
        and name not in {".", ".."}
        and ":" not in name
        and not isreserved(name)
        and posix_path.name == name
        and windows_path.name == name
    )
