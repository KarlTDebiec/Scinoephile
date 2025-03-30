#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages whitespace between characters."""
from __future__ import annotations

from logging import info

import numpy as np

from scinoephile.common import package_root
from scinoephile.image import ImageSubtitle
from scinoephile.image.char_pair import CharPair


class WhitespaceManager:
    """Manages whitespace between characters."""

    file_paths = {}
    """Paths to files containing max gaps for each char type pair."""
    max_gaps = {}
    """Max gaps for each character type pair."""

    def __init__(self):
        """Initialize."""
        types = ("full", "half", "punc")
        for type_1 in types:
            for type_2 in types:
                path = package_root / "data" / "ocr" / f"max_gaps_{type_1}_{type_2}.csv"
                self.file_paths[type_1, type_2] = path
        for (type_1, type_2), max_gaps_file in self.file_paths.items():
            if max_gaps_file.exists():
                arr = np.loadtxt(max_gaps_file, delimiter=",", dtype=int)
                self.max_gaps[type_1, type_2] = arr
                info(f"Loaded {max_gaps_file}.")
            else:
                arr = np.zeros((8, 8), dtype=int)
                self.max_gaps[type_1, type_2] = arr
                self._save_max_gaps(type_1, type_2)

    def validate(
        self,
        subtitle: ImageSubtitle,
        i: int,
        interactive: bool = True,
    ) -> list[str]:
        """Validate spacing in text by comparing with bbox gaps.

        Arguments:
            subtitle: Subtitle to validate
            i: Subtitle index
            interactive: Whether to prompt user for input on proposed updates
        """
        bboxes = subtitle.bboxes
        text = subtitle.text
        widths = subtitle.bbox_widths
        heights = subtitle.bbox_heights
        gaps = subtitle.bbox_gaps

        # Iterate through text and assess gaps
        messages = []
        char_1_i = 0
        width_1_i = 0
        gap_i = 0
        while True:
            if char_1_i > len(text) - 2:
                break

            # Get char 1 and its width
            char_1 = text[char_1_i]
            width_1 = widths[width_1_i]

            # Get provisional char 2 and its width
            char_2_i = char_1_i + 1
            char_2 = text[char_2_i]
            width_2_i = width_1_i + 1
            width_2 = widths[width_2_i]

            # If char 2 is whitespace, iterate to next real char and track whitespace
            whitespace = ""
            while char_2_i < len(text):
                char_2 = text[char_2_i]
                if char_2 in ("\u3000", " "):
                    whitespace += char_2
                    char_2_i += 1
                    continue
                else:
                    break

            # Get gap between char 1 and char 2, and maximum expected gap
            gap = gaps[gap_i]
            pair = CharPair(char_1, char_2, width_1, width_2, gap, whitespace)
            message = self.validate_gap(pair, interactive)
            if message:
                messages.append(message)

            char_1_i = char_2_i
            width_1_i = width_2_i
            gap_i += 1

        return messages

    def validate_gap(self, pair: CharPair, interactive: bool = True) -> str:
        """Validate that whitespace between two chars matches visual gap between them.

        Arguments:
            pair: Character pair to validate
            interactive: Whether to prompt user for input on proposed updates
        """
        # Check if whitespace is appropriate for adjacent characters
        # TODO: Determine appropriate whitespace characters, rather than just boolean
        whitespace_fit_for_adj_chars = len(pair.whitespace) == 0

        # First test if this gap is within the specific limit for these widths
        max_gap = self._get_max_gap(pair)
        gap_fit_for_adj_chars = pair.gap <= max_gap
        if gap_fit_for_adj_chars:
            # Expect no space, have no space
            if whitespace_fit_for_adj_chars:
                return
            # Expect no space, have space
            else:
                return (
                    f"{pair.char_1} and {pair.char_2} "
                    f"are separated by {pair.gap:2d} pixels "
                    f"(<={max_gap:2d}), and appear to be adjacent, "
                    f"but are separated by whitespace '{pair.whitespace}'."
                )

        # Next try a limit based on neighbors
        max_gap = self._get_max_gap_extended(pair)
        gap_fit_for_adj_chars = pair.gap <= max_gap
        if gap_fit_for_adj_chars:
            # Expect no space, have no space
            if whitespace_fit_for_adj_chars:
                self._update_max_gaps(pair)
                return (
                    f"{pair.char_1} and {pair.char_2} "
                    f"are separated by {pair.gap:2d} pixels "
                    f"(<{max_gap:2d}), and appear to be adjacent, "
                    f"and are within extended max gap, added "
                    f"({pair.width_1:2d},{pair.width_2:2d}):{pair.gap:2d} "
                    f"to max_gaps[{pair.type_1},{pair.type_2}]."
                )
            # Expect no space, have space
            else:
                return (
                    f"{pair.char_1} and {pair.char_2} "
                    f"are separated by {pair.gap:2d} pixels "
                    f"(<={max_gap:2d}), and appear to be adjacent, "
                    f"but are separated by whitespace '{pair.whitespace}'."
                )
                # TODO: Automate correction
        else:
            # Expect space, have no space
            if whitespace_fit_for_adj_chars:
                if interactive and pair.gap < 100:
                    response = input(
                        f"{pair.char_1} and {pair.char_2} "
                        f"are separated by {pair.gap:2d} pixels "
                        f"(>{max_gap:2d}). Do you want to update the max gaps? (y/n): "
                    )
                    if response.lower().startswith("y"):
                        self._update_max_gaps(pair)
                        return (
                            f"{pair.char_1} and {pair.char_2} "
                            f"are separated by {pair.gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; added "
                            f"({pair.width_1:2d},{pair.width_2:2d}):{pair.gap:2d} "
                            f"to max_gaps[{pair.type_1},{pair.type_2}]."
                        )
                    else:
                        return (
                            f"{pair.char_1} and {pair.char_2} "
                            f"are separated by {pair.gap:2d} pixels "
                            f"(>{max_gap:2d}), and appear to have whitespace between "
                            f"them, but are not separated by whitespace; did not add "
                            f"({pair.width_1:2d},{pair.width_2:2d}):{pair.gap:2d} "
                            f"to max_gaps[{pair.type_1},{pair.type_2}]."
                        )
                else:
                    return (
                        f"{pair.char_1} and {pair.char_2} "
                        f"are separated by {pair.gap:2d} pixels "
                        f"(>{max_gap:2d}), and appear to have whitespace between "
                        f"them, but are not separated by whitespace."
                    )
            # Expect space, have space
            else:
                return (
                    f"{pair.char_1} and {pair.char_2} "
                    f"are separated by {pair.gap:2d} pixels "
                    f"(>{max_gap:2d}), and appear to have whitespace between them, "
                    f"and as expected are separated by whitespace '{pair.whitespace}'."
                )
                # TODO: Validate that amount of whitespace is appropriate for gap

    def _expand_max_gaps(self, pair: CharPair) -> None:
        """Expand max_gaps to fit new width(s) and resave.

        Arguments:
            pair: Char pair
        """
        max_gaps = self.max_gaps[pair.type_1, pair.type_2]
        current_width = max_gaps.shape[0]
        current_height = max_gaps.shape[1]
        needed_width = max(pair.width_1 + 1, current_width)
        needed_height = max(pair.width_2 + 1, current_height)
        width_pad = needed_width - current_width
        height_pad = needed_height - current_height
        info(
            f"Expanding max_gaps[{pair.type_1},{pair.type_2}] from "
            f"{current_width}x{current_height} to "
            f"{needed_width}x{needed_height}."
        )
        max_gaps = np.pad(
            max_gaps, ((0, width_pad), (0, height_pad)), "constant", constant_values=0
        )
        self.max_gaps[pair.type_1, pair.type_2] = max_gaps
        self._save_max_gaps(pair.type_1, pair.type_2)

    def _get_expected_whitespace(self, pair: CharPair) -> str:
        """Get expected whitespace between a pair of chars.

        Arguments:
            pair: Char pair
        Returns:
            Expected whitespace between chars
        """
        max_gap = self._get_max_gap(pair)

    def _get_max_gap(self, pair: CharPair) -> int:
        """Get max gap between a pair of chars for them to be adjacent.

        Arguments:
            pair: Char pair
        Returns:
            Max gap between chars in pixels, or 0 if not found
        """
        max_gaps = self.max_gaps[pair.type_1, pair.type_2]
        try:
            return max_gaps[pair.width_1, pair.width_2]
        except IndexError:
            return 0

    def _get_max_gap_extended(self, pair: CharPair) -> int:
        """Get extended max gap between a pair of chars for them to be adjacent.

        Arguments:
            pair: Char pair
        Returns:
            Extended max gap between chars in pixels
        """
        max_gaps = self.max_gaps[pair.type_1, pair.type_2]

        # Define the slice boundaries
        x1 = max(0, pair.width_1 - 1)
        x2 = min(max_gaps.shape[0], pair.width_1 + 2)
        y1 = max(0, pair.width_2 - 1)
        y2 = min(max_gaps.shape[1], pair.width_2 + 2)

        # Return the maximum value in the slice plus 1
        try:
            return max(np.nanmax(max_gaps[x1:x2, y1:y2]) + 1, 20)
        except ValueError:
            return 0

    def _save_max_gaps(self, type_1: str, type_2: str) -> None:
        """Save max gaps file for a given pair of char types.

        Arguments:
            type_1: First char type
            type_2: Second char type
        """
        outfile = self.file_paths[type_1, type_2]
        array = self.max_gaps[type_1, type_2]
        np.savetxt(outfile, array, delimiter=",", fmt="%d")
        info(f"Saved {outfile}.")

    def _update_max_gaps(self, pair: CharPair) -> None:
        """Update max gaps between characters of provided type and widths.

        Arguments:
            pair: Char pair
        """
        max_gaps = self.max_gaps[pair.type_1, pair.type_2]
        try:
            max_gaps[pair.width_1, pair.width_2] = pair.gap
        except IndexError as error:
            # If needed size is under 5% larger than current size, expand max_gaps
            shape = max_gaps.shape
            if pair.width_1 <= shape[0] * 1.05 and pair.width_2 <= shape[1] * 1.05:
                self._expand_max_gaps(pair)
                max_gaps = self.max_gaps[pair.type_1, pair.type_2]
                max_gaps[pair.width_1, pair.width_2] = pair.gap
            else:
                raise error
        self._save_max_gaps(pair.type_1, pair.type_2)
