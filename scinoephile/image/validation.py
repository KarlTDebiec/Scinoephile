#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info
from pathlib import Path

from PIL import Image

from scinoephile.common.validation import validate_output_directory
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox import get_char_bboxes
from scinoephile.image.drawing import (
    get_image_annotated_with_char_bboxes,
    get_image_diff,
    get_image_of_text,
    get_image_of_text_with_char_alignment,
    get_image_scaled,
    get_image_with_white_bg,
    get_images_stacked,
)
from scinoephile.image.image_series import ImageSeries


def validate_ocr_hanzi(series: ImageSeries, output_path: Path) -> None:
    """Validate OCR of a hanzi image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    output_path = validate_output_directory(output_path)

    for i, event in enumerate(series.events, 1):
        # Prepare source image
        img_with_white_bg = get_image_with_white_bg(event.img)
        bboxes = get_char_bboxes(img_with_white_bg)
        img_with_bboxes = get_image_annotated_with_char_bboxes(
            img_with_white_bg, bboxes
        )

        # Draw image of OCRed text, aligned to source image
        try:
            img_of_text = get_image_of_text_with_char_alignment(
                event.text, event.img.size, bboxes
            )
        except ScinoephileException as e:
            info(f"Subtitle {i} encountered the following exception: {e}")
            img_of_text = get_image_of_text(event.text, event.img.size)
        img_of_text_scaled = get_image_scaled(img_with_white_bg, img_of_text)

        # Draw difference between source and OCRed text images
        img_diff = get_image_diff(img_with_white_bg, img_of_text_scaled)

        # Stack images and rescale for convenience
        img_stack = get_images_stacked(img_with_bboxes, img_of_text_scaled, img_diff)
        img_resized = img_stack.resize(
            (img_stack.width * 10, img_stack.height * 10), Image.NEAREST  # noqa
        )

        # Save image
        img_resized.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")
