#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to character pair gaps."""

from __future__ import annotations

import csv
from logging import getLogger
from pathlib import Path

from scinoephile.core.text import full_punc, get_char_type

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
    if char_1_type == "full" and char_2 in full_punc.values():
        return "　"
    if char_1 in full_punc.values() and char_2_type == "full":
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
    if char_1_type == "full" and char_2 in full_punc.values():
        return "　　"
    if char_1 in full_punc.values() and char_2_type == "full":
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
        for row in reader:
            if not row:
                continue
            char_1, char_2, cutoff_1, cutoff_2, cutoff_3, cutoff_4 = row
            char_pair_gaps[(char_1, char_2)] = (
                int(cutoff_1),
                int(cutoff_2),
                int(cutoff_3),
                int(cutoff_4),
            )
    return char_pair_gaps


def save_char_pair_gaps(
    char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]], file_path: Path
):
    """Save char pair gaps to file.

    Arguments:
        char_pair_gaps: char pair gaps to save
        file_path: path to file
    """
    rows = [
        (char_1, char_2, cutoff_1, cutoff_2, cutoff_3, cutoff_4)
        for (char_1, char_2), (
            cutoff_1,
            cutoff_2,
            cutoff_3,
            cutoff_4,
        ) in char_pair_gaps.items()
    ]
    rows = sorted({tuple(row) for row in rows})
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    logger.info(f"Saved {file_path}.")
