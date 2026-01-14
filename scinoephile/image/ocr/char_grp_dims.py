#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to character group dimensions."""

from __future__ import annotations

import csv
from logging import info
from pathlib import Path

__all__ = [
    "load_char_grp_dims",
    "save_char_grp_dims",
]


def load_char_grp_dims(
    file_path: Path,
) -> dict[int, dict[str, set[tuple[int, ...]]]]:
    """Load character group dimensions from file.

    Arguments:
        file_path: path to file
    Returns:
        character group dimensions keyed by group size
    """
    char_grp_dims: dict[int, dict[str, set[tuple[int, ...]]]] = {}
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            char_grp = row[0]
            dims = tuple(map(int, row[1:]))
            group_size = len(char_grp)
            dims_set = char_grp_dims.setdefault(group_size, {}).setdefault(
                char_grp, set()
            )
            dims_set.add(dims)

    info(f"Loaded {file_path}")
    return char_grp_dims


def save_char_grp_dims(
    char_grp_dims: dict[int, dict[str, set[tuple[int, ...]]]], file_path: Path
):
    """Save character group dimensions dict to file.

    Arguments:
        char_grp_dims: character group dims to save
        file_path: path to file
    """
    rows = []
    for char_grp_dims_set in char_grp_dims.values():
        for char_grp, dims_set in char_grp_dims_set.items():
            rows.extend([[char_grp, *dims] for dims in dims_set])
    rows = sorted({tuple(row) for row in rows})
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    info(f"Saved {file_path}")
