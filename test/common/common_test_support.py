#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Filesystem setup shared by common tests."""

from __future__ import annotations

from errno import ENOSYS, ENOTSUP
from pathlib import Path

from pytest import skip

__all__ = ["create_symlink_or_skip"]


def create_symlink_or_skip(
    symlink_path: Path, target_path: Path, *, target_is_directory: bool = False
):
    """Create a symlink, skipping only when the environment lacks the capability.

    Missing Windows privileges and explicit unsupported-operation errors skip the
    caller. Other filesystem failures propagate so broken test setup remains visible.

    Arguments:
        symlink_path: path at which to create the symlink
        target_path: symlink target path
        target_is_directory: whether the target is a directory
    Raises:
        OSError: if a filesystem operation fails
    """
    try:
        symlink_path.symlink_to(target_path, target_is_directory=target_is_directory)
    except NotImplementedError:
        skip("Symbolic link creation is not implemented on this platform")
    except OSError as exc:
        if getattr(exc, "winerror", None) in {50, 1314} or exc.errno in {
            ENOSYS,
            ENOTSUP,
        }:
            skip(f"Symbolic link creation is unavailable: {exc}")
        raise
