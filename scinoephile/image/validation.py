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


def get_max_gap(max_gaps: np.ndarray, x: int, y: int, interpolate: bool = False) -> int:
    """Retrieve value from array or interpolate using the average of all neighbors.

    Arguments:
        max_gaps: Array of maximum gaps
        x: Width of first character in pixels; used as row index
        y: Width of second character in pixels; used as column index
        interpolate: Whether to interpolate if value is zero
    Returns:
        Interpolated or original value
    """
    # If value is nonzero, return it directly
    if max_gaps[x, y] != 0:
        return max_gaps[x, y]

    if not interpolate:
        return 0

    # Get neighboring values (8-way connectivity)
    neighbors = []
    rows, cols = max_gaps.shape

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (dx != 0 or dy != 0):
                neighbors.append(max_gaps[nx, ny])

    # Average all neighbors
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

    # Load maximum gaps
    max_gaps_path = package_root / "data" / "ocr" / "max_gaps.csv"
    max_gaps = np.loadtxt(max_gaps_path, delimiter=",", dtype=int)

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
            if char_2 in ("\u3000", " "):
                whitespace += char_2
                char_2_i += 1
                continue
            else:
                break

        # Get gap between char 1 and char 2, and maximum expected gap
        gap = gaps[gap_i]
        try:
            max_gap = get_max_gap(max_gaps, char_1_width, char_2_width, False)
        except IndexError:
            # Expand max_gaps to fit new width(s) and resave
            max_gaps = np.pad(
                max_gaps,
                (
                    (0, max(0, char_1_width - max_gaps.shape[0] + 1)),
                    (0, max(0, char_2_width - max_gaps.shape[1] + 1)),
                ),
                "constant",
                constant_values=0,
            )
            np.savetxt(max_gaps_path, max_gaps, delimiter=",", fmt="%d")
            info(
                f"Expanded max_gaps to new size of {max_gaps.shape} and saved to "
                f"{max_gaps_path}."
            )
            max_gap = 0

        if max_gap > 0:
            if gap <= max_gap:
                pass
            elif gap <= max(max_gap + 1, np.floor(max_gap * 1.1)):
                max_gaps[char_1_width, char_2_width] = gap
                np.savetxt(max_gaps_path, max_gaps, delimiter=",", fmt="%d")
                info(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap:2d} pixels, "
                    f"exceeding max of {max_gap:2d} by less than 10%. "
                    f"Added ({char_1_width+1:2d},{char_2_width+1:2d}):{gap:2d} "
                    f"to max_gaps and saved to {max_gaps_path}."
                )
            else:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap:2d} pixels, "
                    f"exceeding max of {max_gap:2d} by more than 10%. "
                    f"May add ({char_1_width+1:2d},{char_2_width+1:2d}):{gap:2d} "
                    f"to max_gaps."
                )
        else:
            max_gap_interpolate = get_max_gap(
                max_gaps, char_1_width, char_2_width, True
            )
            if gap <= max_gap_interpolate:
                max_gaps[char_1_width, char_2_width] = gap
                np.savetxt(max_gaps_path, max_gaps, delimiter=",", fmt="%d")
                info(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap:2d} pixels, "
                    f"within interpolated max of {max_gap_interpolate:2d}. "
                    f"Added ({char_1_width+1:2d},{char_2_width+1:2d}):{gap:2d} "
                    f"to max_gaps and saved to {max_gaps_path}."
                )
            else:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap:2d} pixels, "
                    f"exceeding interpolated max of {max_gap_interpolate:2d}. "
                    f"May add ({char_1_width+1:2d},{char_2_width+1:2d}):{gap:2d} "
                    f"to max_gaps."
                )

        char_1_i = char_2_i
        char_1_width_i = char_2_width_i
        gap_i += 1
