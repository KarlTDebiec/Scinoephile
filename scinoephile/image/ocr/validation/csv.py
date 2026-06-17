#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CSV persistence helpers for OCR validation data."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from time import sleep

__all__ = ["save_csv_rows"]


_REPLACE_ATTEMPTS = 10
_REPLACE_DELAY_SECONDS = 0.05
_save_lock = RLock()


def save_csv_rows(rows: Iterable[Iterable[object]], file_path: Path):
    """Atomically save CSV rows to a file.

    Arguments:
        rows: rows to save
        file_path: path to file
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    with _save_lock:
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                dir=file_path.parent,
                prefix=f".{file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                tmp_path = Path(handle.name)
                writer = csv.writer(handle)
                writer.writerows(rows)
            _replace_with_retry(tmp_path, file_path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def _replace_with_retry(source_path: Path, target_path: Path):
    """Replace target path, retrying transient permission failures.

    Arguments:
        source_path: temporary source path
        target_path: target path to replace
    """
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            source_path.replace(target_path)
            return
        except PermissionError:
            if attempt == _REPLACE_ATTEMPTS - 1:
                raise
            sleep(_REPLACE_DELAY_SECONDS * (attempt + 1))
