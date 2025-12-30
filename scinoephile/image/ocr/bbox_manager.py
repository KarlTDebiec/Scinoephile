#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

import ast
import csv
from dataclasses import dataclass, field
from logging import info, warning
from pathlib import Path

import numpy as np

from scinoephile.common import package_root
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.colors import (
    get_fill_and_outline_colors,
    get_grayscale_and_alpha,
)
from scinoephile.image.subtitles import ImageSubtitle

from .drawing import get_img_with_bboxes

__all__ = ["BboxManager"]


@dataclass(slots=True)
class CharDimsSpec:
    """Char dims spec for grouped bboxes."""

    count: int
    """Number of bboxes merged."""
    file_path: Path
    """Path to char dims csv file."""
    word_label: str
    """Word label for messages."""
    name_label: str
    """Name label for logging."""
    char_dims: dict[tuple[int, ...], str] = field(default_factory=dict)
    """Characters keyed by bbox dimensions and gaps."""


class BboxManager:
    """Manages bboxes around characters."""

    def __init__(self):
        """Initialize."""
        self.char_dims_specs = [
            CharDimsSpec(
                count=1,
                file_path=package_root / "data" / "ocr" / "char_dims_1.csv",
                word_label="one",
                name_label="single",
            ),
            CharDimsSpec(
                count=2,
                file_path=package_root / "data" / "ocr" / "char_dims_2.csv",
                word_label="two",
                name_label="double",
            ),
            CharDimsSpec(
                count=3,
                file_path=package_root / "data" / "ocr" / "char_dims_3.csv",
                word_label="three",
                name_label="triple",
            ),
            CharDimsSpec(
                count=4,
                file_path=package_root / "data" / "ocr" / "char_dims_4.csv",
                word_label="four",
                name_label="quadruple",
            ),
            CharDimsSpec(
                count=5,
                file_path=package_root / "data" / "ocr" / "char_dims_5.csv",
                word_label="five",
                name_label="quintuple",
            ),
        ]
        for spec in self.char_dims_specs:
            if spec.file_path.exists():
                expected_len = 3 * spec.count
                spec.char_dims = self._load_char_dims(spec.file_path, expected_len)
                self._save_char_dims(spec.char_dims, spec.file_path)

    def validate_bboxes(
        self,
        sub: ImageSubtitle,
        sub_idx: int,
        interactive: bool = False,
    ) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            sub: Subtitle to validate
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            List of validation messages
        """
        bboxes = sub.bboxes
        if bboxes is None:
            bboxes = self._get_raw_bboxes(sub)

        merged_bboxes, messages = self._merge_and_validate_bboxes(
            sub,
            bboxes,
            sub_idx=sub_idx,
            interactive=interactive,
        )
        sub.bboxes = merged_bboxes
        return messages

    def _get_raw_bboxes(self, sub: ImageSubtitle) -> list[Bbox]:
        """Get raw bboxes from white interior pixels.

        Arguments:
            sub: subtitle for which to get bboxes
        Returns:
            raw Bboxes
        """
        grayscale, alpha = get_grayscale_and_alpha(sub.img)
        fill_color, _outline = get_fill_and_outline_colors(grayscale, alpha)
        white_mask = self._get_white_mask(grayscale, alpha, fill_color)

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
        bboxes: list[Bbox] = []
        for x1, x2 in sections:
            section = white_mask[:, x1:x2]
            white_pixels = np.sum(section, axis=1)
            y1 = int(np.argmax(white_pixels > 0))
            y2 = int(len(white_pixels) - np.argmax(white_pixels[::-1] > 0) - 1)
            bboxes.append(Bbox(x1=x1, x2=x2, y1=y1, y2=y2))

        return bboxes

    def _merge_and_validate_bboxes(  # noqa: PLR0912, PLR0915
        self,
        subtitle: ImageSubtitle,
        bboxes: list[Bbox],
        sub_idx: int,
        interactive: bool = False,
    ) -> tuple[list[Bbox], list[str]]:
        """Merge bboxes per character and collect validation messages.

        Arguments:
            subtitle: Subtitle to validate
            bboxes: Initial bboxes to validate and merge
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            Merged bboxes and validation messages
        """
        messages = []
        text = subtitle.text

        merged_bboxes: list[Bbox] = []
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
                message = f"ran out of bboxes at '{char}'."
                messages.append(
                    f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - {message}"
                )
                break

            expected = self._get_expected_dims(char)
            bbox = bboxes[bbox_i]
            bbox_dims = (bbox.width, bbox.height)

            merged = False
            for spec in self.char_dims_specs:
                if bbox_i > len(bboxes) - spec.count:
                    continue
                key, merged_bbox = self._get_key_and_merged_bbox(
                    bboxes, bbox_i, spec.count
                )
                merged_dims = (merged_bbox.width, merged_bbox.height)
                if key in spec.char_dims and char in spec.char_dims[key]:
                    self._update_char_dims(spec, key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += spec.count
                    char_i += 1
                    merged = True
                    break
                fuzzy_key = self._get_fuzzy_merge_key(spec.char_dims, key, char)
                if fuzzy_key is not None:
                    if spec.count == 1:
                        messages.append(
                            f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - "
                            f"accepted fuzzy dims for '{char}' as {bbox_dims}."
                        )
                    else:
                        messages.append(
                            f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: "
                            f"{text} - accepted fuzzy merge-{spec.word_label} for "
                            f"'{char}' as {merged_dims}."
                        )
                    self._update_char_dims(spec, key, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += spec.count
                    char_i += 1
                    merged = True
                    break
                if (
                    spec.count > 1
                    and expected
                    and self._dims_match_any(merged_dims, expected)
                ):
                    self._update_char_dims(spec, key, char)
                    messages.append(
                        f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - "
                        f"merged {spec.word_label} bboxes for '{char}' into "
                        f"{merged_dims}."
                    )
                    merged_bboxes.append(merged_bbox)
                    bbox_i += spec.count
                    char_i += 1
                    merged = True
                    break
            if merged:
                continue

            if not expected:
                accepted = self._confirm_bbox_dims(
                    subtitle,
                    bbox,
                    char,
                    bbox_dims,
                    interactive,
                )
                if accepted:
                    messages.append(
                        f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - "
                        f"added dims for '{char}' as {bbox_dims}."
                    )
                    self._update_char_dims(
                        self.char_dims_specs[0], (bbox_dims[0], bbox_dims[1]), char
                    )
                    merged_bboxes.append(bbox)
                    bbox_i += 1
                    char_i += 1
                    continue

                for spec in self.char_dims_specs:
                    if bbox_i > len(bboxes) - spec.count:
                        continue
                    key, merged_bbox = self._get_key_and_merged_bbox(
                        bboxes, bbox_i, spec.count
                    )
                    merged_dims = (merged_bbox.width, merged_bbox.height)
                    accepted = self._confirm_bbox_dims(
                        subtitle,
                        merged_bbox,
                        char,
                        merged_dims,
                        interactive,
                        merge_count=spec.count,
                    )
                    if accepted:
                        self._update_char_dims(spec, key, char)
                        messages.append(
                            f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: "
                            f"{text} - merged {spec.word_label} bboxes for '{char}' "
                            f"into {merged_dims}."
                        )
                        merged_bboxes.append(merged_bbox)
                        bbox_i += spec.count
                        char_i += 1
                        merged = True
                        break
                if merged:
                    continue

            messages.append(
                f"Sub {sub_idx + 1:04d} Char {char_sub_idx:02d}: {text} - bbox dims "
                f"{bbox_dims} for '{char}' do not match expected {expected or None}."
            )
            merged_bboxes.append(bbox)
            bbox_i += 1
            char_i += 1

        if bbox_i < len(bboxes):
            merged_bboxes.extend(bboxes[bbox_i:])
            messages.append(
                f"Sub {sub_idx + 1:04d}: {text} - "
                f"{len(bboxes) - bbox_i} extra bboxes remain."
            )

        return merged_bboxes, messages

    @staticmethod
    def _get_white_mask(
        grayscale: np.ndarray,
        alpha: np.ndarray,
        fill_color: int,
    ) -> np.ndarray:
        """Get a white interior mask from grayscale/alpha arrays.

        Arguments:
            grayscale: grayscale values
            alpha: alpha values
            fill_color: fill color used in rendering
        Returns:
            Boolean mask of white interior pixels
        """
        tolerance = 10
        lower = max(0, fill_color - tolerance)
        upper = min(255, fill_color + tolerance)
        return (alpha > 0) & (grayscale >= lower) & (grayscale <= upper)

    def _get_expected_dims(self, char: str) -> list[tuple[int, int]]:
        """Get expected bbox dimensions for a character.

        Arguments:
            char: Character to check
        Returns:
            Expected (width, height) pairs
        """
        spec = self.char_dims_specs[0]
        return [
            (key[0], key[1]) for key, chars in spec.char_dims.items() if char in chars
        ]

    def _get_fuzzy_merge_key(
        self,
        char_dims: dict[tuple[int, ...], str],
        key: tuple[int, ...],
        char: str,
        tolerance: int = 1,
    ) -> tuple[int, ...] | None:
        """Return a fuzzy-matched key for a character.

        Arguments:
            char_dims: Char dims dictionary to search
            key: Key to match
            char: Character to match
            tolerance: Allowed difference per dimension
        Returns:
            Matching key if found
        """
        for known_key, chars in char_dims.items():
            if char not in chars:
                continue
            if all(abs(known_key[i] - key[i]) <= tolerance for i in range(len(key))):
                return known_key
        return None

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

    def _dims_match_any(
        self,
        bbox_dims: tuple[int, int],
        expected_dims: list[tuple[int, int]],
        tolerance: int = 1,
    ) -> bool:
        """Return whether bbox dims match any expected dimensions."""
        return any(
            self._dims_match(bbox_dims, expected, tolerance=tolerance)
            for expected in expected_dims
        )

    def _update_char_dims(
        self, spec: CharDimsSpec, key: tuple[int, ...], value: str
    ) -> None:
        """Update char dims and save.

        Arguments:
            spec: Char dims spec to update
            key: Key including width, height, gap dimensions
            value: Character
        """
        if key in spec.char_dims:
            if value in spec.char_dims[key]:
                return
            spec.char_dims[key] += value
        else:
            spec.char_dims[key] = str(value)
        info(f"Added ({value}, {', '.join(map(str, key))}) to {spec.name_label}_bbox")
        self._save_char_dims(spec.char_dims, spec.file_path)

    def _confirm_bbox_dims(
        self,
        sub: ImageSubtitle,
        bbox: Bbox,
        char: str,
        dims: tuple[int, int],
        interactive: bool,
        merge_count: int = 1,
    ) -> bool:
        """Confirm bbox dims interactively.

        Arguments:
            sub: Subtitle containing the character
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
        annotated = get_img_with_bboxes(sub.img, [bbox])
        annotated.show()
        merge_note = "merged " if merge_count > 1 else ""
        response = input(f"Accept {merge_note}bbox dims {dims} for '{char}'? (y/n): ")
        return response.lower().startswith("y")

    @staticmethod
    def _get_key_and_merged_bbox(
        bboxes: list[Bbox],
        i: int,
        n: int,
    ) -> tuple[tuple[int, ...], Bbox]:
        """Get key and merged bbox from bboxes.

        Arguments:
            bboxes: Nascent list of bboxes
            i: Index of first bbox
            n: Number of bboxes whose merging is under consideration
        Returns:
            Key and merged bbox
        """
        bboxes_slice = bboxes[i : i + n]
        widths = [bbox.width for bbox in bboxes_slice]
        heights = [bbox.height for bbox in bboxes_slice]
        gaps = [
            bboxes_slice[i + 1].x1 - bboxes_slice[i].x2
            for i in range(len(bboxes_slice) - 1)
        ]
        key = tuple(
            [dim for group in zip(widths, heights, gaps + [0]) for dim in group][:-1]
        )
        merged_bbox = Bbox(
            x1=min(bbox.x1 for bbox in bboxes_slice),
            x2=max(bbox.x2 for bbox in bboxes_slice),
            y1=min(bbox.y1 for bbox in bboxes_slice),
            y2=max(bbox.y2 for bbox in bboxes_slice),
        )

        return key, merged_bbox

    @staticmethod
    def _load_char_dims(
        file_path: Path,
        expected_len: int | None = None,
    ) -> dict[tuple[int, ...], str]:
        """Load char dims dict from file.

        Arguments:
            file_path: path to file
            expected_len: expected number of columns per row
        """
        char_dims = {}
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
            if key in char_dims:
                char_dims[key] += value
            else:
                char_dims[key] = str(value)

        info(f"Loaded {file_path}")
        return char_dims

    @staticmethod
    def _save_char_dims(
        char_dims: dict[tuple[int, ...], str],
        file_path: Path,
    ):
        """Save char dims dict to file.

        Arguments:
            char_dims: Dictionary to save
            file_path: Path to file
        1st column: valuez
        """
        rows = []
        for key, value in char_dims.items():
            for char in value:
                rows.extend([[char] + list(key)])
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}")
