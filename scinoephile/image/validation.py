#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info, warning
from pathlib import Path

from PIL import Image

from scinoephile.common.validation import validate_output_directory
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox_manager import BboxManager
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
from scinoephile.image.max_gap_manager import MaxGapManager


def validate_ocr_hanzi(series: ImageSeries, output_path: Path | None = None) -> None:
    """Validate OCR of a hanzi image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    if output_path:
        output_path = validate_output_directory(output_path)

    bbox_manager = BboxManager()
    max_gap_manager = MaxGapManager()

    for i, event in enumerate(series.events, 1):
        # Prepare source image
        img_with_white_bg = get_image_with_white_bg(event.img)
        bboxes = bbox_manager.get_char_bboxes(img_with_white_bg, event.text)

        try:
            messages = _validate_spaces_hanzi(event.text, bboxes, max_gap_manager)
            if messages:
                for message in messages:
                    warning(f"Subtitle {i}: {message}")
        except ScinoephileException as e:
            warning(f"Subtitle {i}: {e}")

        # Skip if no output path
        if not output_path:
            continue

        # Draw annotated source image
        img_with_bboxes = get_image_annotated_with_char_bboxes(
            img_with_white_bg, bboxes
        )

        # Draw image of OCRed text, aligned to source image
        try:
            img_of_text = get_image_of_text_with_char_alignment(
                event.text, event.img.size, bboxes
            )
        except ScinoephileException as e:
            img_of_text = get_image_of_text(event.text, event.img.size)
        img_of_text_scaled = get_image_scaled(img_with_white_bg, img_of_text)

        # Draw difference between source and OCRed text images
        img_diff = get_image_diff(img_with_white_bg, img_of_text_scaled)

        # Stack images
        img_stack = get_images_stacked(img_with_bboxes, img_of_text_scaled, img_diff)
        img_resized = img_stack.resize(
            (img_stack.width * 10, img_stack.height * 10), Image.NEAREST  # noqa
        )

        # Save image
        img_resized.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")


def _validate_spaces_hanzi(
    text: str, bboxes: list[tuple[int, int, int, int]], max_gap_manager: MaxGapManager
) -> list[str]:
    """Validate spacing in text by comparing with bbox gaps.

    Arguments:
        text: Provisional text
        bboxes: Bounding boxes [(x1, y1, x2, y2), ...]
        max_gap_manager: Manages maximum gaps between characters of different types
    """
    # Calculate widths and gaps
    widths = [bboxes[i][2] - bboxes[i][0] for i in range(len(bboxes))]
    heights = [bboxes[i][3] - bboxes[i][1] for i in range(len(bboxes))]
    gaps = [bboxes[i + 1][0] - bboxes[i][2] for i in range(len(bboxes) - 1)]

    # Validation requires a 1:1 mapping between bboxes and characters
    filtered_text = "".join([char for char in text if char not in ("\u3000", " ")])
    if len(filtered_text) != len(bboxes):
        dimensions_str = (
            ",".join(f"{w:3d},{h:3d},{g:3d}" for w, h, g in zip(widths, heights, gaps))
            + f",{widths[-1]:3d},{heights[-1]:3d}"
        )
        labels_str = (
            ",".join(f"W{i+1:<2d},H{i+1:<2d},G{i+1:<2d}" for i in range(len(gaps)))
            + f",W{len(widths):<2d},H{len(heights):<2d}"
        )
        raise ScinoephileException(
            f"Number of characters in text ({len(filtered_text)}) "
            f"does not match number of boxes ({len(bboxes)});\n"
            f"Text: {text}\n"
            f"Dimensions: {dimensions_str}\n"
            f"Labels:     {labels_str}"
        )

    # Iterate through text and assess gaps
    messages = []
    char_1_i = 0
    char_1_width_i = 0
    gap_i = 0
    while True:
        if char_1_i > len(text) - 2:
            break

        # Get char 1 and its width
        char_1 = text[char_1_i]
        char_1_width = widths[char_1_width_i]

        # Get provisional char 2 and its width
        char_2_i = char_1_i + 1
        char_2 = text[char_2_i]
        char_2_width_i = char_1_width_i + 1
        char_2_width = widths[char_2_width_i]

        # If char 2 is whitespace, iterate to next real char and track whitespace
        whitespace = ""
        while char_2_i < len(text):
            char_2 = text[char_2_i]
            if char_2 in ("\u3000", " "):
                whitespace += char_2
                char_2_i += 1
                continue
            else:
                break

        # Get gap between char 1 and char 2, and maximum expected gap
        gap = gaps[gap_i]
        message = max_gap_manager.validate_gap(
            char_1, char_2, char_1_width, char_2_width, gap, whitespace
        )
        if message:
            messages.append(message)

        char_1_i = char_2_i
        char_1_width_i = char_2_width_i
        gap_i += 1

    return messages
