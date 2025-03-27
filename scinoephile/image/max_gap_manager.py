#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages maximum gaps between characters of different types."""
from __future__ import annotations

from logging import info

import numpy as np

from scinoephile.common import package_root
from scinoephile.core.text import get_char_type


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
        interactive: bool = True,
    ) -> str:
        """Validate gap between two characters.

        Arguments:
            char_1: First character
            char_2: Second character
            char_1_width: Width of first character in pixels
            char_2_width: Width of second character in pixels
            gap: Gap between characters in pixels
            whitespace: Whitespace between characters
            interactive: Whether to prompt user for input on proposed updates
        """
        type_1 = get_char_type(char_1)
        type_2 = get_char_type(char_2)

        # Check if whitespace is appropriate for adjacent characters
        whitespace_fit_for_adj_chars = len(whitespace) == 0

        # First test if this gap is within the specific limit for these widths
        max_gap = self._get_max_gap(type_1, type_2, char_1_width, char_2_width)
        gap_fit_for_adj_chars = gap <= max_gap
        if gap_fit_for_adj_chars:
            # Expect no space, have no space
            if whitespace_fit_for_adj_chars:
                return
            # Expect no space, have space
            else:
                return (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(<={max_gap:2d}), and appear to be adjacent, "
                    f"but are separated by whitespace '{whitespace}'."
                )

        # Next try a limit based on neighbors
        max_gap = self._get_max_gap_extended(type_1, type_2, char_1_width, char_2_width)
        gap_fit_for_adj_chars = gap <= max_gap
        if gap_fit_for_adj_chars:
            # Expect no space, have no space
            if whitespace_fit_for_adj_chars:
                self._update_max_gaps(type_1, type_2, char_1_width, char_2_width, gap)
                return (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(<{max_gap:2d}), and appear to be adjacent, "
                    f"and are within extended max gap, added "
                    f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                    f"to max_gaps[{type_1},{type_2}]."
                )
            # Expect no space, have space
            else:
                return (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(<={max_gap:2d}), and appear to be adjacent, "
                    f"but are separated by whitespace '{whitespace}'."
                )
                # TODO: Automate correction
        else:
            # Expect space, have no space
            if whitespace_fit_for_adj_chars:
                if interactive and gap < 100:
                    response = input(
                        f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                        f"(>{max_gap:2d}). Do you want to update the max gaps? (y/n): "
                    )
                    if response.lower().startswith("y"):
                        self._update_max_gaps(
                            type_1, type_2, char_1_width, char_2_width, gap
                        )
                        return (
                            f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; added "
                            f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                            f"to max_gaps[{type_1},{type_2}]."
                        )
                    else:
                        return (
                            f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; did not add "
                            f"({char_1_width:2d},{char_2_width:2d}):{gap:2d} "
                            f"to max_gaps[{type_1},{type_2}]."
                        )
                else:
                    return (
                        f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                        f"(>{max_gap:2d}), and appear to have whitespace between "
                        f"them, but are not separated by whitespace."
                    )
            # Expect space, have space
            else:
                return (
                    f"{char_1} and {char_2} are separated by {gap:2d} pixels "
                    f"(>{max_gap:2d}), and appear to have whitespace between them, "
                    f"and as expected are separated by whitespace '{whitespace}'."
                )
                # TODO: Validate that amount of whitespace is appropriate for gap

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
            return 0

    def _get_max_gap_extended(
        self, type_1: str, type_2: str, width_1: int, width_2: int
    ) -> int:
        """Get extended max gap between characters of provided type and widths.

        Arguments:
            type_1: Type of first character
            type_2: Type of second character
            width_1: Width of first character in pixels, used as row index
            width_2: Width of second character in pixels, used as column index
        Returns:
            Extended max gap between characters in pixels
        """
        max_gaps = self.max_gaps[type_1, type_2]

        # Define the slice boundaries
        x1 = max(0, width_1 - 1)
        x2 = min(max_gaps.shape[0], width_1 + 2)
        y1 = max(0, width_2 - 1)
        y2 = min(max_gaps.shape[1], width_2 + 2)

        # Return the maximum value in the slice plus 1
        try:
            return max(np.nanmax(max_gaps[x1:x2, y1:y2]) + 1, 20)
        except ValueError:
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
        try:
            max_gaps[width_1, width_2] = gap
        except IndexError as error:
            # If needed size is under 5% larger than current size, expand max_gaps
            if (
                width_1 <= max_gaps.shape[0] * 1.05
                and width_2 <= max_gaps.shape[1] * 1.05
            ):
                self._expand_max_gaps(type_1, type_2, width_1, width_2)
                max_gaps = self.max_gaps[type_1, type_2]
                max_gaps[width_1, width_2] = gap
            else:
                raise error
        self._save_max_gaps(type_1, type_2)
