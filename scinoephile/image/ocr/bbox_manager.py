#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes around characters."""

from __future__ import annotations

import csv
from logging import info
from pathlib import Path

import numpy as np

from scinoephile.common import package_root
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox, get_merged_bbox
from scinoephile.image.colors import (
    get_fill_and_outline_colors,
    get_grayscale_and_alpha,
)
from scinoephile.image.subtitles import ImageSubtitle

from .drawing import get_img_with_bboxes

__all__ = ["BboxManager"]


class BboxManager:
    """Manages bboxes around characters."""

    def __init__(self):
        """Initialize."""
        # Set up data structure for characters in one or more bboxes
        self.char_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        """Data structure for characters in one or more bboxes.
        
        First key is the number of bboxes.
        Second key is the character.
        Values are a set of approved bbox width, heights, and gaps for that character.
        """
        for n in range(1, 6):
            file_path = self._char_dims_path(n)
            self.char_dims_by_n[n] = {}
            if file_path.exists():
                self.char_dims_by_n[n] = self._load_char_dims(file_path)

        # Set up data structures for bboxes that contain two or more characters
        self.char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        """Data structure for bboxes containing two or more characters.
        
        First key is the number of characters in the group.
        Second key is the character group.
        Values are a set of approved bbox width and heights for that character group.
        """
        file_path = self._char_grp_dims_path()
        if file_path.exists():
            char_grp_dims = self._load_char_dims(file_path)
            for char_grp, dims_set in char_grp_dims.items():
                n = len(char_grp)
                if n not in self.char_grp_dims_by_n:
                    self.char_grp_dims_by_n[n] = {}
                self.char_grp_dims_by_n[n][char_grp] = dims_set

    def validate_bboxes(
        self, sub: ImageSubtitle, sub_idx: int, interactive: bool = False
    ) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            list of validation messages
        """
        bboxes = sub.bboxes
        if bboxes is None:
            bboxes = self._get_raw_bboxes(sub)

        bboxes, messages = self._validate_bboxes(sub, bboxes, sub_idx, interactive)
        sub.bboxes = bboxes
        return messages

    def _get_raw_bboxes(self, sub: ImageSubtitle) -> list[Bbox]:  # noqa: PLR0912
        """Get raw bboxes from white interior pixels.

        Arguments:
            sub: subtitle for which to get bboxes
        Returns:
            raw bboxes
        """
        grayscale, alpha = get_grayscale_and_alpha(sub.img)
        fill_color, _outline = get_fill_and_outline_colors(grayscale, alpha)
        white_mask = self._get_white_mask(grayscale, alpha, fill_color)

        # Determine top and bottom of each line separated by whitespace
        lines = []
        line = None
        for i, white_pixels in enumerate(np.sum(white_mask, axis=1)):
            if white_pixels > 0:
                if line is None:
                    line = [i, i]
                else:
                    line[1] = i
            elif line is not None:
                lines.append(line)
                line = None
        if line is not None:
            lines.append(line)

        # Determine left and right of each section per line to get final bbox
        bboxes: list[Bbox] = []
        for y1, y2 in lines:
            line_mask = white_mask[y1:y2]
            sections = []
            section = None
            for i, white_pixels in enumerate(np.sum(line_mask, axis=0)):
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

            for x1, x2 in sections:
                section_mask = line_mask[:, x1:x2]
                white_pixels = np.sum(section_mask, axis=1)
                if np.max(white_pixels) == 0:
                    continue
                section_y1 = int(np.argmax(white_pixels > 0))
                section_y2 = int(
                    len(white_pixels) - np.argmax(white_pixels[::-1] > 0) - 1
                )
                bboxes.append(
                    Bbox(
                        x1=x1,
                        x2=x2,
                        y1=y1 + section_y1,
                        y2=y1 + section_y2,
                    )
                )

        return bboxes

    def _validate_bboxes(  # noqa: PLR0912, PLR0915
        self,
        sub: ImageSubtitle,
        bboxes: list[Bbox],
        sub_idx: int,
        interactive: bool = False,
    ) -> tuple[list[Bbox], list[str]]:
        """Merge bboxes per character and collect validation messages.

        Arguments:
            sub: subtitle to validate
            bboxes: initial bboxes to validate and merge
            sub_idx: subtitle index for logging
            interactive: whether to prompt user for confirmations
        Returns:
            merged bboxes and validation messages
        """
        messages = []
        text = sub.text

        merged_bboxes: list[Bbox] = []
        bbox_idx = 0
        char_idx = 0
        char_nonws_idx = 0

        while char_idx < len(text):
            char = text[char_idx]
            if char in whitespace_chars or char == "\n":
                char_idx += 1
                continue
            char_nonws_idx += 1
            if bbox_idx >= len(bboxes):
                messages.append(
                    f"Sub {sub_idx + 1:04d} Char {char_nonws_idx:02d} {text}: "
                    f"Ran out of bboxes at '{char}'"
                )
                break
            char_matched_to_bbox = False

            # Check if grouped chars are matched by previously-confirmed dims
            for n in self.char_grp_dims_by_n.keys():
                if char_idx + n > len(text):
                    continue
                char_grp = text[char_idx : char_idx + n]
                if any(c in whitespace_chars for c in char_grp) or "\n" in char_grp:
                    continue
                dims = (bboxes[bbox_idx].width, bboxes[bbox_idx].height)
                ok_dims = self.char_grp_dims_by_n[n].get(char_grp, set())

                # Exact match
                if dims in ok_dims:
                    merged_bboxes.append(bboxes[bbox_idx])
                    bbox_idx += 1
                    char_idx += n
                    char_matched_to_bbox = True
                    break

                # Fuzzy match
                for ok_dim in ok_dims:
                    diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                    max_diff = max(diffs)
                    if max_diff <= 2:
                        merged_bboxes.append(bboxes[bbox_idx])
                        bbox_idx += 1
                        char_idx += n
                        self._update_char_grp_dims(char_grp, dims)
                        char_matched_to_bbox = True
                        break
            if char_matched_to_bbox:
                continue

            # Check if char is matched by any previously-confirmed dims
            for n in self.char_dims_by_n.keys():
                if bbox_idx + n > len(bboxes):
                    continue
                dims = self._get_dims_tuple(bboxes[bbox_idx : bbox_idx + n])
                ok_dims = self.char_dims_by_n[n].get(char, set())

                # Exact match
                if dims in ok_dims:
                    merged_bboxes.append(
                        get_merged_bbox(bboxes[bbox_idx : bbox_idx + n])
                    )
                    bbox_idx += n
                    char_idx += 1
                    char_matched_to_bbox = True
                    break

                # Fuzzy match
                for ok_dim in ok_dims:
                    diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                    max_diff = max(diffs)
                    if max_diff <= 2:
                        merged_bboxes.append(
                            get_merged_bbox(bboxes[bbox_idx : bbox_idx + n])
                        )
                        bbox_idx += n
                        char_idx += 1
                        self._update_char_dims(char, dims)
                        char_matched_to_bbox = True
                        break
            if char_matched_to_bbox:
                continue

            # Prompt for confirmation if char is matched by dims
            for n in self.char_dims_by_n.keys():
                if bbox_idx + n > len(bboxes):
                    continue
                dims = self._get_dims_tuple(bboxes[bbox_idx : bbox_idx + n])

                approved = False
                grouped = False
                if interactive:
                    annotated = get_img_with_bboxes(
                        sub.img, bboxes[bbox_idx : bbox_idx + n]
                    )
                    annotated.show()
                    response = input(f"Accept '{char}' bbox dims {dims}? (y/n): ")
                    approved = response.lower().startswith("y")
                    if n == 1:
                        try:
                            group_size = int(response)
                            if group_size > 1:
                                grouped = True
                        except ValueError:
                            pass

                if approved:
                    merged_bboxes.append(
                        get_merged_bbox(bboxes[bbox_idx : bbox_idx + n])
                    )
                    bbox_idx += n
                    char_idx += 1
                    self._update_char_dims(char, dims)
                    char_matched_to_bbox = True
                    break
                elif grouped:
                    if char_idx + group_size > len(text):
                        messages.append(
                            f"Sub {sub_idx + 1:04d} Char {char_nonws_idx:02d} {text}: "
                            f"Cannot group {group_size} chars starting at '{char}' "
                            f"beyond text length"
                        )
                        continue
                    char_grp = text[char_idx : char_idx + group_size]
                    if any(c in whitespace_chars for c in char_grp):
                        messages.append(
                            f"Sub {sub_idx + 1:04d} Char {char_nonws_idx:02d} {text}: "
                            f"Cannot group '{char_grp}' due to whitespace"
                        )
                        continue
                    dims = (bboxes[bbox_idx].width, bboxes[bbox_idx].height)
                    merged_bboxes.append(bboxes[bbox_idx])
                    bbox_idx += 1
                    char_idx += group_size
                    self._update_char_grp_dims(char_grp, dims)
                    char_matched_to_bbox = True
                    break
            if char_matched_to_bbox:
                continue

            # No match found; log message and merge single bbox
            dims = self._get_dims_tuple(bboxes[bbox_idx : bbox_idx + 1])
            messages.append(
                f"Sub {sub_idx + 1:04d} Char {char_nonws_idx:02d} {text}: "
                f"No match for '{char}' bbox dims {dims}"
            )

        return merged_bboxes, messages

    @staticmethod
    def _get_dims_tuple(bboxes: list[Bbox]) -> tuple[int, ...]:
        """Get dims tuple from bboxes.

        Arguments:
            bboxes: bboxes
        Returns:
            dims tuple
        """
        widths = [bbox.width for bbox in bboxes]
        heights = [bbox.height for bbox in bboxes]
        gaps = [bboxes[i + 1].x1 - bboxes[i].x2 for i in range(len(bboxes) - 1)]
        dims = tuple([d for grp in zip(widths, heights, gaps + [0]) for d in grp][:-1])
        return dims

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
            boolean mask of white interior pixels
        """
        tolerance = 10
        lower = max(0, fill_color - tolerance)
        upper = min(255, fill_color + tolerance)
        return (alpha > 0) & (grayscale >= lower) & (grayscale <= upper)

    def _update_char_dims(self, char: str, dims: tuple[int, ...]) -> None:
        """Update char dims and save.

        Arguments:
            char: Character
            dims: Dimensions including width, height, gap values
        """
        n = (len(dims) + 1) // 3
        dims_set = self.char_dims_by_n[n].setdefault(char, set())
        if dims in dims_set:
            return
        dims_set.add(dims)
        info(f"Added ({char}, {dims})")
        self._save_char_dims(self.char_dims_by_n[n], self._char_dims_path(n))

    def _update_char_grp_dims(self, group: str, dims: tuple[int, ...]) -> None:
        """Update char group dims and save.

        Arguments:
            group: Group of characters
            dims: Dimensions including width and height
        """
        n = len(group)
        dims_set = self.char_grp_dims_by_n.setdefault(n, {}).setdefault(group, set())
        if dims in dims_set:
            return
        dims_set.add(dims)
        info(f"Added ({group}, {dims})")
        self._save_char_grp_dims(self.char_grp_dims_by_n, self._char_grp_dims_path())

    @staticmethod
    def _char_dims_path(n: int) -> Path:
        """Path to csv file."""
        return package_root / "data" / "ocr" / f"char_dims_{n}.csv"

    @staticmethod
    def _char_grp_dims_path() -> Path:
        """Path to character group dims csv file."""
        return package_root / "data" / "ocr" / "char_grp_dims.csv"

    @staticmethod
    def _load_char_dims(file_path: Path) -> dict[str, set[tuple[int, ...]]]:
        """Load char dims from file.

        Arguments:
            file_path: path to file
        Returns:
            char dims
        """
        char_dims: dict[str, set[tuple[int, ...]]] = {}
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                char = row[0]
                dims = tuple(map(int, row[1:]))
                dims_set = char_dims.setdefault(char, set())
                dims_set.add(dims)

        info(f"Loaded {file_path}")
        return char_dims

    @staticmethod
    def _save_char_dims(char_dims: dict[str, set[tuple[int, ...]]], file_path: Path):
        """Save char dims dict to file.

        Arguments:
            char_dims: char dims to save
            file_path: path to file
        """
        rows = []
        for char, dims_set in char_dims.items():
            rows.extend([[char, *dims] for dims in dims_set])
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}")

    @staticmethod
    def _save_char_grp_dims(
        char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]], file_path: Path
    ):
        """Save character group dims dict to file.

        Arguments:
            char_grp_dims_by_n: character group dims to save
            file_path: path to file
        """
        rows = []
        for n, char_grop_dims_set in char_grp_dims_by_n.items():
            for char_grp, dims_set in char_grop_dims_set.items():
                rows.extend([[char_grp, *dims] for dims in dims_set])
        rows = sorted({tuple(row) for row in rows})
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        info(f"Saved {file_path}")
