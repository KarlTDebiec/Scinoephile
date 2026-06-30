#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to character pair gaps."""

from __future__ import annotations

import csv
from logging import getLogger
from pathlib import Path

from scinoephile.core.text import FULL_PUNC, get_char_type

from .csv import save_csv_rows

__all__ = [
    "get_default_char_pair_cutoffs",
    "get_expected_space",
    "get_expected_tab",
    "load_char_pair_gaps",
    "save_char_pair_gaps",
]


logger = getLogger(__name__)


def get_default_char_pair_cutoffs(  # noqa: PLR0911, PLR0912
    char_1: str, char_2: str
) -> tuple[int, int, int, int]:
    """Get default cutoff tuple for a character pair.

    Arguments:
        char_1: first character
        char_2: second character
    Returns:
        default cutoff tuple
    """
    char_1_type = get_char_type(char_1)
    char_2_type = get_char_type(char_2)

    if char_1_type == "full" and char_2_type == "full":
        return 22, 89, 90, 200
    if char_1_type == "full":
        if char_2 in {"〞"}:
            return 18, 89, 90, 200
        if char_2 in {"⋯"}:
            return 22, 89, 90, 200
        if char_2 in {"」", "』"}:
            return 24, 89, 90, 200
        if char_2 in {"？"}:
            return 40, 89, 90, 200
        if char_2 in {"、", "！", "，", "．", "：", "；", "。"}:
            return 47, 89, 90, 200
        if char_2 in {"「", "『"}:
            return 61, 89, 90, 200
        return 8, 89, 90, 200
    if char_2_type == "full":
        if char_1 in {"〝"}:
            return 18, 89, 90, 200
        if char_1 in {"⋯"}:
            return 22, 89, 90, 200
        if char_1 in {"「", "『"}:
            return 24, 89, 90, 200
        if char_1 in {"？"}:
            return 40, 89, 90, 200
        if char_1 in {"、", "！", "，", "．", "：", "；", "。"}:
            return 47, 89, 90, 200
        if char_1 in {"」", "』"}:
            return 61, 89, 90, 200
        return 8, 89, 90, 200
    if char_1_type == "punc" or char_2_type == "punc":
        return 8, 89, 90, 200
    return 8, 24, 90, 200


def get_expected_space(char_1: str, char_2: str) -> str:
    """Get space string between two characters.

    Arguments:
        char_1: first character
        char_2: second character
    Returns:
        space string
    """
    char_1_type = get_char_type(char_1)
    char_2_type = get_char_type(char_2)

    if char_1_type == "full" and char_2_type == "full":
        return "　"
    if char_1_type == "full" and char_2 in FULL_PUNC.values():
        return "　"
    if char_1 in FULL_PUNC.values() and char_2_type == "full":
        return "　"
    return " "


def get_expected_tab(char_1: str, char_2: str) -> str:
    """Get tab string between two characters.

    Arguments:
        char_1: first character
        char_2: second character
    Returns:
        tab string
    """
    char_1_type = get_char_type(char_1)
    char_2_type = get_char_type(char_2)

    if char_1_type == "full" and char_2_type == "full":
        return "　　"
    if char_1_type == "full" and char_2 in FULL_PUNC.values():
        return "　　"
    if char_1 in FULL_PUNC.values() and char_2_type == "full":
        return "　　"
    return "    "


def load_char_pair_gaps(
    file_path: Path,
) -> dict[tuple[str, str], tuple[int, int, int, int]]:
    """Load char pair gaps from file.

    Arguments:
        file_path: path to file
    Returns:
        char pair gaps
    """
    char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for line_no, row in enumerate(reader, start=1):
            if not row:
                continue
            char_1, char_2, cutoff_1, cutoff_2, cutoff_3, cutoff_4 = row
            char_pair = (char_1, char_2)
            cutoffs = (
                int(cutoff_1),
                int(cutoff_2),
                int(cutoff_3),
                int(cutoff_4),
            )
            _validate_char_pair_gap_cutoffs(
                char_pair, cutoffs, file_path=file_path, line_no=line_no
            )
            char_pair_gaps[char_pair] = cutoffs
    return char_pair_gaps


def save_char_pair_gaps(
    char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]], file_path: Path
):
    """Save char pair gaps to file.

    Arguments:
        char_pair_gaps: char pair gaps to save
        file_path: path to file
    """
    rows: list[tuple[str, str, int, int, int, int]] = []
    for (char_1, char_2), cutoffs in char_pair_gaps.items():
        char_pair = (char_1, char_2)
        _validate_char_pair_gap_cutoffs(char_pair, cutoffs, file_path=file_path)
        if cutoffs == get_default_char_pair_cutoffs(char_1, char_2):
            continue
        cutoff_1, cutoff_2, cutoff_3, cutoff_4 = cutoffs
        rows.append((char_1, char_2, cutoff_1, cutoff_2, cutoff_3, cutoff_4))
    rows = sorted({tuple(row) for row in rows})
    save_csv_rows(rows, file_path)
    logger.info(f"Saved {file_path}.")


def _validate_char_pair_gap_cutoffs(
    char_pair: tuple[str, str],
    cutoffs: tuple[int, int, int, int],
    *,
    file_path: Path | None = None,
    line_no: int | None = None,
):
    """Validate that character pair gap cutoffs are ordered.

    Arguments:
        char_pair: character pair
        cutoffs: gap cutoffs
        file_path: optional source or destination file path
        line_no: optional source line number
    Raises:
        ValueError: if cutoffs are not monotonic
    """
    if cutoffs[0] <= cutoffs[1] <= cutoffs[2] <= cutoffs[3]:
        return

    location = ""
    if file_path is not None:
        location = f" in {file_path}"
        if line_no is not None:
            location = f"{location}:{line_no}"
    raise ValueError(
        f"Character pair gap cutoffs must be monotonic for {char_pair!r}"
        f"{location}: {cutoffs!r}"
    )
