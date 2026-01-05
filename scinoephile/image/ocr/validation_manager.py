#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validates OCRed subtitle text using source images."""

from __future__ import annotations

from logging import info
from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.bboxes import get_bboxes, get_merged_bbox
from scinoephile.image.drawing import get_img_with_bboxes
from scinoephile.image.subtitles import ImageSubtitle

from .char_dims import get_dims_tuple, load_char_dims, save_char_dims
from .char_grp_dims import save_char_grp_dims
from .char_pair_gaps import load_char_pair_gaps

__all__ = ["ValidationManager"]


class ValidationManager:
    """Validates OCRed subtitle text using source images."""

    char_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
    """Data structure for characters in one or more bboxes.
    
    First key is the number of bboxes.
    Second key is the character.
    Values are a set of approved bbox width, heights, and gaps for that character.
    """

    char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
    """Data structure for bboxes containing two or more characters.
    
    First key is the number of characters in the group.
    Second key is the character group.
    Values are a set of approved bbox width and heights for that character group.
    """

    char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
    """Data structure for gaps between bboxes.
    
    Key is a pair of characters.
    Value is a tuple of four ints, representing cutoffs:
      * Upper bound for 'adjacent' characters
      * Lower bound for 'space' characters
      * Upper bound for 'space' characters
      * Lower bound for 'tab' characters
    """

    def __init__(self):
        """Initialize."""
        # Initalize char_dims_by_n.
        for n in range(1, 6):
            file_path = self._char_dims_path(n)
            self.char_dims_by_n[n] = {}
            if file_path.exists():
                self.char_dims_by_n[n] = load_char_dims(file_path)

        # Initialize char_grp_dims_by_n.
        file_path = self._char_grp_dims_path()
        if file_path.exists():
            char_grp_dims = load_char_dims(file_path)
            for char_grp, dims_set in char_grp_dims.items():
                n = len(char_grp)
                if n not in self.char_grp_dims_by_n:
                    self.char_grp_dims_by_n[n] = {}
                self.char_grp_dims_by_n[n][char_grp] = dims_set

        # Initialize char_pair_gaps.
        file_path = self._char_pair_gaps_path()
        if file_path.exists():
            self.char_pair_gaps = load_char_pair_gaps(file_path)

    def validate(
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
            bboxes = get_bboxes(sub.img)

        bboxes, messages = self._validate_chars(sub, bboxes, sub_idx, interactive)
        sub.bboxes = bboxes
        return messages

    def _validate_chars(  # noqa: PLR0912, PLR0915
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
                dims = get_dims_tuple(bboxes[bbox_idx : bbox_idx + n])
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
                dims = get_dims_tuple(bboxes[bbox_idx : bbox_idx + n])

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
            dims = get_dims_tuple(bboxes[bbox_idx : bbox_idx + 1])
            messages.append(
                f"Sub {sub_idx + 1:04d} Char {char_nonws_idx:02d} {text}: "
                f"No match for '{char}' bbox dims {dims}"
            )

        return merged_bboxes, messages

    def _update_char_dims(self, char: str, dims: tuple[int, ...]):
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
        save_char_dims(self.char_dims_by_n[n], self._char_dims_path(n))

    def _update_char_grp_dims(self, group: str, dims: tuple[int, ...]):
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
        save_char_grp_dims(self.char_grp_dims_by_n, self._char_grp_dims_path())

    @staticmethod
    def _char_dims_path(n: int) -> Path:
        """Path to character dimensions csv file."""
        return package_root / "data" / "ocr" / f"char_dims_{n}.csv"

    @staticmethod
    def _char_grp_dims_path() -> Path:
        """Path to character group dimensions csv file."""
        return package_root / "data" / "ocr" / "char_grp_dims.csv"

    @staticmethod
    def _char_pair_gaps_path() -> Path:
        """Path to character pair gap csv file."""
        return package_root / "data" / "ocr" / "char_pair_gaps.csv"
