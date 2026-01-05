#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages whitespace between characters."""

from __future__ import annotations

import csv
from logging import info
from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSubtitle

__all__ = ["WhitespaceManager"]


class WhitespaceManager:
    """Manages whitespace between characters."""

    def __init__(self):
        """Initialize."""
        self.char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        """Data structure for gaps between bboxes.
        
        Key is a pair of characters.
        Value is a tuple of four ints, representing cutoffs:
          * Upper bound for 'adjacent' characters
          * Lower bound for 'space' characters
          * Upper bound for 'space' characters
          * Lower bound for 'tab' characters
        """
        file_path = self._char_pair_gaps_path()
        if file_path.exists():
            self.char_pair_gaps = self._load_char_pair_gaps(file_path)

    def validate(
        self, sub: ImageSubtitle, sub_idx: int, interactive: bool = False
    ) -> list[str]:
        """Validate spacing in text by comparing with bbox gaps.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index
            interactive: whether to prompt user for confirmations
        Returns:
            list of validation messages
        """
        if sub.bboxes is None:
            raise ScinoephileError(
                f"Subtitle {sub_idx} has no bboxes; cannot validate whitespace."
            )
        messages = []
        for pair in _get_char_pairs(sub.text, sub.bboxes):
            message = self.validate_gap(pair, sub_idx, interactive=interactive)
            if message is not None:
                messages.append(message)
        return messages

    def validate_gap(  # noqa: PLR0911
        self,
        pair: tuple[str, str, int, int, int, str],
        i: int,
        interactive: bool = True,
    ) -> str | None:
        """Validate that whitespace between two chars matches visual gap between them.

        Arguments:
            pair: (char_1, char_2, width_1, width_2, gap, whitespace)
            i: Subtitle index
            interactive: Whether to prompt user for input on proposed updates
        """
        char_1, char_2, _width_1, _width_2, gap, whitespace = pair
        observed_label = self._get_observed_label(whitespace)
        label, updated = self._get_label_for_gap(pair, interactive=interactive, i=i)
        if updated:
            self._save_char_pair_gaps(
                self.char_pair_gaps, self._char_pair_gaps_file_path
            )
        if label is None:
            return f"Sub {i + 1:04d} {char_1}{char_2}: No classification for gap {gap}."
        if observed_label != label:
            return (
                f"Sub {i + 1:04d} {char_1}{char_2}: "
                f"gap {gap} suggests {label}, "
                f"but whitespace is '{whitespace}'."
            )
        return None

    def _get_label_for_gap(
        self, pair: tuple[str, str, int, int, int, str], interactive: bool, i: int
    ) -> tuple[str | None, bool]:
        """Get or infer a label for a char pair and gap.

        Arguments:
            pair: (char_1, char_2, width_1, width_2, gap, whitespace)
            interactive: whether to prompt user for input
            i: subtitle index
        Returns:
            label or None if not available, and whether data changed
        """
        char_1, char_2, _width_1, _width_2, gap, _whitespace = pair
        adj_max, adj_space_max, space_min, tab_max = self.char_pair_gaps.get(
            (char_1, char_2), self._get_default_cutoffs(char_1, char_2)
        )
        updated = False

        label = None
        if gap <= adj_max:
            label = "adjacent"
        elif gap < adj_space_max:
            if interactive:
                response = self._prompt_for_label(
                    pair, i, options=("adjacent", "space")
                )
                if response == "adjacent":
                    adj_max = max(adj_max, gap)
                    updated = True
                elif response == "space":
                    adj_space_max = min(adj_space_max, gap)
                    updated = True
                label = response
        elif gap <= space_min:
            label = "space"
        elif gap < tab_max:
            if interactive:
                response = self._prompt_for_label(pair, i, options=("space", "tab"))
                if response == "space":
                    space_min = max(space_min, gap)
                    updated = True
                elif response == "tab":
                    tab_max = min(tab_max, gap)
                    updated = True
                label = response
        else:
            label = "tab"

        updated = self._update_cutoffs(
            (char_1, char_2), (adj_max, adj_space_max, space_min, tab_max), updated
        )
        return label, updated

    def _prompt_for_label(
        self,
        pair: tuple[str, str, int, int, int, str],
        i: int,
        options: tuple[str, str],
    ) -> str | None:
        """Prompt user to classify a gap.

        Arguments:
            pair: (char_1, char_2, width_1, width_2, gap, whitespace)
            i: Subtitle index
            options: allowed label options
        Returns:
            Selected label or None if not provided
        """
        char_1, char_2, _width_1, _width_2, gap, whitespace = pair
        prompt = (
            f"Sub {i + 1:04d} {char_1}{char_2} "
            f"gap {gap} whitespace '{whitespace}': "
            f"{', '.join(options)}? "
        )
        response = input(prompt).strip().lower()
        if "adjacent" in options and response in {"a", "adj", "adjacent"}:
            return "adjacent"
        if "space" in options and response in {"s", "space"}:
            return "space"
        if "tab" in options and response in {"t", "tab"}:
            return "tab"
        return None

    def _update_cutoffs(
        self,
        key: tuple[str, str],
        cutoffs: tuple[int, int, int, int],
        updated: bool,
    ) -> bool:
        """Update stored cutoffs when needed.

        Arguments:
            key: character pair key
            cutoffs: cutoff tuple
            updated: whether an update should be saved
        Returns:
            whether an update was saved
        """
        if not updated:
            return False
        self.char_pair_gaps[key] = self._normalize_cutoffs(cutoffs)
        return True

    @staticmethod
    def _get_observed_label(whitespace: str) -> str:
        """Infer label from whitespace.

        Arguments:
            whitespace: whitespace between characters
        Returns:
            label for observed whitespace
        """
        if len(whitespace) == 0:
            return "adjacent"
        if len(whitespace) == 1:
            return "space"
        return "tab"

    @staticmethod
    def _load_char_pair_gaps(
        file_path: Path,
    ) -> dict[tuple[str, str], tuple[int, int, int, int]]:
        """Load gap labels from file.

        Arguments:
            file_path: path to file
        Returns:
            labels keyed by (char_1, char_2)
        """
        labels: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                char_1, char_2, adj_max, adj_space_max, space_min, tab_max = row
                labels[(char_1, char_2)] = (
                    int(adj_max),
                    int(adj_space_max),
                    int(space_min),
                    int(tab_max),
                )
        return labels

    def _save_char_pair_gaps(
        self,
        char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]],
        file_path: Path,
    ) -> None:
        """Save gap labels to file.

        Arguments:
            char_pair_gaps: char pair gaps to save
            file_path: path to file
        """
        rows = [
            (char_1, char_2, adj_max, adj_space_max, space_min, tab_max)
            for (char_1, char_2), (
                adj_max,
                adj_space_max,
                space_min,
                tab_max,
            ) in char_pair_gaps.items()
        ]
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}.")

    @staticmethod
    def _char_pair_gaps_path() -> Path:
        """Path to character pair gap labels csv file."""
        return package_root / "data" / "ocr" / "char_pair_gaps.csv"

    @staticmethod
    def _get_default_cutoffs(char_1: str, char_2: str) -> tuple[int, int, int, int]:
        """Get default cutoff tuple for a character pair.

        Arguments:
            char_1: first character
            char_2: second character
        Returns:
            default cutoff tuple
        """
        return (1, 50, 50, 100)

    @staticmethod
    def _normalize_cutoffs(
        cutoffs: tuple[int, int, int, int],
    ) -> tuple[int, int, int, int]:
        """Ensure cutoff ordering is monotonic.

        Arguments:
            cutoffs: cutoff tuple
        Returns:
            normalized cutoff tuple
        """
        adj_max, adj_space_max, space_min, tab_max = cutoffs
        adj_space_max = max(adj_space_max, adj_max)
        space_min = max(space_min, adj_space_max)
        tab_max = max(tab_max, space_min)
        return adj_max, adj_space_max, space_min, tab_max


