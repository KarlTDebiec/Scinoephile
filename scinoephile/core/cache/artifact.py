#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache artifact filesystem operations."""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree

__all__ = ["remove_cache_artifact"]


def remove_cache_artifact(artifact_path: Path) -> bool:
    """Remove a cache artifact without following directory symbolic links.

    Arguments:
        artifact_path: cache file, directory, or symbolic link to remove
    Returns:
        whether an artifact was removed
    """
    try:
        if artifact_path.is_dir() and not artifact_path.is_symlink():
            rmtree(artifact_path)
        else:
            artifact_path.unlink()
    except FileNotFoundError:
        return False
    return True
