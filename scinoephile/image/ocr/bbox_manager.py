#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

import ast
import csv
from logging import info, warning
from pathlib import Path

import numpy as np

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.text import whitespace_chars
from scinoephile.image.drawing import get_img_with_bboxes

from .types import OcrSubtitle

__all__ = ["BboxManager"]


class BboxManager:
    """Manages bboxes around characters."""

    single_bbox_file_path = package_root / "data" / "ocr" / "single_bbox.csv"
    """Path to file containing expected single bbox widths and heights."""
    single_bbox: dict[str, tuple[int, int]] = {}
    """Expected single bbox widths and heights keyed by character."""
    double_bbox_file_path = package_root / "data" / "ocr" / "double_bbox.csv"
    """Path to file containing specs for sets of two bboxes that should be merged."""
    double_bbox: dict[tuple[int, int, int, int, int], str] = {}
    """Dimensions and gaps between sets of two bboxes that should be merged."""
    triple_bbox_file_path = package_root / "data" / "ocr" / "triple_bbox.csv"
    """Path to file containing specs for sets of three bboxes that should be merged."""
    triple_bbox: dict[tuple[int, int, int, int, int, int, int, int], str] = {}
    """Dimensions and gaps between sets of three bboxes that should be merged."""
    quadruple_bbox_file_path = package_root / "data" / "ocr" / "quadruple_bbox.csv"
    """Path to file containing specs for sets of four bboxes that should be merged."""
    quadruple_bbox: dict[tuple[int, ...], str] = {}
    """Dimensions and gaps between sets of four bboxes that should be merged."""
    quintuple_bbox_file_path = package_root / "data" / "ocr" / "quintuple_bbox.csv"
    """Path to file containing specs for sets of five bboxes that should be merged."""
    quintuple_bbox: dict[tuple[int, ...], str] = {}
    """Dimensions and gaps between sets of five bboxes that should be merged."""

    def __init__(self):
        """Initialize."""
        if self.single_bbox_file_path.exists():
            self.single_bbox = self._load_single_bbox(self.single_bbox_file_path)
            self._save_single_bbox(self.single_bbox, self.single_bbox_file_path)
        if self.double_bbox_file_path.exists():
            self.double_bbox = self._load_merge_dict(self.double_bbox_file_path, 6)
            self._save_merge_dict(self.double_bbox, self.double_bbox_file_path)
        if self.triple_bbox_file_path.exists():
            self.triple_bbox = self._load_merge_dict(self.triple_bbox_file_path, 9)
            self._save_merge_dict(self.triple_bbox, self.triple_bbox_file_path)
        if self.quadruple_bbox_file_path.exists():
            self.quadruple_bbox = self._load_merge_dict(
                self.quadruple_bbox_file_path, 12
            )
            self._save_merge_dict(self.quadruple_bbox, self.quadruple_bbox_file_path)
        if self.quintuple_bbox_file_path.exists():
            self.quintuple_bbox = self._load_merge_dict(
                self.quintuple_bbox_file_path, 15
            )
            self._save_merge_dict(self.quintuple_bbox, self.quintuple_bbox_file_path)

    @property
    def double_bbox_chars(self):
        """Characters that are known to potentially be spread across two bboxes."""
        return set(char for chars in self.double_bbox.values() for char in chars)

    @property
    def triple_bbox_chars(self):
        """Characters that are known to potentially be spread across three bboxes."""
        return set(char for chars in self.triple_bbox.values() for char in chars)

    @property
    def quadruple_bbox_chars(self):
        """Characters that are known to potentially be spread across four bboxes."""
        return set(char for chars in self.quadruple_bbox.values() for char in chars)

    @property
    def quintuple_bbox_chars(self):
        """Characters that are known to potentially be spread across five bboxes."""
        return set(char for chars in self.quintuple_bbox.values() for char in chars)

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
        bboxes = self._get_initial_bboxes(subtitle)
        merged_bboxes, _ = self._merge_and_validate_char_bboxes(
            subtitle, bboxes, sub_idx=None
        )
        return merged_bboxes

    def validate_char_bboxes(
        self,
        subtitle: OcrSubtitle,
        sub_idx: int | None = None,
        interactive: bool = False,
    ) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            subtitle: Subtitle to validate
            sub_idx: optional subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            List of validation messages
        """
        bboxes = subtitle.bboxes
        if bboxes is None:
            bboxes = self._get_initial_bboxes(subtitle)

        merged_bboxes, messages = self._merge_and_validate_char_bboxes(
            subtitle,
            bboxes,
            sub_idx=sub_idx,
            interactive=interactive,
        )
        subtitle.bboxes = merged_bboxes
        return messages

    def _get_initial_bboxes(
        self, subtitle: OcrSubtitle
    ) -> list[tuple[int, int, int, int]]:
        """Get initial bboxes from white interior pixels.

        Arguments:
            subtitle: Subtitle for which to get bboxes
        Returns:
            Initial bboxes before character-level merging
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

        return bboxes

    def _merge_and_validate_char_bboxes(  # noqa: PLR0912, PLR0915
        self,
        subtitle: OcrSubtitle,
        bboxes: list[tuple[int, int, int, int]],
        sub_idx: int | None = None,
        interactive: bool = False,
    ) -> tuple[list[tuple[int, int, int, int]], list[str]]:
        """Merge bboxes per character and collect validation messages.

        Arguments:
            subtitle: Subtitle to validate
            bboxes: Initial bboxes to validate and merge
            sub_idx: optional subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            Merged bboxes and validation messages
        """
        messages = []
        text = subtitle.text
        merged_bboxes: list[tuple[int, int, int, int]] = []
        bbox_i = 0
        char_i = 0
        char_sub_idx = 0
        while char_i < len(text):
            char = text[char_i]
            if char in whitespace_chars:
                char_i += 1
                continue
            char_sub_idx += 1
            if bbox_i >= len(bboxes):
                messages.append(
                    self._format_message(
                        sub_idx,
                        char_sub_idx,
                        text,
                        f"ran out of bboxes at character '{char}'.",
                    )
                )
                break

            expected = self._get_expected_single_bbox(char)
            bbox = bboxes[bbox_i]
            bbox_dims = self._get_bbox_dims(bbox)

            fuzzy_expected = self._get_fuzzy_single_bbox(char, bbox_dims)
            if expected is not None and self._dims_match(bbox_dims, expected):
                merged_bboxes.append(bbox)
                bbox_i += 1
                char_i += 1
                continue
            if fuzzy_expected is not None:
                messages.append(
                    self._format_message(
                        sub_idx,
                        char_sub_idx,
                        text,
                        f"accepted fuzzy dims for '{char}' as {bbox_dims}.",
                    )
                )
                self._update_single_bbox(char, bbox_dims)
                merged_bboxes.append(bbox)
                bbox_i += 1
                char_i += 1
                continue

            if bbox_i <= len(bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)
                merged_dims = self._get_bbox_dims(merged_bbox)
                if key in self.double_bbox and char in self.double_bbox[key]:
                    self._update_double_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 2
                    char_i += 1
                    continue
                fuzzy_key = self._get_fuzzy_merge_key(self.double_bbox, key, char)
                if fuzzy_key is not None:
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"accepted fuzzy merge-two for '{char}' as {merged_dims}.",
                        )
                    )
                    self._update_double_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 2
                    char_i += 1
                    continue
                if expected is not None and self._dims_match(merged_dims, expected):
                    self._update_double_bbox(key, char)
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"merged two bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 2
                    char_i += 1
                    continue

            if bbox_i <= len(bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)
                merged_dims = self._get_bbox_dims(merged_bbox)
                if key in self.triple_bbox and char in self.triple_bbox[key]:
                    self._update_triple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 3
                    char_i += 1
                    continue
                fuzzy_key = self._get_fuzzy_merge_key(self.triple_bbox, key, char)
                if fuzzy_key is not None:
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"accepted fuzzy merge-three for '{char}' as "
                            f"{merged_dims}.",
                        )
                    )
                    self._update_triple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 3
                    char_i += 1
                    continue
                if expected is not None and self._dims_match(merged_dims, expected):
                    self._update_triple_bbox(key, char)
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"merged three bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 3
                    char_i += 1
                    continue

            if bbox_i <= len(bboxes) - 4:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 4)
                merged_dims = self._get_bbox_dims(merged_bbox)
                if key in self.quadruple_bbox and char in self.quadruple_bbox[key]:
                    self._update_quadruple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 4
                    char_i += 1
                    continue
                fuzzy_key = self._get_fuzzy_merge_key(self.quadruple_bbox, key, char)
                if fuzzy_key is not None:
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"accepted fuzzy merge-four for '{char}' as {merged_dims}.",
                        )
                    )
                    self._update_quadruple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 4
                    char_i += 1
                    continue
                if expected is not None and self._dims_match(merged_dims, expected):
                    self._update_quadruple_bbox(key, char)
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"merged four bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 4
                    char_i += 1
                    continue

            if bbox_i <= len(bboxes) - 5:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 5)
                merged_dims = self._get_bbox_dims(merged_bbox)
                if key in self.quintuple_bbox and char in self.quintuple_bbox[key]:
                    self._update_quintuple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 5
                    char_i += 1
                    continue
                fuzzy_key = self._get_fuzzy_merge_key(self.quintuple_bbox, key, char)
                if fuzzy_key is not None:
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"accepted fuzzy merge-five for '{char}' as {merged_dims}.",
                        )
                    )
                    self._update_quintuple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 5
                    char_i += 1
                    continue
                if expected is not None and self._dims_match(merged_dims, expected):
                    self._update_quintuple_bbox(key, char)
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"merged five bboxes for '{char}' into {merged_dims}.",
                        )
                    )
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 5
                    char_i += 1
                    continue

            if expected is None:
                accepted = self._confirm_bbox_dims(
                    subtitle,
                    bbox,
                    char,
                    bbox_dims,
                    interactive,
                )
                if accepted:
                    self._update_single_bbox(char, bbox_dims)
                    messages.append(
                        self._format_message(
                            sub_idx,
                            char_sub_idx,
                            text,
                            f"added dims for '{char}' as {bbox_dims}.",
                        )
                    )
                    merged_bboxes.append(bbox)
                    bbox_i += 1
                    char_i += 1
                    continue

                if bbox_i <= len(bboxes) - 2:
                    key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)
                    merged_dims = self._get_bbox_dims(merged_bbox)
                    accepted = self._confirm_bbox_dims(
                        subtitle,
                        merged_bbox,
                        char,
                        merged_dims,
                        interactive,
                        merge_count=2,
                    )
                    if accepted:
                        self._update_double_bbox(key, char)
                        messages.append(
                            self._format_message(
                                sub_idx,
                                char_sub_idx,
                                text,
                                f"merged two bboxes for '{char}' into {merged_dims}.",
                            )
                        )
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 2
                        char_i += 1
                        continue

                if bbox_i <= len(bboxes) - 3:
                    key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)
                    merged_dims = self._get_bbox_dims(merged_bbox)
                    accepted = self._confirm_bbox_dims(
                        subtitle,
                        merged_bbox,
                        char,
                        merged_dims,
                        interactive,
                        merge_count=3,
                    )
                    if accepted:
                        self._update_triple_bbox(key, char)
                        messages.append(
                            self._format_message(
                                sub_idx,
                                char_sub_idx,
                                text,
                                f"merged three bboxes for '{char}' into {merged_dims}.",
                            )
                        )
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 3
                        char_i += 1
                        continue

                if bbox_i <= len(bboxes) - 4:
                    key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 4)
                    merged_dims = self._get_bbox_dims(merged_bbox)
                    accepted = self._confirm_bbox_dims(
                        subtitle,
                        merged_bbox,
                        char,
                        merged_dims,
                        interactive,
                        merge_count=4,
                    )
                    if accepted:
                        self._update_quadruple_bbox(key, char)
                        messages.append(
                            self._format_message(
                                sub_idx,
                                char_sub_idx,
                                text,
                                f"merged four bboxes for '{char}' into {merged_dims}.",
                            )
                        )
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 4
                        char_i += 1
                        continue

                if bbox_i <= len(bboxes) - 5:
                    key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 5)
                    merged_dims = self._get_bbox_dims(merged_bbox)
                    accepted = self._confirm_bbox_dims(
                        subtitle,
                        merged_bbox,
                        char,
                        merged_dims,
                        interactive,
                        merge_count=5,
                    )
                    if accepted:
                        self._update_quintuple_bbox(key, char)
                        messages.append(
                            self._format_message(
                                sub_idx,
                                char_sub_idx,
                                text,
                                f"merged five bboxes for '{char}' into {merged_dims}.",
                            )
                        )
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 5
                        char_i += 1
                        continue

            messages.append(
                self._format_message(
                    sub_idx,
                    char_sub_idx,
                    text,
                    f"bbox dims {bbox_dims} for '{char}' do not match "
                    f"expected {expected}.",
                )
            )
            merged_bboxes.append(bbox)
            bbox_i += 1
            char_i += 1

        if bbox_i < len(bboxes):
            merged_bboxes.extend(bboxes[bbox_i:])
            messages.append(
                self._format_message(
                    sub_idx,
                    None,
                    text,
                    f"{len(bboxes) - bbox_i} extra bboxes remain.",
                )
            )

        return merged_bboxes, messages

    @staticmethod
    def _get_white_mask(
        grayscale: np.ndarray,
        alpha: np.ndarray,
        fill_color: int,
        outline_color: int,
    ) -> np.ndarray:
        """Get a white interior mask from grayscale/alpha arrays.

        Arguments:
            grayscale: grayscale values
            alpha: alpha values
            fill_color: fill color used in rendering
            outline_color: outline color used in rendering
        Returns:
            Boolean mask of white interior pixels
        """
        del outline_color
        tolerance = 10
        lower = max(0, fill_color - tolerance)
        upper = min(255, fill_color + tolerance)
        return (alpha > 0) & (grayscale >= lower) & (grayscale <= upper)

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
        if img.mode == "L":
            alpha = np.ones(arr.shape, dtype=np.uint8) * 255
            return arr, alpha
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

    def _get_expected_single_bbox(self, char: str) -> tuple[int, int] | None:
        """Get expected bbox dimensions for a character.

        Arguments:
            char: Character to check
        Returns:
            Expected (width, height)
        """
        if char in self.single_bbox:
            return self.single_bbox[char]
        return None

    def _get_fuzzy_single_bbox(
        self, char: str, dims: tuple[int, int], tolerance: int = 1
    ) -> tuple[int, int] | None:
        """Get a fuzzy-matched expected bbox for a character.

        Arguments:
            char: Character to check
            dims: Dimensions to match against
            tolerance: Allowed difference per dimension
        Returns:
            Matching dimensions if found
        """
        expected = self.single_bbox.get(char)
        if expected is None:
            return None
        if (
            abs(dims[0] - expected[0]) <= tolerance
            and abs(dims[1] - expected[1]) <= tolerance
        ):
            return expected
        return None

    def _get_fuzzy_merge_key(
        self,
        merge_dict: dict[tuple[int, ...], str],
        key: tuple[int, ...],
        char: str,
        tolerance: int = 1,
    ) -> tuple[int, ...] | None:
        """Return a fuzzy-matched merge key for a character.

        Arguments:
            merge_dict: Merge dictionary to search
            key: Key to match
            char: Character to match
            tolerance: Allowed difference per dimension
        Returns:
            Matching key if found
        """
        for known_key, chars in merge_dict.items():
            if char not in chars:
                continue
            if all(abs(known_key[i] - key[i]) <= tolerance for i in range(len(key))):
                return known_key
        return None

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

    def _update_single_bbox(self, char: str, dims: tuple[int, int]) -> None:
        """Update single_bbox dictionary and save.

        Arguments:
            char: Character to update
            dims: Expected dimensions
        """
        self.single_bbox[char] = dims
        self._save_single_bbox(self.single_bbox, self.single_bbox_file_path)

    def _confirm_bbox_dims(
        self,
        subtitle: OcrSubtitle,
        bbox: tuple[int, int, int, int],
        char: str,
        dims: tuple[int, int],
        interactive: bool,
        merge_count: int = 1,
    ) -> bool:
        """Confirm bbox dims interactively.

        Arguments:
            subtitle: Subtitle containing the character
            bbox: Bounding box to confirm
            char: Character under review
            dims: Bounding box dimensions
            interactive: Whether to prompt user
            merge_count: Number of merged bboxes represented
        Returns:
            Whether the bbox is accepted
        """
        if not interactive:
            return False
        annotated = get_img_with_bboxes(subtitle.img, [bbox])
        annotated.show()
        merge_note = "merged " if merge_count > 1 else ""
        response = input(f"Accept {merge_note}bbox dims {dims} for '{char}'? (y/n): ")
        return response.lower().startswith("y")

    @staticmethod
    def _format_message(
        sub_idx: int | None,
        char_sub_idx: int | None,
        text: str,
        message: str,
    ) -> str:
        """Format a validation message."""
        if sub_idx is None:
            return f"{text} - {message}"
        if char_sub_idx is None:
            return f"Sub {sub_idx + 1:04d}: {text} - {message}"
        return f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - {message}"

    @staticmethod
    def _load_single_bbox(
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
        single_bbox = {}
        for row in arr:
            char = row[0]
            width = int(row[1])
            height = int(row[2])
            single_bbox[char] = (width, height)
        info(f"Loaded {file_path}")
        return single_bbox

    @staticmethod
    def _save_single_bbox(
        single_bbox: dict[str, tuple[int, int]],
        file_path: Path,
    ):
        """Save character dimensions to file.

        Arguments:
            single_bbox: Character dimension map to save
            file_path: Path to file
        """
        rows = [[char, dims[0], dims[1]] for char, dims in sorted(single_bbox.items())]
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

            # Merge set of five bboxes if appropriate
            if bbox_i <= len(bboxes) - 5:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 5)

                # Dimensions are known to be mergable
                if key in self.quintuple_bbox:
                    # Dimensions and char match
                    if char in self.quintuple_bbox[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 5
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.quintuple_bbox_chars:
                        self._update_quintuple_bbox(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 5
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_quintuple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 5
                    char_i = self._get_next_char_i(text, char_i)
                    continue

            # Merge set of four bboxes if appropriate
            if bbox_i <= len(bboxes) - 4:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 4)

                # Dimensions are known to be mergable
                if key in self.quadruple_bbox:
                    # Dimensions and char match
                    if char in self.quadruple_bbox[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 4
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.quadruple_bbox_chars:
                        self._update_quadruple_bbox(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 4
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_quadruple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 4
                    char_i = self._get_next_char_i(text, char_i)
                    continue

            # Merge set of three bboxes if appropriate
            if bbox_i <= len(bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)

                # Dimensions are known to be mergable
                if key in self.triple_bbox:
                    # Dimensions and char match
                    if char in self.triple_bbox[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 3
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.triple_bbox_chars:
                        self._update_triple_bbox(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 3
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_triple_bbox(key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += 3
                    char_i = self._get_next_char_i(text, char_i)
                    continue

            # Merge set of two bboxes if appropriate
            if bbox_i <= len(bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)

                # Dimensions are known to be mergable
                if key in self.double_bbox:
                    # Dimensions and char match
                    if char in self.double_bbox[key]:
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 2
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                    # Dimensions match, and char is known as mergable
                    if char in self.double_bbox_chars:
                        self._update_double_bbox(key, char)
                        merged_bboxes.append(merged_bbox)
                        bbox_i += 2
                        char_i = self._get_next_char_i(text, char_i)
                        continue

                # Dimensions are close to those known to be mergable for char
                fuzzy_matches = self._fuzzy_match_key(key)
                if char in fuzzy_matches:
                    self._update_double_bbox(key, char)
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
        """Fuzzy match keys in triple_bbox and double_bbox.

        Arguments:
            key: Key to match
        """
        length = len(key)
        if length == 5:
            merge_dict = self.double_bbox
        elif length == 8:
            merge_dict = self.triple_bbox
        elif length == 11:
            merge_dict = self.quadruple_bbox
        elif length == 14:
            merge_dict = self.quintuple_bbox
        else:
            raise ScinoephileError(
                f"Key must be of length 5, 8, 11, or 14, not {len(key)}"
            )

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

            # If char is known to be a quintuple_bbox, check key for next five bboxes
            if char in self.quintuple_bbox_chars and bbox_i <= len(bboxes) - 5:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 5)
                response = input(
                    f"{char} may be split across five bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}), "
                    f"{key[5]}, ({key[6]}, {key[7]}), {key[8]}, "
                    f"({key[9]}, {key[10]})). "
                    f"Do you want to update quintuple_bbox? (y/n):"
                )
                if response.lower() == "y":
                    self._update_quintuple_bbox(key, char)
                    bbox_i += 5

            # If char is known to be a quadruple_bbox, check key for next four bboxes
            if char in self.quadruple_bbox_chars and bbox_i <= len(bboxes) - 4:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 4)
                response = input(
                    f"{char} may be split across four bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}), "
                    f"{key[5]}, ({key[6]}, {key[7]}), {key[8]}, "
                    f"({key[9]}, {key[10]})). "
                    f"Do you want to update quadruple_bbox? (y/n):"
                )
                if response.lower() == "y":
                    self._update_quadruple_bbox(key, char)
                    bbox_i += 4

            # If char is known to be a triple_bbox, check key for next three bboxes
            if char in self.triple_bbox_chars and bbox_i <= len(bboxes) - 3:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 3)
                response = input(
                    f"{char} may be split across three bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}), "
                    f"{key[5]}, ({key[6]}, {key[7]})). "
                    f"Do you want to update triple_bbox? (y/n):"
                )
                if response.lower() == "y":
                    self._update_triple_bbox(key, char)
                    bbox_i += 3

            # If char is known to be a double_bbox, check key for next two bboxes
            if char in self.double_bbox_chars and bbox_i <= len(bboxes) - 2:
                key, merged_bbox = self._get_key_and_merged_bbox(bboxes, bbox_i, 2)
                response = input(
                    f"{char} may be split across two bboxes with dimensions "
                    f"(({key[0]}, {key[1]}), {key[2]}, ({key[3]}, {key[4]}). "
                    f"Do you want to update double_bbox? (y/n):"
                )
                if response.lower() == "y":
                    self._update_double_bbox(key, char)
                    bbox_i += 2

            char_i = self._get_next_char_i(text, char_i)
            bbox_i += 1

    def _update_triple_bbox(
        self,
        key: tuple[int, int, int, int, int, int, int, int],
        value: str,
    ):
        """Update triple_bbox dictionary.

        Arguments:
            key: Key including width, height, gap, width, height, gap, width, height
            value: Character
        """
        if key in self.triple_bbox:
            if value in self.triple_bbox[key]:
                return
            self.triple_bbox[key] += value
        else:
            self.triple_bbox[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to triple_bbox")
        self._save_merge_dict(self.triple_bbox, self.triple_bbox_file_path)

    def _update_quadruple_bbox(
        self,
        key: tuple[int, ...],
        value: str,
    ):
        """Update quadruple_bbox dictionary.

        Arguments:
            key: Key including width, height, gap pairs for four bboxes
            value: Character
        """
        if key in self.quadruple_bbox:
            if value in self.quadruple_bbox[key]:
                return
            self.quadruple_bbox[key] += value
        else:
            self.quadruple_bbox[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to quadruple_bbox")
        self._save_merge_dict(self.quadruple_bbox, self.quadruple_bbox_file_path)

    def _update_quintuple_bbox(
        self,
        key: tuple[int, ...],
        value: str,
    ):
        """Update quintuple_bbox dictionary.

        Arguments:
            key: Key including width, height, gap pairs for five bboxes
            value: Character
        """
        if key in self.quintuple_bbox:
            if value in self.quintuple_bbox[key]:
                return
            self.quintuple_bbox[key] += value
        else:
            self.quintuple_bbox[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to quintuple_bbox")
        self._save_merge_dict(self.quintuple_bbox, self.quintuple_bbox_file_path)

    def _update_double_bbox(
        self,
        key: tuple[int, int, int, int, int],
        value: str,
    ):
        """Update double_bbox dictionary.

        Arguments:
            key: Key including width, height, gap, width, height
            value: Character
        """
        if key in self.double_bbox:
            if value in self.double_bbox[key]:
                return
            self.double_bbox[key] += value
        else:
            self.double_bbox[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to double_bbox")
        self._save_merge_dict(self.double_bbox, self.double_bbox_file_path)

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
        expected_len: int | None = None,
    ) -> dict[tuple[int, ...], str]:
        """Load merge dict from file.

        Arguments:
            file_path: path to file
            expected_len: expected number of columns per row
        """
        merge_dict = {}
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    parts = ast.literal_eval(stripped)
                except (ValueError, SyntaxError):
                    warning(
                        f"Skipping {file_path} line {line_num}: could not parse list."
                    )
                    continue
            else:
                parts = [part.strip() for part in stripped.split(",")]
            if expected_len is None:
                expected_len = len(parts)
            if len(parts) != expected_len:
                warning(
                    f"Skipping {file_path} line {line_num}: "
                    f"expected {expected_len} columns, got {len(parts)}."
                )
                continue
            try:
                key = tuple(map(int, parts[1:]))
            except ValueError:
                warning(
                    f"Skipping {file_path} line {line_num}: "
                    "could not parse bbox dimensions."
                )
                continue
            value = parts[0]
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
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}")
