#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""View models for OCR validation web concerns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import ClassVar

from scinoephile.image.bbox import Bbox
from scinoephile.lang.cmn.romanization import get_cmn_char_romanized
from scinoephile.lang.yue.romanization import get_yue_char_romanized

from .measurement_images import NumberLineBand, NumberLineImage, get_number_line_image
from .size_maps import CharacterSizeMap, get_character_size_maps

__all__ = [
    "FILTER_OPTIONS",
    "CharDimsConcern",
    "ConcernKind",
    "ErrorConcern",
    "GapConcern",
    "OcrConcern",
    "SubtitleRowView",
    "get_review_status",
]

FILTER_OPTIONS = {
    "needs-review": ("Needs review", "alert-circle-outline"),
    "boxes": ("Bounding boxes need review", "alert-circle-outline"),
    "character": ("Characters need review", "text-box-edit-outline"),
    "spacing": ("Spacing needs review", "minus-box-outline"),
    "done": ("Validated", "checkbox-marked"),
}
"""Labels and icons for the OCR review filters."""


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


@dataclass(frozen=True)
class ErrorConcern:
    """Validation concern requiring a manual correction before scanning can continue."""

    message: str
    """Error message."""
    bbox_count_mismatch: bool = False
    """Whether the scan ran out of boxes or found boxes left over."""
    kind: ConcernKind = field(default=ConcernKind.ERROR, init=False)
    """Concern kind."""


@dataclass(frozen=True)
class GapConcern:
    """Ambiguous gap between adjacent characters."""

    scale_colors: ClassVar[dict[str, tuple[str, str]]] = {
        "adjacent": ("#758395", "#9aaabc"),
        "space-prompt": ("#ad7000", "#e3b252"),
        "space": ("#356ac3", "#75a8f5"),
        "tab-prompt": ("#af5041", "#ed9689"),
        "tab": ("#267763", "#67c6ae"),
    }
    """Light and dark colors shared by the scale image and legend."""

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
    def action_options(self) -> tuple[tuple[str, str, int], ...]:
        """Form actions with labels and the displayed boundary each changes.

        Raises:
            ValueError: if a value is invalid
        """
        # Show the final pixel in the prompt range for actions that lower a cutoff
        if self.kind == ConcernKind.SPACE_GAP:
            return (
                ("adjacent", "Auto adjacent", self.space_prompt[0]),
                ("space", "Auto space", self.space_prompt[1] - 1),
            )
        if self.kind == ConcernKind.TAB_GAP:
            return (
                ("space", "Auto space", self.tab_prompt[0]),
                ("tab", "Auto tab", self.tab_prompt[1] - 1),
            )
        raise ValueError(f"Invalid gap concern kind: {self.kind}")

    @property
    def scale_bands(self) -> tuple[NumberLineBand, ...]:
        """Number line bands with inclusive pixel bounds and None for open ends."""
        adjacent, space_start = self.space_prompt
        space_end, tab = self.tab_prompt
        bands: tuple[NumberLineBand, ...] = (
            ("adjacent", "Auto adjacent", None, adjacent),
            ("space-prompt", "Prompt for space", adjacent + 1, space_start - 1),
            ("space", "Auto space", max(adjacent + 1, space_start), space_end),
            ("tab-prompt", "Prompt for tab", space_end + 1, tab - 1),
            ("tab", "Auto tab", max(space_end + 1, tab), None),
        )
        return tuple(
            band
            for band in bands
            if band[2] is None or band[3] is None or band[2] <= band[3]
        )

    @property
    def scale_image(self) -> NumberLineImage:
        """Rendered spacing scale with the observed gap marked."""
        return get_number_line_image(
            self.scale_ticks,
            self.scale_bands,
            self.scale_colors,
            width=480,
            reading=self.gap,
        )

    @property
    def scale_ticks(self) -> range:
        """Number line ticks covering zero, the gap, and both prompt ranges."""
        lower = min(0, self.gap, self.space_prompt[0])
        # Show at least 200 px and leave room for the automatic tab band
        upper = max(199, self.gap, self.tab_prompt[1])
        step = max(50, (upper - lower + 249) // 250 * 50)
        return range(lower // step * step, (upper // step + 2) * step, step)


@dataclass(frozen=True)
class SubtitleRowView:
    """Template view model for one OCR subtitle row."""

    sub_idx: int
    """Zero-based subtitle index."""
    number: int
    """One-based subtitle number."""
    start: int
    """Subtitle start time in milliseconds."""
    end: int
    """Subtitle end time in milliseconds."""
    image_width: int
    """Subtitle image width in pixels."""
    image_height: int
    """Subtitle image height in pixels."""
    text: str
    """Editable subtitle OCR text."""
    concern: OcrConcern | None
    """Current validation concern for this subtitle."""
    boxes: tuple[Bbox, ...] = ()
    """Boxes to overlay on the source subtitle image."""
    text_color_css: str = "rgb(255, 255, 255)"
    """Detected subtitle fill color as a CSS color."""
    text_shadow_color_css: str = "rgb(0, 0, 0)"
    """Detected subtitle outline color as a CSS color."""
    text_font_size_px: int = 50
    """Detected series subtitle font size in pixels."""
    text_letter_spacing_px: int = 10
    """Detected subtitle letter spacing in pixels."""
    known_char_dims: tuple[tuple[int, ...], ...] = ()
    """Stored configurations for the current character and box count."""

    @property
    def character_size_maps(self) -> tuple[CharacterSizeMap, ...]:
        """Size maps for the current character concern, rendered on demand."""
        if isinstance(self.concern, CharDimsConcern):
            return get_character_size_maps(self.concern.dims, self.known_char_dims)
        return ()

    @property
    def editable_text(self) -> str:
        """Subtitle text with literal line breaks for a textarea."""
        return self.text.replace("\\N", "\n")

    @property
    def status(self) -> str:
        """Validation status key shared with the review filter."""
        return get_review_status(self.concern)

    @property
    def status_label(self) -> str:
        """Validation status label shared with the review filter."""
        return FILTER_OPTIONS[self.status][0]

    @property
    def text_font_size_cqw_css(self) -> str:
        """Detected series subtitle font size as a container query length."""
        return _px_to_cqw_css(self.text_font_size_px, self.image_width)

    @property
    def text_letter_spacing_cqw_css(self) -> str:
        """Subtitle letter spacing as a container query length."""
        return _px_to_cqw_css(self.text_letter_spacing_px, self.image_width)

    @property
    def version(self) -> str:
        """Identify the text and specific concern a form was rendered for."""
        return sha256(f"{self.text!r}:{self.concern!r}".encode()).hexdigest()


OcrConcern = CharDimsConcern | ErrorConcern | GapConcern
"""Validation concern shown by the OCR validation web UI."""


def get_review_status(concern: OcrConcern | None) -> str:
    """Get the review filter key for a subtitle's current concern.

    Arguments:
        concern: current unresolved concern, if any
    Returns:
        matching review status key
    """
    if concern is None:
        return "done"
    if isinstance(concern, ErrorConcern) and concern.bbox_count_mismatch:
        return "boxes"
    if isinstance(concern, CharDimsConcern):
        return "character"
    return "spacing"


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
