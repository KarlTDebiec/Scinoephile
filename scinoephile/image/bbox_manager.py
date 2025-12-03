#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError

from .image_subtitle import ImageSubtitle

__all__ = ["BboxManager"]


class BboxManager:
    """Manages bboxes around characters."""

    merge_three_file_path = package_root / "data" / "ocr" / "merge_threes.csv"
    """Path to file containing specs for sets of three bboxes that should be merged."""
    merge_threes: dict[tuple[int, int, int, int, int, int, int, int], str] = {}
    """Dimensions and gaps betwee sets of three bboxes that should be merged."""
    merge_two_file_path = package_root / "data" / "ocr" / "merge_twos.csv"
    """Path to file containing specs for sets of two bboxes that should be merged."""
    merge_twos: dict[tuple[int, int, int, int, int], str] = {}
    """Dimensions and gaps between sets of two bboxes that should be merged."""

    def __init__(self):
        """Initialize."""
        if self.merge_two_file_path.exists():
            self.merge_twos = self._load_merge_dict(self.merge_two_file_path)
            self._save_merge_dict(self.merge_twos, self.merge_two_file_path)
        if self.merge_three_file_path.exists():
            self.merge_threes = self._load_merge_dict(self.merge_three_file_path)
            self._save_merge_dict(self.merge_threes, self.merge_three_file_path)

    @property
    def merge_two_chars(self):
        """Characters that are known to potentially be spread across two bboxes."""
        return set(char for chars in self.merge_twos.values() for char in chars)

    @property
    def merge_three_chars(self):
        """Characters that are known to potentially be spread across three bboxes."""
        return set(char for chars in self.merge_threes.values() for char in chars)

    def get_bboxes(
        self,
        subtitle: ImageSubtitle,
        interactive: bool = False,
    ) -> list[tuple[int, int, int, int]]:
        """Get character bboxes within an image.

        Arguments:
            subtitle: Subtitle for which to get bboxes
            interactive: Whether to prompt user for input on proposed updates
        Returns:
            Character bounding boxes [(x1, y1, x2, y2), ...]
        """
        arr = np.array(subtitle.img_with_white_bg)

        # Determine left and right of each section separated by whitespace
        sections = []
        section = None
        for i, nonwhite_pixels in enumerate(np.sum(arr < 255, axis=0)):
            if nonwhite_pixels > 0:
                if section is None:
                    section = [i, i]
                else:
                    section[1] = i
            elif section is not None:
                sections.append(section)
                section = None
        if section is not None:
            sections.append(section)

        # Determine top and bottom of each section to get final bbox
        bboxes = []
        for x1, x2 in sections:
            section = arr[:, x1:x2]
            nonwhite_pixels = np.sum(section < 255, axis=1)
            y1 = int(np.argmax(nonwhite_pixels > 0))
            y2 = int(len(nonwhite_pixels) - np.argmax(nonwhite_pixels[::-1] > 0) - 1)
            bboxes.append((x1, y1, x2, y2))

        # Merge sets of adjacent bboxes known to have vertical whitespace within them
        bboxes = self._apply_known_merges(bboxes, subtitle.text)

        # Propose additional merges of adjacent boxes, if found
        filtered_text = "".join(
            [char for char in subtitle.text if char not in ("\u3000", " ")]
        )
        if len(filtered_text) != len(bboxes):
            if interactive:
                self._propose_merges(bboxes, subtitle.text)
            bboxes = self._apply_known_merges(bboxes, subtitle.text)

        return bboxes

    def _apply_known_merges(
        self,
        bboxes: list[tuple[int, int, int, int]],
        text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Merge sets of adjacent bboxes that match specifications.

        Arguments:
            bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
            text: Provisional text present in image
        Returns:
            bboxes with sets of adjacent bboxes matching specifications merged
        """
        merged_bboxes = []
        bbox_i = 0
        char_i = 0
        while True:
            if char_i >= len(text):
                merged_bboxes += bboxes[bbox_i:]
                break
            char = text[char_i]
            if bbox_i >= len(bboxes):
                break

            # Merge set of three bboxes if appropriate
            if bbox_i <= len(bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)

                # Dimensions are known to be mergable
                if key in self.merge_threes:
                    # Dimensions and char match
                    if char in self.merge_threes[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 3
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.merge_three_chars:
                        self._update_merge_threes(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 3
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_merge_threes(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 3
                    char_i = self._get_next_char_i(text, char_i)
                    continue

            # Merge set of two bboxes if appropriate
            if bbox_i <= len(bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)

                # Dimensions are known to be mergable
                if key in self.merge_twos:
                    # Dimensions and char match
                    if char in self.merge_twos[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 2
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.merge_two_chars:
                        self._update_merge_twos(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 2
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_merge_twos(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 2
                    char_i = self._get_next_char_i(text, char_i)
                    continue

            # Otherwise, keep as is
            merged_bboxes.append(bboxes[bbox_i])
            bbox_i += 1
            char_i = self._get_next_char_i(text, char_i)

        return merged_bboxes

    def _fuzzy_match_key(self, key: tuple[int, ...]) -> set[str]:
        """Fuzzy match keys in merge_threes and merge_twos.

        Arguments:
            key: Key to match
        """
        length = len(key)
        if length == 5:
            merge_dict = self.merge_twos
        elif length == 8:
            merge_dict = self.merge_threes
        else:
            raise ScinoephileError(f"Key must be of length 5 or 8, not {len(key)}")

        known_values = set()
        for known_key in merge_dict.keys():
            if all(abs(known_key[i] - key[i]) <= 1 for i in range(length)):
                known_values.update(list(merge_dict[known_key]))

        return known_values

    def _propose_merges(self, bboxes: list[tuple[int, int, int, int]], text: str):
        """Propose merges of adjacent bboxes.

        Arguments:
            bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
            text: Provisional text present in image
        """
        bbox_i = 0
        char_i = 0
        while char_i < len(text):
            char = text[char_i]

            # If char is known to be a merge_three, check key for next three bboxes
            if char in self.merge_three_chars and bbox_i <= len(bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)
                response = input(
                    f"{char} may be split across three bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}), "
                    f"{key[5]}, ({key[6]}, {key[7]})). "
                    f"Do you want to update merge_threes? (y/n):"
                )
                if response.lower() == "y":
                    self._update_merge_threes(key, char)
                    bbox_i += 3

            # If char is known to be a merge_two, check key for next two bboxes
            if char in self.merge_two_chars and bbox_i <= len(bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)
                response = input(
                    f"{char} may be split across two bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}). "
                    f"Do you want to update merge_twos? (y/n):"
                )
                if response.lower() == "y":
                    self._update_merge_twos(key, char)
                    bbox_i += 2

            char_i = self._get_next_char_i(text, char_i)
            bbox_i += 1

    def _update_merge_threes(
        self,
        key: tuple[int, int, int, int, int, int, int, int],
        value: str,
    ):
        """Update merge_threes dictionary.

        Arguments:
            key: Key including width, height, gap, width, height, gap, width, height
            value: Character
        """
        if key in self.merge_threes:
            self.merge_threes[key] += value
        else:
            self.merge_threes[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to merge_threes")
        self._save_merge_dict(self.merge_threes, self.merge_three_file_path)

    def _update_merge_twos(
        self,
        key: tuple[int, int, int, int, int],
        value: str,
    ):
        """Update merge_twos dictionary.

        Arguments:
            key: Key including width, height, gap, width, height
            value: Character
        """
        if key in self.merge_twos:
            self.merge_twos[key] += value
        else:
            self.merge_twos[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to merge_twos")
        self._save_merge_dict(self.merge_twos, self.merge_two_file_path)

    @staticmethod
    def _get_key_and_merged_bbox(
        bboxes: list[tuple[int, int, int, int]],
        i: int,
        n: int,
    ) -> tuple[tuple[int, ...], tuple[int, int, int, int]]:
        """Get key and merged bbox from bboxes.

        Arguments:
            bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
            i: Index of first bbox
            n: Number of bboxes whose merging is under consideration
        Returns:
            Key and merged bbox
        """
        bboxes_slice = bboxes[i : i + n]
        widths = [bbox[2] - bbox[0] for bbox in bboxes_slice]
        heights = [bbox[3] - bbox[1] for bbox in bboxes_slice]
        gaps = [
            bboxes_slice[i + 1][0] - bboxes_slice[i][2]
            for i in range(len(bboxes_slice) - 1)
        ]
        key = tuple(
            [dim for group in zip(widths, heights, gaps + [0]) for dim in group][:-1]
        )
        merged_bbox = (
            min(bbox[0] for bbox in bboxes_slice),
            min(bbox[1] for bbox in bboxes_slice),
            max(bbox[2] for bbox in bboxes_slice),
            max(bbox[3] for bbox in bboxes_slice),
        )

        return key, merged_bbox

    @staticmethod
    def _get_next_char_i(text: str, char_i: int) -> int:
        """Get index of next non-whitespace character.

        Arguments:
            text: Provisional text present in image
            char_i: Index of current character
        Returns:
            Index of next non-whitespace character
        """
        char_i += 1
        while char_i < len(text):
            char = text[char_i]
            if char in ("\u3000", " "):
                char_i += 1
                continue
            break
        return char_i

    @staticmethod
    def _load_merge_dict(
        file_path: Path,
    ) -> dict[tuple[int, int, int, int, int, int, int, int], str]:
        """Load merge dict from file.

        Arguments:
            file_path: Path to file
        """
        arr = np.genfromtxt(file_path, delimiter=",", dtype=str, encoding="utf-8")

        merge_dict = {}
        for row in arr:
            key = tuple(map(int, row[1:]))
            value = row[0]
            if key in merge_dict:
                merge_dict[key] += value
            else:
                merge_dict[key] = str(value)

        info(f"Loaded {file_path}")
        return merge_dict

    @staticmethod
    def _save_merge_dict(
        merge_dict: dict[tuple[int, int, int, int], str],
        file_path: Path,
    ):
        """Save merge dict to file.

        Arguments:
            merge_dict: Dictionary to save
            file_path: Path to file
        1st column: valuez
        """
        rows = []
        for key, value in merge_dict.items():
            for char in value:
                rows.extend([[char] + list(key)])

        arr = np.array(sorted(rows))
        np.savetxt(
            file_path,
            arr,
            delimiter=",",
            fmt="%s",
            encoding="utf-8",
        )
        info(f"Saved {file_path}")
