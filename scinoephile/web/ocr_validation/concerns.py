#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""View models for OCR validation web concerns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from scinoephile.lang.cmn.romanization import get_cmn_char_romanized
from scinoephile.lang.yue.romanization import get_yue_char_romanized

__all__ = [
    "CharDimsConcern",
    "ConcernKind",
    "ErrorConcern",
    "GapConcern",
    "OcrConcern",
    "SubtitleRowView",
    "ValidationStatus",
]


class ConcernKind(StrEnum):
    """Kinds of OCR validation concerns shown by the web UI."""

    CHAR_DIMS = "char-dims"
    """Character bbox dimensions need confirmation."""
    SPACE_GAP = "space-gap"
    """Gap may need a normal space."""
    TAB_GAP = "tab-gap"
    """Gap may need a tab or wide space."""
    ERROR = "error"
    """Validation cannot continue for this subtitle."""


@dataclass(frozen=True)
class CharDimsConcern:
    """Character bbox dimensions needing user confirmation."""

    sub_idx: int
    """Zero-based subtitle index."""
    char_idx: int
    """Zero-based character index."""
    bbox_idx: int
    """Zero-based bbox index."""
    n_bboxes: int
    """Number of bboxes currently selected."""
    max_n_bboxes: int
    """Maximum number of bboxes available for selection."""
    char: str
    """Character being validated."""
    dims: tuple[int, ...]
    """Dimensions of the selected bbox group."""
    kind: ConcernKind = field(default=ConcernKind.CHAR_DIMS, init=False)
    """Concern kind."""

    @property
    def can_contract(self) -> bool:
        """Whether the current bbox selection can be contracted."""
        return self.n_bboxes > 1

    @property
    def can_expand(self) -> bool:
        """Whether the current bbox selection can be expanded."""
        return self.n_bboxes < self.max_n_bboxes

    @property
    def char_pinyin(self) -> str:
        """Pinyin for the character being validated."""
        return get_cmn_char_romanized(self.char)

    @property
    def char_yale(self) -> str:
        """Cantonese Yale for the character being validated."""
        return get_yue_char_romanized(self.char)

    @property
    def status_label(self) -> str:
        """Short status label for templates."""
        return "Check character box"


@dataclass(frozen=True)
class ErrorConcern:
    """Validation concern representing an unrecoverable state."""

    message: str
    """Error message."""
    kind: ConcernKind = field(default=ConcernKind.ERROR, init=False)
    """Concern kind."""

    @property
    def status_label(self) -> str:
        """Short status label for templates."""
        return "Needs review"


@dataclass(frozen=True)
class GapConcern:
    """Ambiguous gap between adjacent characters."""

    sub_idx: int
    """Zero-based subtitle index."""
    char_1_idx: int
    """Zero-based first character index."""
    char_2_idx: int
    """Zero-based second character index."""
    char_1: str
    """First character."""
    char_2: str
    """Second character."""
    gap: int
    """Observed pixel gap."""
    space_prompt: tuple[int, int]
    """Gap range prompting for a normal space."""
    tab_prompt: tuple[int, int]
    """Gap range prompting for a tab or wide space."""
    observed: str
    """Observed text between characters."""
    expected: str
    """Proposed replacement gap text."""
    kind: ConcernKind
    """Concern kind."""

    @property
    def action_options(self) -> tuple[tuple[str, str], ...]:
        """Form actions available for this gap prompt."""
        if self.kind == ConcernKind.SPACE_GAP:
            return (("adjacent", "Adjacent"), ("space", "Space"))
        if self.kind == ConcernKind.TAB_GAP:
            return (("space", "Space"), ("tab", "Tab"))
        raise ValueError(f"Invalid gap concern kind: {self.kind}")

    @property
    def char_1_pinyin(self) -> str:
        """Pinyin for the first character."""
        return get_cmn_char_romanized(self.char_1)

    @property
    def char_1_yale(self) -> str:
        """Cantonese Yale for the first character."""
        return get_yue_char_romanized(self.char_1)

    @property
    def char_2_pinyin(self) -> str:
        """Pinyin for the second character."""
        return get_cmn_char_romanized(self.char_2)

    @property
    def char_2_yale(self) -> str:
        """Cantonese Yale for the second character."""
        return get_yue_char_romanized(self.char_2)

    @property
    def expected_display(self) -> str:
        """Proposed replacement gap text for display."""
        escaped = self.expected.replace("\n", "\\n")
        return f"'{escaped}'"

    @property
    def observed_display(self) -> str:
        """Observed gap text for display."""
        escaped = self.observed.replace("\n", "\\n")
        return f"'{escaped}'"

    @property
    def space_prompt_display(self) -> str:
        """Gap range prompting for a normal space, formatted for display."""
        return f"{self.space_prompt[0]}-{self.space_prompt[1]}"

    @property
    def status_label(self) -> str:
        """Short status label for templates."""
        if self.kind == ConcernKind.TAB_GAP:
            return "Check wide spacing"
        return "Check spacing"

    @property
    def tab_prompt_display(self) -> str:
        """Gap range prompting for a tab or wide space, formatted for display."""
        return f"{self.tab_prompt[0]}-{self.tab_prompt[1]}"


