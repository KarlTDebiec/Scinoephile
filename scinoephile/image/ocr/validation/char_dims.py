#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to character dimensions."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from scinoephile.image.bbox import Bbox

from .csv import save_csv_rows

__all__ = [
    "CHAR_DIM_TOLERANCE",
    "char_dims_match_approved",
    "char_dims_within_tolerance",
    "get_dims_tuple",
    "load_char_dims",
    "save_char_dims",
]


logger = getLogger(__name__)

CHAR_DIM_TOLERANCE = 2
"""Maximum pixel difference allowed for each box dimension and gap."""


def char_dims_match_approved(
    dims: tuple[int, ...], approved_dims: Iterable[tuple[int, ...]]
) -> bool:
    """Match each box and internal gap to the same position in an approved example.

    Arguments:
        dims: proposed widths, heights, and gaps in box order
        approved_dims: previously approved measurements for the character
    Returns:
        whether every box and gap has a match within tolerance
    """
    examples = [example for example in approved_dims if len(example) == len(dims)]
    if not examples:
        return False
    for start in range(0, len(dims), 3):
        gap_index = start + 2
        box = dims[start:gap_index]
        if not any(
            char_dims_within_tolerance(box, example[start:gap_index])
            for example in examples
        ):
            return False
        if gap_index < len(dims) and not any(
            abs(dims[gap_index] - example[gap_index]) <= CHAR_DIM_TOLERANCE
            for example in examples
        ):
            return False
    return True


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
