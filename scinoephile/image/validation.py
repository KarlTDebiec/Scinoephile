#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info, warning
from pathlib import Path

import numpy as np
from PIL import Image

from scinoephile.common import package_root
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

max_gaps = np.loadtxt(
    package_root / "data" / "ocr" / "max_gaps.csv", delimiter=",", dtype=int
)


def create_max_gap_array(max_gaps: dict[tuple[int, int], int]) -> np.ndarray:
    """Create a 2D NumPy array from a dictionary of (x, y) -> z mappings.

    Arguments:
        max_gaps: Dictionary mapping (x, y) pairs to z values.

    Returns:
        A NumPy array of shape (max_x + 1, max_y + 1) where known (x, y) pairs
        are filled with z, and all other positions are 0.
    """
    # Find max x and y to determine array size
    max_x = max(x for x, y in max_gaps)
    max_y = max(y for x, y in max_gaps)

    # Initialize 2D array filled with zeros
    arr = np.zeros((max_x + 1, max_y + 1), dtype=int)

    # Fill the array with z values from the dictionary
    for (x, y), z in max_gaps.items():
        arr[x, y] = z

    return arr


def get_max_gap(x: int, y: int) -> int:
    """Retrieve value from array or interpolate using the average of all neighbors.

    Arguments:
        x: X-coordinate (row index).
        y: Y-coordinate (column index).
    Returns:
        Interpolated or original value.
    """
    # If value is nonzero, return it directly
    if max_gaps[x, y] != 0:
        return max_gaps[x, y]

    # Get neighboring values (8-way connectivity)
    neighbors = []
    rows, cols = max_gaps.shape

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (dx != 0 or dy != 0):
                neighbors.append(max_gaps[nx, ny])  # Include zeros

    # Average all neighbors (zeros included)
    return int(sum(neighbors) / len(neighbors)) if neighbors else 0


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
            validate_spaces_hanzi(event.text, bboxes)
        except ScinoephileException as e:
            warning(f"Subtitle {i} encountered the following exception: {e}")
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


def validate_spaces_hanzi(text: str, bboxes: list[tuple[int, int, int, int]]) -> None:
    """Validate spacing in text by comparing with bbox gaps.

    Arguments:
        text: Text to validate
        bboxes: Bounding boxes [(x1, y1, x2, y2), ...]
    """
    # Check if validation is possible
    filtered_text = "".join([char for char in text if char not in ("\u3000", " ")])
    if len(filtered_text) != len(bboxes):
        raise ScinoephileException(
            f"Number of characters in text ({len(filtered_text)})"
            f" does not match number of boxes ({len(bboxes)})"
        )

    # Calculate widths and gaps
    widths = [bboxes[i][2] - bboxes[i][0] for i in range(len(bboxes))]
    gaps = [bboxes[i + 1][0] - bboxes[i][2] for i in range(len(bboxes) - 1)]

    # Iterate through text and assess gaps
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
        while char_2_i < len(text) - 1:
            char_2 = text[char_2_i]
            if char_2 in (" ", "\u3000"):
                whitespace += char_2
                char_2_i += 1
                continue
            else:
                break

        # Get gap between char 1 and char 2, and maximum expected gap
        gap = gaps[gap_i]
        max_gap = get_max_gap(char_1_width, char_2_width)

        if gap > max_gap:
            if whitespace:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap} pixels, exceeding max of {max_gap}. "
                    f"Separated by whitespace '{whitespace}'."
                )
            else:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap} pixels, exceeding max of {max_gap}. "
                    f"(May add  ({char_1_width+1},{char_2_width+1}):{gap},  to max_gaps)"
                )
        char_1_i = char_2_i
        char_1_width_i = char_2_width_i
        gap_i += 1