class ValidationStatus(StrEnum):
    """Row-level OCR validation status."""

    DONE = "done"
    """Subtitle has no unresolved concerns."""
    ERROR = "error"
    """Subtitle validation hit an unrecoverable state."""
    NEEDS_ACTION = "needs-action"
    """Subtitle has a concern awaiting human action."""


@dataclass(frozen=True)
class SubtitleRowView:
    """Template view model for one OCR subtitle row."""

    sub_idx: int
    """Zero-based subtitle index."""
    number: int
    """One-based subtitle number."""
    start: str
    """Formatted subtitle start time."""
    end: str
    """Formatted subtitle end time."""
    image_width: int
    """Subtitle image width in pixels."""
    image_height: int
    """Subtitle image height in pixels."""
    text: str
    """Editable subtitle OCR text."""
    concern: OcrConcern | None
    """Current validation concern for this subtitle."""
    text_color_css: str = "rgb(255, 255, 255)"
    """Detected subtitle fill color as a CSS color."""
    text_shadow_color_css: str = "rgb(0, 0, 0)"
    """Detected subtitle outline color as a CSS color."""
    text_font_size_px: int = 50
    """Detected series subtitle font size in pixels."""
    text_letter_spacing_px: int = 10
    """Detected subtitle letter spacing in pixels."""

    @property
    def image_cache_key(self) -> str:
        """Cache key for dynamic validation images."""
        if isinstance(self.concern, CharDimsConcern):
            return (
                f"{self.concern.kind}-{self.concern.char_idx}-"
                f"{self.concern.bbox_idx}-{self.concern.n_bboxes}"
            )
        if isinstance(self.concern, GapConcern):
            return (
                f"{self.concern.kind}-{self.concern.char_1_idx}-"
                f"{self.concern.char_2_idx}-{self.concern.gap}"
            )
        return str(self.status)

    @property
    def has_concern_image(self) -> bool:
        """Whether this row should render the focused concern image."""
        return isinstance(self.concern, CharDimsConcern | GapConcern)

    @property
    def status(self) -> ValidationStatus:
        """Row-level validation status."""
        if self.concern is None:
            return ValidationStatus.DONE
        if isinstance(self.concern, ErrorConcern):
            return ValidationStatus.ERROR
        return ValidationStatus.NEEDS_ACTION

    @property
    def status_label(self) -> str:
        """Short validation status label."""
        if self.concern is not None:
            return self.concern.status_label
        return "OK"

    @property
    def text_font_size_cqw_css(self) -> str:
        """Detected series subtitle font size as a container query length."""
        return _px_to_cqw_css(self.text_font_size_px, self.image_width)

    @property
    def text_font_size_css(self) -> str:
        """Detected series subtitle font size as a CSS length."""
        return f"{self.text_font_size_px}px"

    @property
    def text_letter_spacing_css(self) -> str:
        """Subtitle letter spacing as a CSS length."""
        return f"{self.text_letter_spacing_px}px"

    @property
    def text_letter_spacing_cqw_css(self) -> str:
        """Subtitle letter spacing as a container query length."""
        return _px_to_cqw_css(self.text_letter_spacing_px, self.image_width)


OcrConcern = CharDimsConcern | ErrorConcern | GapConcern
"""Validation concern shown by the OCR validation web UI."""


def _px_to_cqw_css(value: int, container_width: int) -> str:
    """Convert a pixel length to an equivalent container query width length.

    Arguments:
        value: pixel length at the container's natural width
        container_width: natural container width in pixels
    Returns:
        CSS container query width length
    """
    if container_width <= 0:
        return f"{value}px"
    return f"{(value * 100) / container_width:.6g}cqw"
