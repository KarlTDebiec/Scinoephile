#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocols for OCR validation inputs."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol

from PIL import Image

__all__ = ["OcrSeries", "OcrSubtitle"]


class OcrSubtitle(Protocol):
    """Protocol for image subtitle objects used by OCR validation."""

    text: str

    @property
    def text_without_whitspace(self) -> str:
        """Text excluding whitespace."""

    @property
    def bboxes(self) -> list[tuple[int, int, int, int]] | None:
        """Bounding boxes for each non-whitespace character."""

    @bboxes.setter
    def bboxes(self, bboxes: list[tuple[int, int, int, int]]):  # noqa: D105
        ...

    @property
    def img(self) -> Image.Image:
        """Image of the subtitle."""

    @property
    def img_with_white_bg(self) -> Image.Image:
        """Image with white background."""

    @property
    def img_with_bboxes(self) -> Image.Image:
        """Image with bounding boxes."""


class OcrSeries(Protocol):
    """Protocol for image subtitle series used by OCR validation."""

    fill_color: int
    outline_color: int

    def __iter__(self) -> Iterator[OcrSubtitle]:
        """Iterate through the series."""

    def save(self, path: str) -> None:
        """Save the series to a path."""

    def __len__(self) -> int:
        """Return number of subtitles."""
