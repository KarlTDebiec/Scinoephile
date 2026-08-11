#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generic cache namespace declaration."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path, PurePosixPath

from scinoephile.common.validation import val_child_path

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
        template_path = PurePosixPath(self.value)
        if template_path.name != _OPERATION_PLACEHOLDER:
            namespace_dir_path = self.get_dir_path(cache_root_path)
            if namespace_dir_path.is_dir() and not namespace_dir_path.is_symlink():
                return [self.value]
            return []

        parent_dir_path = cache_root_path.joinpath(*template_path.parent.parts)
        if not parent_dir_path.is_dir() or parent_dir_path.is_symlink():
            return []
        return sorted(
            self.get_name(operation=child_path.name)
            for child_path in parent_dir_path.iterdir()
            if child_path.is_dir() and not child_path.is_symlink()
        )

    def get_dir_path(
        self, cache_root_path: Path, *, operation: str | None = None
    ) -> Path:
        """Get this namespace's directory beneath a cache root.

        Arguments:
            cache_root_path: cache root directory path
            operation: operation name required by parameterized namespaces
        Returns:
            cache namespace directory path
        """
        namespace_path = PurePosixPath(self.get_name(operation=operation))
        return cache_root_path.joinpath(*namespace_path.parts)

    def get_name(self, *, operation: str | None = None) -> str:
        """Get this namespace's portable name.

        Arguments:
            operation: operation name required by parameterized namespaces
        Returns:
            portable namespace name
        Raises:
            ValueError: if operation usage is invalid
        """
        template_path = PurePosixPath(self.value)
        if template_path.name == _OPERATION_PLACEHOLDER:
            if operation is None:
                raise ValueError(f"Cache namespace {self.name} requires an operation")
            validated_operation = val_child_path(Path(), operation).name
            return (template_path.parent / validated_operation).as_posix()
        if operation is not None:
            raise ValueError(
                f"Cache namespace {self.name} does not accept an operation"
            )
        return self.value
