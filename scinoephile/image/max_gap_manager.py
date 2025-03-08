#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages maximum gaps between characters of different types."""
from __future__ import annotations

from logging import info

import numpy as np
import unicodedata

from scinoephile.common import package_root
from scinoephile.core import ScinoephileException
from scinoephile.core.text import full_punc_dict, half_punc_dict


class MaxGapManager:
    """Manages maximum gaps between characters of different types."""

    file_paths = {}
    """Paths to files containing max gaps for each character type pair."""
    max_gaps = {}
    """Max gaps for each character type pair."""

    def __init__(self):
        """Initialize."""
        types = ("full", "half", "punc")
        for type_1 in types:
            for type_2 in types:
                self.file_paths[type_1, type_2] = (
                    package_root / "data" / "ocr" / f"max_gaps_{type_1}_{type_2}.csv"
                )
        for (type_1, type_2), max_gaps_file in self.file_paths.items():
            if max_gaps_file.exists():
                self.max_gaps[type_1, type_2] = np.loadtxt(
                    max_gaps_file, delimiter=",", dtype=int
                )
                info(f"Loaded {max_gaps_file}.")
            else:
                self.max_gaps[type_1, type_2] = np.zeros((8, 8), dtype=int)
                self._save_max_gaps(type_1, type_2)

    def validate_gap(
        self,
        char_1: str,
        char_2: str,
        char_1_width: int,
        char_2_width: int,
        gap: int,
        whitespace: str,
    ) -> str:
        """Validate gap between two characters.

        Arguments:
            char_1: First character
            char_2: Second character
            char_1_width: Width of first character in pixels
            char_2_width: Width of second character in pixels
            gap: Gap between characters in pixels
            whitespace: Whitespace between characters
        """
        type_1 = self.get_char_type(char_1)
        type_2 = self.get_char_type(char_2)

        # Get max gap
        max_gap_was_interpolated = False
        max_gap = self._get_max_gap(type_1, type_2, char_1_width, char_2_width)
        if max_gap == 0:
            max_gap = self._get_max_gap_interpolated(
                type_1, type_2, char_1_width, char_2_width
            )
            max_gap_was_interpolated = True

        # Validate gap
        gap_fit_for_adj_chars = gap <= max_gap

        # Validate whitespace
        whitespace_fit_for_adj_chars = len(whitespace) == 0

        message = None
        if gap_fit_for_adj_chars:
            if whitespace_fit_for_adj_chars:
                if max_gap_was_interpolated:
                    self._update_max_gaps(
                        type_1, type_2, char_1_width, char_2_width, gap
                    )
                    message = (
                        f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                        f"(<{max_gap:2d}), and appear to be adjacent, "
                        f"and are within interpolated max gap, added "
                        f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                        f"to max_gaps[{type_1},{type_2}]."
                    )
            else:
                message = (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(<={max_gap:2d}), and appear to be adjacent, "
                    f"but are separated by whitespace '{whitespace}'."
                )
        else:
            if whitespace_fit_for_adj_chars:
                if gap <= 20:
                    self._update_max_gaps(
                        type_1, type_2, char_1_width, char_2_width, gap
                    )
                    message = (
                        f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                        f"(>{max_gap:2d}), but are within 20 pixels of each other, "
                        f"added ({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                        f"to max_gaps[{type_1},{type_2}]."
                    )
                else:
                    response = input(
                        f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                        f"(>{max_gap:2d}). Do you want to update the max gaps? (y/n): "
                    )
                    if response.lower().startswith("y"):
                        self._update_max_gaps(
                            type_1, type_2, char_1_width, char_2_width, gap
                        )
                        message = (
                            f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; added "
                            f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                            f"to max_gaps[{type_1},{type_2}]."
                        )
                    else:
                        message = (
                            f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; did not add "
                            f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                            f"to max_gaps[{type_1},{type_2}]."
                        )
            else:
                message = (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(>{max_gap:2d}), and appear to have whitespace between them, "
                    f"and as expected are separated by whitespace '{whitespace}'."
                )
        return message

    def _expand_max_gaps(
        self, type_1: str, type_2: str, width_1: int, width_2: int
    ) -> None:
        """Expand max_gaps to fit new width(s) and resave.

        Arguments:
            type_1: First character type
            type_2: Second character type
            width_1: Width of first character in pixels
            width_2: Width of second character in pixels
        """
        max_gaps = self.max_gaps[type_1, type_2]
        current_width = max_gaps.shape[0]
        current_height = max_gaps.shape[1]
        needed_width = max(width_1 + 1, current_width)
        needed_height = max(width_2 + 1, current_height)
        width_pad = needed_width - current_width
        height_pad = needed_height - current_height
        info(
            f"Expanding max_gaps[{type_1},{type_2}] from "
            f"{current_width}x{current_height} to "
            f"{needed_width}x{needed_height}."
        )
        max_gaps = np.pad(
            max_gaps, ((0, width_pad), (0, height_pad)), "constant", constant_values=0
        )
        self.max_gaps[type_1, type_2] = max_gaps
        self._save_max_gaps(type_1, type_2)

    def _get_max_gap(self, type_1: str, type_2: str, width_1: int, width_2: int) -> int:
        """Get max gap between characters of provided type and widths.

        Arguments:
            type_1: Type of first character
            type_2: Type of second character
            width_1: Width of first character in pixels; used as row index
            width_2: Width of second character in pixels; used as column index
        Returns:
            Max gap between characters in pixels, or 0 if not found
        """
        max_gaps = self.max_gaps[type_1, type_2]
        try:
            return max_gaps[width_1, width_2]
        except IndexError as e:
            self._expand_max_gaps(type_1, type_2, width_1, width_2)
            return self._get_max_gap(type_1, type_2, width_1, width_2)

    def _get_max_gap_interpolated(
        self, type_1: str, type_2: str, width_1: int, width_2: int
    ) -> int:
        """Get interpolated max gap between characters of provided type and widths.

        Arguments:
            type_1: Type of first character
            type_2: Type of second character
            width_1: Width of first character in pixels, used as row index
            width_2: Width of second character in pixels, used as column index
        Returns:
            Interpolated max gap between characters in pixels
        """
        max_gaps = self.max_gaps[type_1, type_2]

        # Sum neighbors
        neighbors = []
        rows, cols = max_gaps.shape
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = width_1 + dx, width_2 + dy
                if 0 <= nx < rows and 0 <= ny < cols and (dx != 0 or dy != 0):
                    neighbor_value = max_gaps[nx, ny]
                    if neighbor_value != 0:
                        neighbors.append(neighbor_value)

        # Return average of neighbors, or 0 if no neighbors
        if neighbors:
            return int(sum(neighbors) / len(neighbors))
        return 0

    def _save_max_gaps(self, type_1: str, type_2: str) -> None:
        """Save max gaps file for a given pair of character types.

        Arguments:
            type_1: First character type
            type_2: Second character type
        """
        outfile = self.file_paths[type_1, type_2]
        array = self.max_gaps[type_1, type_2]
        np.savetxt(outfile, array, delimiter=",", fmt="%d")
        info(f"Saved {outfile}.")

    def _update_max_gaps(
        self, type_1: str, type_2: str, width_1: int, width_2: int, gap: int
    ) -> None:
        """Update max gaps between characters of provided type and widths.

        Arguments:
            type_1: Type of first character
            type_2: Type of second character
            width_1: Width of first character in pixels; used as row index
            width_2: Width of second character in pixels; used as column index
            gap: New max gap between characters in pixels
        """
        max_gaps = self.max_gaps[type_1, type_2]
        max_gaps[width_1, width_2] = gap
        self._save_max_gaps(type_1, type_2)

    @staticmethod
    def get_char_type(char: str) -> str:
        """Return character type.

        Arguments:
            char: Character
        Returns:
            Character type
        Raises:
            ScinoephileException: If character type is not recognized
        """
        punctuation = set(half_punc_dict.values()) | set(full_punc_dict.values())

        # Check if character is punctuation
        if char in punctuation:
            return "punc"

        # Check if character is full-width (CJK)
        if any(
            [
                "\u4E00" <= char <= "\u9FFF",  # CJK Unified Ideographs
                "\u3400" <= char <= "\u4DBF",  # CJK Unified Ideographs Extension A
                "\uF900" <= char <= "\uFAFF",  # CJK Compatibility Ideographs
                "\U00020000" <= char <= "\U0002A6DF",  # CJK Unified Ideographs Ext B
                "\U0002A700" <= char <= "\U0002B73F",  # CJK Unified Ideographs Ext C
                "\U0002B740" <= char <= "\U0002B81F",  # CJK Unified Ideographs Ext D
                "\U0002B820" <= char <= "\U0002CEAF",  # CJK Unified Ideographs Ext E
                "\U0002CEB0" <= char <= "\U0002EBEF",  # CJK Unified Ideographs Ext F
                "\u3000" <= char <= "\u303F",  # CJK Symbols and Punctuation
            ]
        ):
            return "full"

        # Check if character is half-width (Western)
        if any(
            [
                "\u0020" <= char <= "\u007F",  # Basic Latin
                "\u00A0" <= char <= "\u00FF",  # Latin-1 Supplement
                "\u0100" <= char <= "\u017F",  # Latin Extended-A
                "\u0180" <= char <= "\u024F",  # Latin Extended-B
            ]
        ):
            return "half"

        # Raise exception if character type is not recognized
        raise ScinoephileException(
            f"Unrecognized char type for '{char}' of name {unicodedata.name(char)}"
        )
