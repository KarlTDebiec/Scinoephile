#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages OCR validation."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from logging import info, warning
from pathlib import Path

from scinoephile.common.validation import val_input_dir_path, val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.image.drawing import (
    get_img_diff,
    get_img_of_text,
    get_img_of_text_with_bboxes,
    get_img_scaled_to_bbox,
    get_imgs_stacked,
)

from .bbox_manager import BboxManager
from .types import OcrSeries, OcrSubtitle
from .whitespace_manager import WhitespaceManager

__all__ = ["ValidationManager"]


class ValidationManager:
    """Manages OCR validation."""

    def __init__(
        self,
        series: OcrSeries,
        series_path: Path | str | None = None,
        series_dir_path: Path | str | None = None,
        validation_dir_path: Path | None = None,
        interactive: bool = True,
    ):
        """Initialize.

        Arguments:
            series: Image series to validate
            series_path: Path for saving updated series
            series_dir_path: Directory containing image series to validate
            validation_dir_path: Directory in which to save validation results
            interactive: Whether to prompt user for input on proposed updates
        """
        self.series = series
        self.series_path = (
            Path(series_path).resolve() if series_path is not None else None
        )
        self.series_dir_path = (
            val_input_dir_path(series_dir_path) if series_dir_path is not None else None
        )
        self.validation_dir_path = (
            val_output_dir_path(validation_dir_path) if validation_dir_path else None
        )
        self.interactive = interactive

        self.bbox_mgr = BboxManager()
        self.whitespace_mgr = WhitespaceManager()

    @classmethod
    def from_input_dir(
        cls,
        input_dir_path: Path | str,
        series_loader: Callable[[Path | str], OcrSeries],
        validation_dir_path: Path | str | None = None,
        interactive: bool = True,
    ) -> ValidationManager:
        """Create validation manager using a series loader.

        Arguments:
            input_dir_path: Directory containing image series to validate
            series_loader: Callable that loads a series from a path
            validation_dir_path: Directory in which to save validation results
            interactive: Whether to prompt user for input on proposed updates
        Returns:
            ValidationManager instance
        """
        series_dir_path = val_input_dir_path(input_dir_path)
        series_path = (series_dir_path / f"{series_dir_path.name}.srt").resolve()
        series = series_loader(input_dir_path)
        return cls(
            series=series,
            series_path=series_path,
            series_dir_path=series_dir_path,
            validation_dir_path=validation_dir_path,
            interactive=interactive,
        )

    def validate(self) -> None:
        """Validate OCR of image series."""
        series_changed = False
        for i, subtitle in enumerate(self.series, 1):
            subtitle_changed = self._validate_subtitle(subtitle, i)
            if subtitle_changed:
                series_changed = True

        if series_changed and self.series_path is not None:
            self.series.save(self.series_path)
            info(f"Saved changes to {self.series_path}.")

        if self.validation_dir_path is not None and self.series_dir_path is not None:
            series_index_path = self.series_dir_path / "index.html"
            validation_index_path = self.validation_dir_path / "index.html"
            if series_index_path.exists() and not validation_index_path.exists():
                shutil.copy(series_index_path, validation_index_path)

    def _validate_subtitle(self, subtitle: OcrSubtitle, i: int) -> bool:
        """Validate OCR of a single subtitle in the series.

        Arguments:
            subtitle: Subtitle to validate
            i: Index of the subtitle in the series
        Returns:
            Whether the subtitle was changed
        """
        original_text = subtitle.text
        if subtitle.bboxes is None:
            subtitle.bboxes = self.bbox_mgr.get_bboxes(subtitle, self.interactive)

        try:
            if subtitle.bboxes is None:
                raise ScinoephileError("No bboxes found after bbox detection.")
            if len(subtitle.text_without_whitspace) != len(subtitle.bboxes):
                raise ScinoephileError(
                    f"Number of characters in text "
                    f"({len(subtitle.text_without_whitspace)}) "
                    f"does not match number of boxes "
                    f"({len(subtitle.bboxes)});\n"
                    f"Text: {subtitle.text}\n"
                )
            self.whitespace_mgr.validate(subtitle, i, self.interactive)
        except Exception as exc:
            warning(f"Subtitle {i}: {exc}")

        if self.validation_dir_path is not None:
            self._save_validation_img(subtitle, i)
        return subtitle.text != original_text

    def _save_validation_img(self, subtitle: OcrSubtitle, i: int) -> None:
        if self.validation_dir_path is None:
            raise ScinoephileError(
                "Validation directory path is not set; cannot save validation image."
            )
        if subtitle.bboxes is None:
            raise ScinoephileError("No bboxes found for validation image.")

        # Draw image of OCRed text
        try:
            tst_img = get_img_of_text_with_bboxes(
                subtitle.text,
                subtitle.img.size,
                subtitle.bboxes,
                fill_color=self.series.fill_color,
                outline_color=self.series.outline_color,
            )
        except ScinoephileError as exc:
            warning(f"Subtitle {i}: {exc}")
            tst_img = get_img_of_text(
                subtitle.text,
                subtitle.img.size,
                fill_color=self.series.fill_color,
                outline_color=self.series.outline_color,
            )
            tst_img = get_img_scaled_to_bbox(subtitle.img, tst_img)

        # Draw diff between source and OCRed text images
        diff_img = get_img_diff(subtitle.img_with_white_bg, tst_img)

        # Draw stacked image
        stack_img = get_imgs_stacked(subtitle.img_with_bboxes, tst_img, diff_img)

        # Save image
        img_path = self.validation_dir_path / f"{i:04d}.png"
        stack_img.save(img_path)
        info(f"Saved {img_path}")
