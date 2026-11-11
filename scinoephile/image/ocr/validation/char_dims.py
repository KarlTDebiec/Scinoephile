#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to character dimensions."""

from __future__ import annotations

import csv
from logging import getLogger
from pathlib import Path

from scinoephile.image.bbox import Bbox

from .csv import save_csv_rows

__all__ = [
    "CHAR_DIM_TOLERANCE",
    "char_dims_within_tolerance",
    "get_dims_tuple",
    "load_char_dims",
    "save_char_dims",
]


logger = getLogger(__name__)

CHAR_DIM_TOLERANCE = 2
"""Maximum pixel difference allowed for each box dimension and gap."""


def char_dims_within_tolerance(
    dims: tuple[int, ...], known_dims: tuple[int, ...]
) -> bool:
    """Compare all selected dimensions or gaps with their stored values.

    Arguments:
        dims: proposed measurements
        known_dims: corresponding measurements from one stored configuration
    Returns:
        whether every corresponding measurement is within tolerance
    """
    return len(dims) == len(known_dims) and all(
        abs(proposed - known) <= CHAR_DIM_TOLERANCE
        for proposed, known in zip(dims, known_dims, strict=True)
    )


def get_dims_tuple(bboxes: Bbox | list[Bbox]) -> tuple[int, ...]:
    """Get dims tuple from bboxes.

    Arguments:
        bboxes: bbox or list of bboxes
    Returns:
        dims tuple
    """
    if isinstance(bboxes, Bbox):
        return (bboxes.width, bboxes.height)
    if len(bboxes) == 1:
        return (bboxes[0].width, bboxes[0].height)
    widths = [bbox.width for bbox in bboxes]
    heights = [bbox.height for bbox in bboxes]
    gaps = [bboxes[i + 1].x1 - bboxes[i].x2 for i in range(len(bboxes) - 1)]
    dims = tuple([d for grp in zip(widths, heights, gaps + [0]) for d in grp][:-1])
    return dims


def load_char_dims(file_path: Path) -> dict[str, set[tuple[int, ...]]]:
    """Load char dims from file.

    Arguments:
        file_path: path to file
    Returns:
        char dims
    """
    char_dims: dict[str, set[tuple[int, ...]]] = {}
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            char = row[0]
            dims = tuple(map(int, row[1:]))
            dims_set = char_dims.setdefault(char, set())
            dims_set.add(dims)

    logger.info(f"Loaded {file_path}")
    return char_dims


def save_char_dims(char_dims: dict[str, set[tuple[int, ...]]], file_path: Path):
    """Save char dims dict to file.

    Arguments:
        char_dims: char dims to save
        file_path: path to file
    """
    rows = []
    for char, dims_set in char_dims.items():
        rows.extend([[char, *dims] for dims in dims_set])
    rows = sorted({tuple(row) for row in rows})
    save_csv_rows(rows, file_path)
    logger.info(f"Saved {file_path}")
