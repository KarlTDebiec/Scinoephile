#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validates OCRed subtitle text using source images."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.common import package_root
from scinoephile.common.validation import val_input_dir_path, val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.text import WHITESPACE_CHARS
from scinoephile.image.bboxes import get_bboxes, get_merged_bbox
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .char_cursor import CharCursor
from .char_dims import get_dims_tuple, load_char_dims, save_char_dims
from .char_grp_dims import load_char_grp_dims, save_char_grp_dims
from .char_pair_gaps import (
    get_default_char_pair_cutoffs,
    load_char_pair_gaps,
    save_char_pair_gaps,
)
from .gap_cursor import GapCursor

__all__ = [
    "MAX_CHAR_DIM_BBOXES",
    "ValidationManager",
]


logger = getLogger(__name__)

MAX_CHAR_DIM_BBOXES = 6
"""Maximum supported bbox count for one character."""


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

    def __init__(
        self,
        *,
        cache_dir_path: Path | str | None = None,
        dev: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory for local OCR validation data
            dev: whether validation data updates should write to repo data
        """
        try:
            self._init_data(cache_dir_path, dev)
        except (OSError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to initialize OCR validation data: {exc}"
            ) from exc

    def validate(
        self,
        series: ImageSeries,
    ) -> ImageSeries:
        """Validate all subtitles in an image series.

        Arguments:
            series: image series to validate
        Returns:
            validated image series
        """
        messages = []
        events = []
        for sub_idx, sub in enumerate(series.events):
            sub_messages = self._validate_sub(sub, sub_idx)
            messages.extend(sub_messages)
            events.append(
                ImageSubtitle(img=sub.img, start=sub.start, end=sub.end, text=sub.text)
            )
        output_series = ImageSeries(events=events)
        for message in messages:
            logger.warning(message)
        return output_series

    def _init_data(  # noqa: PLR0912
        self,
        cache_dir_path: Path | str | None,
        dev: bool,
    ):
        """Initialize OCR validation data.

        Arguments:
            cache_dir_path: cache directory for local OCR validation data
            dev: whether validation data updates should write to repo data
        """
        repo_data_dir_path = val_input_dir_path(package_root / "data/ocr")

        # Initialize char_dims_by_n
        self.char_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        for n in range(1, MAX_CHAR_DIM_BBOXES + 1):
            self.char_dims_by_n[n] = {}
            file_path = repo_data_dir_path / f"char_dims_{n}.csv"
            if file_path.exists():
                self.char_dims_by_n[n] = load_char_dims(file_path)

        # Initialize char_grp_dims_by_n
        self.char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        file_path = repo_data_dir_path / "char_grp_dims.csv"
        if file_path.exists():
            self.char_grp_dims_by_n = load_char_grp_dims(file_path)

        # Initialize char_pair_gaps
        self.char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        file_path = repo_data_dir_path / "char_pair_gaps.csv"
        if file_path.exists():
            self.char_pair_gaps = load_char_pair_gaps(file_path)

        # If not in dev mode, updates are written to cache directory instead of repo
        self.dev = dev
        self.cache_char_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        self.cache_char_grp_dims_by_n: dict[int, dict[str, set[tuple[int, ...]]]] = {}
        self.cache_char_pair_gaps: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        if not self.dev:
            if cache_dir_path is None:
                self.cache_dir_path = get_runtime_cache_dir_path(
                    "ocr_validation", create=False
                )
            else:
                self.cache_dir_path = val_output_dir_path(cache_dir_path, create=False)

            # Initialize char_dims_by_n
            for n in range(1, MAX_CHAR_DIM_BBOXES + 1):
                self.cache_char_dims_by_n[n] = {}
                file_path = self.cache_dir_path / f"char_dims_{n}.csv"
                if file_path.exists():
                    self.cache_char_dims_by_n[n] = load_char_dims(file_path)
                    for char, dims_set in self.cache_char_dims_by_n[n].items():
                        self.char_dims_by_n[n].setdefault(char, set()).update(dims_set)

            # Initialize char_grp_dims_by_n
            file_path = self.cache_dir_path / "char_grp_dims.csv"
            if file_path.exists():
                self.cache_char_grp_dims_by_n = load_char_grp_dims(file_path)
                for group_size, char_grp_dims in self.cache_char_grp_dims_by_n.items():
                    target_char_grp_dims = self.char_grp_dims_by_n.setdefault(
                        group_size, {}
                    )
                    for char_grp, dims_set in char_grp_dims.items():
                        target_char_grp_dims.setdefault(char_grp, set()).update(
                            dims_set
                        )

            # Initialize char_pair_gaps
            file_path = self.cache_dir_path / "char_pair_gaps.csv"
            if file_path.exists():
                self.cache_char_pair_gaps = load_char_pair_gaps(file_path)
                self.char_pair_gaps.update(self.cache_char_pair_gaps)

    def _validate_sub(self, sub: ImageSubtitle, sub_idx: int) -> list[str]:
        """Validate per-character bboxes for a subtitle.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
        Returns:
            validation messages
        """
        sub.bboxes = get_bboxes(sub.img)

        char_messages = self._validate_chars(sub, sub_idx)
        if len(char_messages) > 0:
            return char_messages

        original_text = sub.text
        gap_messages = self._validate_gaps(sub, sub_idx)
        if len(gap_messages) > 0:
            sub.text = original_text

        return char_messages + gap_messages

    def _validate_chars(
        self,
        sub: ImageSubtitle,
        sub_idx: int,
    ) -> list[str]:
        """Merge bboxes per character and collect validation messages.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
        Returns:
            validation messages
        """
        messages = []

        cursor = CharCursor(sub=sub, sub_idx=sub_idx)
        while cursor.char_idx < len(sub.text_with_newline):
            # No validation to perform for whitespace
            if cursor.char in WHITESPACE_CHARS or cursor.char == "\n":
                cursor.advance(n_chars=1, n_bboxes=0)
                continue

            # Cannot validate without bboxes
            if cursor.bbox_idx >= len(cursor.bboxes):
                messages.append(
                    f"{cursor.intro_msg} | ran out of bboxes at '{cursor.char}'"
                )
                break

            # Check if next bbox matches two or more characters
            matched = self.match_grouped_chars(cursor)
            if matched:
                continue

            # Check if next one or more bboxes matches single character
            matched = self.match_char_dims(cursor)
            if matched:
                continue

            messages.append(
                f"{cursor.intro_msg} | question about bboxes for '{cursor.char}'"
            )
            break

        # Cannot have leftover bboxes
        if cursor.bbox_idx != len(cursor.bboxes):
            messages.append(
                f"{cursor.intro_msg} | "
                f"{len(cursor.bboxes) - cursor.bbox_idx} leftover bboxes"
            )

        return messages

    def match_grouped_chars(self, cursor: CharCursor) -> bool:
        """Match grouped characters against approved dimensions.

        Arguments:
            cursor: character cursor
        Returns:
            whether a match was found
        """
        for n_chars in self.char_grp_dims_by_n.keys():
            if cursor.char_idx + n_chars > len(cursor.sub.text_with_newline):
                continue
            char_grp = cursor.char_grp(n_chars)
            if any(c in WHITESPACE_CHARS for c in char_grp) or "\n" in char_grp:
                continue
            dims = get_dims_tuple(cursor.bboxes[cursor.bbox_idx])
            ok_dims = self.char_grp_dims_by_n[n_chars].get(char_grp, set())

            # Exact match
            if dims in ok_dims:
                cursor.advance(n_chars=n_chars, n_bboxes=1)
                return True

            # Fuzzy match
            for ok_dim in ok_dims:
                diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                max_diff = max(diffs)
                if max_diff <= 2:
                    self._update_char_grp_dims(char_grp, dims)
                    cursor.advance(n_chars=n_chars, n_bboxes=1)
                    return True
        return False

    def match_char_dims(self, cursor: CharCursor) -> bool:
        """Match character against approved dimensions.

        Arguments:
            cursor: character cursor
        Returns:
            whether a match was found
        """
        for n_bboxes in self.char_dims_by_n.keys():
            if cursor.bbox_idx + n_bboxes > len(cursor.bboxes):
                break
            dims = get_dims_tuple(cursor.bbox_grp(n_bboxes))
            ok_dims = self.char_dims_by_n[n_bboxes].get(cursor.char, set())

            # Exact match
            if dims in ok_dims:
                bbox_grp = cursor.bbox_grp(n_bboxes)
                merged_bbox = get_merged_bbox(bbox_grp)
                cursor.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [
                    merged_bbox
                ]
                cursor.advance(n_chars=1, n_bboxes=1)
                return True

            # Fuzzy match
            for ok_dim in ok_dims:
                diffs = [abs(dims[i] - ok_dim[i]) for i in range(len(dims))]
                max_diff = max(diffs)
                if max_diff <= 2:
                    bbox_grp = cursor.bbox_grp(n_bboxes)
                    merged_bbox = get_merged_bbox(bbox_grp)
                    cursor.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [
                        merged_bbox
                    ]
                    self.update_char_dims(cursor.char, dims)
                    cursor.advance(n_chars=1, n_bboxes=1)
                    return True
        return False

    def _validate_gaps(  # noqa: PLR0912, PLR0915
        self,
        sub: ImageSubtitle,
        sub_idx: int,
    ) -> list[str]:
        """Validate gaps between bboxes and collect validation messages.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
        Returns:
            validation messages
        """
        messages = []

        cursor = GapCursor(sub=sub, sub_idx=sub_idx)
        while cursor.char_1_idx < len(sub.text_with_newline) - 1:
            prepared = cursor.prepare_gap()
            if prepared is None:
                if cursor.bbox_1_idx >= len(cursor.bboxes) and cursor.char_1:
                    messages.append(
                        f"{cursor.intro_msg} | ran out of bboxes at '{cursor.char_1}'"
                    )
                elif cursor.bbox_2_idx >= len(cursor.bboxes) and cursor.char_2:
                    messages.append(
                        f"{cursor.intro_msg} | "
                        f"Ran out of bboxes when checking gap between "
                        f"'{cursor.char_1}' and '{cursor.char_2}'"
                    )
                break
            bbox_1, bbox_2 = prepared

            # If char 1 and char 2 and bbox_1 are all together, obviously adjacent
            if len(cursor.gap_chars) == 0:
                char_grp = f"{cursor.char_1}{cursor.char_2}"
                dims = get_dims_tuple(bbox_1)
                ok_dims = self.char_grp_dims_by_n.get(2, {}).get(char_grp, set())
                if dims in ok_dims:
                    logger.debug(
                        f"|{cursor.char_1_idx}|{cursor.char_2_idx}|"
                        f"{cursor.bbox_1_idx}| -> |"
                        f"{cursor.char_1}|{cursor.char_2}|group|"
                    )
                    cursor.char_1_idx += 1
                    continue

            # get gap
            cursor.gap = bbox_2.x1 - bbox_1.x2
            logger.debug(
                f"|{cursor.char_1_idx}|{cursor.char_2_idx}|"
                f"{cursor.bbox_1_idx}|{cursor.bbox_2_idx}| -> |"
                f"{cursor.char_1}|{cursor.char_2}|{cursor.gap}|"
                f"{cursor.gap_chars_escaped}|"
            )

            # If gap is negative, ensure that gap_chars is a newline
            if cursor.gap < 0:
                if cursor.gap_chars != "\n":
                    messages.append(
                        f"{cursor.intro_msg} | {cursor.gap_msg} | "
                        f"expected '\\n' "
                        f"observed '{cursor.gap_chars_escaped}'"
                    )
                cursor.advance()
                continue

            # Validate
            cutoffs = self.char_pair_gaps.get(cursor.char_pair)
            if not cutoffs:
                cutoffs = get_default_char_pair_cutoffs(cursor.char_1, cursor.char_2)
                self.update_pair_gaps(cursor.char_pair, cutoffs)

            # Adjacent
            if cursor.gap <= cutoffs[0]:
                if cursor.gap_chars != "":
                    self._replace_gap_text(cursor, "")
                cursor.advance()
                continue

            # Adjacent or space needs human judgment
            if cutoffs[0] < cursor.gap < cutoffs[1]:
                if cursor.gap == cutoffs[0] + 1 and cursor.gap_chars == "":
                    self.update_pair_gaps(
                        cursor.char_pair,
                        (cursor.gap, cutoffs[1], cutoffs[2], cutoffs[3]),
                    )
                    cursor.advance()
                    continue
                if (
                    cursor.gap == cutoffs[1] - 1
                    and cursor.gap_chars == cursor.expected_space
                ):
                    self.update_pair_gaps(
                        cursor.char_pair,
                        (cutoffs[0], cursor.gap, cutoffs[2], cutoffs[3]),
                    )
                    cursor.advance()
                    continue
                messages.append(
                    f"{cursor.intro_msg} | {cursor.gap_msg} | "
                    f"question about adjacent or space gap, observed "
                    f"'{cursor.gap_chars_escaped}'"
                )
                return messages

            # Space
            if cutoffs[1] <= cursor.gap <= cutoffs[2]:
                if cursor.gap_chars != cursor.expected_space:
                    self._replace_gap_text(cursor, cursor.expected_space)
                cursor.advance()
                continue

            # Space or tab needs human judgment
            if cutoffs[2] < cursor.gap < cutoffs[3]:
                if (
                    cursor.gap == cutoffs[2] + 1
                    and cursor.gap_chars == cursor.expected_space
                ):
                    self.update_pair_gaps(
                        cursor.char_pair,
                        (cutoffs[0], cutoffs[1], cursor.gap, cutoffs[3]),
                    )
                    cursor.advance()
                    continue
                if (
                    cursor.gap == cutoffs[3] - 1
                    and cursor.gap_chars == cursor.expected_tab
                ):
                    self.update_pair_gaps(
                        cursor.char_pair,
                        (cutoffs[0], cutoffs[1], cutoffs[2], cursor.gap),
                    )
                    cursor.advance()
                    continue
                messages.append(
                    f"{cursor.intro_msg} | {cursor.gap_msg} | "
                    f"question about space or tab gap, observed "
                    f"'{cursor.gap_chars_escaped}'"
                )
                return messages

            # Tab
            if cutoffs[3] <= cursor.gap:
                if cursor.gap_chars != cursor.expected_tab:
                    self._replace_gap_text(cursor, cursor.expected_tab)
                cursor.advance()
                continue

        return messages

    def _replace_gap_text(self, cursor: GapCursor, replacement: str):
        """Replace the current gap text in a subtitle.

        Arguments:
            cursor: prepared gap cursor
            replacement: replacement gap text
        """
        replacement_escaped = replacement.replace(chr(10), "\\n")
        logger.info(
            f"{cursor.intro_msg} | {cursor.gap_msg} | corrected gap text from "
            f"'{cursor.gap_chars_escaped}' to '{replacement_escaped}'"
        )
        text = cursor.sub.text_with_newline
        start_idx = cursor.char_1_idx + 1
        end_idx = cursor.char_2_idx
        updated_text = f"{text[:start_idx]}{replacement}{text[end_idx:]}"
        cursor.sub.text = updated_text.replace("\n", "\\N")
        cursor.char_2_idx = start_idx + len(replacement)
        cursor.gap_chars = replacement

    def update_char_dims(self, char: str, dims: tuple[int, ...]):
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
        logger.info(f"Added ({char}, {dims})")
        if self.dev:
            output_char_dims = self.char_dims_by_n[n]
        else:
            output_char_dims = self.cache_char_dims_by_n.setdefault(n, {})
            output_char_dims.setdefault(char, set()).add(dims)
        save_char_dims(output_char_dims, self._char_dims_path(n))

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
        logger.info(f"Added ({group}, {dims})")
        if self.dev:
            output_char_grp_dims = self.char_grp_dims_by_n
        else:
            output_char_grp_dims = self.cache_char_grp_dims_by_n
            output_char_grp_dims.setdefault(n, {}).setdefault(group, set()).add(dims)
        save_char_grp_dims(output_char_grp_dims, self._char_grp_dims_path())

    def update_pair_gaps(
        self, char_pair: tuple[str, str], cutoffs: tuple[int, int, int, int]
    ):
        """Update char pair gaps and save.

        Arguments:
            char_pair: character pair
            cutoffs: cutoffs
        """
        previous_cutoffs = self.char_pair_gaps.get(char_pair)
        if previous_cutoffs == cutoffs:
            return
        if cutoffs == get_default_char_pair_cutoffs(*char_pair):
            self.char_pair_gaps[char_pair] = cutoffs
            if previous_cutoffs is None:
                return
            if self.dev:
                output_char_pair_gaps = self.char_pair_gaps
            elif char_pair in self.cache_char_pair_gaps:
                self.cache_char_pair_gaps.pop(char_pair, None)
                output_char_pair_gaps = self.cache_char_pair_gaps
            else:
                return
            save_char_pair_gaps(output_char_pair_gaps, self._char_pair_gaps_path())
            return
        self.char_pair_gaps[char_pair] = cutoffs
        logger.info(f"Added ({char_pair}, {cutoffs})")
        if self.dev:
            output_char_pair_gaps = self.char_pair_gaps
        else:
            self.cache_char_pair_gaps[char_pair] = cutoffs
            output_char_pair_gaps = self.cache_char_pair_gaps
        save_char_pair_gaps(output_char_pair_gaps, self._char_pair_gaps_path())

    def _char_dims_path(self, n: int) -> Path:
        """Path to character dimensions csv file."""
        return self._data_output_dir_path() / f"char_dims_{n}.csv"

    def _char_grp_dims_path(self) -> Path:
        """Path to character group dimensions csv file."""
        return self._data_output_dir_path() / "char_grp_dims.csv"

    def _char_pair_gaps_path(self) -> Path:
        """Path to character pair gap csv file."""
        return self._data_output_dir_path() / "char_pair_gaps.csv"

    def _data_output_dir_path(self) -> Path:
        """Get validation data directory to which updates should be written.

        Returns:
            validation data directory
        """
        # If in dev mode, write directly into repo
        if self.dev:
            return val_input_dir_path(package_root / "data/ocr")

        # Otherwise write to cache
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        return self.cache_dir_path