def _get_char_pairs(
    text: str, bboxes: list[Bbox]
) -> list[tuple[str, str, int, int, int, str]]:
    """Build character pairs from text and bboxes.

    Arguments:
        text: subtitle text
        bboxes: bounding boxes for each non-whitespace character
    Returns:
        list of (char_1, char_2, width_1, width_2, gap, whitespace)
    """
    non_ws_chars: list[tuple[int, str, Bbox]] = []
    bbox_idx = 0
    for text_idx, char in enumerate(text):
        if char in whitespace_chars or char == "\n":
            continue
        if bbox_idx >= len(bboxes):
            break
        non_ws_chars.append((text_idx, char, bboxes[bbox_idx]))
        bbox_idx += 1

    char_pairs: list[tuple[str, str, int, int, int, str]] = []
    for idx in range(len(non_ws_chars) - 1):
        text_idx_1, char_1, bbox_1 = non_ws_chars[idx]
        text_idx_2, char_2, bbox_2 = non_ws_chars[idx + 1]
        gap_whitespace = text[text_idx_1 + 1 : text_idx_2]
        if "\n" in gap_whitespace:
            continue
        gap = bbox_2.x1 - bbox_1.x2
        char_pairs.append(
            (char_1, char_2, bbox_1.width, bbox_2.width, gap, gap_whitespace)
        )

    return char_pairs
