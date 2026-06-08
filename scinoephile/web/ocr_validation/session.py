#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Stateful OCR validation workflow for the web UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from PIL import Image

from scinoephile.core import ScinoephileError
from scinoephile.core.text import whitespace_chars
from scinoephile.image.bboxes import get_bboxes, get_merged_bbox
from scinoephile.image.drawing import get_img_with_bboxes
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.ocr.validation.char_cursor import CharCursor
from scinoephile.image.ocr.validation.char_dims import get_dims_tuple
from scinoephile.image.ocr.validation.char_pair_gaps import (
    get_default_char_pair_cutoffs,
)
from scinoephile.image.ocr.validation.gap_cursor import GapCursor
from scinoephile.image.subtitles import ImageSeries

from .concerns import (
    CharDimsConcern,
    ConcernKind,
    ErrorConcern,
    GapConcern,
    OcrConcern,
    SubtitleRowView,
    ValidationStatus,
)
from .html_index import HtmlSubtitleEntry, load_html_entries, update_html_entry_text

__all__ = ["OcrValidationSession"]


@dataclass
class _SubtitleValidationState:
    """Validation state for one subtitle row."""

    sub_idx: int
    """Zero-based subtitle index."""
    phase: str = "chars"
    """Validation phase."""
    char_cursor: CharCursor | None = None
    """Character bbox validation cursor."""
    gap_cursor: GapCursor | None = None
    """Gap validation cursor."""
    char_n_bboxes: int = 1
    """Number of bboxes selected for the current character concern."""
    status: ValidationStatus | None = None
    """Row-level validation status."""
    concern: OcrConcern | None = None
    """Current validation concern."""


