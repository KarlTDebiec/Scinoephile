#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages OCR validation."""

from __future__ import annotations

import shutil
from logging import info, warning
from pathlib import Path

from scinoephile.common.typing import PathLike
from scinoephile.common.validation import validate_input_directory, validate_input_file
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox_manager import BboxManager
from scinoephile.image.drawing import (
    get_img_diff,
    get_img_of_text,
    get_img_of_text_with_bboxes,
    get_img_scaled_to_bbox,
    get_imgs_stacked,
)
from scinoephile.image.image_series import ImageSeries
from scinoephile.image.image_subtitle import ImageSubtitle
from scinoephile.image.whitespace_manager import WhitespaceManager


class ValidationManager:
    """Manages OCR validation."""

    def __init__(
        self,
        input_dir_path: PathLike,
        validation_dir_path: Path | None = None,
        interactive: bool = True,
    ):
        """Initialize.

        Arguments:
            input_dir_path: Directory containing image series to validate
            validation_dir_path: Directory in which to save validation results
            interactive: Whether to prompt user for input on proposed updates
        """
        self.series_dir_path = validate_input_directory(input_dir_path)
        self.series_path = validate_input_file(
            self.series_dir_path / f"{self.series_dir_path.name}.srt"
        )
        self.validation_dir_path = None
        if validation_dir_path:
            self.validation_dir_path = validate_input_directory(validation_dir_path)
        self.interactive = interactive

        self.series = ImageSeries.load(input_dir_path)
        self.bbox_mgr = BboxManager()
        self.whitespace_mgr = WhitespaceManager()

    def validate(self) -> None:
        """Validate OCR of image series."""
        series_changed = False
        for i, subtitle in enumerate(self.series.events, 1):
            subtitle_changed = self._validate_subtitle(subtitle, i)
            if subtitle_changed:
                series_changed = True

        if series_changed:
            self.series.save(self.series_path)
            info(f"Saved changes to {self.series_path}.")

        if self.validation_dir_path is not None:
            series_index_path = self.validation_dir_path / "index.html"
            validation_index_path = self.validation_dir_path / "index.html"
            if series_index_path.exists() and not validation_index_path.exists():
                shutil.copy(series_index_path, validation_index_path)

    def _validate_subtitle(self, subtitle: ImageSubtitle, i: int) -> bool:
        """Validate OCR of a single subtitle in the series.

        Arguments:
            subtitle: Subtitle to validate
            i: Index of the subtitle in the series
        Returns:
            Whether the subtitle was changed
        """
        if subtitle.bboxes is None:
            subtitle.bboxes = self.bbox_mgr.get_bboxes(subtitle, self.interactive)

        try:
            if len(subtitle.text_excluding_whitespace) != len(subtitle.bboxes):
                raise ScinoephileException(
                    f"Number of characters in text "
                    f"({len(subtitle.text_excluding_whitespace)}) "
                    f"does not match number of boxes "
                    f"({len(subtitle.bboxes)});\n"
                    f"Text: {subtitle.text}\n"
                )
            self.whitespace_mgr.validate(subtitle, i, self.interactive)
        except Exception as exc:
            warning(f"Subtitle {i}: {exc}")

        if self.validation_dir_path is not None:
            self._save_validation_img(subtitle, i)

    def _save_validation_img(self, subtitle: ImageSubtitle, i: int) -> None:
        if self.validation_dir_path is None:
            raise ScinoephileException(
                "Validation directory path is not set; cannot save validation image."
            )

        # Draw image of OCRed text
        try:
            tst_img = get_img_of_text_with_bboxes(
                subtitle.text,
                subtitle.img.size,
                subtitle.bboxes,
                fill_color=self.series.fill_color,
                outline_color=self.series.outline_color,
            )
        except ScinoephileException as exc:
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
