#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose functions for file interaction and manipulation."""

from __future__ import annotations

from contextlib import contextmanager
from logging import getLogger
from os import remove
from pathlib import Path
from shutil import move, rmtree
from tempfile import NamedTemporaryFile, mkdtemp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = [
    "get_temp_directory_path",
    "get_temp_file_path",
    "rename_preexisting_output_path",
]

logger = getLogger(__name__)


@contextmanager
def get_temp_directory_path() -> Generator[Path]:
    """Provide path to a temporary directory and remove it once no longer needed.

    Returns:
        Path to temporary directory
    """
    temp_directory_path = None
    try:
        temp_directory_path = Path(mkdtemp()).resolve()
        yield temp_directory_path
    finally:
        if temp_directory_path:
            rmtree(temp_directory_path)


@contextmanager
def get_temp_file_path(suffix: str | None = None) -> Generator[Path]:
    """Provide path to a temporary file and remove it once no longer needed.

    Arguments:
        suffix: Suffix of named temporary file
    Returns:
        Path to temporary file
    """
    temp_file_path = None
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        temp_file_path = Path(temp_file.name)
        remove(temp_file_path)
        yield temp_file_path
    finally:
        if temp_file_path and temp_file_path.exists():
            try:
                remove(temp_file_path)
            except PermissionError as exc:
                logger.debug(
                    f"temp_file_path encountered PermissionException '{exc}'; "
                    f"temporary file {temp_file_path}, will not be removed."
                )


def rename_preexisting_output_path(output_path: Path):
    """Check if a proposed output file exists, and if so rename the existing file.

    Arguments:
        output_path: Path to proposed output file
    """
    output_path = output_path.resolve()
    if output_path.exists():
        backup_i = 0
        while True:
            backup_path = output_path.with_stem(f"{output_path.stem}_{backup_i:03d}")
            if not backup_path.exists():
                logger.info(f"Moving pre-existing file {output_path} to {backup_path}")
                move(output_path, backup_path)
                break
            backup_i += 1