class OcrValidationSession:
    """Stateful OCR validation session for the local web UI."""

    def __init__(
        self,
        *,
        dir_path: Path,
        entries: list[HtmlSubtitleEntry],
        series: ImageSeries,
        manager: ValidationManager,
        include_done_subtitles: bool = False,
        outfile_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            dir_path: OCR image HTML directory path
            entries: HTML subtitle entries
            series: image subtitle series
            manager: OCR validation manager
            include_done_subtitles: whether to include subtitles with no concerns
            outfile_path: optional subtitle output file path
        """
        self.dir_path = dir_path
        self.entries = entries
        self.series = series
        self.manager = manager
        self.include_done_subtitles = include_done_subtitles
        self.outfile_path = outfile_path
        self.text_color_css = _gray_css(self.series.fill_color)
        self.text_shadow_color_css = _gray_css(self.series.outline_color)
        self.text_font_size_px = self.series.text_font_size
        self._states: dict[int, _SubtitleValidationState] = {}

    @classmethod
    def from_dir_path(
        cls,
        dir_path: Path,
        *,
        include_done_subtitles: bool = False,
        outfile_path: Path | None = None,
        cache_dir_path: Path | None = None,
        dev: bool = False,
    ) -> Self:
        """Create a session from an OCR image directory.

        Arguments:
            dir_path: OCR image HTML directory path
            include_done_subtitles: whether to include subtitles with no concerns
            outfile_path: optional subtitle output file path
            cache_dir_path: cache directory for local OCR validation data
            dev: whether validation data updates should write to repo data
        Returns:
            OCR validation session
        """
        dir_path = Path(dir_path).resolve()
        if not dir_path.is_dir():
            raise ScinoephileError(f"Expected {dir_path} to be a directory.")
        if not (dir_path / "index.html").is_file():
            raise ScinoephileError(f"Expected {dir_path / 'index.html'} to be a file.")

        try:
            entries = load_html_entries(dir_path)
            series = ImageSeries.load(dir_path)
            manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
            session = cls(
                dir_path=dir_path,
                entries=entries,
                series=series,
                manager=manager,
                include_done_subtitles=include_done_subtitles,
                outfile_path=outfile_path,
            )
            session._save_outfile()
            return session
        except ScinoephileError:
            raise
        except (OSError, ValueError) as exc:
            raise ScinoephileError(str(exc)) from exc

    def subtitle_row(self, sub_idx: int) -> SubtitleRowView:
        """Return one subtitle row view model.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            subtitle row view model
        """
        self._validate_sub_idx(sub_idx)
        state = self._state(sub_idx)
        if state.status is None:
            raise ValueError(f"Subtitle {sub_idx} has no validation state.")
        entry = self.entries[sub_idx]
        image_width = self.series.events[sub_idx].img.width
        image_height = self.series.events[sub_idx].img.height
        return SubtitleRowView(
            sub_idx=sub_idx,
            number=entry.index,
            start=ImageSeries._format_html_time(entry.start),
            end=ImageSeries._format_html_time(entry.end),
            image_width=image_width,
            image_height=image_height,
            text=entry.text,
            status=state.status,
            concern=state.concern,
            text_color_css=self.text_color_css,
            text_shadow_color_css=self.text_shadow_color_css,
            text_font_size_px=self.text_font_size_px,
        )

    def subtitle_rows(self) -> list[SubtitleRowView]:
        """Return row view models for all in-scope subtitles.

        Returns:
            subtitle row view models
        """
        rows = []
        for sub_idx in range(len(self.entries)):
            row = self.subtitle_row(sub_idx)
            if self.subtitle_row_is_visible(row):
                rows.append(row)
        return rows

    def subtitle_row_is_visible(self, row: SubtitleRowView) -> bool:
        """Return whether a subtitle row should be rendered in the list.

        Arguments:
            row: subtitle row view model
        Returns:
            whether the row should be shown
        """
        if self.include_done_subtitles:
            return True
        return row.status != ValidationStatus.DONE

    def concern_image(self, sub_idx: int) -> Image.Image:
        """Return an annotated image for the current concern.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            annotated concern image
        """
        state = self._state(sub_idx)
        sub = self.series.events[sub_idx]
        if isinstance(state.concern, CharDimsConcern):
            cursor = self._char_cursor(state)
            return get_img_with_bboxes(sub.img, cursor.bbox_grp(state.concern.n_bboxes))
        if isinstance(state.concern, GapConcern):
            cursor = self._gap_cursor(state)
            return cursor.annotated_img(2)
        return sub.img

    def update_text(self, sub_idx: int, text: str) -> SubtitleRowView:
        """Persist corrected OCR text and rebuild the subtitle state.

        Arguments:
            sub_idx: zero-based subtitle index
            text: replacement subtitle text using ASS newline escapes
        Returns:
            updated subtitle row view model
        """
        self._validate_sub_idx(sub_idx)
        update_html_entry_text(self.dir_path, sub_idx, text)
        self.entries = load_html_entries(self.dir_path)
        self.series.events[sub_idx].text = text
        self._states.pop(sub_idx, None)
        self._save_outfile()
        return self.subtitle_row(sub_idx)

    def validation_image(self, sub_idx: int) -> Image.Image:
        """Return a row image annotated with all current bboxes.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            annotated validation image
        """
        self._state(sub_idx)
        sub = self.series.events[sub_idx]
        if sub.bboxes is None:
            return sub.img
        return get_img_with_bboxes(sub.img, sub.bboxes)

    def resolve_char_concern(
        self,
        sub_idx: int,
        *,
        action: str,
        n_bboxes: int,
    ) -> SubtitleRowView:
        """Resolve the current character bbox concern for one subtitle.

        Arguments:
            sub_idx: zero-based subtitle index
            action: user action to apply
            n_bboxes: number of selected bboxes
        Returns:
            updated subtitle row view model
        """
        state = self._state(sub_idx)
        if not isinstance(state.concern, CharDimsConcern):
            raise ValueError(f"Subtitle {sub_idx} has no character concern.")

        if action == "expand":
            state.char_n_bboxes = self._validated_n_bboxes(state, n_bboxes + 1)
            state.concern = self._char_dims_concern(state)
            return self.subtitle_row(sub_idx)
        if action == "contract":
            state.char_n_bboxes = self._validated_n_bboxes(state, n_bboxes - 1)
            state.concern = self._char_dims_concern(state)
            return self.subtitle_row(sub_idx)
        if action == "accept":
            self._accept_char_dims(state, n_bboxes)
            return self.subtitle_row(sub_idx)
        raise ValueError(f"Unrecognized character concern action: {action}")

    def reset_states(self):
        """Clear cached per-subtitle validation states."""
        self._states.clear()

    def resolve_gap_concern(self, sub_idx: int, *, action: str) -> SubtitleRowView:
        """Resolve the current spacing concern for one subtitle.

        Arguments:
            sub_idx: zero-based subtitle index
            action: user action to apply
        Returns:
            updated subtitle row view model
        """
        state = self._state(sub_idx)
        if not isinstance(state.concern, GapConcern):
            raise ValueError(f"Subtitle {sub_idx} has no gap concern.")

        cursor = self._gap_cursor(state)
        cutoffs = self._gap_cutoffs(cursor)
        if state.concern.kind == ConcernKind.SPACE_GAP:
            expected_gap_chars = self._resolve_space_gap_action(cursor, cutoffs, action)
        else:
            expected_gap_chars = self._resolve_tab_gap_action(cursor, cutoffs, action)

        return self._replace_gap_text(
            sub_idx,
            start_idx=cursor.char_1_idx + 1,
            end_idx=cursor.char_2_idx,
            replacement=expected_gap_chars,
        )

    def _accept_char_dims(self, state: _SubtitleValidationState, n_bboxes: int):
        """Accept selected bbox dimensions for the current character.

        Arguments:
            state: subtitle validation state
            n_bboxes: number of selected bboxes
        """
        cursor = self._char_cursor(state)
        n_bboxes = self._validated_n_bboxes(state, n_bboxes)
        bbox_grp = cursor.bbox_grp(n_bboxes)
        dims = get_dims_tuple(bbox_grp)
        merged_bbox = get_merged_bbox(bbox_grp)
        cursor.bboxes[cursor.bbox_idx : cursor.bbox_idx + n_bboxes] = [merged_bbox]
        self.manager._update_char_dims(cursor.char, dims)
        cursor.advance(n_chars=1, n_bboxes=1)
        state.char_n_bboxes = 1
        state.concern = None
        self._scan_state(state)
        self._save_outfile()

    def _char_cursor(self, state: _SubtitleValidationState) -> CharCursor:
        """Get the state's character cursor.

        Arguments:
            state: subtitle validation state
        Returns:
            character cursor
        """
        if state.char_cursor is None:
            raise ValueError("Character cursor is not initialized.")
        return state.char_cursor

    def _char_dims_concern(self, state: _SubtitleValidationState) -> CharDimsConcern:
        """Build the current character dimension concern.

        Arguments:
            state: subtitle validation state
        Returns:
            character dimension concern
        """
        cursor = self._char_cursor(state)
        max_n_bboxes = self._max_n_bboxes(state)
        state.char_n_bboxes = min(state.char_n_bboxes, max_n_bboxes)
        dims = get_dims_tuple(cursor.bbox_grp(state.char_n_bboxes))
        return CharDimsConcern(
            sub_idx=state.sub_idx,
            char_idx=cursor.char_idx,
            bbox_idx=cursor.bbox_idx,
            n_bboxes=state.char_n_bboxes,
            max_n_bboxes=max_n_bboxes,
            char=cursor.char,
            dims=dims,
        )

    def _gap_cursor(self, state: _SubtitleValidationState) -> GapCursor:
        """Get the state's gap cursor.

        Arguments:
            state: subtitle validation state
        Returns:
            gap cursor
        """
        if state.gap_cursor is None:
            raise ValueError("Gap cursor is not initialized.")
        return state.gap_cursor

    def _gap_cutoffs(self, cursor: GapCursor) -> tuple[int, int, int, int]:
        """Get existing or default cutoffs for the current gap.

        Arguments:
            cursor: gap cursor
        Returns:
            gap cutoff tuple
        """
        cutoffs = self.manager.char_pair_gaps.get(cursor.char_pair)
        if cutoffs is None:
            cutoffs = get_default_char_pair_cutoffs(cursor.char_1, cursor.char_2)
            self.manager._update_pair_gaps(cursor.char_pair, cutoffs)
        return cutoffs

    def _gap_replace_text(self, cursor: GapCursor, replacement: str):
        """Replace the current gap text without resetting validation state.

        Arguments:
            cursor: prepared gap cursor
            replacement: replacement gap text
        """
        text = cursor.sub.text_with_newline
        start_idx = cursor.char_1_idx + 1
        end_idx = cursor.char_2_idx
        updated_text = f"{text[:start_idx]}{replacement}{text[end_idx:]}"
        cursor.sub.text = updated_text.replace("\n", "\\N")
        cursor.char_2_idx = start_idx + len(replacement)
        cursor.gap_chars = replacement
        update_html_entry_text(self.dir_path, cursor.sub_idx, cursor.sub.text)
        self.entries = load_html_entries(self.dir_path)
        self._save_outfile()

    def _gap_concern(
        self,
        cursor: GapCursor,
        cutoffs: tuple[int, int, int, int],
        *,
        kind: ConcernKind,
        expected: str | None = None,
        action_options: tuple[tuple[str, str], ...] | None = None,
    ) -> GapConcern:
        """Build a gap concern for the current cursor position.

        Arguments:
            cursor: gap cursor
            cutoffs: gap cutoff tuple
            kind: gap concern kind
            expected: expected replacement gap text
            action_options: optional form actions
        Returns:
            gap concern
        """
        if expected is None or action_options is None:
            if kind == ConcernKind.SPACE_GAP:
                expected = cursor.expected_space
                action_options = (("adjacent", "Adjacent"), ("space", "Space"))
            elif kind == ConcernKind.TAB_GAP:
                expected = cursor.expected_tab
                action_options = (("space", "Space"), ("tab", "Tab"))
            else:
                raise ValueError(f"Invalid gap concern kind: {kind}")

        return GapConcern(
            sub_idx=cursor.sub_idx,
            char_1_idx=cursor.char_1_idx,
            char_2_idx=cursor.char_2_idx,
            char_1=cursor.char_1,
            char_2=cursor.char_2,
            gap=cursor.gap,
            space_prompt=(cutoffs[0], cutoffs[1]),
            tab_prompt=(cutoffs[2], cutoffs[3]),
            observed=cursor.gap_chars,
            expected=expected,
            action_options=action_options,
            kind=kind,
        )

    def _state(self, sub_idx: int) -> _SubtitleValidationState:
        """Get or initialize validation state for one subtitle.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            validation state
        """
        state = self._states.get(sub_idx)
        if state is None:
            sub = self.series.events[sub_idx]
            sub.bboxes = get_bboxes(sub.img)
            state = _SubtitleValidationState(
                sub_idx=sub_idx,
                char_cursor=CharCursor(sub=sub, sub_idx=sub_idx),
            )
            self._states[sub_idx] = state
            self._scan_state(state)
        return state

    def _max_n_bboxes(self, state: _SubtitleValidationState) -> int:
        """Maximum bbox selection for the current character concern.

        Arguments:
            state: subtitle validation state
        Returns:
            maximum selectable bbox count
        """
        cursor = self._char_cursor(state)
        available = len(cursor.bboxes) - cursor.bbox_idx
        configured = max(self.manager.char_dims_by_n.keys(), default=1)
        return max(1, min(available, configured))

    def _scan_state(self, state: _SubtitleValidationState):
        """Scan a subtitle until the next unresolved concern.

        Arguments:
            state: subtitle validation state
        """
        if state.phase == "chars":
            char_concern = self._scan_chars(state)
            if char_concern is not None:
                self._set_concern(state, char_concern)
                return
            state.phase = "gaps"
            cursor = self._char_cursor(state)
            state.gap_cursor = GapCursor(sub=cursor.sub, sub_idx=state.sub_idx)

        if state.phase == "gaps":
            gap_concern = self._scan_gaps(state)
            if gap_concern is not None:
                self._set_concern(state, gap_concern)
                return

        state.status = ValidationStatus.DONE
        state.concern = None

    def _scan_chars(self, state: _SubtitleValidationState) -> OcrConcern | None:
        """Scan character bboxes until a concern is found or chars complete.

        Arguments:
            state: subtitle validation state
        Returns:
            next concern, or None when character validation is complete
        """
        cursor = self._char_cursor(state)
        while cursor.char_idx < len(cursor.sub.text_with_newline):
            if cursor.char in whitespace_chars or cursor.char == "\n":
                cursor.advance(n_chars=1, n_bboxes=0)
                continue

            if cursor.bbox_idx >= len(cursor.bboxes):
                return ErrorConcern(message=f"Ran out of bboxes at '{cursor.char}'.")

            if self.manager._match_grouped_chars(cursor):
                continue
            if self.manager._match_char_dims(cursor):
                continue

            return self._char_dims_concern(state)

        if cursor.bbox_idx != len(cursor.bboxes):
            leftover = len(cursor.bboxes) - cursor.bbox_idx
            return ErrorConcern(message=f"{leftover} leftover bboxes.")
        return None

    def _scan_gaps(self, state: _SubtitleValidationState) -> OcrConcern | None:
        """Scan character gaps until a concern is found or gaps complete.

        Arguments:
            state: subtitle validation state
        Returns:
            next concern, or None when gap validation is complete
        """
        cursor = self._gap_cursor(state)
        while cursor.char_1_idx < len(cursor.sub.text_with_newline) - 1:
            prepared = cursor.prepare_gap()
            if prepared is None:
                return None
            bbox_1, bbox_2 = prepared

            if len(cursor.gap_chars) == 0:
                char_grp = f"{cursor.char_1}{cursor.char_2}"
                dims = get_dims_tuple(bbox_1)
                ok_dims = self.manager.char_grp_dims_by_n.get(2, {}).get(
                    char_grp, set()
                )
                if dims in ok_dims:
                    cursor.char_1_idx += 1
                    continue

            cursor.gap = bbox_2.x1 - bbox_1.x2
            if cursor.gap < 0:
                if cursor.gap_chars != "\n":
                    return ErrorConcern(
                        message=(
                            f"{cursor.gap_msg} expected '\\n' "
                            f"observed '{cursor.gap_chars_escaped}'."
                        )
                    )
                cursor.advance()
                continue

            cutoffs = self._gap_cutoffs(cursor)
            concern = self._scan_gap_with_cutoffs(cursor, cutoffs)
            if concern is not None:
                return concern
            cursor.advance()
        return None

    def _save_outfile(self):
        """Persist the session's current subtitle text to the output file."""
        if self.outfile_path is None:
            return
        self.outfile_path.parent.mkdir(parents=True, exist_ok=True)
        self.series.save(self.outfile_path, format_="srt", exist_ok=True)

    def _scan_gap_with_cutoffs(  # noqa: PLR0911
        self,
        cursor: GapCursor,
        cutoffs: tuple[int, int, int, int],
    ) -> OcrConcern | None:
        """Scan one prepared gap using its cutoff tuple.

        Arguments:
            cursor: gap cursor
            cutoffs: gap cutoff tuple
        Returns:
            gap concern, error concern, or None when the gap is valid
        """
        if cursor.gap <= cutoffs[0]:
            if cursor.gap_chars != "":
                self._gap_replace_text(cursor, "")
            return None

        if cutoffs[0] < cursor.gap < cutoffs[1]:
            if cursor.gap == cutoffs[0] + 1 and cursor.gap_chars == "":
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cursor.gap, cutoffs[1], cutoffs[2], cutoffs[3]),
                )
                return None
            if cursor.gap_chars and cursor.gap_chars == cursor.expected_space:
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cursor.gap, cutoffs[2], cutoffs[3]),
                )
                return None
            return self._gap_concern(cursor, cutoffs, kind=ConcernKind.SPACE_GAP)

        if cutoffs[1] <= cursor.gap <= cutoffs[2]:
            if cursor.gap_chars != cursor.expected_space:
                self._gap_replace_text(cursor, cursor.expected_space)
            return None

        if cutoffs[2] < cursor.gap < cutoffs[3]:
            if cursor.gap_chars == cursor.expected_space:
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cutoffs[1], cursor.gap, cutoffs[3]),
                )
                return None
            if cursor.gap_chars in (cursor.expected_tab, "\n"):
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cutoffs[1], cutoffs[2], cursor.gap),
                )
                return None
            return self._gap_concern(cursor, cutoffs, kind=ConcernKind.TAB_GAP)

        if cursor.gap_chars not in (cursor.expected_tab, "\n"):
            self._gap_replace_text(cursor, cursor.expected_tab)
        return None

    def _set_concern(self, state: _SubtitleValidationState, concern: OcrConcern):
        """Set the current concern and matching row-level status.

        Arguments:
            state: subtitle validation state
            concern: current validation concern
        """
        if isinstance(concern, ErrorConcern):
            state.status = ValidationStatus.ERROR
        else:
            state.status = ValidationStatus.NEEDS_ACTION
        state.concern = concern

    def _replace_gap_text(
        self,
        sub_idx: int,
        *,
        start_idx: int,
        end_idx: int,
        replacement: str,
    ) -> SubtitleRowView:
        """Replace text between two non-whitespace characters.

        Arguments:
            sub_idx: zero-based subtitle index
            start_idx: start character index
            end_idx: end character index
            replacement: replacement gap text
        Returns:
            updated subtitle row view model
        """
        text = self.series.events[sub_idx].text_with_newline
        updated_text = f"{text[:start_idx]}{replacement}{text[end_idx:]}"
        return self.update_text(sub_idx, updated_text.replace("\n", "\\N"))

    def _resolve_adjacent_gap_action(
        self,
        cursor: GapCursor,
        cutoffs: tuple[int, int, int, int],
    ):
        """Update cutoffs after choosing adjacent spacing.

        Arguments:
            cursor: gap cursor
            cutoffs: current gap cutoffs
        """
        if cursor.gap <= cutoffs[0]:
            return
        if cursor.gap < cutoffs[1]:
            updated_cutoffs = (cursor.gap, cutoffs[1], cutoffs[2], cutoffs[3])
        else:
            updated_cutoffs = (cursor.gap, cursor.gap, cutoffs[2], cutoffs[3])
        self.manager._update_pair_gaps(cursor.char_pair, updated_cutoffs)

    def _resolve_space_gap_action(
        self,
        cursor: GapCursor,
        cutoffs: tuple[int, int, int, int],
        action: str,
    ) -> str:
        """Resolve one adjacent-or-space gap action.

        Arguments:
            cursor: gap cursor
            cutoffs: current gap cutoffs
            action: selected action
        Returns:
            replacement gap text
        """
        if action == "space":
            if cutoffs[0] < cursor.gap < cutoffs[1]:
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cursor.gap, cutoffs[2], cutoffs[3]),
                )
            return cursor.expected_space
        if action == "adjacent":
            self._resolve_adjacent_gap_action(cursor, cutoffs)
            return ""
        raise ValueError(f"Unrecognized space gap action: {action}")

    def _resolve_tab_gap_action(
        self,
        cursor: GapCursor,
        cutoffs: tuple[int, int, int, int],
        action: str,
    ) -> str:
        """Resolve one space-or-tab gap action.

        Arguments:
            cursor: gap cursor
            cutoffs: current gap cutoffs
            action: selected action
        Returns:
            replacement gap text
        """
        if action == "tab":
            if cutoffs[2] < cursor.gap < cutoffs[3]:
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cutoffs[1], cutoffs[2], cursor.gap),
                )
            return cursor.expected_tab
        if action == "space":
            if cutoffs[2] < cursor.gap < cutoffs[3]:
                self.manager._update_pair_gaps(
                    cursor.char_pair,
                    (cutoffs[0], cutoffs[1], cursor.gap, cutoffs[3]),
                )
            return cursor.expected_space
        raise ValueError(f"Unrecognized tab gap action: {action}")

    def _validated_n_bboxes(
        self,
        state: _SubtitleValidationState,
        n_bboxes: int,
    ) -> int:
        """Validate and clamp a bbox selection count.

        Arguments:
            state: subtitle validation state
            n_bboxes: requested bbox count
        Returns:
            validated bbox count
        """
        if n_bboxes < 1:
            return 1
        return min(n_bboxes, self._max_n_bboxes(state))

    def _validate_sub_idx(self, sub_idx: int):
        """Validate a subtitle index.

        Arguments:
            sub_idx: zero-based subtitle index
        """
        if sub_idx < 0 or sub_idx >= len(self.entries):
            raise IndexError(f"Subtitle index {sub_idx} out of range.")


def _gray_css(value: int) -> str:
    """Format a grayscale value as a CSS rgb color.

    Arguments:
        value: grayscale color value
    Returns:
        CSS rgb color
    """
    return f"rgb({value}, {value}, {value})"
