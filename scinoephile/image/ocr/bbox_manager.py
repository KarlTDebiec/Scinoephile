#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.text import whitespace_chars
from scinoephile.image.drawing import get_img_of_text

from .types import OcrSubtitle

__all__ = ["BboxManager"]


class BboxManager:
    """Manages bboxes around characters."""

    char_dims_file_path = package_root / "data" / "ocr" / "char_dims.csv"
    """Path to file containing expected character widths and heights."""
    char_dims: dict[str, tuple[int, int]] = {}
    """Expected character widths and heights keyed by character."""
    merge_two_file_path = package_root / "data" / "ocr" / "merge_twos.csv"
    """Path to file containing specs for sets of two bboxes that should be merged."""
    merge_twos: dict[tuple[int, int, int, int, int], str] = {}
    """Dimensions and gaps between sets of two bboxes that should be merged."""
    merge_three_file_path = package_root / "data" / "ocr" / "merge_threes.csv"
    """Path to file containing specs for sets of three bboxes that should be merged."""
    merge_threes: dict[tuple[int, int, int, int, int, int, int, int], str] = {}
    """Dimensions and gaps betwee sets of three bboxes that should be merged."""

    def __init__(self):
        """Initialize."""
        if self.char_dims_file_path.exists():
            self.char_dims = self._load_char_dims(self.char_dims_file_path)
            self._save_char_dims(self.char_dims, self.char_dims_file_path)
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
        subtitle: OcrSubtitle,
        interactive: bool = False,
    ) -> list[tuple[int, int, int, int]]:
        """Get character bboxes within an image.

        Arguments:
            subtitle: Subtitle for which to get bboxes
            interactive: Whether to prompt user for input on proposed updates
        Returns:
            Character bounding boxes [(x1, y1, x2, y2), ...]
        """
        grayscale, alpha = self._get_grayscale_and_alpha(subtitle)
        fill_color, outline_color = self._get_fill_and_outline_colors(
            subtitle, grayscale, alpha
        )
        white_mask = self._get_white_mask(grayscale, alpha, fill_color, outline_color)

        # Determine left and right of each section separated by whitespace
        sections = []
        section = None
        for i, white_pixels in enumerate(np.sum(white_mask, axis=0)):
            if white_pixels > 0:
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
            section = white_mask[:, x1:x2]
            white_pixels = np.sum(section, axis=1)
            y1 = int(np.argmax(white_pixels > 0))
            y2 = int(len(white_pixels) - np.argmax(white_pixels[::-1] > 0) - 1)
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

    def validate_char_bboxes(
        self,
        subtitle: OcrSubtitle,
        subtitle_index: int | None = None,
    ) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            subtitle: Subtitle to validate
            subtitle_index: Optional subtitle index for logging
        Returns:
            List of validation messages
        """
        if subtitle.bboxes is None:
            raise ScinoephileError("Subtitle has no bboxes to validate.")

        messages = []
        text = subtitle.text
        bbox_i = 0
        char_i = 0
        while char_i < len(text):
            char = text[char_i]
            if char in whitespace_chars:
                char_i += 1
                continue
            if bbox_i >= len(subtitle.bboxes):
                messages.append(
                    self._format_message(
                        subtitle_index,
                        text,
                        f"ran out of bboxes at character '{char}'.",
                    )
                )
                break

            expected = self._get_expected_char_dims(char, subtitle)
            bbox = subtitle.bboxes[bbox_i]
            bbox_dims = self._get_bbox_dims(bbox)
            if self._dims_match(bbox_dims, expected):
                if char not in self.char_dims:
                    self._update_char_dims(char, bbox_dims)
                    messages.append(
                        self._format_message(
                            subtitle_index,
                            text,
                            f"added dims for '{char}' as {bbox_dims}.",
                        )
                    )
                bbox_i += 1
                char_i += 1
                continue

            matched = False
            if bbox_i <= len(subtitle.bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(
                    subtitle.bboxes, bbox_i, 2
                )
                merged_dims = self._get_bbox_dims(merged_bbox)
                if self._dims_match(merged_dims, expected):
                    self._update_merge_twos(key, char)
                    messages.append(
                        self._format_message(
                            subtitle_index,
                            text,
                            f"merged two bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    bbox_i += 2
                    char_i += 1
                    matched = True
            if not matched and bbox_i <= len(subtitle.bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(
                    subtitle.bboxes, bbox_i, 3
                )
                merged_dims = self._get_bbox_dims(merged_bbox)
                if self._dims_match(merged_dims, expected):
                    self._update_merge_threes(key, char)
                    messages.append(
                        self._format_message(
                            subtitle_index,
                            text,
                            f"merged three bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    bbox_i += 3
                    char_i += 1
                    matched = True

            if not matched:
                messages.append(
                    self._format_message(
                        subtitle_index,
                        text,
                        f"bbox dims {bbox_dims} for '{char}' do not match "
                        f"expected {expected}.",
                    )
                )
                bbox_i += 1
                char_i += 1

        if bbox_i < len(subtitle.bboxes):
            messages.append(
                self._format_message(
                    subtitle_index,
                    text,
                    f"{len(subtitle.bboxes) - bbox_i} extra bboxes remain.",
                )
            )

        return messages

    @staticmethod
    def _get_white_mask(
        grayscale: np.ndarray,
        alpha: np.ndarray,
        fill_color: int,
        outline_color: int,
    ) -> np.ndarray:
        """Get a white interior mask from grayscale/alpha arrays.

        Arguments:
            grayscale: Grayscale values
            alpha: Alpha values
            fill_color: Fill color used in rendering
            outline_color: Outline color used in rendering
        Returns:
            Boolean mask of white interior pixels
        """
        if fill_color == outline_color:
            threshold = max(fill_color - 10, 0)
        else:
            threshold = int((fill_color + outline_color) / 2)
        return (alpha > 0) & (grayscale >= threshold)

    @staticmethod
    def _get_grayscale_and_alpha(
        subtitle: OcrSubtitle,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get grayscale and alpha arrays for the subtitle image.

        Arguments:
            subtitle: Subtitle for which to get grayscale and alpha
        Returns:
            Grayscale values and alpha mask
        """
        return BboxManager._get_grayscale_and_alpha_from_image(subtitle.img)

    @staticmethod
    def _get_grayscale_and_alpha_from_image(
        img,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get grayscale and alpha arrays for an image.

        Arguments:
            img: Image from which to extract grayscale and alpha
        Returns:
            Grayscale values and alpha mask
        """
        arr = np.array(img)
        if img.mode == "LA":
            return arr[:, :, 0], arr[:, :, 1]
        if img.mode == "RGBA":
            rgb = arr[:, :, :3].astype(np.float32)
            grayscale = (
                0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
            ).astype(np.uint8)
            alpha = arr[:, :, 3]
            return grayscale, alpha
        raise ScinoephileError(
            f"Unsupported image mode '{img.mode}' for white interior bboxes."
        )

    @staticmethod
    def _get_fill_and_outline_colors(
        subtitle: OcrSubtitle,
        grayscale: np.ndarray,
        alpha: np.ndarray,
    ) -> tuple[int, int]:
        """Get fill and outline grayscale values.

        Arguments:
            subtitle: Subtitle for which to get fill and outline colors
            grayscale: Grayscale values
            alpha: Alpha values
        Returns:
            Fill and outline grayscale values
        """
        series = getattr(subtitle, "series", None)
        if (
            series is not None
            and hasattr(series, "fill_color")
            and hasattr(series, "outline_color")
        ):
            return int(series.fill_color), int(series.outline_color)

        mask = alpha != 0
        values = grayscale[mask]
        if values.size == 0:
            return 255, 0
        hist = np.bincount(values, minlength=256)
        fill, outline = map(int, np.argsort(hist)[-2:])
        if outline > fill:
            fill, outline = outline, fill
        return fill, outline

    def _get_expected_char_dims(
        self, char: str, subtitle: OcrSubtitle
    ) -> tuple[int, int]:
        """Get expected bbox dimensions for a character.

        Arguments:
            char: Character to check
            subtitle: Subtitle containing the character
        Returns:
            Expected (width, height)
        """
        if char in self.char_dims:
            return self.char_dims[char]

        measured = self._measure_char_dims(char, subtitle)
        return measured

    def _measure_char_dims(
        self,
        char: str,
        subtitle: OcrSubtitle,
    ) -> tuple[int, int]:
        """Measure character dimensions by rendering the character.

        Arguments:
            char: Character to measure
            subtitle: Subtitle containing the character
        Returns:
            Measured (width, height)
        """
        series = getattr(subtitle, "series", None)
        fill_color = 31
        outline_color = 235
        if (
            series is not None
            and hasattr(series, "fill_color")
            and hasattr(series, "outline_color")
        ):
            fill_color = int(series.fill_color)
            outline_color = int(series.outline_color)

        rendered = get_img_of_text(
            char,
            subtitle.img.size,
            fill_color=fill_color,
            outline_color=outline_color,
        )
        grayscale, alpha = self._get_grayscale_and_alpha_from_image(rendered)
        mask = self._get_white_mask(grayscale, alpha, fill_color, outline_color)
        bbox = self._get_bbox_from_mask(mask)
        return self._get_bbox_dims(bbox)

    @staticmethod
    def _get_bbox_dims(bbox: tuple[int, int, int, int]) -> tuple[int, int]:
        """Get width and height from a bbox."""
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    @staticmethod
    def _get_bbox_from_mask(mask: np.ndarray) -> tuple[int, int, int, int]:
        """Get bbox from a boolean mask."""
        cols = np.where(np.any(mask, axis=0))[0]
        rows = np.where(np.any(mask, axis=1))[0]
        if cols.size == 0 or rows.size == 0:
            return (0, 0, 0, 0)
        return (int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1]))

    @staticmethod
    def _dims_match(
        bbox_dims: tuple[int, int],
        expected_dims: tuple[int, int],
        tolerance: int = 1,
    ) -> bool:
        """Return whether bbox dimensions match expected dimensions."""
        return (
            abs(bbox_dims[0] - expected_dims[0]) <= tolerance
            and abs(bbox_dims[1] - expected_dims[1]) <= tolerance
        )

    def _update_char_dims(self, char: str, dims: tuple[int, int]) -> None:
        """Update char_dims dictionary and save.

        Arguments:
            char: Character to update
            dims: Expected dimensions
        """
        self.char_dims[char] = dims
        self._save_char_dims(self.char_dims, self.char_dims_file_path)

    @staticmethod
    def _format_message(
        subtitle_index: int | None,
        text: str,
        message: str,
    ) -> str:
        """Format a validation message."""
        if subtitle_index is None:
            return f"{text} - {message}"
        return f"Subtitle {subtitle_index:04d}: {text} - {message}"

    @staticmethod
    def _load_char_dims(
        file_path: Path,
    ) -> dict[str, tuple[int, int]]:
        """Load character dimensions from file.

        Arguments:
            file_path: Path to file
        Returns:
            Character dimension map
        """
        arr = np.genfromtxt(file_path, delimiter=",", dtype=str, encoding="utf-8")
        if arr.size == 0:
            return {}
        if arr.ndim == 1:
            arr = np.array([arr])
        char_dims = {}
        for row in arr:
            char = row[0]
            width = int(row[1])
            height = int(row[2])
            char_dims[char] = (width, height)
        info(f"Loaded {file_path}")
        return char_dims

    @staticmethod
    def _save_char_dims(
        char_dims: dict[str, tuple[int, int]],
        file_path: Path,
    ):
        """Save character dimensions to file.

        Arguments:
            char_dims: Character dimension map to save
            file_path: Path to file
        """
        rows = [[char, dims[0], dims[1]] for char, dims in sorted(char_dims.items())]
        if rows:
            arr = np.array(rows, dtype=object)
            np.savetxt(file_path, arr, delimiter=",", fmt="%s", encoding="utf-8")
        else:
            file_path.write_text("", encoding="utf-8")
        info(f"Saved {file_path}")

    def _apply_known_merges(  # noqa: PLR0912, PLR0915
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
