#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info, warning
from pathlib import Path

from scinoephile.common.validation import validate_output_directory
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox_manager import BboxManager
from scinoephile.image.char_pair import CharPair
from scinoephile.image.drawing import (
    get_images_stacked,
    get_img_diff,
    get_img_of_text,
    get_img_of_text_with_bboxes,
    get_img_with_bbox,
    get_img_with_bboxes,
    get_img_with_white_bg,
)
from scinoephile.image.image_series import ImageSeries
from scinoephile.image.whitespace_manager import WhitespaceManager


def validate_ocr_hanzi(
    series: ImageSeries,
    output_path: Path | None = None,
    interactive: bool = True,
) -> None:
    """Validate OCR of a hanzi image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
        interactive: Whether to prompt user for input on proposed updates
    """
    if output_path:
        output_path = validate_output_directory(output_path)

    bbox_mgr = BboxManager()
    whitespace_mgr = WhitespaceManager()

    for i, event in enumerate(series.events, 1):
        # Prepare source image
        ref_img = get_img_with_white_bg(event.img)
        bboxes = bbox_mgr.get_bboxes(ref_img, event.text, interactive)

        try:
            messages = _validate_spaces_hanzi(
                event.text, bboxes, whitespace_mgr, interactive
            )
            if messages:
                for message in messages:
                    warning(f"Subtitle {i}: {message}")
        except ScinoephileException as exc:
            warning(f"Subtitle {i}: {exc}")

        # Skip if no output path
        if not output_path:
            continue

        # Draw annotated source image
        ref_annotated_img = get_img_with_bboxes(ref_img, bboxes)

        # Draw image of OCRed text, aligned to source image
        try:
            tst_img = get_img_of_text_with_bboxes(
                event.text,
                event.img.size,
                bboxes,
                fill_color=series.fill_color,
                outline_color=series.outline_color,
            )
        except ScinoephileException as exc:
            warning(f"Subtitle {i}: {exc}")
            tst_img = get_img_of_text(
                event.text,
                event.img.size,
                fill_color=series.fill_color,
                outline_color=series.outline_color,
            )
        tst_scaled_img = get_img_with_bbox(ref=ref_img, tst=tst_img)

        # Draw difference between source and OCRed text images
        diff_img = get_img_diff(ref_img, tst_scaled_img)

        # Stack images
        stack_img = get_images_stacked(ref_annotated_img, tst_scaled_img, diff_img)

        # Save image
        stack_img.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")


def _validate_spaces_hanzi(
    text: str,
    bboxes: list[tuple[int, int, int, int]],
    whitespace_mgr: WhitespaceManager,
    interactive: bool = True,
) -> list[str]:
    """Validate spacing in text by comparing with bbox gaps.

    Arguments:
        text: Provisional text
        bboxes: Bounding boxes [(x1, y1, x2, y2), ...]
        whitespace_mgr: Manages maximum gaps between characters of different types
        interactive: Whether to prompt user for input on proposed updates
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
    width_1_i = 0
    gap_i = 0
    while True:
        if char_1_i > len(text) - 2:
            break

        # Get char 1 and its width
        char_1 = text[char_1_i]
        width_1 = widths[width_1_i]

        # Get provisional char 2 and its width
        char_2_i = char_1_i + 1
        char_2 = text[char_2_i]
        width_2_i = width_1_i + 1
        width_2 = widths[width_2_i]

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
        pair = CharPair(char_1, char_2, width_1, width_2, gap, whitespace)
        message = whitespace_mgr.validate_gap(pair, interactive)
        if message:
            messages.append(message)

        char_1_i = char_2_i
        width_1_i = width_2_i
        gap_i += 1

    return messages
