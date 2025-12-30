#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from logging import info
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
    char_dims: dict[str, list[tuple[int, ...]]] = field(default_factory=dict)
    """Acceptable bbox dimensions and gaps keyed by character."""


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
                spec.char_dims = self._load_char_dims(spec.file_path)
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
                dims_tuple, merged_bbox = self._get_key_and_merged_bbox(
                    bboxes, bbox_i, spec.count
                )
                merged_dims = (merged_bbox.width, merged_bbox.height)
                if dims_tuple in spec.char_dims.get(char, []):
                    self._update_char_dims(spec, dims_tuple, char)
                    merged_bboxes.append(merged_bbox)
                    bbox_i += spec.count
                    char_i += 1
                    merged = True
                    break
                fuzzy_dims = self._get_fuzzy_char_dims(spec.char_dims, dims_tuple, char)
                if fuzzy_dims is not None:
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
                    self._update_char_dims(spec, dims_tuple, char)
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
                    self._update_char_dims(spec, dims_tuple, char)
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
                    dims_tuple, merged_bbox = self._get_key_and_merged_bbox(
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
                        self._update_char_dims(spec, dims_tuple, char)
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
        return [tuple(dim[:2]) for dim in spec.char_dims.get(char, [])]

    def _get_fuzzy_char_dims(
        self,
        char_dims: dict[str, list[tuple[int, ...]]],
        dims_tuple: tuple[int, ...],
        char: str,
        tolerance: int = 1,
    ) -> tuple[int, ...] | None:
        """Return a fuzzy-matched key for a character.

        Arguments:
            char_dims: Char dims dictionary to search
            dims_tuple: Dimensions to match
            char: Character to match
            tolerance: Allowed difference per dimension
        Returns:
            Matching key if found
        """
        for known_key in char_dims.get(char, []):
            if all(
                abs(known_key[i] - dims_tuple[i]) <= tolerance
                for i in range(len(dims_tuple))
            ):
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
        self, spec: CharDimsSpec, dims_tuple: tuple[int, ...], char: str
    ) -> None:
        """Update char dims and save.

        Arguments:
            spec: Char dims spec to update
            dims_tuple: Dimensions including width, height, gap values
            char: Character
        """
        dims_list = spec.char_dims.setdefault(char, [])
        if dims_tuple in dims_list:
            return
        dims_list.append(dims_tuple)
        info(
            f"Added ({char}, {', '.join(map(str, dims_tuple))}) to "
            f"{spec.name_label}_bbox"
        )
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
    def _load_char_dims(file_path: Path) -> dict[str, list[tuple[int, ...]]]:
        """Load char dims from file.

        Arguments:
            file_path: path to file
        Returns:
            char dims
        """
        char_dims: dict[str, list[tuple[int, ...]]] = {}
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                char = row[0]
                dims = tuple(map(int, row[1:]))
                if char not in char_dims:
                    char_dims[char] = []
                char_dims[char].append(dims)

        info(f"Loaded {file_path}")
        return char_dims

    @staticmethod
    def _save_char_dims(char_dims: dict[str, list[tuple[int, ...]]], file_path: Path):
        """Save char dims dict to file.

        Arguments:
            char_dims: data to save
            file_path: path to file
        """
        rows = []
        for char, dims_list in char_dims.items():
            rows.extend([[char, *dims] for dims in dims_list])
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}")
